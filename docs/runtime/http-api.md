# IOP HTTP API · 0.8.1

[中文安装](README.zh-CN.md) · [Installation](README.md)

Base URL: `http://127.0.0.1:8765`. API bodies are JSON objects. Requests to `/v1/*` include `Authorization: Bearer <config.json token>`. Responses use UTF-8 JSON, except binary file transfers. Errors return `{"error":"message"}` with status 400, 401, 404, 503 or 500. The browser page and `/health` are readable without the token. Maximum JSON request size is 64 MiB.

## Endpoints

| Method | Path | Body / query | Response |
| --- | --- | --- | --- |
| GET | `/health` | — | Service name and version |
| GET | `/v1/ui` | — | Desktop availability and local connection status |
| POST | `/v1/ui/desktop` | `{"view":"devices"}` | Open a native window on the service computer; local requests only |
| GET | `/v1/context` | `refresh=true` for a new connection scan | Compact laboratory description: instruments, platforms, drivers, resources and remaining setup |
| GET | `/v1/schemas/{name}` | `device`, `platform`, `workflow`, `instrument-profile` | Packaged JSON schema |
| GET | `/v1/adapters` | — | Built-in and installed driver entries |
| GET | `/v1/resources` | — | Configured capacities and current allocation |
| POST | `/v1/resources` | `{"capacities":{"cpu":16,"solver":2}}` | Replace named capacities; accepted work must still fit |
| POST | `/v1/devices/{device_id}/reconnect` | `{}` | Reconnect idle devices sharing a worker |
| GET | `/v1/status` | — | Active/queued counts, worker limits, service errors, version, hostname, system and uptime |
| GET | `/v1/devices` | — | Instrument descriptions |
| GET | `/v1/devices/{device_id}` | — | One instrument description |
| GET | `/v1/devices/{device_id}/configuration` | — | Saved driver configuration, suitable for export and registration |
| POST | `/v1/devices/batch` | `{"devices":[...]}` | Per-input index with `device` or `error`; successful entries remain saved |
| GET / POST | `/v1/instrument-profiles` | Model description for POST | List or save exact manufacturer/model matching and operations |
| POST | `/v1/devices/{device_id}/identify` | Optional `request_id` | Accepted identity-query run; saves reported identity and model operations |
| POST | `/v1/discovery/retry` | Optional `key` connection key | Clear retry delay and start shared background discovery |
| POST | `/v1/discovery` | `{}` | Start or join a background scan; returns cached inventory and `scanning` immediately |
| POST | `/v1/devices` | Device record | Registered description; persists configuration; identical retries reuse the device |
| GET | `/v1/discovery` | `cached=true` to reuse the last scan | Current scan, provider availability and registered devices |
| POST | `/v1/runs` | Workflow below | Accepted run record |
| POST | `/v1/packages` | Package below | Accepted run record |
| GET | `/v1/runs` | `limit=100&details=false` for compact summaries | Most recent runs first |
| GET | `/v1/runs/{run_id}` | `details=false` for a compact state | Run; detailed response includes recent `operation_records` |
| GET | `/v1/runs/{run_id}/operations` | `after=0&limit=200` | `{"operations":[...],"cursor":N}`; ordered operation history |
| POST | `/v1/runs/{run_id}/operations` | Operation below | Operation in a running package |
| GET | `/v1/operations/{operation_id}` | — | State, times, result or error |
| POST | `/v1/runs/{run_id}/cancel` | `{}` | Current run, cancellation requested |
| GET | `/v1/runs/{run_id}/result` | — | Saved result without operation history |
| POST | `/v1/runs/{run_id}/result` | `{"result": ...}` | Saved result; run must be running |
| POST | `/v1/runs/{run_id}/artifacts` | `{"name":"scan.csv","data":"<base64>"}` | Saved output file record |
| GET | `/v1/runs/{run_id}/artifacts` | — | File records |
| POST | `/v1/runs/{run_id}/files?name=raw/data.bin` | Binary body and `Content-Length` | Stream a file without base64 encoding |
| GET | `/v1/artifacts/{artifact_id}` | — | File bytes, streamed |
| GET | `/v1/events` | `after=0&run_id=...&limit=200&wait=25` | `{"events":[...],"cursor":N}` |
| POST | `/v1/shutdown` | `{}` | `{"stopping":true}` |

