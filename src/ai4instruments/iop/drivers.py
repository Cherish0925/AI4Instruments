"""Device drivers. Model-specific behavior stays in drivers and descriptions."""
from __future__ import annotations
import importlib
import math
import socket
import time
from concurrent.futures import CancelledError
from .store import now


def parameters(spec, supplied):
    fields = spec.get("parameters", {})
    unknown = set(supplied) - set(fields)
    if unknown:
        raise ValueError("Unknown parameters: " + ", ".join(sorted(unknown)))
    result = {}
    for name, field in fields.items():
        if name not in supplied:
            if "default" in field:
                value = field["default"]
            elif field.get("required", True):
                raise ValueError("Missing parameter: " + name)
            else:
                continue
        else:
            value = supplied[name]
        kind = field.get("type")
        if kind in {"number", "integer"}:
            if isinstance(value, bool) or not isinstance(value, (int, float)) or not math.isfinite(value):
                raise ValueError(name + " must be a finite number")
            if kind == "integer" and not isinstance(value, int):
                raise ValueError(name + " must be an integer")
            if "minimum" in field and value < field["minimum"] or "maximum" in field and value > field["maximum"]:
                raise ValueError(name + " is outside the operation's range")
        elif kind == "string" and not isinstance(value, str):
            raise ValueError(name + " must be a string")
        elif kind == "boolean" and not isinstance(value, bool):
            raise ValueError(name + " must be boolean")
        elif kind == "array":
            if not isinstance(value,list):
                raise ValueError(name + " must be an array")
            if len(value) < field.get("minItems",0) or len(value) > field.get("maxItems",1000000):
                raise ValueError(name + " has an unsupported length")
            if "items" in field:
                for item in value:
                    parameters({"parameters":{"item":field["items"]}},{"item":item})
        elif kind == "object" and not isinstance(value,dict):
            raise ValueError(name + " must be an object")
        if "enum" in field and value not in field["enum"]:
            raise ValueError(name + " must be one of " + str(field["enum"]))
        result[name] = value
    return result


class Driver:
    def __init__(self, device_id, config, registry):
        self.id, self.config, self.registry = device_id, config, registry

    def describe(self):
        raise NotImplementedError

    def invoke(self, operation, arguments, cancelled):
        raise NotImplementedError

    def close(self):
        pass


class Simulated(Driver):
    def __init__(self, *args):
        super().__init__(*args)
        self.position = 0.0
        self.exposure = 0.02

    def describe(self):
        duration = {"type":"number", "unit":"s", "minimum":0, "maximum":60, "default":0.05}
        operations = {
            "move_to": {"description":"Move and report the settled simulated angle", "parameters":{
                "angle_deg":{"type":"number", "unit":"deg"}, "duration":duration}},
            "position": {"description":"Read the simulated angle", "parameters":{}},
            "configure": {"description":"Set simulated acquisition duration", "parameters":{
                "exposure_s":{**duration, "default":0.02}}},
            "measure": {"description":"Sample ideal half-wave-plate transmission", "parameters":{}},
            "wait": {"description":"Wait without changing the device", "parameters":{"duration":duration}},
        }
        kind = self.config.get("kind", "stage")
        selected = ["configure", "measure", "wait"] if kind == "meter" else ["move_to", "position", "wait"]
        return {"name":self.config.get("name", self.id), "mode":"simulation", "kind":kind,
                "model":"ideal-polarization/1", "operations":{k:operations[k] for k in selected}}

    def invoke(self, operation, arguments, cancelled):
        duration = arguments.get("duration", self.exposure if operation == "measure" else 0)
        if cancelled.wait(duration):
            raise CancelledError("Operation cancelled")
        if operation == "move_to":
            self.position = arguments["angle_deg"]
        elif operation == "configure":
            self.exposure = arguments["exposure_s"]
            return {"exposure_s":self.exposure, "time":now(), "source":"simulation"}
        elif operation == "wait":
            return {"elapsed_s":duration, "time":now(), "source":"simulation"}
        elif operation == "measure":
            stage_id = self.config.get("stage")
            stage = self.registry.get(stage_id)
            angle = stage.position if isinstance(stage, Simulated) else 0
            return {"power":math.cos(math.radians(2 * angle)) ** 2, "unit":"W",
                    "angle_actual":angle, "time":now(), "source":"simulation"}
        return {"angle_actual":self.position, "unit":"deg", "time":now(), "source":"simulation"}


