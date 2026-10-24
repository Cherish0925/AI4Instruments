# IOP · Continuing experiments

[中文](continuity.zh-CN.md) · [Installation](../docs/runtime/README.md) · [HTTP API](../docs/runtime/http-api.md) · [Example program](../examples/iop/resumable-acquisition)

Version 0.8.2 connects discovery, editable instrument descriptions, saved program progress and continuous data. Configuration and records belong to the laboratory service. Accepted experiments continue when an Agent or interface disconnects.

## Connections and configuration

Discovery publishes each provider as it finishes, then publishes instrument identities individually. Slow VISA or SDK enumeration no longer hides completed results. Scan duration counts toward the configured interval. `present` records discovery, `communication` records the latest operation response, and `state` records driver and resource availability.

Choose **Edit configuration** in an instrument's details. Saved versions remain available; selecting an older definition and saving restores it. Accepted work involving that instrument must finish before configuration changes take effect. Other instruments continue operating.

```python
from ai4instruments.iop import Client
lab = Client()
current = lab.device_history('meter')[0]
definition = current['definition']
definition['config']['name'] = 'Measurement station'
lab.configure_device('meter', definition, current['revision'])
```

For several instruments sharing one SDK process, update their group configuration and restart the service. Automatic model matching continues to add missing operations. Replace an existing operation through the instrument configuration endpoint.

## Agent context

`lab.context()` returns a compact overview. Retrieve full instrument descriptions from `/v1/devices/{id}` and platforms from `/v1/platforms/{id}`. Device lists longer than 100 items include a continuation URL.

Use `lab.changes(context['cursor'])` for subsequent reads. Changes contain summaries and detail URLs, without arrays of measurement results. `lab.context(detail='full')` returns the full inventory. MCP uses `lab_context(after=cursor)` or `device_offset` for another device page. Errors retain a short message and provide a stable `code`, relevant parameter definitions, current revision or expected chunk sequence.

## Saved program progress

Declare `"resume": true` in `package.json`. The program reads and writes its own progress:

```python
run = lab.current_run()
progress = run.checkpoints().get('main', {}).get('state', {'next': 0})
for index in range(progress['next'], 100):
    result = run.invoke('meter', 'read_batch', request_id=f'{run.id}-{index}')
    # Save this batch, then save the position of the next one.
    run.checkpoint({'next': index + 1})
```

Continue with `iop resume RUN_ID --request-id continue-1`, `run.resume()`, or **Continue from saved progress** in the interface. The run ID, files and operation history remain the same; terminal output is retained per attempt. Save progress after the program's instrument operations have returned.

Continuation restores explicitly saved program progress. Stable operation IDs reuse completed results. An action that never returned an outcome is not reissued automatically. Read device state through an operation explicitly described with `effect: "observe"`, then record that observation through `/v1/resources/resolve`. The generic `query` operation is not automatically classified as observation. Work that had not started remains queued across restart.

## Continuous data

Experiment programs, acquisition adapters and computation software can send batches:

```python
stream = run.stream('voltage', {
    'format': 'float32-le',
    'channels': [{'name': 'voltage', 'unit': 'V'}],
    'sample_rate_hz': 100000
})
stream.append(batch_bytes, sequence=0)
print(stream.info()['next_sequence'])
```

Chunks use binary HTTP bodies, ordered sequence numbers and idempotent retries. Descriptions retain the format, channels, units and acquisition conditions. Download chunks through the artifact interface. Transfers use bounded file reads outside the instrument scheduler lock. Wait for each append before sending the next chunk to bound producer memory.

Hardware clocks, triggers, device buffers and acquisition stopping belong to the instrument driver. Use hardware-buffered acquisition for high sampling rates; Runtime chunks transport and retain its output.

## SDK processes

An installed Python driver can use the existing Rust supervisor without implementing a separate transport:

```json
{
  "id": "camera",
  "driver": "vendor_camera:Camera",
  "config": {"serial_number": "CAM-001"},
  "execution": {"mode": "process", "startup_timeout": 30, "timeout": 300, "cancel_timeout": 2}
}
```

Startup, operations and cancellation have separate deadlines. An unresponsive SDK process ends without stopping other instruments; reconnect creates its driver again. In-process drivers retain their existing behavior. Use the existing `process` adapter configuration for several devices sharing one SDK or bus. Install vendor libraries in the relevant worker environment.

## Installation

Windows, macOS and Linux x86_64 / ARM64 archives include Python, the Rust executor and Runtime/Agent dependencies. `install.ps1` or `sh install.sh` installs the core, browser interface and Agent integration offline. Desktop installers additionally download native UI dependencies. Vendor SDKs and operating-system device drivers are installed for the relevant hardware.

Upgrades retain the laboratory directory. The installer stops an idle previous service; finish or cancel accepted experiments before upgrading. Source installations continue to support Python 3.10+. WSL uses the Linux distribution and devices exposed to WSL.
