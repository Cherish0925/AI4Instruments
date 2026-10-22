"""Persistent experiment records and ordered events."""
from __future__ import annotations
import json
import sqlite3
import threading
from datetime import datetime, timezone
from contextlib import contextmanager


def now():
    return datetime.now(timezone.utc).isoformat(timespec="milliseconds")


def dumps(value):
    return json.dumps(value, ensure_ascii=False, allow_nan=False, separators=(",", ":"))


class Store:
    def __init__(self, path):
        self.lock = threading.RLock()
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
        ''')
        self.db.commit()

    @contextmanager
    def transaction(self):
        with self.lock:
            try:
                yield
                self.db.commit()
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

    def get(self, table, identifier):
        if table not in {"runs", "operations", "artifacts"}:
            raise ValueError(table)
        with self.lock:
            row = self.db.execute(f"SELECT body FROM {table} WHERE id=?", (identifier,)).fetchone()
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

    def list(self, table, run_id=None, limit=100):
        if table not in {"runs", "operations", "artifacts"}:
            raise ValueError(table)
        with self.lock:
            where, args = (" WHERE run_id=?", [run_id]) if run_id else ("", [])
            args.append(min(max(int(limit), 1), 10000))
            rows = self.db.execute(f"SELECT body FROM {table}{where} ORDER BY rowid DESC LIMIT ?", args)
            return [json.loads(r[0]) for r in rows]

    def event(self, kind, run_id=None, **data):
        self.db.execute("INSERT INTO events(time,run_id,kind,body) VALUES(?,?,?,?)",
                        (now(), run_id, kind, dumps(data)))

    def events(self, after=0, run_id=None, limit=200):
        query = "SELECT sequence,time,run_id,kind,body FROM events WHERE sequence>?"
        args = [int(after)]
        if run_id:
            query += " AND run_id=?"
            args.append(run_id)
        query += " ORDER BY sequence LIMIT ?"
        args.append(min(max(int(limit), 1), 1000))
        with self.lock:
            rows = self.db.execute(query, args).fetchall()
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

    def close(self):
        with self.lock:
            self.db.close()
