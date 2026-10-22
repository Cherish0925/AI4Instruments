# IOP HTTP API · 0.3.0

[中文安装](README.zh-CN.md) · [Installation](README.md)

Base URL: `http://127.0.0.1:8765`. API bodies are JSON objects. Requests to `/v1/*` include `Authorization: Bearer <config.json token>`. Responses use UTF-8 JSON, except file downloads. Errors return `{"error":"message"}` with status 400, 401, 404 or 500. The browser page and `/health` are readable without the token. Maximum JSON request size is 64 MiB.

## Endpoints

| Method | Path | Body / query | Response |
| --- | --- | --- | --- |
| GET | `/health` | — | Service name and version |
| GET | `/v1/status` | — | Active/queued counts, worker limits, service errors |
| GET | `/v1/devices` | — | Instrument descriptions |
| GET | `/v1/devices/{device_id}` | — | One instrument description |
| POST | `/v1/devices` | Device record | Registered description; persists configuration |
| GET | `/v1/discovery` | — | Current scan, provider availability and registered devices |
| POST | `/v1/runs` | Workflow below | Accepted run record |
| POST | `/v1/packages` | Package below | Accepted run record |
| GET | `/v1/runs` | `limit=100` | Most recent runs first |
| GET | `/v1/runs/{run_id}` | — | Run with `operation_records` |
| POST | `/v1/runs/{run_id}/operations` | Operation below | Operation in a running package |
| GET | `/v1/operations/{operation_id}` | — | State, times, result or error |
| POST | `/v1/runs/{run_id}/cancel` | `{}` | Current run, cancellation requested |
| POST | `/v1/runs/{run_id}/result` | `{"result": ...}` | Saved result; run must be running |
| POST | `/v1/runs/{run_id}/artifacts` | `{"name":"scan.csv","data":"<base64>"}` | Saved output file record |
| GET | `/v1/runs/{run_id}/artifacts` | — | File records |
| GET | `/v1/artifacts/{artifact_id}` | — | File bytes, streamed |
| GET | `/v1/events` | `after=0&run_id=...&limit=200` | `{"events":[...],"cursor":N}` |
| POST | `/v1/shutdown` | `{}` | `{"stopping":true}` |

`after` is an exclusive event sequence number. Poll using the returned `cursor`; an empty page means no new events. Omit `run_id` for events across the platform. The Python `Run.watch()` iterator handles this polling.

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
