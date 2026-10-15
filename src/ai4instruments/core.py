"""Typed operation calls, parent-linked traces, and dependency scheduling."""

import asyncio
import json
import math
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Awaitable, Callable


LAYERS = ("Basic Operations", "Standard Operations", "Workflow Operations")


@dataclass(frozen=True)
class Parameter:
    unit: str
    minimum: float
    maximum: float

    def check(self, name: str, supplied: Any) -> float:
        if not isinstance(supplied, dict) or set(supplied) != {"value", "unit"}:
            raise ValueError(f"{name} requires exactly value and unit")
        value = supplied["value"]
        if supplied["unit"] != self.unit:
            raise ValueError(f"{name}: expected unit {self.unit}")
        if isinstance(value, bool) or not isinstance(value, (int, float)):
            raise ValueError(f"{name}: expected a finite number")
        if not math.isfinite(value) or not self.minimum <= value <= self.maximum:
            raise ValueError(f"{name}: expected [{self.minimum}, {self.maximum}]")
        return float(value)

    def describe(self) -> dict:
        return {"unit": self.unit, "minimum": self.minimum, "maximum": self.maximum}


@dataclass(frozen=True)
class Operation:
    id: str
    layer: str
    description: str
    parameters: dict[str, Parameter]
    handler: Callable[[dict[str, float], str], Awaitable[dict]] = field(repr=False)
    timing: str = ""
    result_fields: dict[str, str] = field(default_factory=dict)

    def describe(self) -> dict:
        return {"id": self.id, "layer": self.layer, "description": self.description,
                "parameters": {k: v.describe() for k, v in self.parameters.items()},
                "timing": self.timing, "result_fields": self.result_fields}


class Trace:
    """A total event order; sequence numbers are not physical timestamps."""

    def __init__(self, metadata: dict):
        self.events: list[dict] = []
        self.append("run", schema="ai4instruments.trace/1", **metadata)

    def append(self, event: str, **fields: Any) -> None:
        # Snapshot values so later device changes cannot rewrite prior evidence.
        record = {"sequence": len(self.events), "event": event, **fields}
        self.events.append(json.loads(json.dumps(record, allow_nan=False)))

    def write(self, path: str | Path) -> None:
        path = Path(path)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text("".join(json.dumps(e, sort_keys=True) + "\n"
                                for e in self.events), encoding="utf-8")


class Runtime:
    def __init__(self, trace: Trace):
        self.trace = trace
        self.operations: dict[str, Operation] = {}
        self._next_call = 0

    def register(self, operation: Operation) -> None:
        if operation.id in self.operations or operation.layer not in LAYERS:
            raise ValueError(f"invalid or duplicate operation: {operation.id}")
        self.operations[operation.id] = operation

    async def invoke(self, operation_id: str, arguments: dict | None = None,
                     parent_id: str | None = None, node_id: str | None = None) -> dict:
        operation = self.operations[operation_id]
        arguments = {} if arguments is None else arguments
        if set(arguments) != set(operation.parameters):
            raise ValueError(f"{operation_id}: parameters must be {list(operation.parameters)}")
        values = {k: spec.check(k, arguments[k]) for k, spec in operation.parameters.items()}
        self._next_call += 1
        call_id = f"call-{self._next_call:05d}"
        self.trace.append("started", call_id=call_id, parent_id=parent_id,
                          node_id=node_id, operation_id=operation_id,
                          layer=operation.layer, arguments=arguments)
        try:
            result = await operation.handler(values, call_id)
        except BaseException as error:
            self.trace.append("failed", call_id=call_id, operation_id=operation_id,
                              error_type=type(error).__name__, message=str(error))
            raise
        self.trace.append("completed", call_id=call_id, operation_id=operation_id,
                          result=result)
        return result

    def catalog(self) -> list[dict]:
        return [self.operations[k].describe() for k in sorted(self.operations)]


@dataclass(frozen=True)
class Node:
    id: str
    operation_id: str
    arguments: dict = field(default_factory=dict)
    after: tuple[str, ...] = ()


async def run_dag(runtime: Runtime, nodes: list[Node], parent_id: str | None = None) -> dict:
    """Run independent nodes concurrently, and dependents after completion."""
    indexed = {node.id: node for node in nodes}
    if len(indexed) != len(nodes):
        raise ValueError("duplicate node ID")
    remaining = set(indexed)
    visited: set[str] = set()
    while remaining:
        ready = {key for key in remaining if set(indexed[key].after) <= visited}
        if not ready:
            raise ValueError("workflow contains a cycle or an unknown dependency")
        visited |= ready
        remaining -= ready
    for node in nodes:
        if node.operation_id not in runtime.operations:
            raise ValueError(f"unknown operation: {node.operation_id}")
    tasks: dict[str, asyncio.Task] = {}

    async def execute(node: Node) -> dict:
        for dependency in node.after:
            await tasks[dependency]
        return await runtime.invoke(node.operation_id, node.arguments, parent_id, node.id)

    for node in nodes:
        tasks[node.id] = asyncio.create_task(execute(node))
    try:
        results = await asyncio.gather(*(tasks[node.id] for node in nodes))
    except BaseException:
        for task in tasks.values():
            task.cancel()
        await asyncio.gather(*tasks.values(), return_exceptions=True)
        raise
    return dict(zip((node.id for node in nodes), results))
