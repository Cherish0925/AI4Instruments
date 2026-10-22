"""Platform descriptions: device membership, physical connections and procedures."""
from __future__ import annotations
from collections import deque
import json
import re


def name(value, what='ID'):
    if not isinstance(value, str) or not re.fullmatch(r'[A-Za-z0-9][A-Za-z0-9_.-]{0,79}', value):
        raise ValueError(what + ' must use 1–80 letters, digits, dots, dashes or underscores')
    return value


def strings(values, what):
    if not isinstance(values, list) or any(not isinstance(v, str) or not v for v in values):
        raise ValueError(what + ' must be a list of nonempty strings')
    if len(set(values)) != len(values):
        raise ValueError(what + ' contains duplicates')
    return values


def steps(value):
    if not isinstance(value, list) or not 1 <= len(value) <= 10000:
        raise ValueError('A workflow needs between 1 and 10000 steps')
    if any(not isinstance(s, dict) for s in value):
        raise ValueError('Each step must be an object')
    ids = strings([s.get('id') for s in value], 'Step IDs')
    children, counts = {i: [] for i in ids}, {}
    for step in value:
        dependencies = strings(step.get('after', []), 'Step dependencies')
        if not set(dependencies) <= children.keys():
            raise ValueError('Step dependencies contain an unknown step')
        counts[step['id']] = len(dependencies)
        for parent in dependencies:
            children[parent].append(step['id'])
    ready = deque(i for i in ids if counts[i] == 0)
    visited = 0
    while ready:
        visited += 1
        for child in children[ready.popleft()]:
            counts[child] -= 1
            if not counts[child]:
                ready.append(child)
    if visited != len(value):
        raise ValueError('Step dependencies contain a cycle')
    return value


def description(value, devices):
    if not isinstance(value, dict):
        raise ValueError('Platform description must be an object')
    value = json.loads(json.dumps(value, allow_nan=False))
    allowed = {'schema_version', 'id', 'name', 'description', 'devices', 'resources', 'connections', 'procedures'}
    if value.keys() - allowed:
        raise ValueError('Unknown platform fields: ' + ', '.join(sorted(value.keys() - allowed)))
    name(value.get('id'), 'Platform ID')
    if type(value.get('schema_version')) is not int or value['schema_version'] != 1:
        raise ValueError('Platform schema_version must be 1')
    for field in ('name', 'description'):
        if field in value and not isinstance(value[field], str):
            raise ValueError(field + ' must be text')
    members = set(strings(value.get('devices'), 'Platform devices'))
    missing = members - devices.keys()
    if missing:
        raise ValueError('Register these devices first: ' + ', '.join(sorted(missing)))
    resources = value.setdefault('resources', [])
    if not isinstance(resources, list) or any(not isinstance(r, dict) for r in resources):
        raise ValueError('Platform resources must be objects')
    strings([r.get('id') for r in resources], 'Resource IDs')
    for resource in resources:
        name(resource['id'], 'Resource ID')
        if resource['id'] in devices:
            raise ValueError('Resource ID must differ from device IDs: ' + resource['id'])
        used = set(strings(resource.get('devices'), 'Resource devices'))
        if not used or not used <= members:
            raise ValueError('Resource devices must belong to the platform')
        selected = resource.get('operations', {})
        if not isinstance(selected, dict) or not selected.keys() <= used:
            raise ValueError('Resource operation selections must name its devices')
        for device, operations in selected.items():
            strings(operations, 'Resource operation names')
            if not set(operations) <= devices[device].describe()['operations'].keys():
                raise ValueError('Unknown resource operation for device: ' + device)
    connections = value.setdefault('connections', [])
    if not isinstance(connections, list):
        raise ValueError('Connections must be a list')
    for connection in connections:
        if not isinstance(connection, dict) or not isinstance(connection.get('kind'), str) or not connection['kind']:
            raise ValueError('Each connection needs a kind')
        for side in ('from', 'to'):
            endpoint = connection.get(side)
            if not isinstance(endpoint, dict) or endpoint.get('device') not in members:
                raise ValueError('Connection endpoints must name platform devices')
            if not isinstance(endpoint.get('port'), str) or not endpoint['port']:
                raise ValueError('Connection endpoints need a port name')
    procedures = value.setdefault('procedures', {})
    if not isinstance(procedures, dict):
        raise ValueError('Procedures must be an object')
    for procedure_id, procedure in procedures.items():
        name(procedure_id, 'Procedure ID')
        if not isinstance(procedure, dict):
            raise ValueError('Procedure must be an object')
        for step in steps(procedure.get('steps')):
            if step.get('device') not in members:
                raise ValueError('Procedure device must belong to the platform')
        strings(procedure.get('resources', []), 'Procedure resources')
    value.setdefault('name', value['id'])
    return value


def resource_index(platforms):
    index = {}
    for platform in platforms.values():
        for resource in platform['definition']['resources']:
            for device in resource['devices']:
                index.setdefault(device, set()).add('shared:' + resource['id'])
    return index


def operation_resources(platforms, device, operation):
    return {'shared:' + r['id'] for p in platforms.values() for r in p['definition']['resources']
            if device in r['devices'] and (device not in r.get('operations', {})
            or operation in r['operations'][device])}
