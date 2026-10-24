"""Configuration and one running service per data directory."""
from __future__ import annotations
import json
import os
import secrets
import sys
from pathlib import Path

VERSION = "0.8.1"


def home_path(value=None):
    return Path(value or os.environ.get("IOP_HOME", Path.home() / ".iop")).expanduser().resolve()


def save_json(path, value):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + ".tmp")
    with os.fdopen(os.open(temporary, os.O_WRONLY | os.O_CREAT | os.O_TRUNC, 0o600), "w", encoding="utf-8") as file:
        file.write(json.dumps(value, ensure_ascii=False, indent=2, allow_nan=False) + "\n")
    os.replace(temporary, path)


def initialize(home=None, demo=False, port=8765):
    home = home_path(home)
    home.mkdir(parents=True, exist_ok=True)
    path = home / "config.json"
    existing = json.loads(path.read_text(encoding="utf-8")) if path.exists() else None
    if existing and not demo:
        return existing
    if existing and existing.get("devices"):
        if all(d.get("driver") == "simulated" for d in existing["devices"]):
            return existing
        raise ValueError("Use a separate --home directory for simulated devices")
    devices = []
    if demo:
        devices = [
            {"id": "stage", "driver": "simulated", "config": {"kind": "stage"}},
            {"id": "meter", "driver": "simulated", "config": {"kind": "meter", "stage": "stage"}},
            {"id": "aux", "driver": "simulated", "config": {"kind": "stage"}},
        ]
    config = {"host": "127.0.0.1", "port": port, "token": secrets.token_urlsafe(32),
              "workers": 8, "package_workers": 4, "discovery_interval": 30, "profiles": [],
              "software_profiles": [], "resource_pools": {}, "devices": devices}
    if existing:
        existing["devices"] = devices
        config = existing
    save_json(path, config)
    try:
        path.chmod(0o600)
    except OSError:
        pass
    return config


class InstanceLock:
    def __init__(self, home):
        self.file = open(Path(home) / "service.lock", "a+b")
        try:
            if os.fstat(self.file.fileno()).st_size == 0:
                self.file.write(b"0")
                self.file.flush()
            self.file.seek(0)
            if sys.platform == "win32":
                import msvcrt
                msvcrt.locking(self.file.fileno(), msvcrt.LK_NBLCK, 1)
            else:
                import fcntl
                fcntl.flock(self.file.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
        except OSError:
            self.file.close()
            raise RuntimeError("An IOP service already owns this data directory") from None

    def close(self):
        if not self.file.closed:
            self.file.seek(0)
            if sys.platform == "win32":
                import msvcrt
                msvcrt.locking(self.file.fileno(), msvcrt.LK_UNLCK, 1)
            self.file.close()