`after` is an exclusive event sequence number. Poll using the returned `cursor`; an empty page means no new events. Omit `run_id` for events across the platform. The optional `wait` (0–25 seconds) waits for new events; a terminal run returns immediately. Python and TypeScript watch iterators resume from the returned cursor.

## Workflow

```json
{
  "name": "Polarization point",
  "project": "polarization-study",
  "experiment": "angle-response",
  "request_id": "polarization-point-001",
  "resources": ["stage", "meter", "optical-path"],
  "parameters": {},
  "steps": [
    {"id":"move","device":"stage","operation":"move_to","arguments":{"angle_deg":15}},
    {"id":"setup","device":"meter","operation":"configure","arguments":{"exposure_s":0.05}},
    {"id":"read","device":"meter","operation":"measure","after":["move","setup"]}
  ]
}
```

`steps` contains 1–10,000 uniquely named steps. `after` references earlier dependencies in the graph; the input list need not be topologically sorted. Cycles and missing references are rejected before submission. Step `resources` adds shared resource names to the device's own resources. Submission `resources` retains resources across the entire experiment; a workflow reservation automatically includes all devices in its steps.

The result maps step IDs to driver results. Step arguments follow the corresponding instrument description, including defaults, types, ranges and units.

## Package

```json
{
  "name": "Polarization scan",
  "project": "polarization-study",
  "resources": ["stage", "meter", "optical-path"],
  "parameters": {"angles_deg": [0,15,30,45]},
  "request_id": "polarization-scan-001",
  "archive": "<base64 ZIP>"
}
```

A ZIP has `package.json` and program files at its root. The default command is `["{python}","experiment.py"]`. Maximum expanded size is 128 MiB. The service sets:

| Variable | Meaning |
| --- | --- |
| `IOP_ENDPOINT` | This service's HTTP address |
| `IOP_TOKEN` | Platform connection token |
| `IOP_RUN_ID` | Current run identifier |
| `IOP_RUN_DIR` | Absolute output directory |
| `IOP_PARAMETERS_JSON` | Submitted parameters as JSON |

The working directory contains extracted program files. Save data in `IOP_RUN_DIR`; the service indexes output files when the process ends. `save_file` registers a file immediately. Program stdout, stderr and the original package remain associated with the run. The command runs in the host environment; install required libraries there.

Within a running package, submit an operation:

```json
{"device":"stage","operation":"move_to","arguments":{"angle_deg":15},"request_id":"point-001-move"}
```

The response contains `id`, `run_id` and `state`; poll `/v1/operations/{id}`. Programs express dependencies by waiting for results and parallelism by concurrent submissions. A package with a run reservation may only use resources included in that reservation.

## States and repeated requests

Runs: `queued → running → completed`, or `failed`, `cancelled`, `interrupted`. `cancelling` means the service is ending pending/process work and waiting for active driver calls to return. Operations: `queued → running → completed`, or `failed`, `cancelled`, `interrupted`.

A failed operation ends its run and cancels dependent work. Device calls already executing retain their resources until they return. Cancellation requests do not imply that a physical instrument has instantly stopped; the driver implements the instrument's stop/completion behavior.

The same `request_id` with the same submitted definition returns the original record. Reusing it for a different definition returns an error. Package equality includes the uploaded ZIP bytes. Retrying after a network interruption should reuse the original request ID and payload.

After a service restart, queued runs remain queued, while previously started runs become `interrupted`. Completed physical operations are not automatically repeated. `Run.wait(timeout=...)` only limits client waiting; use `cancel()` to request cancellation.

## File records

```json
{
  "id": "file_...",
  "run_id": "run_...",
  "name": "output/scan.csv",
  "size": 348,
  "media_type": "text/csv",
  "created": "2026-10-22T12:00:00.000000+00:00"
}
```

Names are relative to the run directory. Uploaded files go under `output/`; an existing filename is not overwritten. Large outputs can be written directly by a hosted program and downloaded through the streaming endpoint.

## Platforms and native drivers

