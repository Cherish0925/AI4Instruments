# IOP · Instrument Operation Protocol

[中文](README.zh-CN.md) · [Download](https://github.com/Cherish0925/AI4Instruments/releases/tag/iop-v0.4.0) · [Installation](../docs/runtime/README.md) · [Platform configuration](platforms.md) · [Agent integration](agent-setup.md)

**One persistent service for people and agents to use experimental platforms.** It runs on the computer connected to instruments, maintains devices and platform descriptions, executes experiment programs, schedules serial and parallel work, and preserves operations and data. Accepted experiments continue after the submitting terminal, browser or agent session closes.

One computer can serve several experimental platforms. Each platform describes its devices, physical connections, shared resources and initialization procedures. Platforms may reference the same instrument; one service coordinates its use across them.

## Start

Download the matching IOP 0.4.0 archive and run `install.sh` on Linux, macOS or WSL, or `install.ps1` on Windows. Python 3.10+ is required. Archives include the platform-specific Rust executor; users do not need a Rust compiler. The installer prints the installed commands.

| Archive | Runtime environment |
| --- | --- |
| Linux x86_64 / arm64 | Ubuntu 22.04 or compatible, glibc 2.35+ |
| Windows x86_64 / arm64 | Matching 64-bit Windows |
| macOS arm64 | Apple Silicon, macOS 14+ |
| macOS x86_64 | Intel, macOS 15+ |
| Other OS / CPU combinations | [Install from source](../docs/runtime/README.md) and build the Rust component for that system. |

WSL uses Linux packages and devices exposed to WSL. Windows-specific SDKs can remain with a Windows service.

```sh
iop init
iop start
iop open
```

The browser's platform page displays connections, imports and exports configuration, saves configuration versions and starts initialization. CLI and clients share the same API.

## Configure the platform, then run experiments

| Stage | Work |
| --- | --- |
| Discover | Inventory visible USB, serial, VISA and registered network connections; match configured drivers. |
| Configure | A person or agent uses actual wiring and instrument documentation to define membership, ports, shared physical objects and initialization. |
| Initialize | Execute declared steps and retain their results. Saving a description does not operate instruments. |
| Experiment | Local or remote programs submit operations or packages, expressing dependencies and resource requirements. |
| Preserve | Link each run to its platform revision, parameters, operations, readings, analysis and files. |

Physical topology and experimental timing are separate. A trigger cable alone does not establish synchronized acquisition: the program must configure and prepare the devices before triggering. Software orders operations; device clocks and hardware triggers provide precise timing.

## Implemented in 0.4.0

| Component | Implementation |
| --- | --- |
| Persistent service | Python HTTP API, scheduler, experiment processes and CLI. |
| Native executor | Rust `iop-execd` supervises independent driver processes, messaging, cancellation requests, response deadlines and exit. |
| Drivers | SCPI TCP / serial / VISA, Modbus TCP / RTU, HTTP JSON, Python adapters and executable adapters. |
| Clients | Python, TypeScript, HTTP, CLI and browser interface. |
| Records | SQLite, configuration history, events, packages, output files and raw-data relationships. |

C, C++, C#, Java and other executable SDK adapters can implement the same [driver interface](drivers.md). Their language environments are required only for the relevant adapters. Development continues toward the [Rust core architecture](../docs/runtime/architecture.md); workflow scheduling in this release remains Python.

## Project entry points

| Component | Location |
| --- | --- |
| Platform descriptions | [Configuration guide](platforms.md), [JSON Schema](schema/platform.schema.json) |
| Native driver supervision | [daemon/](daemon/) |
| Python service, clients and drivers | [src/ai4instruments/iop](../src/ai4instruments/iop/) |
| TypeScript client | [clients/typescript](clients/typescript/) |
| Platform and executable-driver examples | [examples/](examples/) |
| Experiment packages | [examples/iop/](../examples/iop/) |
| HTTP interface | [API](../docs/runtime/http-api.md) |

Discovery, driver connection and operation support are documented separately. An attached instrument needs a usable driver and description before its operations can be invoked. Instrument-model coverage and actual hardware results grow with laboratory use.
