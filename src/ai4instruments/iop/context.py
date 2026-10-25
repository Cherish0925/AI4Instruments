"""A compact laboratory description shared by people and agent clients."""
from __future__ import annotations
import json
import platform
import sys
from pathlib import Path
from .config import VERSION
from .plugins import adapters
from .store import dumps, now


SCHEMAS = ('device', 'platform', 'workflow', 'instrument-profile')


def schema_document(name):
    if name not in SCHEMAS:
        raise KeyError('Unknown schema: ' + name)
    path = Path(__file__).with_name('schema') / (name + '.schema.json')
    if not path.exists():
        path = Path(__file__).resolve().parents[3] / 'iop/schema' / path.name
    return json.loads(path.read_text(encoding='utf-8'))


def laboratory(engine, refresh=False, detail='summary'):
    if detail not in ('summary', 'full'):
        raise ValueError('Context detail must be summary or full')
    if refresh:
        engine.scan()
    with engine.lock:
        inventory = engine.inventory()
        devices = [{key: value for key, value in record.items() if key != 'operations'} |
                   {'operations': list(record['operations'])}
                   for record in engine.descriptions.values()]
        platforms = engine.list_platforms()
        assigned = {d for p in platforms for d in p['definition']['devices']}
        unassigned = sorted(engine.devices.keys() - assigned)
        pending = [c for c in inventory.get('groups', inventory.get('connections', []))
                   if c.get('status') != 'registered' and c.get('transport') != 'usb']
        active = [{k: r[k] for k in ('id', 'name', 'kind', 'state') if k in r}
                  for r in engine.runs.values()]
        result = {
            'schema_version': 1, 'generated': now(),
            'service': {'name': 'IOP Runtime', 'version': VERSION, 'endpoint': engine.endpoint,
                        'system': platform.system(), 'architecture': platform.machine(),
                        'python': platform.python_version()},
            'status': engine.metrics(), 'devices': devices, 'platforms': platforms,
            'discovery': inventory, 'resources': engine.resource_info(),
            'active_runs': active,
            'cursor': engine.store.cursor(),
            'setup': {'unassigned_devices': unassigned, 'unregistered_connections': len(pending),
                      'offline_devices': dict(engine.offline),
                      'missing_platform_devices': {p['id']: p['missing_devices'] for p in platforms if p['missing_devices']}},
        }
    result['adapters'] = adapters()
    result['schemas'] = {name: '/v1/schemas/' + name for name in SCHEMAS}
    result['next_steps'] = []
    if engine.instrument_catalog.errors:
        result['next_steps'].append({'action': 'read_instrument_catalog',
                                    'errors': len(engine.instrument_catalog.errors), 'details': '/v1/instrument-catalog'})
    for instrument in inventory.get('instruments', []):
        if instrument.get('required') and instrument.get('present') is not False and instrument.get('transport') != 'usb':
            if instrument['required'] == ['instrument_profile']:
                from urllib.parse import urlencode
                result['next_steps'].append({'action': 'select_instrument_profile', 'device_id': instrument.get('device_id'),
                    'catalog': '/v1/instrument-catalog?' + urlencode(instrument.get('identity', {})),
                    'configuration': '/v1/devices/' + instrument['device_id'] + '/configuration',
                    'history': '/v1/devices/' + instrument['device_id'] + '/history'})
                continue
            result['next_steps'].append({'action':'complete_instrument_setup', 'connection':instrument['key'],
                                         'identity':instrument.get('identity', {}), 'required':instrument['required'],
                                         'device_id':instrument.get('device_id'),
                                         'schema':'/v1/schemas/instrument-profile' if instrument['required'] == ['model_operations'] else '/v1/schemas/device',
                                         'submit':'/v1/instrument-profiles' if instrument['required'] == ['model_operations'] else '/v1/devices',
                                         'documentation': instrument.get('documentation', [])})
    if not devices and not inventory.get('updated'):
        result['next_steps'].append({'action': 'discover', 'reason': 'The first connection inventory is not available yet.'})
    if result['setup']['offline_devices']:
        result['next_steps'].append({'action': 'reconnect', 'devices': sorted(result['setup']['offline_devices'])})
    for platform_id, missing in result['setup']['missing_platform_devices'].items():
        result['next_steps'].append({'action': 'restore_platform_devices', 'platform': platform_id, 'devices': missing})
    result['operation'] = {
        'device_description': '/v1/devices/{id}',
        'submission': '/v1/runs', 'program_submission': '/v1/packages',
        'configuration_executes_actions': False,
        'client_disconnect': 'Accepted experiments continue while the service remains running.',
        'service_restart': 'Queued work is restored. Started work is recorded as interrupted; programs declaring resume:true can continue from saved progress through /v1/runs/{id}/resume.',
        'physical_setup': 'Reuse saved platform descriptions. Ask only for missing wiring, sample details and experimental requirements.',
        'request_id': 'Reuse the same request_id when retrying the same experiment submission.',
        'changes': '/v1/context/changes?after={cursor}',
        'instrument_catalog': '/v1/instrument-catalog',
    }
    if detail == 'summary':
        states = engine.device_states()
        result['devices'] = [{k: v for k, v in d.items() if k in
            ('id', 'name', 'driver', 'mode', 'identity', 'revision', 'operations')} |
            {'status': states.get(d['id'], {}), 'description': '/v1/devices/' + d['id']}
            for d in devices[:100]]
        if len(devices) > 100:
            result['devices_page'] = {'total': len(devices), 'next': '/v1/context/devices?offset=100'}
        result['platforms'] = [{k: p[k] for k in ('id', 'revision', 'updated', 'active_runs', 'missing_devices') if k in p} |
            {'name': p['definition'].get('name', p['id']), 'devices': p['definition']['devices'],
             'description': '/v1/platforms/' + p['id']} for p in platforms]
        result['discovery'] = {k: inventory[k] for k in
            ('scanning', 'phase', 'updated', 'summary', 'identification_summary', 'pending_providers', 'error') if k in inventory}
        result['discovery']['details'] = '/v1/discovery?cached=true'
        result['adapters'] = '/v1/adapters'
        result['status'] = {k: v for k, v in result['status'].items() if k != 'resources'}
    return result