| Method | Path | Body / result |
| --- | --- | --- |
| GET | `/v1/platforms` | Current platform definitions, revisions, missing devices and active runs. |
| POST | `/v1/platforms/preview` | `{ "definition": { ... } }`; parses a platform without saving or executing it. |
| POST | `/v1/platforms` | `{ "definition": { ... }, "expected_revision": 0 }`; use current revision for updates. |
| GET | `/v1/platforms/{id}` | One platform. |
| GET | `/v1/platforms/{id}/history` | Saved versions, newest first. |
| POST | `/v1/platforms/{id}/procedures/{name}` | `{ "request_id": "..." }`; submit a configured procedure and return a run. |
| POST | `/v1/resources/resolve` | `{ "resources": ["..."], "observation": "..." }`; record observed equipment state and release resources retained after a driver interruption. |

Workflow and package submissions accept `platform` and optional `platform_revision`. The selected definition is retained in the run. Device calls must belong to that platform. Platform resources also apply to calls without a platform ID. `GET /v1/status` includes platform count and `resource_holds`.

[Platform configuration](../../iop/platforms.md) · [中文](../../iop/platforms.zh-CN.md) · [Executable drivers](../../iop/drivers.md)

## Quantities and result bindings

`requirements` maps configured resource names to positive integer quantities. It may appear on a driver description, an operation description, a workflow step or a run. Driver, operation and step quantities combine by taking the maximum for each resource. Run-level requirements reserve capacity for the whole experiment; operations consume those reserved quantities without double counting. `resources` continues to name exclusive shared objects and whole devices.

A step's `bindings` maps parameter names to `{ "step": "source-step", "path": ["value", 0] }`. These sources are implicit dependencies. Paths select keys or array indices; an omitted path selects the whole result. Bound arguments are checked before invoking the destination operation.

`operation.progress` events contain `operation_id` and `progress` with `fraction`, `message` and optional driver fields. Progress is also available on the operation record. Completed package operations remain in SQLite; `operation_count` counts all submitted calls while a running package's `operations` list contains only its unfinished calls. Detailed run responses include up to 10,000 recent operation records; use the cursor endpoint for full history.

HTTP 503 indicates that the configured active-work capacity has been reached and includes `retry_after` in seconds. Submission retries should retain their request identifier. Queued work and accepted experiments continue while new work waits at the caller.

The command adapter's operation context and HTTP asynchronous job descriptions are documented in [software extensions](../../iop/software.md). The schemas for [platforms](../../iop/schema/platform.schema.json) and [workflows](../../iop/schema/workflow.schema.json) are shipped with the source and installation archives.

## Instrument setup and efficient reads

An instrument's `id` may be omitted on registration. The service generates and saves it; identical registrations reuse the same driver. `GET /v1/discovery?cached=true` reports the current background scan without starting another. `connections` retains raw interfaces, `groups` combines known aliases, and `summary` separates configurable interfaces from USB inventory. Windows `COMn` and `ASRLn::INSTR` are recognized as the same endpoint. A USB entry alone does not specify the device's command language.

`GET /v1/operations/{id}?wait=25` waits for that operation to finish, or returns its current state after at most 25 seconds. Python and TypeScript clients use this path for calls inside experiment programs; they do not read the experiment's entire event history for each operation.

Use `GET /v1/runs?details=false` and `GET /v1/runs/{id}?details=false` for summaries. Results, operation lists, experiment definitions and full platform definitions are excluded before the response enters the application. Read `/result` and cursor-paged `/operations` only when needed.

## Instrument discovery records

`instruments` contains persistent identity and setup records with `key`, `device_id`, `identity`, `identity_source`, `required`, `status`, `present`, `first_seen`, `last_seen` and `connection_info`. Presence is `true` for observed, `false` for absent from a working source and `null` when unconfirmed. `identification_summary` reports identified/configured counts and incomplete setup. `groups` retains interface aliases; `related_connections` links USB interfaces sharing VID/PID and serial number without merging logical channels.

The list of required fields uses `protocol`, `communication_parameters`, `control_interface`, `driver` and `model_operations`. `GET /v1/context` includes the corresponding `complete_instrument_setup` tasks. Background identity reads are serialized with device operations. Discovery never runs a profile's measurement or output commands.
