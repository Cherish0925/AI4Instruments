"""Deterministic, explicitly simulated two-axis optical alignment."""

import asyncio
import math
import random
from dataclasses import dataclass

from .core import Node, Operation, Parameter, Runtime, Trace, run_dag


MODEL_ID = "gaussian-coupling-with-first-order-motion/1"
POSITION = Parameter("mm", -2.0, 2.0)
EXPOSURE = Parameter("ms", 1.0, 100.0)


def quantity(value: float, unit: str) -> dict:
    return {"value": value, "unit": unit}


@dataclass
class Axis:
    target: float = 0.0
    position: float = 0.0
    sample: int = 0


class OpticalBench:
    def __init__(self, seed: int = 17):
        self.axes = {"x": Axis(), "y": Axis()}
        self.exposure = 10.0
        self.measurement = 0
        self.detector_time_ms = 0.0
        self.rng = random.Random(seed)
        self.trace = Trace({"run_id": f"optical-alignment-{seed}", "mode": "simulation",
                            "model_id": MODEL_ID, "seed": seed,
                            "event_clock": "logical sequence",
                            "initial_state": {"x_mm": 0, "y_mm": 0, "exposure_ms": 10}})
        self.runtime = Runtime(self.trace)
        self._register()

    def _register(self) -> None:
        for name, axis in self.axes.items():
            async def write(values, call_id, axis=axis):
                axis.target = values["target"]
                await asyncio.sleep(0)
                return {"commanded": {"target": quantity(axis.target, "mm")}}

            async def read(values, call_id, axis=axis):
                axis.position += 0.75 * (axis.target - axis.position)
                axis.sample += 1
                await asyncio.sleep(0)
                return {"observed": {"position": quantity(axis.position, "mm")},
                        "sample_index": axis.sample, "device_time_ms": axis.sample}

            async def position(values, call_id, name=name):
                await self.runtime.invoke(f"{name}.write_target",
                                          {"target": quantity(values["target"], "mm")}, call_id)
                for _ in range(16):
                    result = await self.runtime.invoke(f"{name}.read_position", parent_id=call_id)
                    actual = result["observed"]["position"]["value"]
                    if abs(actual - values["target"]) <= 0.001:
                        return result
                raise RuntimeError(f"{name}: position did not converge within 16 samples")

            self.runtime.register(Operation(f"{name}.write_target", "Basic Operations",
                f"Set the {name}-axis target; acknowledgment does not establish position.",
                {"target": POSITION}, write, "Acknowledgment; no modeled elapsed time.",
                {"commanded.target": "mm"}))
            self.runtime.register(Operation(f"{name}.read_position", "Basic Operations",
                f"Sample the {name}-axis position after one modeled servo step.", {}, read,
                "1 ms of local model time per sample; not wall-clock timing.",
                {"observed.position": "mm", "sample_index": "integer", "device_time_ms": "ms"}))
            self.runtime.register(Operation(f"{name}.position", "Standard Operations",
                f"Set {name} and observe convergence to within 0.001 mm.", {"target": POSITION},
                position, "Up to 16 position samples.", {"observed.position": "mm"}))

        async def write_exposure(values, call_id):
            self.exposure = values["exposure"]
            return {"commanded": {"exposure": quantity(self.exposure, "ms")}}

        async def read_exposure(values, call_id):
            return {"observed": {"exposure": quantity(self.exposure, "ms")}}

        async def acquire(values, call_id):
            self.measurement += 1
            self.detector_time_ms += self.exposure
            x, y = (self.axes[key].position for key in ("x", "y"))
            ideal = 100 * math.exp(-((x - 0.65) ** 2 + (y + 0.4) ** 2) / (2 * 0.45 ** 2))
            power = ideal + self.rng.uniform(-0.02, 0.02) / math.sqrt(self.exposure)
            await asyncio.sleep(0)
            return {"observed": {"power": quantity(power, "uW"),
                                  "exposure": quantity(self.exposure, "ms")},
                    "measurement_id": f"measurement-{self.measurement:04d}",
                    "device_time_ms": self.detector_time_ms, "model_id": MODEL_ID}

        async def capture(values, call_id):
            await self.runtime.invoke("detector.write_exposure",
                                      {"exposure": quantity(values["exposure"], "ms")}, call_id)
            readback = await self.runtime.invoke("detector.read_exposure", parent_id=call_id)
            if readback["observed"]["exposure"]["value"] != values["exposure"]:
                raise RuntimeError("exposure readback differs from the requested value")
            return await self.runtime.invoke("detector.acquire", parent_id=call_id)

        self.runtime.register(Operation("detector.write_exposure", "Basic Operations",
            "Set detector exposure.", {"exposure": EXPOSURE}, write_exposure,
            "Acknowledgment; no modeled elapsed time.", {"commanded.exposure": "ms"}))
        self.runtime.register(Operation("detector.read_exposure", "Basic Operations",
            "Read back the active detector exposure.", {}, read_exposure,
            "Immediate simulated readback.", {"observed.exposure": "ms"}))
        self.runtime.register(Operation("detector.acquire", "Basic Operations",
            "Measure optical power at the current positions and exposure.", {}, acquire,
            "Consumes the configured exposure in detector model time.",
            {"observed.power": "uW", "observed.exposure": "ms",
             "measurement_id": "string", "device_time_ms": "ms", "model_id": "string"}))
        self.runtime.register(Operation("detector.capture", "Standard Operations",
            "Configure exposure, verify its readback, and acquire one measurement.",
            {"exposure": EXPOSURE}, capture, "One exposure plus configuration and readback.",
            {"observed.power": "uW", "measurement_id": "string"}))

        async def measure_at(values, call_id):
            result = await run_dag(self.runtime, [
                Node("position_x", "x.position", {"target": quantity(values["x"], "mm")}),
                Node("position_y", "y.position", {"target": quantity(values["y"], "mm")}),
                Node("capture", "detector.capture", {"exposure": quantity(values["exposure"], "ms")},
                     after=("position_x", "position_y")),
            ], call_id)
            return {"positions": {key: result[f"position_{key}"]["observed"]["position"]
                                  for key in ("x", "y")}, "measurement": result["capture"]}

        self.runtime.register(Operation("optics.measure_at", "Workflow Operations",
            "Position independent axes concurrently; capture after both converge.",
            {"x": POSITION, "y": POSITION, "exposure": EXPOSURE}, measure_at,
            "Dependency ordering; no real-time scheduling guarantee.",
            {"positions.x": "mm", "positions.y": "mm", "measurement": "detector result"}))

    def capabilities(self) -> dict:
        return {"schema": "ai4instruments.capabilities/1", "model_id": MODEL_ID,
                "mode": "simulation", "abstraction_level": "two-axis position and detector acquisition",
                "coverage": {"claim": "Complete for the controls and observations implemented by this model.",
                             "controls": ["x target", "y target", "detector exposure"],
                             "observations": ["x position", "y position", "detector exposure", "optical power"],
                             "excluded": ["electronics", "firmware", "optical polarization", "real hardware"]},
                "state": {"axes": "Commanded target and observed position are separate.",
                          "detector": "Exposure readback precedes acquisition."},
                "concurrency": "Independent x and y operations may overlap. Calls on the same device are serialized by the workflow.",
                "operations": self.runtime.catalog()}


