"""Ordered binary data chunks; instrument commands use the normal scheduler."""
import hashlib
import os
import uuid
from .errors import RequestError
from .platforms import name as valid_name
from .store import dumps, now
import json


def describe(engine, run_id, name, definition=None):
    valid_name(name, 'Data stream name')
    engine.store.get('runs', run_id)
    with engine.store.transaction():
        row = engine.store.db.execute('SELECT body FROM streams WHERE run_id=? AND name=?', (run_id, name)).fetchone()
        if definition is not None:
            if not isinstance(definition, dict) or not isinstance(definition.get('format'), str) or not definition['format'].strip():
                raise ValueError('Describe the data format, for example float32-le, npy, tiff or csv')
            record = {'name': name, 'definition': definition, 'created': now()}
            if row:
                if json.loads(row[0])['definition'] != definition:
                    raise RequestError('stream_description_changed', 'Use a new stream name when changing its data format.')
            else:
                engine.store.db.execute('INSERT INTO streams(run_id,name,body) VALUES(?,?,?)', (run_id, name, dumps(record)))
                engine.store.event('stream.created', run_id, stream=name)
                row = (dumps(record),)
        if not row:
            raise KeyError(name)
        count, size = engine.store.db.execute('SELECT chunks,bytes FROM streams WHERE run_id=? AND name=?',
                                            (run_id, name)).fetchone()
        return {**json.loads(row[0]), 'chunks': count, 'bytes': size, 'next_sequence': count}


def chunks(engine, run_id, name, after=-1, limit=100):
    description = describe(engine, run_id, name)
    with engine.store.lock:
        rows = engine.store.db.execute('SELECT body FROM stream_chunks WHERE run_id=? AND stream=? AND sequence>? '
                                      'ORDER BY sequence LIMIT ?', (run_id, name, int(after), min(max(int(limit), 1), 1000))).fetchall()
    data = [json.loads(row[0]) for row in rows]
    return {'stream': description, 'chunks': data, 'cursor': data[-1]['sequence'] if data else int(after)}


def append(engine, run_id, name, sequence, source, length):
    describe(engine, run_id, name)
    sequence = int(sequence)
    if sequence < 0 or type(length) is not int or length <= 0:
        raise ValueError('Provide a nonnegative sequence and a positive Content-Length')
    # Use a unique filename so an uncommitted transfer cannot overwrite an indexed chunk.
    directory = engine.home / 'runs' / run_id / 'output' / 'streams' / name
    if not directory.resolve().is_relative_to((engine.home / 'runs' / run_id / 'output').resolve()):
        raise ValueError('Data must remain inside its experiment output directory')
    directory.mkdir(parents=True, exist_ok=True)
    path = directory / (str(sequence) + '-' + uuid.uuid4().hex + '.bin')
    committed = False
    try:
        digest = hashlib.sha256()
        with path.open('xb') as file:
            remaining = length
            while remaining:
                data = source.read(min(remaining, 256 * 1024))
                if not data:
                    raise ValueError('Data transfer ended before the declared length')
                file.write(data)
                digest.update(data)
                remaining -= len(data)
            file.flush()
            os.fsync(file.fileno())
        with engine.store.transaction():
            db = engine.store.db
            previous = db.execute('SELECT body FROM stream_chunks WHERE run_id=? AND stream=? AND sequence=?',
                                  (run_id, name, sequence)).fetchone()
            if previous:
                saved = json.loads(previous[0])
                if saved['sha256'] != digest.hexdigest() or saved['size'] != length:
                    raise RequestError('chunk_changed', 'This sequence already contains different data.', sequence=sequence)
                return saved
            expected = db.execute('SELECT chunks FROM streams WHERE run_id=? AND name=?', (run_id, name)).fetchone()[0]
            if sequence != expected:
                raise RequestError('chunk_out_of_order', 'Append the next data chunk, or retry an already saved chunk.', next_sequence=expected)
            record = {'id': 'file_' + uuid.uuid4().hex[:20], 'run_id': run_id, 'stream': name,
                      'sequence': sequence, 'size': length, 'sha256': digest.hexdigest(), 'created': now(),
                      'name': path.relative_to(engine.home / 'runs' / run_id).as_posix(), 'media_type': 'application/octet-stream'}
            db.execute('INSERT INTO artifacts(id,run_id,body,name) VALUES(?,?,?,?)', (record['id'], run_id, dumps(record), record['name']))
            db.execute('INSERT INTO stream_chunks VALUES(?,?,?,?,?)', (run_id, name, sequence, length, dumps(record)))
            db.execute('UPDATE streams SET chunks=chunks+1,bytes=bytes+? WHERE run_id=? AND name=?', (length, run_id, name))
            engine.store.event('stream.chunk', run_id, stream=name, sequence=sequence, artifact_id=record['id'], size=length)
        committed = True
        return record
    finally:
        if not committed:
            path.unlink(missing_ok=True)