def device_page(engine, offset=0, limit=100):
    offset, limit = max(0, int(offset)), min(max(1, int(limit)), 1000)
    with engine.lock:
        rows = list(engine.descriptions.values())
        states = engine.device_states()
        devices = [{k: v for k, v in row.items() if k in ('id', 'name', 'driver', 'mode', 'identity', 'revision')} |
                   {'operations': list(row['operations']), 'status': states.get(row['id'], {}),
                    'description': '/v1/devices/' + row['id']} for row in rows[offset:offset + limit]]
        return {'devices': devices, 'total': len(rows), 'offset': offset,
                'next': f'/v1/context/devices?offset={offset + limit}&limit={limit}' if offset + limit < len(rows) else None}


def changes(engine, after=0, limit=100, wait=0):
    """Summarize a bounded event page; arrays and operation results stay at their URLs."""
    events = engine.store.events(after, limit=limit, wait=wait)
    records = []
    for event in events:
        row = {k: event[k] for k in ('sequence', 'time', 'kind', 'run_id', 'device_id', 'devices',
                                    'connection', 'revision', 'operation_id', 'stream', 'artifact_id', 'size') if event.get(k) is not None}
        if event.get('run_id'):
            row['details'] = '/v1/runs/' + event['run_id'] + '?details=false'
        elif event.get('device_id'):
            row['details'] = '/v1/devices/' + event['device_id']
        records.append(row)
    return {'changes': records, 'cursor': events[-1]['sequence'] if events else int(after)}


def agent_configuration(home, endpoint=None):
    args = ['-m', 'ai4instruments.iop', '--home', str(home)]
    if endpoint:
        args += ['--endpoint', endpoint]
    args += ['mcp']
    return {'mcpServers': {'iop': {'command': sys.executable, 'args': args}}}
