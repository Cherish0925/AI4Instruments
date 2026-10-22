"""One scheduler for experiment dependencies, device resources and worker processes."""
from __future__ import annotations
import base64
import io
import json
import mimetypes
import os
import signal
import subprocess
import sys
import threading
import time
import uuid
import zipfile
from concurrent.futures import ThreadPoolExecutor, CancelledError
from pathlib import Path, PurePosixPath
from .config import save_json
from .drivers import make_driver, parameters
from .store import Store, dumps, now
from . import platforms as platform_model

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
        self.registration_lock = threading.RLock()
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
        self.platforms = {p['id']: p for p in self.store.platforms()}
        self.platform_resources = platform_model.resource_index(self.platforms)
        self.resource_holds = self.store.resource_holds()
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
        if self.stopping:
            return inventory
        for record in match_profiles(inventory, self.config.get("profiles", [])):
            if record["id"] not in self.devices:
                try:
                    self.register(record)
                except Exception as error:
                    inventory.setdefault("profile_errors", []).append({"device":record["id"], "error":str(error)})
        with self.lock:
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

    def _resources(self, values, operation=None):
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
                resources.update(platform_model.operation_resources(self.platforms, value, operation)
                                 if operation else self.platform_resources.get(value, ()))
            else:
                resources.add("shared:" + value)
        return sorted(resources)

    def list_platforms(self):
        with self.lock:
            return [self.platform_info(p) for p in sorted(self.platforms)]

    def resolve_resources(self, resources, observation):
        with self.lock:
            platform_model.strings(resources, 'Resources')
            if not isinstance(observation,str) or not observation.strip():
                raise ValueError('Describe the observed device state before returning resources to use')
            if set(resources) - self.resource_holds.keys():
                raise ValueError('Resource is not awaiting an observed state')
            if set(resources) & (set(self.claims) | set(self.reservations)):
                raise ValueError('Affected operations are still running')
            self.store.resolve_resources(resources, observation)
            self.resource_holds = self.store.resource_holds()
            self.wake.set()
            return {'released':resources}

    def platform_info(self, platform_id):
        with self.lock:
            record = json.loads(dumps(self.platforms[platform_id]))
            record['active_runs'] = [r['id'] for r in self.runs.values() if r.get('platform', {}).get('id') == platform_id]
            record['missing_devices'] = sorted(set(record['definition']['devices']) - self.devices.keys())
            return record

    def prepare_platform(self, definition):
        definition = platform_model.description(definition, self.devices)
        for procedure in definition['procedures'].values():
            for step in procedure['steps']:
                self._operation('prepare', step)
        return definition

    def apply_platform(self, definition, expected_revision=0):
        with self.lock:
            if self.stopping:
                raise ValueError('Service is stopping')
            definition = self.prepare_platform(definition)
            old = self.platforms.get(definition['id'])
            revision = old['revision'] if old else 0
            if type(expected_revision) is not int or expected_revision != revision:
                raise ValueError('Platform revision changed; current revision is ' + str(revision))
            if old and old['definition'] == definition:
                return self.platform_info(definition['id'])
            affected = set(definition['devices']) | set(old['definition']['devices'] if old else [])
            resource_ids = {r['id'] for r in definition['resources'] + (old['definition']['resources'] if old else [])}
            for p in self.platforms.values():
                for resource in p['definition']['resources']:
                    if resource['id'] in resource_ids:
                        affected.update(resource['devices'])
            for run in self.runs.values():
                used = {self.operations[o]['device'] for o in run['operations']}
                used.update(r[7:] for r in run['resources'] if r.startswith('device:'))
                if run['kind'] == 'package' and not run['resources']:
                    used.update(run.get('platform', {}).get('definition', {}).get('devices', self.devices))
                if affected & used or {'shared:' + r for r in resource_ids} & set(run['resources']):
                    raise ValueError('Wait for or cancel affected experiment before changing platform: ' + run['id'])
            record = {'id': definition['id'], 'revision': revision + 1, 'updated': now(), 'definition': definition}
            self.store.save_platform(record)
            self.platforms[record['id']] = record
            self.platform_resources = platform_model.resource_index(self.platforms)
            return self.platform_info(record['id'])

    def run_procedure(self, platform_id, procedure_id, request_id=None):
        with self.lock:
            record = self.platforms[platform_id]
            procedure = record['definition']['procedures'][procedure_id]
            return self.submit({'name': record['definition']['name'] + ': ' + procedure_id,
                'platform': platform_id, 'procedure': procedure_id, 'platform_revision': record['revision'],
                'steps': procedure['steps'], 'resources': procedure.get('resources', record['definition']['devices']),
                'request_id': request_id})

    def register(self, record, persist=True):
        # SDK startup can take time; it must not hold the experiment scheduler lock.
        with self.registration_lock:
            record = json.loads(dumps(record))
            device_id = record.get("id", "")
            platform_model.name(device_id, 'Device ID')
            with self.lock:
                if self.stopping:
                    raise ValueError("Service is stopping")
                if device_id in self.devices:
                    raise ValueError("Device is already registered: " + device_id)
                if any(device_id == r['id'] for p in self.platforms.values() for r in p['definition']['resources']):
                    raise ValueError('Device ID already names a shared platform resource: ' + device_id)
                if record["driver"] == "scpi":
                    c = record.get("config", {}); transport = c.get("transport", "tcp")
                    address = (transport, c.get("host"), c.get("port", 5025) if transport == "tcp" else c.get("port"), c.get("resource"))
                    for old in self.device_records.values():
                        o = old.get("config", {}); kind = o.get("transport", "tcp")
                        other = (kind, o.get("host"), o.get("port", 5025) if kind == "tcp" else o.get("port"), o.get("resource"))
                        if old["driver"] == "scpi" and address == other:
                            raise ValueError("This connection already belongs to " + old["id"])
            driver = make_driver(record, self.devices)
            try:
                description = driver.describe()
                if not isinstance(description.get("operations"), dict) or not description["operations"]:
                    raise ValueError("Driver must describe its operations")
                if any(not isinstance(spec, dict) for spec in description["operations"].values()):
                    raise ValueError("Invalid operation description")
                with self.lock:
                    if self.stopping:
                        raise ValueError("Service is stopping")
                    self.devices[device_id] = driver
                    self.device_records[device_id] = record
                    self.descriptions[device_id] = json.loads(dumps({"id":device_id, "driver":record["driver"], **description}))
                    if persist:
                        self.config["devices"] = list(self.device_records.values())
                        save_json(self.home / "config.json", self.config)
                        with self.store.transaction():
                            self.store.event("device.registered", device_id=device_id)
                    return self.descriptions[device_id]
            except BaseException:
                if not any(getattr(other,'worker',None) is getattr(driver,'worker',object()) for other in self.devices.values()):
                    driver.close()
                raise

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
                "resources":sorted(set(self._resources([device_id], name) + self._resources(step.get("resources", [])))),
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
            platform_id = spec.get('platform')
            platform = self.platforms.get(platform_id) if platform_id else None
            if platform_id and platform is None:
                raise ValueError('Unknown platform: ' + str(platform_id))
            if platform and spec.get('platform_revision', platform['revision']) != platform['revision']:
                raise ValueError('Platform revision changed')
            run = {"id":run_id, "state":"queued", "created":now(), "request_id":spec.get("request_id"),
                   "kind":"package" if package is not None else "workflow", "name":spec.get("name", "Experiment"),
                   "project":spec.get("project"), "experiment":spec.get("experiment"), "spec":spec,
                   "parameters":spec.get("parameters", {}), "resources":self._resources(spec.get("resources", [])),
                   "devices":self.descriptions.copy(), "operations":[], "result":None}
            if platform:
                run['platform'] = json.loads(dumps(platform))
                outside = set(spec.get('resources', [])) & (self.devices.keys() - set(platform['definition']['devices']))
                if outside:
                    raise ValueError('Reserved devices must belong to the selected platform')
            operations = []
            if package is None:
                steps = spec.get("steps", [])
                platform_model.steps(steps)
                operations = [self._operation(run_id, s) for s in steps]
                if platform and any(op['device'] not in platform['definition']['devices'] for op in operations):
                    raise ValueError('Workflow devices must belong to the selected platform')
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
            if run.get('platform') and op['device'] not in run['platform']['definition']['devices']:
                raise ValueError('Operation device must belong to the selected platform')
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
        if run.get('platform'):
            env['IOP_PLATFORM_ID'] = run['platform']['id']
            env['IOP_PLATFORM_REVISION'] = str(run['platform']['revision'])
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
                from .process_driver import DriverUnavailable
                if isinstance(error, DriverUnavailable):
                    op['outcome_unknown'] = True
                    self.store.hold_resources(set(op['resources']) | set(run['resources']), op_id, str(error))
                    self.resource_holds = self.store.resource_holds()
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
            involved = set(run['resources']).union(*(self.operations[oid]['resources'] for oid in run['operations']))
            if run['state'] in {'queued','running'} and involved & self.resource_holds.keys():
                run.update(state='cancelling', end_state='interrupted', error='Device outcome is unresolved: ' + ', '.join(sorted(involved & self.resource_holds.keys())))
                self._stop_pending(run)
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
            return {"devices":len(self.devices), "platforms":len(self.platforms), "queued_runs":sum(r["state"] == "queued" for r in self.runs.values()),
                    "active_runs":sum(r["state"] != "queued" for r in self.runs.values()), "active_operations":len(self.futures),
                    "queued_operations":sum(o["state"] == "queued" for o in self.operations.values()),
                    "workers":self.worker_count, "package_workers":self.package_count, "resource_holds":list(self.resource_holds.values()), "errors":self.errors[-5:]}

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
