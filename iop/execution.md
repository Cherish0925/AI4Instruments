# Experiment execution

[IOP Runtime](README.md) · [中文](execution.zh-CN.md) · [HTTP API](../docs/runtime/http-api.md)

An experiment can use physical instruments, computational programs and remote services together. IOP schedules operations according to dependencies, device concurrency and available resources. Experiment packages express loops, feedback and research methods.

## Dependencies and data

Independent steps may run concurrently. `after` expresses ordering. `bindings` supplies an argument from a completed step and also creates a dependency on that step.

```json
{"steps":[
  {"id":"first","device":"processor","operation":"calculate","arguments":{"x":3}},
  {"id":"second","device":"processor","operation":"calculate",
   "bindings":{"x":{"step":"first","path":["value"]}}}
]}
```

`processor` here is a registered object exposing `calculate(x)`. A binding path contains object keys or array indices; an omitted path selects the complete result. IOP checks the resulting arguments against the destination operation's parameter description before calling it. Use an experiment package for adaptive loops and arbitrary computation.

Devices execute one operation at a time by default. A driver can declare `concurrency` when its operations support independent parallel execution. Shared buses, samples and controllers continue to use common `resources` names.

## Counted resources

```python
from ai4instruments.iop import Client
lab = Client()
lab.configure_resources({"cpu": 16, "gpu": 2, "solver": 3})
```

An operation requests quantities with `requirements`, for example `{"cpu":4,"solver":1}`. All requested quantities are acquired together; waiting operations hold none. This configuration admits at most three such solver operations concurrently. Resource names are laboratory-defined; `gpu-0` and `gpu-1` can represent individual devices.

Requirements may appear in a driver description, an operation description or a workflow step. The largest quantity for each resource applies. Quantities govern admission; programs configure their own thread counts, memory use and GPU selection.

Experiment-level `resources` and `requirements` reserve capacity across steps. Workflows also include their devices in the reservation. Packages must declare their complete device and quantity requirements when reserving resources. Child operations consume the reservation without counting it twice. Two concurrent steps requesting two CPU units each require four reserved units.

## Continuous operation

Accepted work has a persistent `run_id`. Workflows and uploaded experiment packages continue after the submitting client disconnects. Long-running packages may issue successive operations; completed operations live in SQLite and only their unfinished calls remain in memory.

```python
run = lab.run(run_id)
page = run.operations(after=0, limit=200)
next_page = run.operations(after=page["cursor"], limit=200)
for event in run.watch():
    print(event["kind"])
```

Event requests may wait for a new event instead of repeatedly downloading a full run. After service restart, queued experiments remain queued and interrupted experiments retain their completed records. Physical operations are not automatically replayed.

`workers` limits concurrent operations; `package_workers` limits experiment processes. `max_active_runs` and `max_active_operations` in `config.json` default to 10000 and 100000. At capacity, new submissions return HTTP 503 while accepted work continues. Device concurrency and resource quantities apply independently.

## Files and progress

Return small structured results directly. Store images, waveforms and arrays as files associated with the experiment. Uploads and downloads stream in chunks:

```python
record = run.upload("measurement.h5", "raw/measurement.h5")
run.download(record["id"], "downloaded.h5")
```

A driver's third argument remains compatible with `threading.Event` and also exposes `run_id`, `operation_id`, `output_dir`, `file(name)` and `progress(fraction, message)`. Each operation has its own output directory.

## Programs and remote services

Use `command` for ordinary executables, `process` for persistent SDK sessions and `http` for synchronous endpoints or asynchronous job services. See [software and driver extensions](software.md).

The Rust component owns experiment programs, command programs and independent SDK workers. Program output goes directly to files. Cancellation, timeout or loss of the parent connection ends the process tree. Instrument drivers report the outcome of physical actions.

Each service schedules its own registered resources. Another IOP service can be connected through the HTTP job adapter; an upper-level experiment controls the cross-service sequence. Precise acquisition across hosts still uses instrument clocks and trigger facilities.
