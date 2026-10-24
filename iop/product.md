# IOP Runtime · Application and platforms

[中文](product.zh-CN.md) · [Download](https://github.com/Cherish0925/AI4Instruments/releases/latest) · [Install](interface.md) · [Agent integration](agent-setup.md)

IOP Runtime is persistent software installed on the instrument computer. It maintains connections, executes experiments, coordinates resources and stores records and files. Desktop, browser, command-line and agent clients use the same service.

## Changes in 0.8.0

Automatic device IDs, batch descriptions and shared background discovery reduce setup work. Configurable interfaces and USB inventory are displayed separately. Instrument operations and responses share a panel. Program calls wait directly for the target operation; scheduling groups start records, while status queries read compact summaries.

[Instrument setup](instrument-setup.md) · [Measurements](performance/README.md)

## Application interfaces

| Interface | Implementation | Use |
| --- | --- | --- |
| Desktop | Native window and application-menu entries | Platform configuration, instruments, operations and results |
| Web | Browser interface served by IOP | Local or reachable laboratory service |
| CLI | `iop` commands | Startup, configuration, experiment submission and inspection |
| Python / TypeScript | Client libraries | Experiment programs, feedback loops and data processing |
| HTTP API | `/v1/*` | Other languages, applications and remote agents |
| MCP | `iop mcp`, standard input/output | Laboratory descriptions, platform setup and experiment tools |
| Headless | `iop serve` or operating-system startup | Servers and long-running experiments |

IDE-hosted agents use MCP, SDKs or the CLI. There is no separate IOP IDE extension. The web interface is self-hosted by the laboratory service; no hosted cloud product is provided.

## Operating systems and distributions

| System | Architectures | Distribution and requirements |
| --- | --- | --- |
| Windows | x86_64, ARM64 | ZIP and PowerShell installer. Desktop uses WebView2; the installer supplies the ARM64 .NET desktop dependency. |
| macOS | ARM64, x86_64 | ZIP and shell installer. Current build targets are macOS 14+ and 15+, respectively. Application entries are created during desktop installation. |
| Linux | x86_64, ARM64 | ZIP and shell installer. Service builds target glibc 2.35+. Desktop needs a graphical session and Qt libraries; ARM64 desktop requires glibc 2.39+. |
| WSL | Corresponding Linux architecture | Linux service and browser interface. Instruments must be exposed to WSL; Windows-only SDKs run in the Windows service. |

Python 3.10+ is required. Installers create a separate environment and download dependencies. Archives include a matching Rust executor. Distributions currently use ZIPs and scripts; they do not yet include Python, signed Windows installers, notarized macOS installers or automatic updates.

To update, finish current experiments, stop the old service with `iop stop`, and run the new installer. Configuration and experiment data in the default `~/.iop` directory are retained.

## Responsibilities

| Work | Owner | When |
| --- | --- | --- |
| Connections, execution, scheduling, records and files | Runtime | Continuously |
| Read saved instruments, topology, parameters and results | Agent or experiment program | On connection and when configuration changes |
| Match a new model to its driver and operations | Agent, with supplied documentation when needed | First connection of a new instrument |
| Specify wiring, samples, shared objects and experimental intent | Saved platform; agent asks the operator for missing information | Initial setup or a physical change |
| Plan experiments, define dependencies, analyze results and choose subsequent experiments | Agent or person | During research |

Reuse saved platforms. Saving a description does not execute physical actions. Initialization is a named, recorded experiment procedure; it need not run every time an agent connects.

## Current implementation and remaining product work

0.8.0 supplies the shared service, the interfaces above, general adapters, platform configuration, scheduling, records and files, MCP integration and a laboratory context API. The release workflow builds on native operating systems and exercises installation, browser and desktop interfaces, and agent communication.

Remaining product work includes standalone installers, signing and notarization, automatic updates, a broad model/driver catalogue and extended operation in independent laboratories. General adapters support their protocols; model-specific commands, SDKs and operation descriptions still require their corresponding implementations.

## Operation and access

Local clients read local connection settings automatically. Remote clients use the service's existing token. Experiment programs execute with the service account's permissions; remote networks use the laboratory's controlled network or encrypted connection.

Accepted experiments continue after clients close. On service restart, queued work is restored and previously started work is recorded as interrupted. Physical actions with unresolved outcomes are not automatically resubmitted. Devices and shared resources follow their saved scheduling configuration; independent equipment can operate concurrently.