class SCPI(Driver):
    """Persistent TCP, serial or VISA connection with optional named operations."""
    def __init__(self, *args):
        super().__init__(*args)
        self.connection = None
        self.manager = None
        self.timeout = float(self.config.get("timeout", 5))
        if self.timeout <= 0:
            raise ValueError("timeout must be positive")
        self.termination = self.config.get("termination", "\n")
        if not self.termination:
            raise ValueError("A text SCPI termination is required")

    def describe(self):
        operations = {
            "identify":{"description":"Read SCPI identification", "parameters":{}, "query":"*IDN?"},
            "query":{"description":"Send a text query and read its response", "parameters":{"command":{"type":"string"}}},
            "write":{"description":"Send a command", "parameters":{"command":{"type":"string"}}},
        }
        operations.update(self.config.get("operations", {}))
        return {"name":self.config.get("name", self.id), "mode":"hardware", "transport":self.config.get("transport", "tcp"),
                "operations":operations}

    def connect(self):
        if self.connection is not None:
            return
        kind = self.config.get("transport", "tcp")
        if kind == "tcp":
            self.connection = socket.create_connection((self.config["host"], int(self.config.get("port", 5025))), self.timeout)
            self.connection.settimeout(self.timeout)
        elif kind == "serial":
            import serial
            self.connection = serial.Serial(self.config["port"], int(self.config.get("baudrate", 9600)),
                                            timeout=self.timeout, write_timeout=self.timeout)
        elif kind == "visa":
            import pyvisa
            backend = self.config.get("backend")
            self.manager = pyvisa.ResourceManager(backend) if backend else pyvisa.ResourceManager()
            self.connection = self.manager.open_resource(self.config["resource"])
            self.connection.timeout = self.timeout * 1000
            self.connection.read_termination = self.termination
            self.connection.write_termination = self.termination
        else:
            raise ValueError("Unknown SCPI transport: " + kind)

    def exchange(self, command, read=False):
        if "\n" in command or "\r" in command:
            raise ValueError("Use one text command per operation")
        self.connect()
        try:
            kind = self.config.get("transport", "tcp")
            if kind == "visa":
                return self.connection.query(command).strip() if read else self.connection.write(command)
            wire = (command + self.termination).encode(self.config.get("encoding", "ascii"))
            if kind == "tcp":
                self.connection.sendall(wire)
            else:
                self.connection.write(wire)
            if not read:
                return None
            response = bytearray()
            terminator = self.termination.encode()
            deadline = time.monotonic() + self.timeout
            while not response.endswith(terminator):
                if time.monotonic() >= deadline:
                    raise TimeoutError("Instrument response timed out")
                chunk = self.connection.recv(1) if kind == "tcp" else self.connection.read(1)
                if not chunk:
                    raise TimeoutError("Instrument returned no complete response")
                response.extend(chunk)
                if len(response) > 8 * 1024 * 1024:
                    raise ValueError("Response exceeds text-query size")
            return response[:-len(terminator)].decode(self.config.get("encoding", "ascii"))
        except Exception:
            self.close()
            raise

    def invoke(self, operation, arguments, cancelled):
        if cancelled.is_set():
            raise CancelledError()
        spec = self.describe()["operations"][operation]
        is_query = operation == "query" or "query" in spec
        template = spec.get("query", spec.get("write"))
        command = template.format_map(arguments) if template else arguments["command"]
        value = self.exchange(command, is_query)
        completion = spec.get("completion")
        if completion:
            deadline = time.monotonic() + float(completion.get("timeout", 30))
            while True:
                observed = self.exchange(completion["query"].format_map(arguments), True)
                if observed == str(completion.get("equals", "1")):
                    break
                if time.monotonic() >= deadline:
                    raise TimeoutError("Completion response did not arrive")
                time.sleep(float(completion.get("interval", 0.1)))
        result = {"time":now(), "source":"device" if is_query else "driver", "command":command}
        if is_query:
            encoding = spec.get("result", {})
            result["value"] = float(value) if encoding.get("type") == "number" else value
            if "unit" in encoding:
                result["unit"] = encoding["unit"]
        else:
            result["sent"] = True
        if completion:
            result["completion_response"] = observed
        return result

    def close(self):
        for obj in (self.connection, self.manager):
            if obj is not None:
                try:
                    obj.close()
                except Exception:
                    pass
        self.connection = self.manager = None


def make_driver(record, registry):
    if record.get('driver') == 'process':
        from .process_driver import ProcessDriver
        return ProcessDriver(record['id'], record.get('config', {}), registry)
    name = record["driver"]
    from .adapters import Modbus, HTTP
    from .simulation import Laboratory
    builtins = {"simulated":Simulated, "simulated-lab":Laboratory, "scpi":SCPI, "modbus":Modbus, "http":HTTP}
    if name in builtins:
        cls = builtins[name]
    else:
        module, separator, class_name = name.partition(":")
        if not separator:
            raise ValueError("Driver must name a built-in adapter or module:Class")
        cls = getattr(importlib.import_module(module), class_name)
    return cls(record["id"], record.get("config", {}), registry)
