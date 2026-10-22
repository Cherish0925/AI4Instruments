"""One scheduler for experiment dependencies, device resources and worker processes."""
from __future__ import annotations
import base64
import io
import json
import mimetypes
import os
import re
import signal
import subprocess
import sys
import threading
import time
import uuid
import zipfile
from concurrent.futures import ThreadPoolExecutor, CancelledError
from collections import deque
from pathlib import Path, PurePosixPath
from .config import save_json
from .drivers import make_driver, parameters
from .store import Store, dumps, now

TERMINAL = {"completed", "failed", "cancelled", "interrupted"}


def identifier(prefix):
    return prefix + "_" + uuid.uuid4().hex[:20]


def relative_path(name):
    path = PurePosixPath(name)
    if not name or path.is_absolute() or ".." in path.parts or "\\" in name or ":" in name:
        raise ValueError("Expected a relative file path")
    return Path(*path.parts)


class Engine:
    def __init__(self, home, config):
        self.home, self.config = Path(home), config
        self.home.mkdir(parents=True, exist_ok=True)
        self.lock = threading.RLock()
        self.wake = threading.Event()
        self.stopping = False
        self.endpoint = ""
        self.devices, self.descriptions, self.device_records = {}, {}, {}
        self.runs, self.operations, self.futures, self.processes = {}, {}, {}, {}
        self.reservations, self.claims = {}, {}
        self.cancellations = {}
        self.errors = []
        self.discovery = {"connections":[], "providers":[]}
        self.discovery_stop = threading.Event()
        self.discovery_thread = None
        self.store = Store(self.home / "records.sqlite3")
        self.worker_count = max(1, int(config.get("workers", 8)))
        self.package_count = max(1, int(config.get("package_workers", 4)))
        self.pool = ThreadPoolExecutor(max_workers=self.worker_count, thread_name_prefix="iop-device")
        for device in config.get("devices", []):
            try:
                self.register(device, persist=False)
            except Exception as error:
                self.errors.append({"device":device.get("id"), "error":str(error)})
        for run in self.store.recover():
            self.runs[run["id"]] = run
            for op in reversed(self.store.list("operations", run["id"], 10000)):
                self.operations[op["id"]] = op
        self.thread = threading.Thread(target=self._loop, name="iop-scheduler", daemon=True)

    def start(self):
        self.thread.start()
        interval = float(self.config.get("discovery_interval", 30))
        if interval > 0:
            def inventory_loop():
                while not self.discovery_stop.is_set():
                    try:
                        self.scan()
                    except Exception as error:
                        self.discovery = {"connections":[], "providers":[{"name":"inventory", "available":False, "detail":str(error)}]}
                    self.discovery_stop.wait(interval)
            self.discovery_thread = threading.Thread(target=inventory_loop, name="iop-discovery", daemon=True)
            self.discovery_thread.start()

    def scan(self):
        from .discovery import discover, match_profiles
        inventory = discover()
        with self.lock:
            if self.stopping:
                return inventory
            for record in match_profiles(inventory, self.config.get("profiles", [])):
                if record["id"] not in self.devices:
                    try:
                        self.register(record)
                    except Exception as error:
                        inventory.setdefault("profile_errors", []).append({"device":record["id"], "error":str(error)})
            for record in self.device_records.values():
                c = record.get("config", {})
                if record["driver"] == "scpi" and c.get("transport", "tcp") == "tcp":
                    inventory["connections"].append({"transport":"tcp", "address":str(c.get("host"))+":"+str(c.get("port",5025)), "id":record["id"], "status":"registered"})
            for record in self.device_records.values():
                c = record.get("config", {})
                if record["driver"] == "modbus" and c.get("transport","tcp") == "tcp":
                    inventory["connections"].append({"transport":"modbus-tcp","address":str(c.get("host"))+":"+str(c.get("port",502)),"id":record["id"],"status":"registered"})
                elif record["driver"] == "http":
                    inventory["connections"].append({"transport":"http","address":c.get("base_url"),"id":record["id"],"status":"registered"})
            inventory["updated"] = now()
            self.discovery = inventory
            return inventory

    def _resources(self, values):
        if not isinstance(values, (list, tuple)):
            raise ValueError("Resources must be a list")
        resources = set()
        for value in values:
            if not isinstance(value, str) or not value:
                raise ValueError("Resources must be nonempty names")
            if value in self.devices:
                resources.add("device:" + value)
                record = self.device_records[value]
                resources.update("shared:" + r for r in record.get("resources", []))
                resources.update("shared:" + r for r in self.descriptions[value].get("resources", []))
            else:
                resources.add("shared:" + value)
        return sorted(resources)

    def register(self, record, persist=True):
        with self.lock:
            if self.stopping:
                raise ValueError("Service is stopping")
            device_id = record.get("id", "")
            if not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9_.-]{0,79}", device_id):
                raise ValueError("Device ID must use letters, digits, dots, dashes or underscores")
            if device_id in self.devices:
                raise ValueError("Device is already registered: " + device_id)
            record = json.loads(dumps(record))
            driver = make_driver(record, self.devices)
            description = driver.describe()
            if not isinstance(description.get("operations"), dict) or not description["operations"]:
                raise ValueError("Driver must describe its operations")
            for spec in description["operations"].values():
                if not isinstance(spec, dict):
                    raise ValueError("Invalid operation description")
            # A physical connection has one registered owner in this platform.
            if record["driver"] == "scpi":
                c = record.get("config", {}); transport = c.get("transport", "tcp")
                address = (transport, c.get("host"), c.get("port", 5025) if transport == "tcp" else c.get("port"), c.get("resource"))
                for old in self.device_records.values():
                    o = old.get("config", {}); kind = o.get("transport", "tcp")
                    other = (kind, o.get("host"), o.get("port", 5025) if kind == "tcp" else o.get("port"), o.get("resource"))
                    if old["driver"] == "scpi" and address == other:
                        raise ValueError("This connection already belongs to " + old["id"])
            self.devices[device_id] = driver
            self.device_records[device_id] = record
            self.descriptions[device_id] = json.loads(dumps({"id":device_id, "driver":record["driver"], **description}))
            if persist:
                self.config["devices"] = list(self.device_records.values())
                save_json(self.home / "config.json", self.config)
                with self.store.transaction():
                    self.store.event("device.registered", device_id=device_id)
            return self.descriptions[device_id]

    def _operation(self, run_id, step):
        device_id, name = step["device"], step["operation"]
        if device_id not in self.devices:
            raise ValueError("Device is not registered: " + device_id)
        specs = self.descriptions[device_id]["operations"]
        if name not in specs:
            raise ValueError("Unknown operation: " + device_id + "." + name)
        if not isinstance(step.get("arguments", {}), dict):
            raise ValueError("Arguments must be an object")
        args = parameters(specs[name], step.get("arguments", {}))
        return {"id":identifier("op"), "run_id":run_id, "step":step.get("id"), "device":device_id,
                "operation":name, "arguments":args, "after":step.get("after", []), "state":"queued", "created":now(),
                "resources":sorted(set(self._resources([device_id] + step.get("resources", [])))),
                "request_id":step.get("request_id")}

    def submit(self, spec, package=None):
        with self.lock:
            if self.stopping:
                raise ValueError("Service is stopping")
            spec = json.loads(dumps(spec))
            previous = self.store.request("runs", spec.get("request_id"))
            if previous:
                if previous["spec"] != spec or (package is not None and (self.home / "runs" / previous["id"] / "package.zip").read_bytes() != package):
                    raise ValueError("request_id already names a different experiment")
                return previous
            run_id = identifier("run")
            run = {"id":run_id, "state":"queued", "created":now(), "request_id":spec.get("request_id"),
                   "kind":"package" if package is not None else "workflow", "name":spec.get("name", "Experiment"),
                   "project":spec.get("project"), "experiment":spec.get("experiment"), "spec":spec,
                   "parameters":spec.get("parameters", {}), "resources":self._resources(spec.get("resources", [])),
                   "devices":self.descriptions.copy(), "operations":[], "result":None}
            operations = []
            if package is None:
                steps = spec.get("steps", [])
                if not isinstance(steps, list) or not steps or len(steps) > 10000:
                    raise ValueError("A workflow needs between 1 and 10000 steps")
                if any(not isinstance(s, dict) or not isinstance(s.get("after", []), list) for s in steps):
                    raise ValueError("Each step is an object with an optional after list")
                names = [s.get("id") for s in steps]
                if any(not isinstance(n, str) or not n for n in names) or len(set(names)) != len(names):
                    raise ValueError("Each step needs a unique ID")
                dependents = {name:[] for name in names}
                remaining = {}
                for step in steps:
                    dependencies = set(step.get("after", []))
                    if not dependencies <= dependents.keys():
                        raise ValueError("Step dependencies contain an unknown step")
                    remaining[step["id"]] = len(dependencies)
                    for dependency in dependencies:
                        dependents[dependency].append(step["id"])
                ready = deque(name for name,count in remaining.items() if count == 0)
                visited = 0
                while ready:
                    visited += 1
                    for child in dependents[ready.popleft()]:
                        remaining[child] -= 1
                        if remaining[child] == 0:
                            ready.append(child)
                if visited != len(steps):
                    raise ValueError("Step dependencies contain a cycle")
                operations = [self._operation(run_id, s) for s in steps]
                if run["resources"]:
                    run["resources"] = sorted(set(run["resources"]).union(*(op["resources"] for op in operations)))
            directory = self.home / "runs" / run_id
            directory.mkdir(parents=True)
            (directory / "output").mkdir()
            if package is not None:
                run["package"] = self._unpack(directory, package)
            save_json(directory / "experiment.json", {"id":run_id, **spec})
            run["operations"] = [op["id"] for op in operations]
            with self.store.transaction():
                self.store.put("runs", run)
                self.store.event("run.accepted", run_id, name=run["name"], kind_of_run=run["kind"])
                for op in operations:
                    self.store.put("operations", op)
                    self.store.event("operation.queued", run_id, operation_id=op["id"], device=op["device"], operation=op["operation"])
            self.runs[run_id] = run
            self.operations.update({op["id"]:op for op in operations})
            self.wake.set()
            return json.loads(dumps(run))

    def _unpack(self, directory, data):
        package_dir = directory / "package"
        package_dir.mkdir()
        with zipfile.ZipFile(io.BytesIO(data)) as archive:
            if sum(f.file_size for f in archive.infolist()) > 128 * 1024 * 1024:
                raise ValueError("Expanded package exceeds 128 MiB")
            for member in archive.infolist():
                path = package_dir / relative_path(member.filename.rstrip("/"))
                if member.is_dir():
                    path.mkdir(parents=True, exist_ok=True)
                else:
                    path.parent.mkdir(parents=True, exist_ok=True)
                    path.write_bytes(archive.read(member))
        manifest_path = package_dir / "package.json"
        manifest = json.loads(manifest_path.read_text(encoding="utf-8")) if manifest_path.exists() else {"command":["{python}", "experiment.py"]}
        command = manifest.get("command", ["{python}", "experiment.py"])
        if not isinstance(command, list) or not command or any(not isinstance(s, str) or not s for s in command):
            raise ValueError("package.json command must be a nonempty string array")
        manifest["command"] = command
        (directory / "package.zip").write_bytes(data)
        return manifest

    def invoke(self, run_id, step):
        with self.lock:
            run = self.runs.get(run_id)
            if not run or run["kind"] != "package" or run["state"] != "running":
                raise ValueError("Operations require a running experiment package")
            old = self.store.request("operations", step.get("request_id"))
            if old:
                if old["run_id"] != run_id or old["device"] != step["device"] or old["operation"] != step["operation"] or old["arguments"] != parameters(self.descriptions[step["device"]]["operations"][step["operation"]], step.get("arguments", {})):
                    raise ValueError("request_id already names a different operation")
                return old
            op = self._operation(run_id, step)
            if run["resources"] and not set(op["resources"]) <= set(run["resources"]):
                raise ValueError("Include every device used by this package in its resources at submission")
            if op["after"]:
                raise ValueError("Package programs express dependencies by waiting for operation results")
            run["operations"].append(op["id"])
            with self.store.transaction():
                self.store.put("runs", run); self.store.put("operations", op)
                self.store.event("operation.queued", run_id, operation_id=op["id"], device=op["device"], operation=op["operation"])
            self.operations[op["id"]] = op
            self.wake.set()
            return json.loads(dumps(op))

    def _save_run(self, run, kind):
        with self.store.transaction():
            self.store.put("runs", run)
            self.store.event(kind, run["id"], state=run["state"], error=run.get("error"))

    def cancel(self, run_id):
        with self.lock:
            run = self.runs.get(run_id)
            if not run:
                return self.store.get("runs", run_id)
            if run["state"] in TERMINAL:
                return json.loads(dumps(run))
            run["state"] = "cancelling"
            run["end_state"] = "cancelled"
            self._save_run(run, "run.cancelling")
            self._stop_pending(run)
            self.wake.set()
            return json.loads(dumps(run))

    def _stop_pending(self, run):
        for op_id in run["operations"]:
            op = self.operations[op_id]
            if op["state"] == "queued":
                op.update(state="cancelled", ended=now())
                with self.store.transaction():
                    self.store.put("operations", op)
                    self.store.event("operation.cancelled", run["id"], operation_id=op_id)
            elif op["state"] == "running":
                self.cancellations[op_id].set()
        process = self.processes.get(run["id"])
        if process and process.poll() is None:
            self._terminate(process)
            run.setdefault("terminate_at", time.monotonic())

    @staticmethod
    def _terminate(process, force=False):
        try:
            if sys.platform == "win32":
                subprocess.run(["taskkill", "/PID", str(process.pid), "/T", "/F"],
                               stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, timeout=10)
            else:
                os.killpg(process.pid, signal.SIGKILL if force else signal.SIGTERM)
        except (ProcessLookupError, OSError, subprocess.SubprocessError):
            pass

    def _start_package(self, run):
        directory = self.home / "runs" / run["id"]
        env = os.environ.copy()
        env.update(IOP_ENDPOINT=self.endpoint, IOP_TOKEN=self.config["token"], IOP_RUN_ID=run["id"],
                   IOP_RUN_DIR=str(directory / "output"), IOP_PARAMETERS_JSON=dumps(run["parameters"]),
                   PYTHONUNBUFFERED="1")
        source_path = str(Path(__file__).resolve().parents[2])
        env["PYTHONPATH"] = source_path + os.pathsep + env.get("PYTHONPATH", "")
        command = [sys.executable if part == "{python}" else part for part in run["package"]["command"]]
        with open(directory / "stdout.txt", "wb") as out, open(directory / "stderr.txt", "wb") as err:
            options = {"creationflags":subprocess.CREATE_NEW_PROCESS_GROUP} if sys.platform == "win32" else {"start_new_session":True}
            self.processes[run["id"]] = subprocess.Popen(command, cwd=directory / "package", env=env,
                                                          stdin=subprocess.DEVNULL, stdout=out, stderr=err, **options)

    def _finish(self, run, state):
        run.update(state=state, ended=now())
        run.pop("terminate_at", None)
        self.reservations = {r:owner for r,owner in self.reservations.items() if owner != run["id"]}
        directory = self.home / "runs" / run["id"]
        save_json(directory / "run.json", run)
        for root in [directory / "output"]:
            for path in root.rglob("*"):
                if path.is_file() and not path.is_symlink() and path.resolve().is_relative_to(root.resolve()):
                    self._file_record(run["id"], path, "output/" + path.relative_to(root).as_posix())
        for name in ("stdout.txt", "stderr.txt", "experiment.json", "package.zip"):
            if (directory / name).is_file():
                self._file_record(run["id"], directory / name, name)
        self._save_run(run, "run." + state)
        # Completed records live in SQLite; only active work remains in memory.
        for op_id in run["operations"]:
            self.operations.pop(op_id, None)
        self.processes.pop(run["id"], None)
        self.runs.pop(run["id"], None)

    def _file_record(self, run_id, path, name):
        for existing in self.store.list("artifacts", run_id, 10000):
            if existing["name"] == name:
                return existing
        item = {"id":identifier("file"), "run_id":run_id, "name":name, "size":path.stat().st_size,
                "media_type":mimetypes.guess_type(name)[0] or "application/octet-stream", "created":now()}
        with self.store.transaction():
            self.store.db.execute("INSERT INTO artifacts VALUES(?,?,?)", (item["id"], run_id, dumps(item)))
            self.store.event("artifact.saved", run_id, artifact_id=item["id"], name=name, size=item["size"])
        return item

    def save_result(self, run_id, result):
        with self.lock:
            run = self.runs.get(run_id)
            if not run or run["state"] != "running":
                raise ValueError("Run is not running")
            run["result"] = json.loads(dumps(result))
            save_json(self.home / "runs" / run_id / "output" / "result.json", result)
            self._save_run(run, "run.result")
            return result

    def artifact(self, run_id, name, data):
        with self.lock:
            self.store.get("runs", run_id)
            path = self.home / "runs" / run_id / "output" / relative_path(name)
            root = (self.home / "runs" / run_id / "output").resolve()
            if not path.resolve().is_relative_to(root):
                raise ValueError("File must remain in the run output directory")
            if path.exists():
                raise ValueError("An output file already has this name")
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(data)
            return self._file_record(run_id, path, "output/" + relative_path(name).as_posix())

    def _tick(self):
        # Completed device work releases resources only after the driver returns.
        for op_id, future in list(self.futures.items()):
            if not future.done():
                continue
            op = self.operations[op_id]; run = self.runs[op["run_id"]]
            try:
                op["result"] = json.loads(dumps(future.result()))
                op["state"] = "completed"
            except CancelledError:
                op["state"] = "cancelled"
            except BaseException as error:
                op.update(state="failed", error=f"{type(error).__name__}: {error}")
                if run["state"] == "running":
                    run.update(state="cancelling", end_state="failed", error=op["error"])
                    self._save_run(run, "run.failing")
                    self._stop_pending(run)
            op["ended"] = now()
            with self.store.transaction():
                self.store.put("operations", op)
                self.store.event("operation." + op["state"], run["id"], operation_id=op_id, result=op.get("result"), error=op.get("error"))
            self.claims = {r:owner for r,owner in self.claims.items() if owner != op_id}
            del self.futures[op_id]; self.cancellations.pop(op_id, None)
        for run in list(self.runs.values()):
            if run["state"] == "queued":
                continue
            process = self.processes.get(run["id"])
            if process and run["state"] == "cancelling" and process.poll() is None and time.monotonic() - run.get("terminate_at", time.monotonic()) > 3:
                self._terminate(process, force=True)
            process_done = process is None or process.poll() is not None
            ops_done = all(self.operations[oid]["state"] in TERMINAL for oid in run["operations"])
            if run["kind"] == "package" and process_done and process is not None:
                run["exit_code"] = process.returncode
                if process.returncode and run["state"] == "running":
                    run.update(state="cancelling", end_state="failed", error="Experiment process exited with code " + str(process.returncode))
                    self._stop_pending(run)
                    ops_done = all(self.operations[oid]["state"] in TERMINAL for oid in run["operations"])
            if ops_done and process_done:
                if run["state"] == "cancelling":
                    self._finish(run, run.get("end_state", "cancelled"))
                elif run["kind"] == "workflow" or process is not None:
                    if run["kind"] == "workflow":
                        run["result"] = {self.operations[oid]["step"]: self.operations[oid].get("result") for oid in run["operations"]}
                    self._finish(run, "completed")
        if self.stopping:
            return
        # Reserve all requested resources together. Waiting experiments do not hold partial sets.
        waiting = set()
        for run in list(self.runs.values()):
            if run["state"] != "queued":
                continue
            res = set(run["resources"])
            if run["kind"] == "package" and sum(p.poll() is None for p in self.processes.values()) >= self.package_count:
                continue
            if res & (set(self.reservations) | set(self.claims) | waiting):
                waiting.update(res); continue
            for resource in res:
                self.reservations[resource] = run["id"]
            missing = [self.operations[oid]["device"] for oid in run["operations"] if self.operations[oid]["device"] not in self.devices]
            if missing:
                run.update(state="cancelling", end_state="failed", error="Missing registered devices: " + ", ".join(missing))
                self._stop_pending(run)
                continue
            run.update(state="running", started=now())
            self._save_run(run, "run.started")
            if run["kind"] == "package":
                try:
                    self._start_package(run)
                except Exception as error:
                    run.update(state="cancelling", end_state="failed", error=str(error))
        blocked = set()
        states_by_run = {rid:{self.operations[oid]["step"]:self.operations[oid]["state"] for oid in r["operations"]} for rid,r in self.runs.items()}
        for op in self.operations.values():
            if op["state"] != "queued":
                continue
            run = self.runs[op["run_id"]]
            if run["state"] != "running":
                continue
            states = states_by_run[run["id"]]
            if any(states.get(dep) != "completed" for dep in op["after"]):
                continue
            resources = set(op["resources"])
            owned = {r for r,owner in self.reservations.items() if owner == run["id"]}
            unavailable = set(self.claims) | (set(self.reservations) - owned) | (blocked - owned) | (waiting - owned)
            if resources & unavailable:
                blocked.update(resources); continue
            if len(self.futures) >= self.worker_count:
                break
            op.update(state="running", started=now())
            with self.store.transaction():
                self.store.put("operations", op)
                self.store.event("operation.started", run["id"], operation_id=op["id"], device=op["device"], operation=op["operation"])
            for resource in resources:
                self.claims[resource] = op["id"]
            event = threading.Event(); self.cancellations[op["id"]] = event
            future = self.pool.submit(self.devices[op["device"]].invoke, op["operation"], op["arguments"], event)
            self.futures[op["id"]] = future
            future.add_done_callback(lambda _: self.wake.set())

    def _loop(self):
        while True:
            self.wake.wait(0.05); self.wake.clear()
            with self.lock:
                try:
                    self._tick()
                except Exception as error:
                    self.errors.append({"time":now(), "error":str(error)})
                    self.errors = self.errors[-20:]
                if self.stopping and not self.futures and not self.processes:
                    return

    def metrics(self):
        with self.lock:
            return {"devices":len(self.devices), "queued_runs":sum(r["state"] == "queued" for r in self.runs.values()),
                    "active_runs":sum(r["state"] != "queued" for r in self.runs.values()), "active_operations":len(self.futures),
                    "queued_operations":sum(o["state"] == "queued" for o in self.operations.values()),
                    "workers":self.worker_count, "package_workers":self.package_count, "errors":self.errors[-5:]}

    def close(self):
        with self.lock:
            self.stopping = True
            self.discovery_stop.set()
            for run in list(self.runs.values()):
                if run["state"] != "queued":
                    run.update(state="cancelling", end_state="interrupted")
                    self._stop_pending(run)
            self.wake.set()
        if self.thread.is_alive():
            self.thread.join()
        self.pool.shutdown(wait=True)
        for driver in self.devices.values():
            driver.close()
        self.store.close()
