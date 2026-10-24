# IOP · Agent integration

[中文](agent-setup.zh-CN.md) · [Application and platforms](product.md) · [HTTP API](../docs/runtime/http-api.md) · [Platform schema](schema/platform.schema.json)

Codex, Claude Code, DeepSeek Harness, Qiushi Engine and other research software can connect through MCP, CLI, HTTP or the Python/TypeScript clients. All interfaces use the same service, instruments, platform configuration and experiment records.

## First connection

The release installers include the Agent component. Print the MCP connection configuration using the installed `iop` command:

```sh
iop mcp-config
```

Use its `command` and `args` in your agent host's MCP server settings. The output uses the common `mcpServers` JSON structure; hosts using another configuration format use the same command and argument list. Paths refer to the current installation. No connection token is printed.

The host starts `iop mcp`. It connects to the local service, starting it if necessary. Closing the MCP process leaves that service and accepted experiments running. Call `lab_context` first: it returns saved platforms, instrument operation names, available drivers, visible connections, resource usage and remaining setup work.

Terminal-based agents can instead call:

```sh
iop context --start
```

Add `--refresh` for a new connection scan; otherwise IOP reuses its current inventory. The desktop/browser settings page exports the same laboratory description as JSON.

For source installations, install `.[agent]` in the IOP environment. Set `IOP_AGENT=0` in the release installer to omit MCP dependencies. Python 3.10 uses the maintained MCP SDK 1.x; Python 3.11+ uses SDK 2.x. Both paths are covered by the runtime workflow. SDK references: [v1](https://py.sdk.modelcontextprotocol.io/v1/) and [v2](https://py.sdk.modelcontextprotocol.io/).

## Configure once, then reuse

1. Read `lab_context`. Reuse existing instruments and platforms.
2. For a new instrument, read its documentation and choose an installed adapter. Read `configuration_schema("device")`, then call `register_instrument`. Repeating the identical record reuses the connection.
3. Save devices, physical connections, shared objects and named procedures with `configure_platform`. Use the current revision when editing. Ask only for physical details that cannot be obtained from existing descriptions or connected equipment.
4. Run the saved initialization procedure when the experiment needs it. Saving configuration alone performs no device action.
5. Submit an experiment or program; retain its run ID. Inspect progress and results later. Reuse `request_id` when retrying the same submission.

An individual instrument can operate without a platform. A platform records relationships among devices used together. Serial/parallel ordering comes from experiment dependencies; shared resources describe objects requiring coordinated use.

## MCP tools

| Tool | Purpose |
| --- | --- |
| `lab_context` | Current laboratory description; optional connection refresh |
| `describe_instrument` | Operations, arguments and units for one device |
| `configuration_schema` | Device, platform or workflow JSON schema |
| `register_instrument` | Register a connection using an installed driver |
| `register_instruments` | Register multiple descriptions, returning each result; IDs may be omitted |
| `discover_instruments` | Start background discovery or read the cached inventory |
| `configure_platform` | Save or preview platform configuration |
| `configure_resources` | Set named resource capacities |
| `run_procedure` | Execute initialization or another saved procedure |
| `submit_experiment` | Submit a graph of instrument operations and dependencies |
| `submit_program` | Upload a directory or ZIP from the MCP host for service execution |
| `experiment` | Status, paged operations, output files and optional result |
| `cancel_experiment` | Request cancellation |
| `reconnect_instrument` | Reconnect a device or a previously unavailable SDK |
| `resolve_resources` | Record observed instrument state and return interrupted resources to use |
| `download_file` | Save an experiment output on the MCP host |

`iop://laboratory` exposes the same context as an MCP resource. Submissions return immediately. `experiment` returns at most 100 operations per page; pass the returned cursor as `after`. Retrieve large data through output files.

## Remote service

```sh
iop --endpoint http://lab-computer:8765 mcp-config
```

Set `IOP_TOKEN` in the agent host's environment or secret configuration. The MCP process runs beside the agent and forwards work to the reachable instrument service. It does not start another local service when a remote endpoint is selected. See [server configuration](../docs/runtime/README.md).

## SDK access

```python
from ai4instruments.iop import Client
lab = Client()  # Reads environment variables or local connection settings.
print(lab.context()['platforms'])
print(lab.schema('workflow'))
```

```typescript
import { IOP } from '@ai4instruments/iop';
const lab = new IOP(process.env.IOP_ENDPOINT, process.env.IOP_TOKEN);
const context = await lab.context();
const schema = await lab.schema('workflow');
```

HTTP exposes `GET /v1/context` and `GET /v1/schemas/{name}`. Retrieve detailed operations at `GET /v1/devices/{id}` only for instruments needed by the current task.

## Multiple instruments and repeated calls

Start discovery with `discover_instruments()`, then inspect progress with `discover_instruments(refresh=false)`. Serial, VISA and USB inventory remain distinct; model commands come from instrument descriptions, installed drivers and manufacturer documentation. `register_instruments(definitions)` registers multiple devices and returns each generated ID or error. IDs do not require operator input.

Python and TypeScript `run.invoke()` wait for the target operation and return as soon as its result is available. Submit independent calls concurrently; the service schedules device, bus and platform resources. When all steps are known, submit one workflow using `after` and `bindings`. Put feedback-dependent loops inside experiment programs.

[Instrument setup](instrument-setup.md) · [Measurements](performance/README.md)


## 0.8.1 · Identity and automatic setup

Read `lab_context` first. `discover_instruments(refresh=false).instruments` retains identity, source, presence and required setup fields. Use automatically registered instruments directly. `complete_instrument_setup` entries in `next_steps` identify the remaining protocol, communication settings, driver or model operations.

- `identify_instrument(device)`: schedule an identity read and save its result; returns a run ID.
- `instrument_profiles()`: read bundled and local model descriptions.
- `save_instrument_profile(definition)`: save model operations and add new operations to identified devices.
- `retry_instrument_discovery(connection_key)`: retry a connection immediately; omit the key to retry all.

Python: `identify()`, `instrument_profiles()`, `save_instrument_profile()`, `retry_discovery()`. TypeScript: `identify()`, `instrumentProfiles()`, `saveInstrumentProfile()`, `retryDiscovery()`. Read `configuration_schema("instrument-profile")` for the description format.

## 0.8.2 · Continuing work

The default context links to full descriptions; use `lab_context(after=cursor)` for subsequent changes. `instrument_configuration` reads or edits versioned settings. `continue_program` reads progress or continues a program declaring resume support. [Program progress and binary data](continuity.md).