async def align(seed: int = 17) -> tuple[OpticalBench, dict]:
    bench = OpticalBench(seed)
    objective = {"id": "maximize-observed-power/1", "measurement": "observed.power",
                 "direction": "maximize", "unit": "uW"}
    bench.trace.append("objective", definition=objective)
    evaluations = 0

    async def evaluate(x, y):
        nonlocal evaluations
        evaluations += 1
        result = await bench.runtime.invoke("optics.measure_at",
            {"x": quantity(x, "mm"), "y": quantity(y, "mm"), "exposure": quantity(10, "ms")})
        observed = result["measurement"]
        score = observed["observed"]["power"]["value"]
        bench.trace.append("evaluation", objective_id=objective["id"],
            measurement_id=observed["measurement_id"], candidate={"x_mm": x, "y_mm": y}, score=score)
        return score

    x, y = 0.0, 0.0
    initial = best = await evaluate(x, y)
    for step in (0.5, 0.25, 0.125, 0.0625, 0.03125):
        for axis in ("x", "y"):
            origin = (x, y)
            candidates = []
            for direction in (-1, 1):
                cx = origin[0] + (direction * step if axis == "x" else 0)
                cy = origin[1] + (direction * step if axis == "y" else 0)
                if -2 <= cx <= 2 and -2 <= cy <= 2:
                    candidates.append((await evaluate(cx, cy), cx, cy))
            for score, cx, cy in candidates:
                if score > best:
                    best, x, y = score, cx, cy
            bench.trace.append("decision", objective_id=objective["id"],
                selected={"x_mm": x, "y_mm": y}, step_mm=step, best_observed_power_uW=best)
    final = await evaluate(x, y)  # Return the instrument to the selected position and measure again.
    summary = {"mode": "simulation", "seed": seed, "evaluations": evaluations,
               "initial_power_uW": round(initial, 6), "final_power_uW": round(final, 6),
               "selected_position_mm": {"x": x, "y": y}, "objective": objective}
    bench.trace.append("summary", result=summary)
    return bench, summary
