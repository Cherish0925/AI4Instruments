"""Turn reported connections into identified, reusable instrument configurations."""
import copy
import csv
import hashlib
import json
import re
import threading
import time
import string
from concurrent.futures import ThreadPoolExecutor, as_completed
from .discovery import connection_key, device_connection
from .store import now


def same_registration(saved, requested):
    enriched = bool(saved.get('instrument_profile'))
    saved, requested = copy.deepcopy(saved), copy.deepcopy(requested)
    for row in (saved, requested):
        row.pop('id', None)
    for key in ('identity', 'identity_source', 'instrument_profile', 'documentation', 'profile_candidates'):
        if key not in requested:
            saved.pop(key, None)
    # Enrichment adds named operations; repeating the original registration remains idempotent.
    if enriched and 'operations' not in requested.get('config', {}) and saved.get('config'):
        saved['config'].pop('operations', None)
    return saved == requested


def validate_profile(profile):
    from .platforms import name
    name(profile['id'], 'Instrument profile ID')
    match = profile.get('match', {})
    if not isinstance(match, dict) or not match.get('manufacturer') or not match.get('model'):
        raise ValueError('Specify manufacturer and model for an instrument description.')
    if set(match) - {'manufacturer', 'model', 'serial_number', 'firmware'}:
        raise ValueError('Match manufacturer, model, serial_number or firmware.')
    for value in match.values():
        values = value if isinstance(value, list) else [value]
        if not values or any(not isinstance(v, str) or not v.strip() for v in values):
            raise ValueError('Match values must be nonempty names or lists of names.')
    if profile.get('driver', 'scpi') != 'scpi':
        raise ValueError('Instrument profiles describe SCPI operations. Use a discovery profile for an SDK driver.')
    config = profile.get('config', {})
    if not isinstance(config, dict) or set(config) - {'name', 'operations'}:
        raise ValueError('A model description contains a name and operations; connection settings belong to the instrument.')
    operations = config.get('operations', {})
    if not isinstance(operations, dict) or not operations:
        raise ValueError('Provide named instrument operations.')
    if set(operations) & {'identify', 'query', 'write'}:
        raise ValueError('Use descriptive operation names; identify, query and write are provided by the driver.')
    for operation, spec in operations.items():
        name(operation, 'Operation name')
        if not isinstance(spec, dict) or ('query' in spec) == ('write' in spec):
            raise ValueError('Each operation needs exactly one query or write command.')
        command = spec.get('query', spec.get('write'))
        params = spec.get('parameters', {})
        if not isinstance(command, str) or not command.strip() or not isinstance(params, dict):
            raise ValueError('Provide a command string and parameter descriptions.')
        if any(not isinstance(p, dict) for p in params.values()):
            raise ValueError('Each parameter needs a description object.')
        for _, field, _, _ in string.Formatter().parse(command):
            if field is not None and field not in params:
                raise ValueError('Describe command parameter: ' + field)
    docs = profile.get('documentation', [])
    if not isinstance(docs, list) or any(not isinstance(url, str) or not url.startswith(('https://', 'http://')) for url in docs):
        raise ValueError('Documentation must be a list of web links.')
    return profile


def parse_identity(response):
    fields = next(csv.reader([response.strip()]))
    if len(fields) != 4 or not fields[0].strip() or not fields[1].strip():
        raise ValueError('The identification response does not contain manufacturer, model, serial number and firmware.')
    return dict(zip(('manufacturer', 'model', 'serial_number', 'firmware'), (s.strip() for s in fields)))


def identity_key(identity):
    serial = str(identity.get('serial_number', '')).strip()
    if serial.lower() in ('', '0', 'none', 'unknown', 'n/a'):
        return None
    return '|'.join(str(identity.get(k, '')).strip().casefold() for k in ('manufacturer', 'model', 'serial_number'))


def verify_identity(expected, observed):
    keys = ['manufacturer', 'model']
    if identity_key(expected):
        keys.append('serial_number')
    if any(str(expected.get(k, '')).strip().casefold() != str(observed.get(k, '')).strip().casefold() for k in keys):
        raise ValueError('Different instrument at this address. Expected ' + str(expected) + '; received ' + str(observed))


def profile_matches(profile, identity):
    match = profile.get('match', {})
    if not match.get('manufacturer') or not match.get('model'):
        return False
    return all(str(identity.get(key, '')).strip().casefold() in
               [str(v).strip().casefold() for v in (values if isinstance(values, list) else [values])]
               for key, values in match.items())


def profiles(config):
    from .catalog import InstrumentCatalog
    return InstrumentCatalog().profiles(config)


def description(identity, connection, catalog):
    record = {'driver': 'scpi', 'config': dict(connection, name=' '.join(
        str(identity.get(k, '')).replace('_', ' ') for k in ('manufacturer', 'model')).strip())}
    from .catalog import select
    profile, alternatives = select(identity, catalog)
    if profile:
        record['driver'] = profile.get('driver', 'scpi')
        record['config'].update(copy.deepcopy(profile.get('config', {})))
        # The observed endpoint always wins over an example endpoint in a profile.
        record['config'].update(connection)
        record['instrument_profile'] = profile['id']
        record['documentation'] = profile.get('documentation', [])
    elif alternatives:
        record['profile_candidates'] = alternatives
    record['identity'] = identity
    record['identity_source'] = 'scpi-idn'
    return record


