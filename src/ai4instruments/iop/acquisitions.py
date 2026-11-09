"""An acquisition is a saved selection of completed instrument operations."""
import json


def save(engine, run_id, name, operation_ids, conditions, analysis):
    if not isinstance(operation_ids, list) or not operation_ids or any(not isinstance(i, str) for i in operation_ids):
        raise ValueError('Provide completed operation IDs from this experiment')
    if not isinstance(conditions, dict) or not isinstance(analysis, dict):
        raise ValueError('Conditions and analysis must be objects')
    run = engine.store.get('runs', run_id)
    operations, configurations = [], {}
    for oid in dict.fromkeys(operation_ids):
        op = engine.store.get('operations', oid)
        if op['run_id'] != run_id or op['state'] != 'completed':
            raise ValueError('Acquisitions use completed operations from the same experiment')
        operations.append(op)
        key = op['device'] + '@' + str(op.get('device_revision'))
        if key not in configurations:
            with engine.store.lock:
                row = engine.store.db.execute('SELECT body FROM device_versions WHERE id=? AND revision=?',
                    (op['device'], op.get('device_revision'))).fetchone()
            if row is None:
                raise ValueError('Operation has no recorded device configuration: ' + oid)
            configurations[key] = json.loads(row[0])
    document = {'schema_version':1, 'run_id':run_id, 'name':name,
        'experiment':{k:run[k] for k in ('name', 'project', 'experiment', 'parameters', 'platform') if k in run},
        'operations':operations, 'device_configurations':configurations,
        'conditions':conditions, 'analysis':analysis}
    content = json.dumps(document, sort_keys=True, ensure_ascii=False, allow_nan=False, separators=(',', ':')).encode('utf-8')
    from .engine import relative_path
    rel = relative_path(name)
    def existing_acquisition():
        existing = engine.store.artifact_named(run_id, 'output/' + rel.as_posix())
        if existing:
            path = engine.home / 'runs' / run_id / 'output' / rel
            if path.read_bytes() != content:
                raise ValueError('An acquisition with different content already has this name')
            return existing
    existing = existing_acquisition()
    if existing:
        return existing
    try:
        return engine.artifact(run_id, name, content, list(dict.fromkeys(operation_ids)))
    except ValueError:
        # A simultaneous identical upload may have finished while this one copied.
        existing = existing_acquisition()
        if existing:
            return existing
        raise
