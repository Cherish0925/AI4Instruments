"""A compact laboratory description shared by people and agent clients."""
from __future__ import annotations
import json
import platform
import sys
from pathlib import Path
from .config import VERSION
from .plugins import adapters
from .store import dumps, now


SCHEMAS = ('device', 'platform', 'workflow')


def schema_document(name):
    if name not in SCHEMAS:
        raise KeyError('Unknown schema: ' + name)
    path = Path(__file__).with_name('schema') / (name + '.schema.json')
    if not path.exists():
        path = Path(__file__).resolve().parents[3] / 'iop/schema' / path.name
    return json.loads(path.read_text(encoding='utf-8'))


def laboratory(engine, refresh=False):
    if refresh:
        engine.scan()
    with engine.lock:
        inventory = json.loads(dumps(engine.discovery))
        devices = [{key: value for key, value in record.items() if key != 'operations'} |
                   {'operations': list(record['operations'])}
                   for record in engine.descriptions.values()]
        platforms = engine.list_platforms()
        assigned = {d for p in platforms for d in p['definition']['devices']}
        unassigned = sorted(engine.devices.keys() - assigned)
        pending = [c for c in inventory.get('connections', []) if c.get('status') != 'registered']
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
            'setup': {'unassigned_devices': unassigned, 'unregistered_connections': len(pending),
                      'offline_devices': dict(engine.offline),
                      'missing_platform_devices': {p['id']: p['missing_devices'] for p in platforms if p['missing_devices']}},
        }
    result['adapters'] = adapters()
    result['schemas'] = {name: '/v1/schemas/' + name for name in SCHEMAS}
    result['next_steps'] = []
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
        'service_restart': 'Queued work is restored; previously started work is recorded as interrupted.',
        'physical_setup': 'Reuse saved platform descriptions. Ask only for missing wiring, sample details and experimental requirements.',
        'request_id': 'Reuse the same request_id when retrying the same experiment submission.',
    }
    return result


def agent_configuration(home, endpoint=None):
    args = ['-m', 'ai4instruments.iop', '--home', str(home)]
    if endpoint:
        args += ['--endpoint', endpoint]
    args += ['mcp']
    return {'mcpServers': {'iop': {'command': sys.executable, 'args': args}}}