def connection(candidate):
    if candidate.get('protocol') == 'scpi' and candidate.get('connection'):
        return dict(candidate['connection'])
    return None


class Enrollment:
    def __init__(self, engine):
        self.engine = engine
        self.records = engine.store.discovery_records()
        self.lock = threading.RLock()
        self.probing = set()
        self.pending = {}
        self.retry_after = {}
        self.checked = set()

    def scan(self, inventory, on_update=None):
        engine = self.engine
        catalog = engine.instrument_profiles()
        candidates = list(inventory['groups'])
        visible = {connection_key(c) for c in candidates if c.get('provider') != 'configured'}
        available = {p['name'] for p in inventory.get('providers', []) if p.get('available')}
        with ThreadPoolExecutor(max_workers=8, thread_name_prefix='iop-identify') as pool:
            jobs = [pool.submit(self.inspect, c, catalog, visible, available) for c in candidates]
            rows = []
            for job in as_completed(jobs):
                row = job.result()
                rows.append(row)
                with self.lock:
                    previous = self.records.get(row['key'], {})
                    if row.get('provider') == 'configured' and previous.get('provider') not in (None, 'configured'):
                        row['provider'] = previous['provider']
                    row['first_seen'] = previous.get('first_seen') or row['last_seen'] or row['last_checked']
                    self.records[row['key']] = row
                if on_update:
                    on_update(row)
        with self.lock:
            for key, previous in self.records.items():
                if key not in visible:
                    previous['present'] = False if previous.get('provider') in available else None
                    if previous['present'] is False and device_connection(engine.device_records.get(previous.get('device_id'), {})) == key:
                        self.checked.discard(previous.get('device_id'))
            engine.store.save_discovery_records(self.records.values())
            inventory['instruments'] = copy.deepcopy([r for r in self.records.values()
                if r.get('present') or r.get('device_id') or r.get('device_ids') or r.get('identity', {}).get('model')])
        by_key = {r['key']: r for r in rows}
        for row in inventory['connections']:
            report = by_key.get(connection_key(row))
            if report:
                row['identification'] = report
                if report.get('device_id'):
                    row.update(id=report['device_id'], status='registered')
                if report.get('identity', {}).get('model'):
                    row['name'] = ' '.join(report['identity'].get(k, '') for k in ('manufacturer', 'model')).strip()
        inventory['identification_summary'] = {
            'identified': sum(bool(r.get('identity', {}).get('model')) for r in rows),
            'configured': len({d for r in rows for d in ([r['device_id']] if r.get('device_id') else r.get('device_ids', []))}),
            'needs_configuration': sum(bool(r.get('required')) for r in rows if r['transport'] != 'usb'),
        }

    def inspect(self, candidate, catalog, visible, available):
        engine = self.engine
        key = connection_key(candidate)
        report = {'key':key, 'transport':candidate['transport'], 'address':candidate['address'],
                  'name':candidate.get('name'), 'provider':candidate.get('provider'), 'present':candidate.get('present', True),
                  'last_seen':now() if candidate.get('present', True) else self.records.get(key, {}).get('last_seen'), 'last_checked':now(), 'status':'needs_configuration', 'identity':candidate.get('identity', {}),
                  'identity_source':candidate.get('identity_source'), 'required':[],
                  'connection_info':{k:v for k,v in candidate.items() if k not in
                                     ('interfaces', 'identification', 'device', 'connection')}}
        with engine.registration_lock:
            if candidate.get('provider') == 'configured' and self.records.get(key, {}).get('provider') in available:
                report['present'] = False
            with engine.lock:
                device_ids = [d for d in candidate.get('device_ids', []) if d in engine.device_records]
                if len(device_ids) > 1:
                    report.update(device_ids=device_ids, status='ready')
                    return report
                existing = engine.device_records.get(candidate.get('id') or self.records.get(key, {}).get('device_id')) or next((d for d in engine.device_records.values() if device_connection(d) == key), None)
                if existing and existing['driver'] == 'scpi' and device_connection(existing) != key and device_connection(existing) not in visible:
                    existing = None
            if existing:
                return self.registered(report, existing)
            with self.lock:
                previous = self.records.get(key, {})
                if time.monotonic() < self.retry_after.get(key, 0):
                    for field in ('identity', 'identity_source', 'status', 'error', 'required'):
                        if field in previous:
                            report[field] = previous[field]
                    return report
                self.probing.add(key)
        try:
            if candidate.get('device'):
                record = copy.deepcopy(candidate['device'])
                if report['identity']:
                    record.update(identity=report['identity'], identity_source=report['identity_source'])
                device = engine.register(record, enrollment_key=key)
                report.update(device_id=device['id'], status='ready')
                return report
            config = connection(candidate)
            if config is None:
                report['status'] = 'identified' if report['identity'].get('model') else 'needs_configuration'
                report['required'] = (['driver'] if candidate['transport'] in ('sdk', 'usb') else
                                      ['control_interface'] if candidate['transport'] == 'lxi' else
                                      ['protocol', 'communication_parameters'])
                return report
            from .drivers import SCPI
            probe_config = dict(config, timeout=min(float(config.get('timeout', 2)), 5))
            probe = SCPI('identity-query', probe_config, {})
            try:
                identity = parse_identity(probe.exchange('*IDN?', True))
            finally:
                probe.close()
            report.update(identity=identity, identity_source='scpi-idn', status='identified')
            record = description(identity, config, catalog)
            device = self.adopt(record, key, visible, available)
            report.update(device_id=device['id'], status='ready' if record.get('instrument_profile') else 'identified')
            report['required'] = [] if record.get('instrument_profile') else ['model_operations']
            if record.get('profile_candidates'):
                report.update(profile_candidates=record['profile_candidates'], required=['instrument_profile'])
            report['documentation'] = record.get('documentation', [])
            with self.lock:
                self.retry_after.pop(key, None)
                self.checked.add(device['id'])
            with engine.store.transaction():
                engine.store.event('instrument.identified', device_id=device['id'], connection=key,
                                   identity=identity, query='*IDN?')
        except Exception as error:
            report.update(error=str(error), required=['communication_parameters'])
            with self.lock:
                self.retry_after[key] = time.monotonic() + 60
        finally:
            with self.lock:
                self.probing.discard(key)
        return report

    def registered(self, report, record):
        engine = self.engine
        identity = record.get('identity', {})
        report.update(device_id=record['id'], identity=identity,
                      identity_source=record.get('identity_source'), status='ready')
        report['documentation'] = record.get('documentation', [])
        if report['present'] is False:
            report['status'] = 'not_seen'
            return report
        if record['driver'] != 'scpi':
            return report
        if identity.get('model') and record['id'] in self.checked:
            report['required'] = [] if record['config'].get('operations') else ['model_operations']
            if record.get('profile_candidates') and not record['config'].get('operations'):
                report.update(profile_candidates=record['profile_candidates'], required=['instrument_profile'])
            report['status'] = 'ready' if not report['required'] else 'identified'
            return report
        with self.lock:
            pending = self.pending.get(record['id'])
            retry = self.retry_after.get(report['key'], 0)
        if pending:
            operation = engine.store.get('operations', pending)
            if operation['state'] in ('queued', 'running'):
                report.update(status='identifying', operation_id=pending)
                return report
            if operation['state'] == 'completed':
                with self.lock:
                    self.checked.add(record['id'])
                    self.pending.pop(record['id'], None)
                return self.registered(report, engine.device_records[record['id']])
            if operation['state'] != 'completed':
                report.update(error=operation.get('error', operation['state']), required=['communication_parameters'])
                report['status'] = 'needs_configuration'
                if not retry:
                    with self.lock:
                        self.retry_after[report['key']] = time.monotonic() + 60
                    return report
        if time.monotonic() >= retry:
            try:
                run = engine.identify(record['id'])
                with self.lock:
                    self.pending[record['id']] = run['operations'][0]
                    self.retry_after.pop(report['key'], None)
                report.update(status='identifying', operation_id=run['operations'][0])
            except ValueError as error:
                report['error'] = str(error)
        return report

    def adopt(self, record, key, visible, available):
        engine = self.engine
        identity = record['identity']
        stable = identity_key(identity)
        with engine.registration_lock:
            with engine.lock:
                existing = next((d for d in engine.device_records.values()
                    if stable and identity_key(d.get('identity', {})) == stable), None)
            if existing:
                old_key = device_connection(existing)
                with self.lock:
                    previous = self.records.get(old_key, {})
                if old_key in visible or previous.get('provider') not in available:
                    return engine.descriptions[existing['id']]
                replacement = copy.deepcopy(existing)
                for field in ('transport', 'host', 'port', 'resource', 'backend'):
                    replacement['config'].pop(field, None)
                replacement['config'].update({k:v for k,v in record['config'].items()
                                              if k in ('transport', 'host', 'port', 'resource', 'backend')})
                return engine.replace_device(replacement, enrollment_key=key)
            stem = re.sub('[^a-z0-9]+', '-', identity.get('model', 'instrument').lower()).strip('-')[:40] or 'instrument'
            record['id'] = stem + '-' + hashlib.sha256((stable or key).encode()).hexdigest()[:10]
            return engine.register(record, enrollment_key=key)

    def retry(self, key=None):
        with self.lock:
            if key:
                self.retry_after.pop(key, None)
                device_id = self.records.get(key, {}).get('device_id')
                pending = self.pending.get(device_id)
                if not pending or self.engine.store.get('operations', pending)['state'] not in ('queued', 'running'):
                    self.pending.pop(device_id, None)
                    self.checked.discard(device_id)
            else:
                self.retry_after.clear()
                self.pending = {k:v for k,v in self.pending.items() if self.engine.store.get('operations', v)['state'] in ('queued', 'running')}
                self.checked.clear()
