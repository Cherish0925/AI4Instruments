"""Persistent experiment records and ordered events."""
from __future__ import annotations
import json
import sqlite3
import threading
import time
from datetime import datetime, timezone
from contextlib import contextmanager


def now():
    return datetime.now(timezone.utc).isoformat(timespec="milliseconds")


def dumps(value):
    return json.dumps(value, ensure_ascii=False, allow_nan=False, separators=(",", ":"))


class Store:
    def __init__(self, path):
        self.lock = threading.RLock()
        self.changed = threading.Condition(self.lock)
        self.db = sqlite3.connect(path, check_same_thread=False, timeout=30)
        self.db.execute("PRAGMA journal_mode=WAL")
        self.db.execute("PRAGMA synchronous=FULL")
        self.db.executescript('''
          CREATE TABLE IF NOT EXISTS runs(id TEXT PRIMARY KEY, state TEXT NOT NULL, created TEXT NOT NULL,
            request_id TEXT UNIQUE, body TEXT NOT NULL);
          CREATE TABLE IF NOT EXISTS operations(id TEXT PRIMARY KEY, run_id TEXT NOT NULL, state TEXT NOT NULL,
            created TEXT NOT NULL, request_id TEXT UNIQUE, body TEXT NOT NULL);
          CREATE INDEX IF NOT EXISTS operations_run ON operations(run_id);
          CREATE TABLE IF NOT EXISTS events(sequence INTEGER PRIMARY KEY AUTOINCREMENT, time TEXT NOT NULL,
            run_id TEXT, kind TEXT NOT NULL, body TEXT NOT NULL);
          CREATE INDEX IF NOT EXISTS events_run ON events(run_id,sequence);
          CREATE TABLE IF NOT EXISTS artifacts(id TEXT PRIMARY KEY, run_id TEXT NOT NULL, body TEXT NOT NULL);
          CREATE INDEX IF NOT EXISTS artifacts_run ON artifacts(run_id);
          CREATE TABLE IF NOT EXISTS platform_versions(
            id TEXT NOT NULL, revision INTEGER NOT NULL, body TEXT NOT NULL,
            PRIMARY KEY(id,revision));
          CREATE TABLE IF NOT EXISTS resource_holds(resource TEXT PRIMARY KEY, body TEXT NOT NULL);
        ''')
        columns = {row[1] for row in self.db.execute('PRAGMA table_info(artifacts)')}
        if 'name' not in columns:
            self.db.execute('ALTER TABLE artifacts ADD COLUMN name TEXT')
        for identifier, body in self.db.execute('SELECT id,body FROM artifacts WHERE name IS NULL').fetchall():
            self.db.execute('UPDATE artifacts SET name=? WHERE id=?', (json.loads(body)['name'], identifier))
        self.db.execute('CREATE UNIQUE INDEX IF NOT EXISTS artifacts_name ON artifacts(run_id,name)')
        self.db.commit()

    @contextmanager
    def transaction(self):
        with self.lock:
            try:
                yield
                self.db.commit()
                self.changed.notify_all()
            except BaseException:
                self.db.rollback()
                raise

    def put(self, table, item):
        if table not in {"runs", "operations"}:
            raise ValueError(table)
        keys = ["id", "state", "created", "request_id", "body"]
        if table == "operations":
            keys.insert(1, "run_id")
        values = [dumps(item) if k == "body" else item.get(k) for k in keys]
        self.db.execute(f"INSERT INTO {table}({','.join(keys)}) VALUES({','.join('?' for _ in keys)}) "
                        "ON CONFLICT(id) DO UPDATE SET state=excluded.state,body=excluded.body", values)

    def get(self, table, identifier, summary=False):
        if table not in {"runs", "operations", "artifacts"}:
            raise ValueError(table)
        with self.lock:
            body = "json_remove(body, '$.result', '$.operations', '$.definition', '$.manifest', '$.platform.definition')" if summary and table == 'runs' else 'body'
            row = self.db.execute(f"SELECT {body} FROM {table} WHERE id=?", (identifier,)).fetchone()
            if row is None:
                raise KeyError(identifier)
            return json.loads(row[0])

    def request(self, table, request_id):
        if not request_id:
            return None
        if table not in {"runs", "operations"}:
            raise ValueError(table)
        with self.lock:
            row = self.db.execute(f"SELECT body FROM {table} WHERE request_id=?", (request_id,)).fetchone()
            return json.loads(row[0]) if row else None

    def wait_operation(self, identifier, wait=0):
        wait = float(wait)
        if not 0 <= wait <= 25:
            raise ValueError('Operation wait must be between 0 and 25 seconds')
        deadline = time.monotonic() + wait
        with self.changed:
            while True:
                record = self.get('operations', identifier)
                remaining = deadline - time.monotonic()
                if record['state'] not in {'queued', 'running'} or remaining <= 0:
                    return record
                self.changed.wait(remaining)

    def artifact_named(self, run_id, name):
        with self.lock:
            row = self.db.execute('SELECT body FROM artifacts WHERE run_id=? AND name=?', (run_id, name)).fetchone()
            return json.loads(row[0]) if row else None

    def operation_page(self, run_id, after=0, limit=200):
        with self.lock:
            rows = self.db.execute('SELECT rowid,body FROM operations WHERE run_id=? AND rowid>? ORDER BY rowid LIMIT ?',
                                  (run_id, int(after), min(max(int(limit), 1), 1000))).fetchall()
        return {'operations':[json.loads(body) for _, body in rows], 'cursor':rows[-1][0] if rows else int(after)}

    def list(self, table, run_id=None, limit=100, summary=False):
        if table not in {"runs", "operations", "artifacts"}:
            raise ValueError(table)
        with self.lock:
            where, args = (" WHERE run_id=?", [run_id]) if run_id else ("", [])
            args.append(min(max(int(limit), 1), 10000))
            body = "json_remove(body, '$.result', '$.operations', '$.definition', '$.manifest', '$.platform.definition')" if summary and table == 'runs' else 'body'
            rows = self.db.execute(f"SELECT {body} FROM {table}{where} ORDER BY rowid DESC LIMIT ?", args)
            return [json.loads(r[0]) for r in rows]

    def event(self, kind, run_id=None, **data):
        self.db.execute("INSERT INTO events(time,run_id,kind,body) VALUES(?,?,?,?)",
                        (now(), run_id, kind, dumps(data)))

    def events(self, after=0, run_id=None, limit=200, wait=0):
        query = "SELECT sequence,time,run_id,kind,body FROM events WHERE sequence>?"
        args = [int(after)]
        if run_id:
            query += " AND run_id=?"
            args.append(run_id)
        query += " ORDER BY sequence LIMIT ?"
        args.append(min(max(int(limit), 1), 1000))
        wait = float(wait)
        if not 0 <= wait <= 25:
            raise ValueError('Event wait must be between 0 and 25 seconds')
        deadline = time.monotonic() + wait
        with self.changed:
            while True:
                rows = self.db.execute(query, args).fetchall()
                if rows or time.monotonic() >= deadline:
                    break
                if run_id:
                    row = self.db.execute('SELECT state FROM runs WHERE id=?', (run_id,)).fetchone()
                    if not row or row[0] in {'completed', 'failed', 'cancelled', 'interrupted'}:
                        break
                self.changed.wait(deadline - time.monotonic())
        return [{"sequence": n, "time": t, "run_id": r, "kind": k, **json.loads(b)} for n,t,r,k,b in rows]

    def recover(self):
        with self.transaction():
            active = self.db.execute("SELECT body FROM runs WHERE state IN ('running','cancelling')").fetchall()
            for row in active:
                run = json.loads(row[0])
                run.update(state="interrupted", ended=now(), error="Service stopped during this run")
                self.put("runs", run)
                self.event("run.interrupted", run["id"])
                for op_row in self.db.execute("SELECT body FROM operations WHERE run_id=? AND state IN ('queued','running')", (run["id"],)).fetchall():
                    op = json.loads(op_row[0]); op.update(state="interrupted", ended=now())
                    self.put("operations", op)
                    self.event("operation.interrupted", run["id"], operation_id=op["id"])
            rows = self.db.execute("SELECT body FROM runs WHERE state='queued' ORDER BY rowid").fetchall()
            return [json.loads(r[0]) for r in rows]

    def platforms(self):
        with self.lock:
            rows = self.db.execute('''SELECT p.body FROM platform_versions p JOIN
                (SELECT id,MAX(revision) AS revision FROM platform_versions GROUP BY id) latest
                ON p.id=latest.id AND p.revision=latest.revision ORDER BY p.id''').fetchall()
        return [json.loads(row[0]) for row in rows]

    def platform_history(self, platform_id):
        with self.lock:
            return [json.loads(row[0]) for row in self.db.execute(
                'SELECT body FROM platform_versions WHERE id=? ORDER BY revision DESC', (platform_id,))]

    def save_platform(self, record):
        with self.transaction():
            self.db.execute('INSERT INTO platform_versions VALUES(?,?,?)',
                            (record['id'], record['revision'], dumps(record)))
            self.event('platform.configured', platform_id=record['id'], revision=record['revision'])

    def resource_holds(self):
        with self.lock:
            return {resource:json.loads(body) for resource,body in self.db.execute('SELECT resource,body FROM resource_holds')}

    def hold_resources(self, resources, operation_id, reason):
        with self.transaction():
            for resource in resources:
                record = {'resource':resource, 'operation_id':operation_id, 'reason':reason, 'time':now()}
                self.db.execute('INSERT OR REPLACE INTO resource_holds VALUES(?,?)',(resource,dumps(record)))

    def resolve_resources(self, resources, observation):
        with self.transaction():
            for resource in resources:
                self.db.execute('DELETE FROM resource_holds WHERE resource=?',(resource,))
            self.event('resources.resolved', resources=resources, observation=observation)

    def close(self):
        with self.lock:
            self.db.close()
