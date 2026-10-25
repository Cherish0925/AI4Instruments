"""Replace idle instrument configurations and retain their previous definitions."""
import copy
from .config import save_json
from .drivers import make_driver
from .errors import RequestError


METADATA = ('identity', 'identity_source', 'instrument_profile', 'documentation')


def describe(record, driver):
    description = driver.describe()
    operations = description.get('operations')
    if not isinstance(operations, dict) or not operations or any(not isinstance(s, dict) for s in operations.values()):
        raise ValueError('Driver must describe its operations')
    concurrency = description.get('concurrency', 1)
    if type(concurrency) is not int or concurrency < 1:
        raise ValueError('Driver concurrency must be a positive integer')
    return {'id': record['id'], 'driver': record['driver'], **description,
            **{k: record[k] for k in METADATA if k in record}}


def configure(engine, device_id, definition, expected_revision):
    from .engine import TERMINAL
    from .discovery import connection_conflict
    definition = copy.deepcopy(definition)
    if definition.get('id') != device_id:
        raise ValueError('Keep the instrument ID when editing its configuration')
    with engine.registration_lock:
        with engine.lock:
            old = engine.device_records[device_id]
            current = engine.store.device_history(device_id, 1)[0]
            if type(expected_revision) is not int or expected_revision != current['revision']:
                raise RequestError('configuration_changed', 'Read the current instrument configuration before saving.',
                                   current_revision=current['revision'], details_url=f'/v1/devices/{device_id}/history')
            if old == definition:
                return current
            driver = engine.devices[device_id]
            worker = getattr(driver, 'worker', None)
            if worker and any(d is not driver and getattr(d, 'worker', None) is worker for d in engine.devices.values()):
                raise RequestError('shared_worker', 'Update the shared SDK configuration together, then restart the service.')
            if (engine.allocation.used['device:' + device_id] or
                    any(o['device'] == device_id and o['state'] not in TERMINAL for o in engine.operations.values()) or
                    any(device_id in r.get('devices', {}) for r in engine.runs.values())):
                raise RequestError('device_busy', 'Wait for this instrument’s accepted experiments before changing its configuration.',
                                   device_id=device_id)
            if any(d['id'] != device_id and connection_conflict(definition, d) for d in engine.device_records.values()):
                raise RequestError('connection_in_use', 'Another instrument already uses this address.')
            # Reuse identity unless the caller explicitly registers a different instrument.
            if old.get('identity') != definition.get('identity'):
                raise ValueError('Keep the saved instrument identity; register a replacement instrument with a new ID')
            engine.reconnecting.add(device_id)
            registry = {k: v for k, v in engine.devices.items() if k != device_id}
        new = None
        config_written = False
        try:
            driver.close()
            new = make_driver(definition, registry)
            description = describe(definition, new)
            with engine.lock:
                config = dict(engine.config, devices=[definition if d['id'] == device_id else d for d in engine.config['devices']])
                save_json(engine.home / 'config.json', config)
                config_written = True
                version = engine.store.save_device(definition)
                engine.config.update(config)
                engine.devices[device_id] = new
                engine.device_records[device_id] = definition
                engine.descriptions[device_id] = dict(description, revision=version['revision'])
                engine.allocation.limits['device:' + device_id] = description.get('concurrency', 1)
                engine.offline.pop(device_id, None)
            return version
        except BaseException:
            if config_written:
                save_json(engine.home / 'config.json', engine.config)
            if new is not None:
                new.close()
            try:
                restored = make_driver(old, registry)
                with engine.lock:
                    engine.devices[device_id] = restored
            except Exception as error:
                with engine.lock:
                    engine.offline[device_id] = str(error)
            raise
        finally:
            with engine.lock:
                engine.reconnecting.discard(device_id)
