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
import queue
from collections import OrderedDict, deque
from concurrent.futures import ThreadPoolExecutor, CancelledError
from pathlib import Path, PurePosixPath
from .config import save_json
from .drivers import make_driver, parameters
from .store import Store, dumps, now
from . import platforms as platform_model
from .resources import Allocator, QueueFull, capacities, quantities
from .execution import Context

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
        self.reconnecting, self.offline = set(), {}
        self.runs, self.operations, self.futures, self.processes = {}, {}, {}, {}
        self.allocation = Allocator()
        self.capacities = capacities(config.get('resource_pools', {}))
        self.allocation.limits.update({'pool:' + k: v for k, v in self.capacities.items()})
        self.ready, self.dependents, self.remaining_dependencies, self.remaining = {}, {}, {}, {}
        self.step_ids, self.minimum_capacities = {}, {}
        self.completed = queue.SimpleQueue()
        self.progress_lock = threading.Lock()
        self.progress_updates = {}
        self.progress_times = {}
        self.last_scheduled_run = None
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
            self._index_run(run)
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
        inventory = discover(self.config.get('software_profiles', []))
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
                if record['driver'] in ('scpi', 'modbus') and c.get('transport') in ('serial', 'visa'):
                    address = c.get('resource') if c['transport'] == 'visa' else c.get('port')
                    for candidate in inventory['connections']:
                        if candidate.get('transport') == c['transport'] and candidate.get('address') == address:
                            candidate.update(status='registered', id=record['id'])
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
                if value in self.reconnecting or value in self.offline:
                    raise ValueError('Device needs reconnection: ' + value)
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
            if any(self.allocation.used[r] for r in resources):
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

    def configure_resources(self, value):
        value = capacities(value)
        with self.lock:
            for name in self.capacities.keys() | value.keys():
                key = 'pool:' + name
                needed = max([self.allocation.used[key]] +
                    [self._amounts(r, reserve=True).get(key, 0) for r in self.runs.values()] +
                    [self._amounts(o).get(key, 0) for o in self.operations.values() if o['state'] not in TERMINAL])
                if needed > value.get(name, 0):
                    raise ValueError('Capacity is needed by accepted work: ' + name)
            self.allocation.limits = {k: v for k, v in self.allocation.limits.items() if not k.startswith('pool:')}
            self.allocation.limits.update({'pool:' + k: v for k, v in value.items()})
            self.capacities = value
            self.config['resource_pools'] = value
            save_json(self.home / 'config.json', self.config)
            self.wake.set()
            return self.resource_info()

    def resource_info(self):
        with self.lock:
            return {'capacities': dict(self.capacities), 'allocation': self.allocation.snapshot()}

    def _amounts(self, item, reserve=False):
        amounts = {r: self.allocation.limit(r) if reserve else 1 for r in item['resources']}
        amounts.update(item.get('requirements', {}))
        return amounts

    def _index_run(self, run):
        self.ready[run['id']] = OrderedDict()
        run['involved_resources'] = sorted(self._amounts(run, reserve=True).keys() |
            set().union(*(self._amounts(self.operations[o]).keys() for o in run['operations'])))
        ops = [self.operations[oid] for oid in run['operations']]
        by_step = {o['step']: o for o in ops if o.get('step') is not None}
        self.step_ids[run['id']] = {name: op['id'] for name, op in by_step.items()}
        minimum = self._amounts(run, reserve=True)
        for op in ops:
            for key, count in self._amounts(op).items():
                minimum[key] = max(minimum.get(key, 0), count)
        self.minimum_capacities[run['id']] = minimum
        self.remaining[run['id']] = sum(o['state'] not in TERMINAL for o in ops)
        for op in ops:
            if op['state'] != 'queued':
                continue
            parents = [by_step[step] for step in op['after'] if by_step[step]['state'] != 'completed']
            self.remaining_dependencies[op['id']] = len(parents)
            for parent in parents:
                self.dependents.setdefault(parent['id'], []).append(op['id'])
            if not parents:
                self.ready[run['id']][op['id']] = None

    def _operation_ended(self, op):
        self.ready[op['run_id']].pop(op['id'], None)
        self.remaining[op['run_id']] -= 1
        if op['state'] == 'completed':
            for child in self.dependents.pop(op['id'], []):
                self.remaining_dependencies[child] -= 1
                if self.remaining_dependencies[child] == 0 and self.operations[child]['state'] == 'queued':
                    self.ready[op['run_id']][child] = None

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
                'requirements': procedure.get('requirements', {}),
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
                concurrency = description.get('concurrency', 1)
                if type(concurrency) is not int or concurrency < 1:
                    raise ValueError('Driver concurrency must be a positive integer')
                with self.lock:
                    if self.stopping:
                        raise ValueError("Service is stopping")
                    self.devices[device_id] = driver
                    self.device_records[device_id] = record
                    self.descriptions[device_id] = json.loads(dumps({"id":device_id, "driver":record["driver"], **description}))
                    self.allocation.limits['device:' + device_id] = concurrency
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
        if device_id in self.reconnecting or device_id in self.offline:
            raise ValueError('Device needs reconnection: ' + device_id)
        specs = self.descriptions[device_id]["operations"]
        if name not in specs:
            raise ValueError("Unknown operation: " + device_id + "." + name)
        if not isinstance(step.get("arguments", {}), dict):
            raise ValueError("Arguments must be an object")
        bindings = step.get('bindings', {})
        if set(bindings) & step.get('arguments', {}).keys() or set(bindings) - specs[name].get('parameters', {}).keys():
            raise ValueError('Bindings must name operation parameters not supplied in arguments')
        static = {**specs[name], 'parameters': {k: v for k, v in specs[name].get('parameters', {}).items() if k not in bindings}}
        args = parameters(static, step.get("arguments", {}))
        requirements = {}
        for source in (self.descriptions[device_id], specs[name], step):
            for key, count in quantities(source.get('requirements', {}), self.capacities).items():
                requirements[key] = max(requirements.get(key, 0), count)
        return {"id":identifier("op"), "run_id":run_id, "step":step.get("id"), "device":device_id,
                "operation":name, "arguments":args, "bindings": bindings, "requirements": requirements,
                "after":platform_model.dependencies(step), "state":"queued", "created":now(),
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
            if len(self.runs) >= int(self.config.get('max_active_runs', 10000)):
                raise QueueFull('The service has reached its configured number of active experiments')
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
                   "requirements":quantities(spec.get('requirements', {}), self.capacities),
                   "devices":{}, "operations":[], "operation_count":0, "result":None}
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
                if run["resources"] or run['requirements']:
                    run["resources"] = sorted(set(run["resources"]).union(*(op["resources"] for op in operations)))
                    for op in operations:
                        for key, count in op['requirements'].items():
                            if key[5:] in spec.get('requirements', {}) and count > run['requirements'][key]:
                                raise ValueError('Step needs more capacity than the experiment reservation: ' + key)
                            run['requirements'][key] = max(run['requirements'].get(key, 0), count)
            if len(self.operations) + len(operations) > int(self.config.get('max_active_operations', 100000)):
                raise QueueFull('The service has reached its configured number of active operations')
            used = {op['device'] for op in operations}
            if package is not None:
                used = set(platform['definition']['devices']) if platform else (set(spec.get('resources', [])) & self.devices.keys() or self.devices.keys())
            run['devices'] = {name: self.descriptions[name] for name in used}
            directory = self.home / "runs" / run_id
            directory.mkdir(parents=True)
            (directory / "output").mkdir()
            if package is not None:
                run["package"] = self._unpack(directory, package)
            save_json(directory / "experiment.json", {"id":run_id, **spec})
            run["operations"] = [op["id"] for op in operations]
            run['operation_count'] = len(operations)
            with self.store.transaction():
                self.store.put("runs", run)
                self.store.event("run.accepted", run_id, name=run["name"], kind_of_run=run["kind"])
                for op in operations:
                    self.store.put("operations", op)
                    self.store.event("operation.queued", run_id, operation_id=op["id"], device=op["device"], operation=op["operation"])
            self.runs[run_id] = run
            self.operations.update({op["id"]:op for op in operations})
            self._index_run(run)
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
            if len(self.operations) >= int(self.config.get('max_active_operations', 100000)):
                raise QueueFull('The service has reached its configured number of active operations')
            op = self._operation(run_id, step)
            if run.get('platform') and op['device'] not in run['platform']['definition']['devices']:
                raise ValueError('Operation device must belong to the selected platform')
            if run['resources'] or run.get('requirements'):
                reserved = self._amounts(run, reserve=True)
                if any(count > reserved.get(key, 0) for key, count in self._amounts(op).items()):
                    raise ValueError('Include every device and resource quantity used by this package at submission')
            if op["after"]:
                raise ValueError("Package programs express dependencies by waiting for operation results")
            run["operations"].append(op["id"])
            run['operation_count'] = run.get('operation_count', 0) + 1
            with self.store.transaction():
                self.store.put("runs", run); self.store.put("operations", op)
                self.store.event("operation.queued", run_id, operation_id=op["id"], device=op["device"], operation=op["operation"])
            self.operations[op["id"]] = op
            self.ready[run_id][op['id']] = None
            self.remaining[run_id] += 1
            run['involved_resources'] = sorted(set(run['involved_resources']) | self._amounts(op).keys())
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
                self._operation_ended(op)
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
        if hasattr(process, 'terminate') and hasattr(process, 'done'):
            process.terminate()
            return
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
        from .jobs import NativeJob
        from .process_driver import executable
        try:
            executable()
        except ValueError:
            pass
        else:
            self.processes[run['id']] = NativeJob(command, directory / 'package', env,
                directory / 'stdout.txt', directory / 'stderr.txt',
                timeout=run['package'].get('timeout', 0), notify=self.wake.set)
            return
        with open(directory / "stdout.txt", "wb") as out, open(directory / "stderr.txt", "wb") as err:
            options = {"creationflags":subprocess.CREATE_NEW_PROCESS_GROUP} if sys.platform == "win32" else {"start_new_session":True}
            self.processes[run["id"]] = subprocess.Popen(command, cwd=directory / "package", env=env,
                                                          stdin=subprocess.DEVNULL, stdout=out, stderr=err, **options)

    def _finish(self, run, state):
        run.update(state=state, ended=now())
        run.pop("terminate_at", None)
        self.allocation.finish(run['id'])
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
            self.dependents.pop(op_id, None)
            self.remaining_dependencies.pop(op_id, None)
        self.ready.pop(run['id'], None)
        self.remaining.pop(run['id'], None)
        self.step_ids.pop(run['id'], None)
        self.minimum_capacities.pop(run['id'], None)
        process = self.processes.get(run['id'])
        if process and hasattr(process, 'close'):
            process.close()
        self.processes.pop(run["id"], None)
        self.runs.pop(run["id"], None)

    def _file_record(self, run_id, path, name):
        existing = self.store.artifact_named(run_id, name)
        item = {"id":existing['id'] if existing else identifier("file"), "run_id":run_id, "name":name, "size":path.stat().st_size,
                "media_type":mimetypes.guess_type(name)[0] or "application/octet-stream", "created":now()}
        with self.store.transaction():
            self.store.db.execute('INSERT INTO artifacts(id,run_id,body,name) VALUES(?,?,?,?) '
                'ON CONFLICT(id) DO UPDATE SET body=excluded.body', (item['id'], run_id, dumps(item), name))
            if not existing:
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
        return self.artifact_stream(run_id, name, io.BytesIO(data), len(data))

    def artifact_stream(self, run_id, name, stream, length):
        if type(length) is not int or length < 0:
            raise ValueError('File length must be a nonnegative integer')
        self.store.get('runs', run_id)
        rel = relative_path(name)
        incoming = self.home / 'incoming'
        incoming.mkdir(exist_ok=True)
        temporary = incoming / identifier('upload')
        try:
            with temporary.open('xb') as file:
                left = length
                while left:
                    chunk = stream.read(min(left, 256 * 1024))
                    if not chunk:
                        raise ValueError('File transfer ended before the declared length')
                    file.write(chunk)
                    left -= len(chunk)
            with self.lock:
                path = self.home / 'runs' / run_id / 'output' / rel
                root = (self.home / 'runs' / run_id / 'output').resolve()
                if not path.resolve().is_relative_to(root):
                    raise ValueError('File must remain in the run output directory')
                if path.exists():
                    raise ValueError('An output file already has this name')
                path.parent.mkdir(parents=True, exist_ok=True)
                temporary.rename(path)
                return self._file_record(run_id, path, 'output/' + rel.as_posix())
        finally:
            temporary.unlink(missing_ok=True)

    def reconnect(self, device_id):
        with self.registration_lock:
            with self.lock:
                driver = self.devices[device_id]
                worker = getattr(driver, 'worker', None)
                affected = {name for name, other in self.devices.items()
                            if name == device_id or (worker is not None and getattr(other, 'worker', None) is worker)}
                if any(o['device'] in affected and o['state'] not in TERMINAL for o in self.operations.values()):
                    raise ValueError('Wait for or cancel device operations before reconnecting')
                if any(self.allocation.used['device:' + name] for name in affected):
                    raise ValueError('An experiment still reserves this device')
                self.reconnecting.update(affected)
                registry = {k: v for k, v in self.devices.items() if k not in affected}
            created = {}
            try:
                driver.close()
                for name in sorted(affected):
                    created[name] = make_driver(self.device_records[name], registry)
                    registry[name] = created[name]
                    if created[name].describe() != {k: v for k, v in self.descriptions[name].items() if k not in {'id', 'driver'}}:
                        raise ValueError('Driver description changed; update the device configuration before reuse')
                with self.lock:
                    self.devices.update(created)
                    for name in affected:
                        self.offline.pop(name, None)
                    with self.store.transaction():
                        self.store.event('devices.reconnected', devices=sorted(affected))
                return {'devices': sorted(affected), 'state': 'connected'}
            except Exception as error:
                for new in created.values():
                    new.close()
                with self.lock:
                    self.offline.update({name: str(error) for name in affected})
                raise
            finally:
                with self.lock:
                    self.reconnecting.difference_update(affected)

    def run_info(self, run_id, details=True):
        result = self.store.get('runs', run_id)
        if details:
            result['operation_records'] = list(reversed(self.store.list('operations', run_id, 10000)))
        else:
            result = {key: result[key] for key in ('id', 'state', 'name', 'created', 'started', 'ended', 'error') if key in result}
        return result

    def _progress(self, op_id, value):
        with self.progress_lock:
            self.progress_updates[op_id] = value
            current = time.monotonic()
            if current - self.progress_times.get(op_id, 0) >= 0.2:
                self.progress_times[op_id] = current
                self.wake.set()

    def _tick(self):
        with self.progress_lock:
            progress, self.progress_updates = self.progress_updates, {}
        if progress:
            with self.store.transaction():
                for op_id, value in progress.items():
                    op = self.operations.get(op_id)
                    if op and op['state'] == 'running':
                        op['progress'] = value
                        self.store.put('operations', op)
                        self.store.event('operation.progress', op['run_id'], operation_id=op_id, progress=value)
        # Only completed futures and newly ready dependencies enter the scheduler.
        while not self.completed.empty():
            op_id = self.completed.get()
            future = self.futures[op_id]
            op = self.operations[op_id]; run = self.runs[op['run_id']]
            try:
                op['result'] = json.loads(dumps(future.result()))
                op['state'] = 'completed'
            except CancelledError:
                op['state'] = 'cancelled'
                if run['state'] == 'running':
                    run.update(state='cancelling', end_state='cancelled')
                    self._stop_pending(run)
            except BaseException as error:
                op.update(state='failed', error=f'{type(error).__name__}: {error}')
                from .process_driver import DriverUnavailable
                if isinstance(error, DriverUnavailable):
                    op['outcome_unknown'] = True
                    affected = self._amounts(op).keys() | self._amounts(run, reserve=True).keys()
                    self.store.hold_resources(affected, op_id, str(error))
                    self.resource_holds = self.store.resource_holds()
                if run['state'] == 'running':
                    run.update(state='cancelling', end_state='failed', error=op['error'])
                    self._save_run(run, 'run.failing')
                    self._stop_pending(run)
            op['ended'] = now()
            with self.store.transaction():
                self.store.put('operations', op)
                self.store.event('operation.' + op['state'], run['id'], operation_id=op_id,
                                 result=op.get('result'), error=op.get('error'))
            self._operation_ended(op)
            self.allocation.release(op_id)
            del self.futures[op_id]
            self.cancellations.pop(op_id, None)
            self.progress_times.pop(op_id, None)
            if run['kind'] == 'package':
                # Long-lived programs keep only in-flight calls in memory. All
                # completed operations remain in the indexed SQLite history.
                run['operations'].remove(op_id)
                self.operations.pop(op_id)
                with self.store.transaction():
                    self.store.put('runs', run)
        for run in list(self.runs.values()):
            unresolved = set(run['involved_resources']) & self.resource_holds.keys()
            if run['state'] in {'queued', 'running'} and unresolved:
                run.update(state='cancelling', end_state='interrupted',
                           error='Device outcome is unresolved: ' + ', '.join(sorted(unresolved)))
                self._stop_pending(run)
            if run['state'] == 'queued':
                continue
            process = self.processes.get(run['id'])
            if process and run['state'] == 'cancelling' and process.poll() is None and time.monotonic() - run.get('terminate_at', time.monotonic()) > 3:
                self._terminate(process, force=True)
            process_done = process is None or process.poll() is not None
            if run['kind'] == 'package' and process_done and process is not None:
                run['exit_code'] = process.returncode
                if process.returncode and run['state'] == 'running':
                    run.update(state='cancelling', end_state='failed', error='Experiment process exited with code ' + str(process.returncode))
                    self._stop_pending(run)
            if self.remaining[run['id']] == 0 and process_done:
                if run['state'] == 'cancelling':
                    self._finish(run, run.get('end_state', 'cancelled'))
                elif run['kind'] == 'workflow' or process is not None:
                    if run['kind'] == 'workflow':
                        run['result'] = {self.operations[oid]['step']: self.operations[oid].get('result') for oid in run['operations']}
                    self._finish(run, 'completed')
        if self.stopping:
            return
        waiting = set()
        package_slots = self.package_count - len(self.processes)
        for run in list(self.runs.values()):
            if run['state'] != 'queued':
                continue
            if run['kind'] == 'package' and package_slots <= 0:
                continue
            amounts = self._amounts(run, reserve=True)
            unavailable = [k for k, v in self.minimum_capacities[run['id']].items() if v > self.allocation.limit(k)]
            if unavailable:
                run.update(state='cancelling', end_state='failed', error='Configured capacity no longer fits the experiment: ' + ', '.join(sorted(set(unavailable))))
                self._stop_pending(run)
                continue
            if not self.allocation.can_reserve(amounts, waiting):
                waiting.update(amounts)
                continue
            missing = [self.operations[oid]['device'] for oid in run['operations'] if self.operations[oid]['device'] not in self.devices]
            if missing:
                run.update(state='cancelling', end_state='failed', error='Missing registered devices: ' + ', '.join(missing))
                self._stop_pending(run)
                continue
            self.allocation.reserve(run['id'], amounts)
            run.update(state='running', started=now())
            self._save_run(run, 'run.started')
            if run['kind'] == 'package':
                try:
                    self._start_package(run)
                    package_slots -= 1
                except Exception as error:
                    run.update(state='cancelling', end_state='failed', error=str(error))
        # Round-robin between experiments; a large ready set cannot monopolize starts.
        run_ids = [rid for rid, ready in self.ready.items() if ready and self.runs[rid]['state'] == 'running']
        if self.last_scheduled_run in run_ids:
            index = run_ids.index(self.last_scheduled_run) + 1
            run_ids = run_ids[index:] + run_ids[:index]
        candidates = deque((rid, iter(list(self.ready[rid]))) for rid in run_ids)
        blocked = set()
        while candidates and len(self.futures) < self.worker_count:
            rid, items = candidates.popleft()
            try:
                op_id = next(items)
            except StopIteration:
                continue
            candidates.append((rid, items))
            op = self.operations[op_id]
            amounts = self._amounts(op)
            if not self.allocation.can_claim(rid, amounts, blocked | waiting):
                blocked.update(amounts)
                continue
            self.ready[rid].pop(op_id)
            self.last_scheduled_run = rid
            op.update(state='running', started=now())
            self.allocation.claim(op_id, rid, amounts)
            output = self.home / 'runs' / rid / 'output' / 'operations' / op_id
            context = Context(rid, op_id, output, lambda value, oid=op_id: self._progress(oid, value))
            self.cancellations[op_id] = context
            try:
                if op.get('bindings'):
                    args = dict(op['arguments'])
                    for name, binding in op['bindings'].items():
                        value = self.operations[self.step_ids[rid][binding['step']]]['result']
                        for key in binding.get('path', []):
                            value = value[key]
                        args[name] = value
                    op['arguments'] = parameters(self.descriptions[op['device']]['operations'][op['operation']], args)
                with self.store.transaction():
                    self.store.put('operations', op)
                    self.store.event('operation.started', rid, operation_id=op_id, device=op['device'], operation=op['operation'])
                future = self.pool.submit(self.devices[op['device']].invoke, op['operation'], op['arguments'], context)
            except Exception as error:
                from concurrent.futures import Future
                future = Future(); future.set_exception(error)
            self.futures[op_id] = future
            def completed(_, oid=op_id):
                self.completed.put(oid)
                self.wake.set()
            future.add_done_callback(completed)

    def _loop(self):
        while True:
            self.wake.wait(0.25); self.wake.clear()
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
                    "workers":self.worker_count, "package_workers":self.package_count, "resources":self.resource_info(), "resource_holds":list(self.resource_holds.values()), "errors":self.errors[-5:]}

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
