# Continuous experiment programs · 0.8.5

[中文](external-experiments.zh-CN.md) · [HTTP API](http-api.md) · [Runnable example](../../examples/iop/external-experiment/experiment.py)

An external program keeps its scientific computing environment while the laboratory service owns the instruments, operation history and experiment data. Start one experiment, submit successive operations or batches, analyze their results, and finish. Python, TypeScript, MCP and CLI share the same run ID and scheduler.

```python
from ai4instruments.iop import Client

with Client() as lab:
    with lab.start_experiment(name='Sample scan', resources=['stage', 'meter'],
                              request_id='sample-42-scan-1') as run:
        print(run.id)  # Retain this ID to reconnect to the experiment.
        records = run.batch([
            {'id':'set', 'device':'stage', 'operation':'move_to',
             'arguments':{'angle_deg':15}},
            {'id':'read', 'device':'meter', 'operation':'measure'}
        ], request_id='sample-42-point-1')
        measurement = records[-1]['result']
        run.save_acquisition('point-1.json', [op['id'] for op in records],
                             conditions={'sample':'42'},
                             analysis={'accepted':measurement['power'] > 0})
        run.checkpoint({'next_point':2})
        run.save_result({'points':1})
```

The inner context finishes normally or requests cancellation on an exception. Closing a client alone leaves its experiment running. Choose a new request ID for new work; reuse it for an identical retry. These operation names belong to demonstration devices; read registered instrument descriptions for actual operations and units.

## Sequence, parallel branches and shared instruments

Within a batch, omitting `after` means follow the previous step. `after=[]` starts an independent branch; `after=['a','b']` waits for both. Result bindings also create dependencies. All steps are checked and recorded before any starts: the entire batch is accepted or none is. This does not undo physical actions if a later step fails; completed results remain and pending steps are cancelled.

Reserve **all mutually dependent devices and shared physical resources** in `start_experiment(resources=[...])`. Reservations span gaps between batches and last until finish or completed cancellation. Without a reservation, another experiment can run between calls or batch steps. Independent platforms remain available. Device clocks and hardware triggers provide precise synchronization; software dependencies specify completion order.

`batch()` waits and returns operation records. For nonblocking submission use `POST /v1/runs/{id}/batches`, then GET that endpoint with `request_id` and optional `wait=0..25`. A batch supports up to 10,000 steps, subject to the configured active-operation capacity. Long-running programs can send successive batches without retaining completed operations in scheduler memory. Existing `submit()` workflows keep their original rule: omitted dependencies mean independent steps.

## Acquire once, analyze and save the same result

`invoke()` returns the driver result; `invoke_record()` also returns the operation ID, times and device configuration revision. `save_acquisition()` saves selected completed operations and their configuration versions directly from the service. **No instrument commands are sent.** Retrying the same filename and content returns the existing artifact; different content needs a different name.

Include actual setting-readback operations. `conditions` contains caller-supplied sample and setup information, not automatically measured physical conditions. `analysis` contains decisions or derived results based on the selected acquisition. Large images, arrays and continuous streams can retain their binary format: use `upload(..., operation_ids=[...])` or the stream API and reference their artifact IDs in the acquisition. Links remain after the experiment ends.

## Reconnect and continue

Use `Client().run(saved_run_id)` after a client disconnect. Read `info(details=False)`, `operations()` and `checkpoints()`. Identical operation or batch request IDs return the previously accepted records, including after completion. Changed inputs with an existing ID are rejected. The client does not automatically replay a POST after a connection failure.

A service restart interrupts a started experiment. Read operations and progress, then explicitly call `run.resume(request_id='continuation-1')`. The run ID and old operations remain. The external program decides where to continue; the Runtime does not restart that external process or repeat an operation whose physical outcome is unknown. Driver configuration changes must be reconciled before continuation.

Complete file transfers and accepted operations before `finish()`. Use `cancel()` for abandoned work. Stopping a client wait does not stop the experiment.

## Entry points

| Entry | Continuous experiment | Batch | Save acquired results |
| --- | --- | --- | --- |
| Python | `start_experiment` → `finish` | `run.batch` | `run.save_acquisition` |
| TypeScript | `startExperiment` → `finish` | `run.batch` | `run.saveAcquisition` |
| MCP | `start_experiment` → `finish_experiment` | `submit_operations` | `save_acquisition` |
| CLI | `iop begin` → `iop finish` | `iop batch RUN steps.json --request-id ID --wait` | `iop acquisition RUN point.json OP_ID...` |

MCP submissions return immediately; `experiment` retrieves status and results. Agent decisions can occur between batches while program code handles dense numerical work. `Client.invoke()` and `iop call` without a run ID remain standalone single-step workflows; use the experiment handle for repeated work.

## Hand a connection to another application

Call `lab.release(device)` or `iop release DEVICE` after accepted operations and reservations end. The service closes the connection and retains the description. Background discovery and service restarts leave it released. Devices sharing an SDK worker are released and reconnected together. `reconnect(device)` restores access; applying a changed configuration to one released instrument also reconnects it. The desktop and browser instrument panel provides the same controls.

Use `lab.adapters()` or MCP `available_adapters` for connection parameters. SCPI TCP accepts `config.source_address` to select the local instrument-facing IP address. Serial settings include baud rate, character size, parity, stop bits and flow control. An unrecognized identity reply is retained as `identity_unparsed` with `communication: responded`; explicit rediscovery retries it after the format or configuration is understood.
