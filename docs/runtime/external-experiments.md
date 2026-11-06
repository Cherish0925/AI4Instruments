# External experiment programs

[中文](external-experiments.zh-CN.md) · [HTTP API](http-api.md) · [Runnable example](../../examples/iop/external-experiment/experiment.py)

An external Python or TypeScript program can keep its scientific libraries and execute successive instrument operations under one run ID. It uses the same scheduler, reservations, operation records and files as a Runtime-hosted package. These APIs are source changes after 0.8.4; the published 0.8.4 installers do not include them.

```python
import json
from ai4instruments.iop import Client

client = Client()
# Choose a new ID for a new experiment; retain it for submission retries.
run = client.start_experiment(name='Scan', request_id='sample-42-scan-1',
                              resources=['stage', 'meter'])
print(run.id)
run.invoke('stage', 'move_to', {'angle_deg':15}, request_id=run.id + '-move-1')
measurement = run.invoke_record('meter', 'measure', request_id=run.id + '-read-1')
run.save_file('point.json', json.dumps(measurement['result']),
              operation_ids=[measurement['id']])
run.checkpoint({'next_point':2})
run.save_result({'points':1})
run.finish()
```

`invoke()` returns the driver result. `invoke_record()` returns the same result with its operation ID, run ID, timestamps and instrument configuration revision. Use that returned data for analysis and saving; calling the instrument again creates another measurement. `save_file(..., operation_ids=[...])` and `upload(..., operation_ids=[...])` attach completed operations from the same run. Links remain available after completion and restart.

Reserve every mutually dependent device and shared resource when starting the experiment. The reservation lasts through gaps between calls and ends at `finish()` or completed cancellation. Other independent instruments remain available. Without a reservation, each operation still uses the scheduler, but another experiment can act between two calls. A run awaiting reserved instruments can accept operations; those operations wait for the reservation.

Complete file transfers and accepted operations before `finish()`. Finishing while an operation is pending returns `operations_pending`. Repeated successful finishes return the existing completed run. Use `cancel()` to stop an abandoned experiment; closing a client connection does not end its experiment or release its reservation. An operation failure ends the run through the existing failure path.

## Continue from another connection

```python
run = Client().run(saved_run_id)
print(run.info(details=False))
print(run.operations())
print(run.checkpoints())
```

If only the client disconnected, use the active run directly. Reuse the same operation `request_id` and input after a lost response: the service returns the existing operation, including after the run finishes. It does not repeat the physical action. A changed input with that ID is rejected.

A service restart interrupts a started experiment. Inspect its operations and saved progress, then explicitly call `run.resume(request_id='continuation-1')`. The run ID and old operations remain; the external program decides where to continue. The Runtime does not restart the external Python process or replay its calls. An unresolved instrument outcome or changed device configuration prevents continuation until addressed. An interrupted operation remains interrupted when queried with its original ID.

## Other clients

TypeScript has `client.startExperiment(options)`, `run.invokeRecord(...)`, `run.finish()` and the existing checkpoint/resume methods. Link a binary upload using `run.upload(name, blob, undefined, [operation.id])`.

MCP exposes `start_experiment`, `invoke_operation`, `save_experiment_file` and `finish_experiment`. `invoke_operation` returns immediately; use `experiment` to read its completion before dependent actions. Existing workflow and package tools remain available.

```sh
iop begin --name Scan --request-id sample-42-scan-1 --resources stage
iop call stage position --run-id RUN_ID --request-id RUN_ID-read-1
iop finish RUN_ID
```

The default `Client.invoke()` and `iop call` without a run ID still perform a standalone one-step workflow. Use the experiment handle for repeated calls.
