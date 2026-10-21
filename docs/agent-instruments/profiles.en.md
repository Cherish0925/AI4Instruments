# Project profiles and comparisons

## OpenMHP

[kushalsinha/openmhp](https://github.com/kushalsinha/openmhp) · Instrument contracts · Apache-2.0 · Simulation-verified

A device contract covering descriptors, reads, writes, actions, jobs, leases and run records, with bridges to existing drivers. Useful for studying a compact device interface and on-demand discovery.

Maintainer: kushalsinha

Access path: Agent → MCP / CLI / SDK → OpenMHP jobs & leases → device adapter

### Contribution and value

Extends a tool call into a device job with identity, resource ownership, events and results.

### Distinctions and conditions

Compared with a device-specific MCP bridge, the emphasis is a shared lifecycle and on-demand capabilities; current device-package evidence is primarily twin testing.

### Reusable ideas

Reuse job, lease and result structures; establish physical readback and run records for each model.

### Public scope and experiment record

Published specification and implementation. Seven supported-device packages are marked twin tested, plus one manual-operation template; maintainers explicitly distinguish these from hardware-tested drivers.

[Overview](https://github.com/kushalsinha/openmhp/blob/main/README.md) · [License](https://github.com/kushalsinha/openmhp/blob/main/LICENSE) · [Implementation](https://github.com/kushalsinha/openmhp/blob/main/SPEC.md) · [Implementation](https://github.com/kushalsinha/openmhp/blob/main/supported-devices/README.md) · [Implementation](https://github.com/kushalsinha/openmhp/blob/main/supported-devices/biologic-sp300/driver.py)

## Open-MHS · Abenor Labs

[Abenor-Labs/Open-MHS](https://github.com/Abenor-Labs/Open-MHS) · Instrument contracts · Apache-2.0 · Adapter / documentation

Capability tags and a device base class describe sensors, actuators and state, with a serial robotic-arm adapter. An independent community implementation.

Maintainer: Abenor-Labs

Access path: Agent → MCP / REST → capability tags → serial robotic-arm driver

### Contribution and value

Uses capability tags and base classes to make sensing, actions and state discoverable.

### Distinctions and conditions

Focuses on device representation and a serial adapter example, with a different scope from a complete laboratory runtime.

### Reusable ideas

Study the mapping from capability tags to driver methods and define each return meaning.

### Public scope and experiment record

Source includes mock devices and a serial driver; the reviewed material does not document a named hardware validation run.

[Overview](https://github.com/Abenor-Labs/Open-MHS/blob/main/README.md) · [License](https://github.com/Abenor-Labs/Open-MHS/blob/main/LICENSE) · [Implementation](https://github.com/Abenor-Labs/Open-MHS/blob/main/open_mhs/drivers/serial_robotic_arm.py) · [Implementation](https://github.com/Abenor-Labs/Open-MHS/blob/main/schema/capability_schema.json)

## Open MHS · tongriyaotxt

[tongriyaotxt/open-mhs](https://github.com/tongriyaotxt/open-mhs) · Instrument contracts · MIT · Adapter / documentation

Device registration, common commands and MCP tools, extended with robot motion and skill execution. Maintained separately from other similarly named projects.

Maintainer: tongriyaotxt

Access path: Agent → MCP dispatch → command / skill execution → robot backend

### Contribution and value

Adds robot actions and skills above registration and command interfaces.

### Distinctions and conditions

Shares the Open-MHS name but is independently implemented; robot and MuJoCo paths have distinct evidence.

### Reusable ideas

Reuse command dispatch and action composition, with explicit backend capabilities.

### Public scope and experiment record

MCP dispatch code reviewed. Physical-device and MuJoCo examples must be assessed by their individual backends.

[Overview](https://github.com/tongriyaotxt/open-mhs/blob/main/README.md) · [License](https://github.com/tongriyaotxt/open-mhs/blob/main/LICENSE) · [Implementation](https://github.com/tongriyaotxt/open-mhs/blob/main/src/openmhs/mcp/server.py)

## Open MHS · SCUT-ESA

[SCUT-ESA/open-mhs](https://github.com/SCUT-ESA/open-mhs) · Instrument contracts · MIT · Maintainer hardware record

A common device interface with explicit backend policies for VISA instruments, embedded I/O and simulators. A community project inspired by MHS.

Maintainer: SCUT-ESA

Access path: Agent → MCP / REST / CLI → explicit backend → VISA device

### Contribution and value

Connects a common interface to explicit backends and reports tests on two named models.

### Distinctions and conditions

Hardware records cover specified UNI-T scope and generator models; other I/O entries have different statuses.

### Reusable ideas

Reuse backend selection and model-level verification records.

### Public scope and experiment record

Maintainers report real-hardware verification for UNI-T UPO6102N and UTG2062X; other camera and GPIO adapters have separate experimental or simulation status.

[Overview](https://github.com/SCUT-ESA/open-mhs/blob/main/README.md) · [License](https://github.com/SCUT-ESA/open-mhs/blob/main/LICENSE) · [Implementation](https://github.com/SCUT-ESA/open-mhs/blob/main/src/openmhs/core/backend.py)

## Model Hardware Protocol · Cuntinum

[Cuntinum/model-hardware-protocol](https://github.com/Cuntinum/model-hardware-protocol) · Instrument contracts · Apache-2.0 · Adapter / documentation

Organizes drivers and shared state around discover, read, write and execute. Distributed as khp; distinct from OpenMHP.

Maintainer: Cuntinum

Access path: Agent → MCP / Python / TypeScript → khp driver & state bus → device

### Contribution and value

Organizes device access around discovery, read, write, execute and shared state.

### Distinctions and conditions

Differs from OpenMHP’s job/lease organization; compare state propagation and driver behavior.

### Reusable ideas

Evaluate how the operation set represents modes, asynchronous work and external state changes.

### Public scope and experiment record

Public specification, SDKs and driver directory. The README’s production-grade description is not treated as evidence of cross-device validation.

[Overview](https://github.com/Cuntinum/model-hardware-protocol/blob/main/README.md) · [License](https://github.com/Cuntinum/model-hardware-protocol/blob/main/LICENSE)

## Open Agent Hardware Layer

[fredabila/oahl](https://github.com/fredabila/oahl) · Instrument contracts · MIT · Maintainer hardware record

A discover–reserve–execute–release lifecycle separating nodes, adapters and transports, with local operation or optional registry and relay services.

Maintainer: fredabila

Access path: Agent SDK → OAHL node & reservation → transport plugin → physical device

### Contribution and value

Separates nodes, adapters, transport and reservation lifecycle, with local and optional remote discovery.

### Distinctions and conditions

The public demonstration uses phone ADB control; metrology and scientific data need a domain layer.

### Reusable ideas

Reuse pluggable transport and reservations, then add measurement and procedure semantics.

### Public scope and experiment record

README demonstrates Android phone operation through ADB; this does not establish a shared scientific calibration, long-job or measurement model.

[Overview](https://github.com/fredabila/oahl/blob/main/README.md) · [License](https://github.com/fredabila/oahl/blob/main/LICENSE)

## instrMCP

[caidish/instrMCP](https://github.com/caidish/instrMCP) · Persistent execution · MIT · Adapter / documentation

Exposes a QCoDeS Station inside an existing Jupyter kernel, reusing parameters, snapshots, databases and measurement workflows. A direct route for QCoDeS laboratories.

Maintainer: caidish

Access path: Agent → MCP → live Jupyter kernel → QCoDeS Station → instrument driver

### Contribution and value

Reuses an already initialized kernel, instrument connections and measurement state.

### Distinctions and conditions

Unlike a separate device server, ownership remains in the existing QCoDeS session, with explicit fresh and cached read paths.

### Reusable ideas

Useful for incremental integration; define kernel-restart, job-identity and shared-resource behavior.

### Public scope and experiment record

Parameter discovery, caching and fresh-read code reviewed. The running kernel and QCoDeS drivers own the actual device connections.

[Overview](https://github.com/caidish/instrMCP/blob/main/README.md) · [License](https://github.com/caidish/instrMCP/blob/main/LICENSE) · [Implementation](https://github.com/caidish/instrMCP/blob/main/instrmcp/servers/jupyter_qcodes/backend/qcodes.py)

## PUDA

[PUDAP/puda](https://github.com/PUDAP/puda) · Persistent execution · MIT · Adapter / documentation

A headless physical-device runtime separating messaging, layered drivers, protocol execution and result records. Agents author, validate and run experiments through a CLI and skills.

Maintainer: PUDAP

Access path: Agent CLI / Skills → protocol runner → NATS → edge driver → machine

### Contribution and value

Separates communication, drivers, procedures and records in a headless execution platform.

### Distinctions and conditions

Compared with single-device services, it emphasizes distributed dispatch and environments, with a CLI as the main agent surface.

### Reusable ideas

Reuse the boundary between edge drivers and experiment runners and the procedure-to-result mapping.

### Public scope and experiment record

CLI execution path reviewed: it obtains the machine command catalogue before dispatch through NATS; the repository includes an edge-driver example.

[Overview](https://github.com/PUDAP/puda/blob/main/README.md) · [License](https://github.com/PUDAP/puda/blob/main/LICENSE) · [Implementation](https://github.com/PUDAP/puda/blob/main/apps/cli/internal/cli/protocol-run.go) · [Paper](https://arxiv.org/abs/2607.26464)

## Uni-Lab-OS

[deepmodeling/Uni-Lab-OS](https://github.com/deepmodeling/Uni-Lab-OS) · Procedure composition · GPL-3.0 framework + proprietary drivers · Published experiment

Cross-device laboratory orchestration combining actions, resources and laboratory topology. Useful for comparing framework, adapter and workflow-compiler responsibilities.

Maintainer: deepmodeling

Access path: Agent / workflow → action-resource model → ROS 2 → device modules

### Contribution and value

Models actions, resources and laboratory topology together for multi-device workflows.

### Distinctions and conditions

Requires laboratory topology and device roles; framework and device-directory licenses differ.

### Reusable ideas

Reuse resource graphs and workflow compilation while defining independently reusable adapter boundaries.

### Public scope and experiment record

The paper and driver tree describe physical laboratory operation. The framework is GPL-3.0; unilabos/devices/ is separately covered by a DP Technology proprietary license.

[Overview](https://github.com/deepmodeling/Uni-Lab-OS/blob/main/README.md) · [License](https://github.com/deepmodeling/Uni-Lab-OS/blob/main/LICENSE) · [Implementation](https://github.com/deepmodeling/Uni-Lab-OS/blob/main/NOTICE) · [Implementation](https://github.com/deepmodeling/Uni-Lab-OS/blob/main/unilabos/devices/LICENSE) · [Implementation](https://github.com/deepmodeling/Uni-Lab-OS/blob/main/docs/developer_guide/add_device.md) · [Paper](https://arxiv.org/abs/2512.21766)

## Osprey

[als-apg/osprey](https://github.com/als-apg/osprey) · Persistent execution · BSD-3-Clause · Published experiment

An agent interface for large scientific facilities: semantic channel addressing, facility knowledge, control connectors and operational workflows. Includes EPICS, DOOCS and TANGO connectors.

Maintainer: Berkeley Lab · ALS Accelerator Physics Group

Access path: Agent / MCP / CLI → semantic channel lookup → facility connector → EPICS / TANGO / DOOCS

### Contribution and value

Lets agents find and operate facility channels through semantic context and facility knowledge.

### Distinctions and conditions

Adds facility context and workflow organization beyond raw PV/attribute bridges; the current write path includes human approval.

### Reusable ideas

Study how semantic addresses resolve to real channels and how facility knowledge relates to run records.

### Public scope and experiment record

Project publications and facility applications supply experimental context; the current implementation requires human approval for every hardware write.

[Overview](https://github.com/als-apg/osprey/blob/main/README.md) · [License](https://github.com/als-apg/osprey/blob/main/LICENSE.txt) · [Implementation](https://github.com/als-apg/osprey/blob/main/docs/source/architecture/mcp-servers.rst) · [Paper](https://doi.org/10.1063/5.0306302)

## IvoryOS

[ivoryos-ai/IvoryOS](https://github.com/ivoryos-ai/IvoryOS) · Procedure composition · MIT · Published experiment

Turns existing Python automation objects into controls and workflows, with optional natural-language workflow design. Useful for progressively exposing existing device code.

Maintainer: ivoryos-ai

Access path: Python automation objects → introspection → UI / workflow → existing device methods

### Contribution and value

Extracts operations from existing Python objects, lowering the cost of turning scripts into composable experiments.

### Distinctions and conditions

Integrates through introspection rather than requiring a rewritten driver interface; natural-language design is optional.

### Reusable ideas

Reuse incremental adoption and attach physical meaning and result fields to extracted methods.

### Public scope and experiment record

A laboratory-orchestration paper is available. The current README does not document a native MCP server; a Python API is recorded separately.

[Overview](https://github.com/ivoryos-ai/IvoryOS/blob/main/README.md) · [License](https://github.com/ivoryos-ai/IvoryOS/blob/main/LICENSE) · [Implementation](https://github.com/ivoryos-ai/IvoryOS/blob/main/ivoryos/parsers/introspection.py) · [Paper](https://www.nature.com/articles/s41467-025-60514-w)

## Jumpstarter

[jumpstarter-dev/jumpstarter](https://github.com/jumpstarter-dev/jumpstarter) · Persistent execution · Apache-2.0 · Adapter / documentation

Shares and leases physical or virtual devices under test, with power, UART, CAN, SPI, GPIO and USB drivers. Agents can use the same interfaces as test scripts.

Maintainer: jumpstarter-dev

Access path: Agent / test / CI → CLI / Python → lease & exporter → hardware interfaces

### Contribution and value

Makes shared hardware a leasable programmable test resource for humans, CI and agents.

### Distinctions and conditions

Focuses on hardware resources and test infrastructure; experiment reasoning and metrology sit above it.

### Reusable ideas

Reuse hardware leasing, remote exporters and reproducible test environments.

### Public scope and experiment record

Public drivers, Python client, gRPC definitions and controller. Agent-accessible hardware infrastructure rather than a specialized scientific language model.

[Overview](https://github.com/jumpstarter-dev/jumpstarter/blob/main/README.md) · [License](https://github.com/jumpstarter-dev/jumpstarter/blob/main/LICENSE)

## Lager

[lagerdata/lager](https://github.com/lagerdata/lager) · Persistent execution · Apache-2.0 · Adapter / documentation

A bench Linux host connects supplies, scopes, debug probes and buses. A common CLI serves agents, humans and CI; programs can execute next to the devices.

Maintainer: lagerdata

Access path: Agent / CI CLI → bench Linux box → named Net → instrument channel

### Contribution and value

Abstracts instrument channels as named test points and executes scripts on the bench host.

### Distinctions and conditions

Programs address rails, buses and probes rather than vendor commands, preserving names when instruments change.

### Reusable ideas

Reuse physical connection naming and local execution with versioned net-to-channel mappings.

### Public scope and experiment record

README and documentation describe concrete instruments and bench deployment. The reusable contribution is the bench execution layer.

[Overview](https://github.com/lagerdata/lager/blob/main/README.md) · [License](https://github.com/lagerdata/lager/blob/main/LICENSE)

## Experiment Automation Agents

[AdvancedPhotonSource/EAA](https://github.com/AdvancedPhotonSource/EAA) · Persistent execution · Unspecified · Published experiment

An experiment-agent runtime emphasizing visual feedback, image tool results, deterministic workflows and experiment task management.

Maintainer: Argonne · Advanced Photon Source

Access path: Experiment agent → image-aware tools → instrument services → experiment

### Contribution and value

Combines image results, workflows and experiment sessions in one agent environment.

### Distinctions and conditions

Contributes an environment for visual experiments; the repository points to EAA-Pi as its successor.

### Reusable ideas

Study persistence of experiment context and visual tool results.

### Public scope and experiment record

A microscopy experiment publication is available; the README announces migration to EAA-Pi. No top-level license was identified.

[Overview](https://github.com/AdvancedPhotonSource/EAA/blob/main/README.md) · [Paper](https://pmc.ncbi.nlm.nih.gov/articles/PMC13633048/)

## EAA-Pi

[AdvancedPhotonSource/EAA-Pi](https://github.com/AdvancedPhotonSource/EAA-Pi) · Persistent execution · Unspecified · Adapter / documentation

An experiment-assistant interface built on pi-experiment-ops; terminal and web views share workspaces, tools and experiment sessions.

Maintainer: Argonne · Advanced Photon Source

Access path: Terminal / web UI → pi-experiment-ops → MCP instrument server → device

### Contribution and value

Shares an experiment workspace between terminal and web interfaces.

### Distinctions and conditions

It is an application entry point; drivers are supplied by downstream MCP services and legacy EAA evidence does not transfer automatically.

### Reusable ideas

Reuse separation of interface and runtime to keep agent frontends replaceable.

### Public scope and experiment record

Published as EAA’s successor. Instrument capability depends on connected MCP servers; validation from the earlier paper is not automatically transferred.

[Overview](https://github.com/AdvancedPhotonSource/EAA-Pi/blob/main/README.md)

## pi-experiment-ops

[AdvancedPhotonSource/pi-experiment-ops](https://github.com/AdvancedPhotonSource/pi-experiment-ops) · Persistent execution · Unspecified · Adapter / documentation

Combines experiment tools, background execution, persistent terminals and transcript search into a reusable agent runtime for experiment applications.

Maintainer: Argonne · Advanced Photon Source

Access path: Pi agent → extension / CodeMode → persistent tools → MCP services

### Contribution and value

Provides background work, persistent terminals, session retrieval and tool execution for experiment agents.

### Distinctions and conditions

Provides reusable runtime components beneath EAA-Pi; hardware is supplied by external services.

### Reusable ideas

Reuse the distinction between conversation lifetime and instrument-job lifetime.

### Public scope and experiment record

Its MCP adapter connects separate instrument services; the runtime itself does not provide universal device drivers.

[Overview](https://github.com/AdvancedPhotonSource/pi-experiment-ops/blob/main/README.md)

## LabMCP · K-Dense

[K-Dense-AI/lab-instrument-mcps](https://github.com/K-Dense-AI/lab-instrument-mcps) · Device bridges · Apache-2.0 · Simulation-verified

A monorepo of instrument adapters spanning electronic measurement, spectroscopy, temperature control, pumps, microscopy, liquid handling and facility protocols. Components are listed separately.

Maintainer: K-Dense

Access path: Agent → MCP server package → device protocol adapter → simulated backend

### Contribution and value

Packages multiple instrument connectors for consistent installation and discovery.

### Distinctions and conditions

Breadth comes from 32 components, all currently marked simulated rather than 32 hardware validations.

### Reusable ideas

Reuse component inventories, tool naming and model-specific contribution workflows.

### Public scope and experiment record

The machine-readable catalogue lists 32 servers and 411 tools, all marked simulated. Mass-spectrometry data and worklist tools are not direct device control.

[Overview](https://github.com/K-Dense-AI/lab-instrument-mcps/blob/main/README.md) · [License](https://github.com/K-Dense-AI/lab-instrument-mcps/blob/main/LICENSE) · [Implementation](https://github.com/K-Dense-AI/lab-instrument-mcps/blob/main/packages/labmcp/src/labmcp/catalog.json)

## LabLink

[techmanual-ai/lablink-mcp](https://github.com/techmanual-ai/lablink-mcp) · Device bridges · MIT · Adapter / documentation

Brings several transports into one MCP server so agents can use existing commands and scripts. Device semantics remain primarily in configuration and drivers.

Maintainer: techmanual-ai

Access path: Agent → MCP → configured transport → VISA / SSH / REST / Serial / Python

### Contribution and value

Brings several existing laboratory transports into one service.

### Distinctions and conditions

Broad transport coverage leaves quantities, modes and outcomes to command configuration and drivers.

### Reusable ideas

Use as a heterogeneous access layer with a shared measurement and action model above it.

### Public scope and experiment record

Five connection-driver families and configuration examples are documented; generic connectivity does not imply support for every device.

[Overview](https://github.com/techmanual-ai/lablink-mcp/blob/main/README.md) · [License](https://github.com/techmanual-ai/lablink-mcp/blob/main/LICENSE)

## scpi-mcp

[armchairdeity/mcp-server-scpi](https://github.com/armchairdeity/mcp-server-scpi) · Device bridges · MIT · Adapter / documentation

Wraps oscilloscope capture and measurement goals as tools, leaving SCPI details to instrument backends. The first target is the Rigol DS1054Z.

Maintainer: armchairdeity

Access path: Agent → goal-level scope tools → Rigol backend → PyVISA / SCPI

### Contribution and value

Packages acquisition goals as scope tools instead of asking an agent to assemble low-level commands.

### Distinctions and conditions

Uses a bounded operation surface targeting Rigol DS1054Z rather than arbitrary SCPI passthrough.

### Reusable ideas

Compare goal-level operations with raw commands and build reusable measurement procedures.

### Public scope and experiment record

Rigol and mock backends are documented; the README explicitly excludes arbitrary raw SCPI, waveform-generator and logic-analyzer functions.

[Overview](https://github.com/armchairdeity/mcp-server-scpi/blob/main/README.md) · [License](https://github.com/armchairdeity/mcp-server-scpi/blob/main/LICENSE)

## oscilloscope-mcp

[masahiro-999/oscilloscope-mcp](https://github.com/masahiro-999/oscilloscope-mcp) · Device bridges · MIT · Adapter / documentation

Network oscilloscope configuration, triggering, waveform acquisition and measurement feedback, returning structured data, images and standalone waveform views.

Maintainer: masahiro-999

Access path: Agent → MCP acquisition tools → SCPI over TCP → oscilloscope

### Contribution and value

Combines scope configuration, triggering and waveforms into agent-readable feedback.

### Distinctions and conditions

Provides images and standalone waveform pages as well as numerical results for signal-debugging tasks.

### Reusable ideas

Reuse paired waveform summaries and full-data artifacts.

### Public scope and experiment record

The README describes bench operation and FPGA debugging workflows; compatibility remains model-specific.

[Overview](https://github.com/masahiro-999/oscilloscope-mcp/blob/main/README.md) · [License](https://github.com/masahiro-999/oscilloscope-mcp/blob/main/LICENSE)

## lecroy-mcp

[lucasgerads/lecroy-mcp](https://github.com/lucasgerads/lecroy-mcp) · Device bridges · AGPL-3.0 · Maintainer hardware record

LeCroy oscilloscope control and waveform acquisition over LAN VXI-11 or USB.

Maintainer: lucasgerads

Access path: Agent → MCP → VXI-11 / USB SCPI → LeCroy oscilloscope

### Contribution and value

Provides a concrete connection and waveform-acquisition path for LeCroy scopes.

### Distinctions and conditions

Transport choice is decisive: this implementation uses VXI-11 / USB, not VICP.

### Reusable ideas

Record brand, model, transport and mode when matching an adapter.

### Public scope and experiment record

A running demonstration is included. The documented LAN path requires VXI-11 and explicitly excludes LeCroy VICP.

[Overview](https://github.com/lucasgerads/lecroy-mcp/blob/main/README.md) · [License](https://github.com/lucasgerads/lecroy-mcp/blob/main/LICENSE)

## siglent-scpi-mcp

[mp911de/siglent-scpi-mcp](https://github.com/mp911de/siglent-scpi-mcp) · Device bridges · Apache-2.0 · Maintainer hardware record

Typed tools for Siglent oscilloscopes and supplies, recording the SCPI commands applied.

Maintainer: mp911de

Access path: Agent → typed MCP tools → logged SCPI / TCP → scope & supply

### Contribution and value

Covers scopes and supplies while recording the actual instrument commands.

### Distinctions and conditions

Named hardware tests and waveform scaling records help identify data-interpretation errors.

### Reusable ideas

Reuse waveform-to-unit conversion records and bench reproduction material.

### Public scope and experiment record

Maintainers report one SDS1204X HD and SPD3303X-E bench session, including waveform scaling; other listed models are not all hardware-tested.

[Overview](https://github.com/mp911de/siglent-scpi-mcp/blob/main/README.md) · [License](https://github.com/mp911de/siglent-scpi-mcp/blob/main/LICENSE)

## scope-mcp

[Netlist-Studio/scope-mcp](https://github.com/Netlist-Studio/scope-mcp) · Device bridges · MIT · Maintainer hardware record

Configuration, screenshots, waveform download, measurements and serial decoding for Keysight/Agilent oscilloscopes.

Maintainer: Netlist-Studio

Access path: Agent → MCP → PyVISA / Ethernet SCPI → Keysight / Agilent scope

### Contribution and value

Combines screenshots, waveforms, measurements and decoding into a scope operation surface.

### Distinctions and conditions

Names a tested model and firmware, enabling a concrete compatibility assessment.

### Reusable ideas

Build firmware-specific compatibility records and measurement-result formats.

### Public scope and experiment record

README identifies testing on an Agilent MSOX2024A with firmware 02.43.2018020635.

[Overview](https://github.com/Netlist-Studio/scope-mcp/blob/main/README.md) · [License](https://github.com/Netlist-Studio/scope-mcp/blob/main/LICENSE)

## dwf-mcp-server

[KenosInc/dwf-mcp-server](https://github.com/KenosInc/dwf-mcp-server) · Device bridges · MIT · Adapter / documentation

Oscilloscope, arbitrary-waveform and logic-analysis interfaces for Digilent WaveForms devices.

Maintainer: KenosInc

Access path: Agent → MCP → dwfpy → WaveForms SDK → Digilent device

### Contribution and value

Reuses the WaveForms SDK to expose analog and digital device functions.

### Distinctions and conditions

SDK wrapping reduces low-level work while retaining a separate vendor-runtime dependency.

### Reusable ideas

Separate the open adapter, vendor runtime and capability description.

### Public scope and experiment record

The open server depends on separately obtained proprietary libdwf/runtime components; its MIT license does not cover the vendor SDK.

[Overview](https://github.com/KenosInc/dwf-mcp-server/blob/main/README.md) · [License](https://github.com/KenosInc/dwf-mcp-server/blob/main/LICENSE)

## Instrument MCP

[zeng-andrew/instrument-mcp](https://github.com/zeng-andrew/instrument-mcp) · Device bridges · Unspecified · Adapter / documentation

Combines spectrum analyzers, radio testers, supplies, chambers and a logic analyzer using YAML command definitions and multi-instrument sessions.

Maintainer: zeng-andrew

Access path: Agent → MCP sessions → YAML commands → SCPI / Modbus / USB devices

### Contribution and value

Uses configuration-defined commands and multi-instrument sessions for RF and environmental testing.

### Distinctions and conditions

The distinguishing mechanism is configuration-driven adaptation, which still needs units, response parsing and model constraints.

### Reusable ideas

Determine which differences belong in configuration and which require driver code.

### Public scope and experiment record

Lists targets including Keysight MXA/EXA, R&S CMW500 and DSLogic; no license was identified.

[Overview](https://github.com/zeng-andrew/instrument-mcp/blob/main/README.md)

## daqmx-mcp

[BrianDavidCouch/daqmx-mcp](https://github.com/BrianDavidCouch/daqmx-mcp) · Device bridges · Apache-2.0 · Adapter / documentation

Discovers NI DAQ devices and performs finite analog-voltage and digital-input acquisition.

Maintainer: BrianDavidCouch

Access path: Agent → MCP / plugin → nidaqmx → NI DAQ input channels

### Contribution and value

Provides a compact toolset for NI device discovery and finite input acquisition.

### Distinctions and conditions

Deliberately focuses on input; output, continuous acquisition and arbitrary property writes are outside its current scope.

### Reusable ideas

Define acquisition length, timing, input types and completion conditions.

### Public scope and experiment record

A community project. The current version has no outputs, continuous acquisition or arbitrary property writes; NI drivers are installed separately.

[Overview](https://github.com/BrianDavidCouch/daqmx-mcp/blob/main/README.md) · [License](https://github.com/BrianDavidCouch/daqmx-mcp/blob/main/LICENSE)

## DAQiFi Core

[daqifi/daqifi-core](https://github.com/daqifi/daqifi-core) · Device bridges · MIT · Adapter / documentation

Vendor-published wireless DAQ SDK and MCP server covering channels, sampling, digital I/O, PWM, analog outputs and SD-card logging.

Maintainer: DAQiFi

Access path: Agent → MCP → DAQiFi .NET SDK → Wi-Fi / USB device

### Contribution and value

The device vendor exposes agent access through its SDK, joining configuration, acquisition and record download.

### Distinctions and conditions

MCP and the device SDK share a vendor-maintained repository; capabilities remain model-specific.

### Reusable ideas

Reuse the pattern of co-evolving vendor drivers and open tool interfaces.

### Public scope and experiment record

The README connects acquisition control to recorded-data retrieval; capabilities depend on the DAQiFi device model.

[Overview](https://github.com/daqifi/daqifi-core/blob/main/README.md) · [License](https://github.com/daqifi/daqifi-core/blob/main/LICENSE) · [Implementation](https://github.com/daqifi/daqifi-core/tree/main/src/Daqifi.Mcp)

## LabVIEW MCP Server Toolkit

[JanGoebel/LabVIEW-MCP-Server-Toolkit](https://github.com/JanGoebel/LabVIEW-MCP-Server-Toolkit) · Device bridges · MIT · Adapter / documentation

Exposes VIs in existing LabVIEW applications as tools, resources and prompts. A direct way to wrap established laboratory control programs.

Maintainer: JanGoebel

Access path: Agent → MCP HTTP toolkit → exposed VI → existing device code

### Contribution and value

Exposes existing VIs while preserving working instrument-control code.

### Distinctions and conditions

Provides a runtime interface, distinct from development tools that edit VI internals.

### Reusable ideas

Define VI arguments, physical effects and results before publishing discoverable capabilities.

### Public scope and experiment record

The toolkit is open source; LabVIEW itself and instrument VI dependencies have separate licensing.

[Overview](https://github.com/JanGoebel/LabVIEW-MCP-Server-Toolkit/blob/main/readme.md) · [License](https://github.com/JanGoebel/LabVIEW-MCP-Server-Toolkit/blob/main/LICENSE)

## LabVIEW MCP · Zühlke

[Zuehlke/labview-mcp](https://github.com/Zuehlke/labview-mcp) · Instrument development · MIT · Adapter / documentation

Lets agents read, modify and run LabVIEW programs. Primarily a development interface; physical control depends on the invoked VI.

Maintainer: Zühlke

Access path: Agent → MCP → gRPC lvai.LVAI → LabVIEW program editing / running

### Contribution and value

Brings LabVIEW programs into an agent’s read-edit-run loop.

### Distinctions and conditions

It changes control software; hardware capability depends on the VI and access relies on an internal LabVIEW service.

### Reusable ideas

Separate development-time editing from runtime device operation and retain both program versions and experiment records.

### Public scope and experiment record

Depends on the internal lvai.LVAI service, which the README identifies as an unpublished NI API without a stability commitment.

[Overview](https://github.com/Zuehlke/labview-mcp/blob/main/README.md) · [License](https://github.com/Zuehlke/labview-mcp/blob/main/LICENSE)

## OpenFlexure-MCP

[GSIBabu/OpenFlexure-MCP](https://github.com/GSIBabu/OpenFlexure-MCP) · Device bridges · GPL-3.0 · Adapter / documentation

Uses the OpenFlexure client for stage motion, capture, autofocus, z-stacks and extension calls.

Maintainer: GSIBabu

Access path: Agent → MCP → OpenFlexure Python client → microscope HTTP API

### Contribution and value

Adds motion, imaging and focus tools above an existing open microscope API.

### Distinctions and conditions

Builds on a networked OpenFlexure system; the principal addition is the agent-facing surface.

### Reusable ideas

Reuse procedure-level capabilities such as autofocus and Z-stacks.

### Public scope and experiment record

Targets an OpenFlexure microscope on the local network; the repository does not supply a systematic hardware test matrix.

[Overview](https://github.com/GSIBabu/OpenFlexure-MCP/blob/main/README.md) · [License](https://github.com/GSIBabu/OpenFlexure-MCP/blob/main/LICENSE)

## microscope-agent

[BioNanomics/microscope-agent](https://github.com/BioNanomics/microscope-agent) · Device bridges · MIT · Adapter / documentation

A compact interface for Nikon Ti2-E and a Baumer camera: position reads, XY motion and imaging, linking frames to actual stage position and revision counters.

Maintainer: BioNanomics

Access path: Agent → MCP → Nikon / GenICam adapter → stage & camera

### Contribution and value

Associates images with actual position and state revisions so decisions can identify the observed configuration.

### Distinctions and conditions

Adds measurement context beyond image-only tools, with a clearly bounded motion surface.

### Reusable ideas

Return image, position, exposure and configuration revision as one observation.

### Public scope and experiment record

SDK and mock paths return image previews and full files. Absolute Z motion is deliberately absent from the exposed tools.

[Overview](https://github.com/BioNanomics/microscope-agent/blob/main/README.md) · [License](https://github.com/BioNanomics/microscope-agent/blob/main/LICENSE)

## Agent-Lens

[aicell-lab/agent-lens](https://github.com/aicell-lab/agent-lens) · Procedure composition · MIT · Adapter / documentation

Combines microscope control, robotic sample transfer, segmentation, similarity search and OME-Zarr data handling.

Maintainer: KTH / SciLifeLab · AICell Lab

Access path: Agent / web UI → Hypha services → microscope & sample handling → OME-Zarr / BioEngine

### Contribution and value

Combines microscopy, sample handling, analysis services and image data in one working platform.

### Distinctions and conditions

Emphasizes service coordination and data organization, with Hypha as its main integration mechanism.

### Reusable ideas

Reuse shared experiment objects across acquisition, analysis and data browsing.

### Public scope and experiment record

Public service-registration code and a live-demo entry point; device calls primarily use Hypha services. Native MCP is not recorded as verified.

[Overview](https://github.com/aicell-lab/agent-lens/blob/main/README.md) · [License](https://github.com/aicell-lab/agent-lens/blob/main/LICENSE) · [Implementation](https://github.com/aicell-lab/agent-lens/blob/main/agent_lens/register_tools_service.py)

## Agentic microscope

[kyu-softmatter/agentic-microscope](https://github.com/kyu-softmatter/agentic-microscope) · Device bridges · MIT · Adapter / documentation

Translates research goals into microscope configurations grounded in hardware limits and calibrations, spanning microscopy, optical tweezers and piezo stages.

Maintainer: kyu-softmatter

Access path: Research goal → MCP configuration → calibrated device settings → apply & readback

### Contribution and value

Translates research goals into calibrated microscope settings and checks the applied state.

### Distinctions and conditions

Emphasizes configuration meaning and readback across microscopy, tweezers and piezo stages; code is migrating to a successor repository.

### Reusable ideas

Build inspectable mappings among goal parameters, device parameters and observed state.

### Public scope and experiment record

Configuration, application and readback code reviewed. The README distinguishes tweezers command acceptance from physical completion and announces migration to soft-matter-agents.

[Overview](https://github.com/kyu-softmatter/agentic-microscope/blob/main/README.md) · [License](https://github.com/kyu-softmatter/agentic-microscope/blob/main/LICENSE) · [Implementation](https://github.com/kyu-softmatter/agentic-microscope/blob/main/hardware/microscope.py)

## soft-matter-agents

[kyu-softmatter/soft-matter-agents](https://github.com/kyu-softmatter/soft-matter-agents) · Procedure composition · MIT · Adapter / documentation

Combines microscope, simulation, literature and bridge agents; the microscope module is the successor location for Agentic microscope.

Maintainer: kyu-softmatter

Access path: Agent workflow → microscope_agent / simulation / literature modules → configured backend

### Contribution and value

Combines microscope control, simulation and literature modules for soft-matter workflows.

### Distinctions and conditions

Research capabilities are distributed across modules; physical control resides in the device module.

### Reusable ideas

Reuse module separation and track simulation, knowledge and hardware outputs distinctly.

### Public scope and experiment record

Included as a migration target; not every module operates physical devices. Inspect microscope_agent for hardware capabilities.

[Overview](https://github.com/kyu-softmatter/soft-matter-agents/blob/main/README.md) · [License](https://github.com/kyu-softmatter/soft-matter-agents/blob/main/LICENSE)

## AILA

[M3RG-IITD/AILA](https://github.com/M3RG-IITD/AILA) · Experimental decisions · MIT · Published experiment

A language-model assistant for atomic-force-microscope experiments, combining task decomposition, tools and feedback.

Maintainer: IIT Delhi · M3RG

Access path: Research request → planning & feedback agents → AFM control tools → AFM experiment

### Contribution and value

Applies task decomposition, tool execution and feedback assessment to AFM experiments with evaluation material.

### Distinctions and conditions

Contributes agent organization and performance on experimental tasks rather than a cross-vendor AFM standard.

### Reusable ideas

Reuse evaluations that tie tasks to the instrument environment and failure types.

### Public scope and experiment record

The Nature Communications paper reports physical AFM experiments. Code and benchmarks are public; reuse requires a matching instrument-control environment.

[Overview](https://github.com/M3RG-IITD/AILA/blob/main/README.md) · [License](https://github.com/M3RG-IITD/AILA/blob/main/LICENSE.md) · [Paper](https://www.nature.com/articles/s41467-025-64105-7)

## LLM-directed-SPM

[DIAOZHUO/LLM-directed-SPM](https://github.com/DIAOZHUO/LLM-directed-SPM) · Experimental decisions · Unspecified · Published experiment

Command generation, knowledge retrieval and specialized small models for scanning-probe experiments, with local model services and training material.

Maintainer: DIAOZHUO

Access path: User task → domain model & knowledge → WebSocket / spmutil → scanning probe microscope

### Contribution and value

Combines scanning-probe knowledge, command generation and specialized small models for instrument operation.

### Distinctions and conditions

Unlike a thin bridge to a general model, the release includes model-training and local-serving material.

### Reusable ideas

Compare where domain knowledge belongs: model weights, skills or device descriptions.

### Public scope and experiment record

The paper describes physical scanning-probe experiments. No top-level license was identified; model-training code and complete device integration should be assessed separately.

[Overview](https://github.com/DIAOZHUO/LLM-directed-SPM/blob/main/readme.md) · [Paper](https://arxiv.org/abs/2602.20669)

## Quailbot Pi

[BB-84C/quailbot-pi](https://github.com/BB-84C/quailbot-pi) · Persistent execution · ISC · Adapter / documentation

Turns instrument workspaces into a fixed tool surface for parameters, actions, image readbacks and multi-step programs. Actions and subsequent observations are recorded separately; Nanonis uses an external nqctl driver.

Maintainer: BB-84C

Access path: Pi agent → workspace contract → instrument CLI / nqctl → Nanonis backend

### Contribution and value

Uses a workspace contract for parameters, actions, images and procedures, recording actions separately from observations.

### Distinctions and conditions

Uses CLI and workspace files as its instrument surface; the Nanonis driver remains an external nqctl dependency.

### Reusable ideas

Reuse the workspace as a carrier of state and operating knowledge, with explicit driver versions.

### Public scope and experiment record

Public Pi extension and workspace contract. The STM paper supplies related experimental context, not evidence that this extension includes every hardware driver.

[Overview](https://github.com/BB-84C/quailbot-pi/blob/main/README.md) · [License](https://github.com/BB-84C/quailbot-pi/blob/main/LICENSE) · [Paper](https://arxiv.org/abs/2609.27302)

## VISION

[CFN-softbio/VISION](https://github.com/CFN-softbio/VISION) · Experimental decisions · Unspecified · Published experiment

Translates spoken or written requests into beamline-operation code, with modules for transcription, classification, programming and analysis.

Maintainer: Brookhaven · CFN team

Access path: Voice / text → classification & code generation → Bluesky workstation → beamline

### Contribution and value

Translates natural-language intent into operations executable in an existing beamline environment.

### Distinctions and conditions

Focuses on natural interaction and modular intent translation, leaving deterministic execution to existing systems such as Bluesky.

### Reusable ideas

Reuse intent-to-plan translation and retain generated code alongside execution results.

### Public scope and experiment record

The project shows deployment at NSLS-II 11-BM CMS, executing after user confirmation. It is not a universal unattended instrument protocol; no license was identified.

[Overview](https://github.com/CFN-softbio/VISION/blob/main/README.md) · [Paper](https://doi.org/10.1088/2632-2153/add9e4)

## LeeQ

[ShuxiangCao/LeeQ](https://github.com/ShuxiangCao/LeeQ) · Persistent execution · BSD-3-Clause · Published experiment

Pulse experiments, sweeps, calibration state and analysis for superconducting devices, with experiment descriptions and text/visual inspection hooks for agents.

Maintainer: ShuxiangCao

Access path: Experiment agent / Python → LeeQ experiment & sweep → pulse backend → quantum device

### Contribution and value

Provides discoverable quantum experiment objects, sweeps, calibration state and result analysis.

### Distinctions and conditions

It supplies experiment/control infrastructure while agents such as k-agents select and assess experiments.

### Reusable ideas

Reuse composable experiment objects, descriptions and result-inspection interfaces.

### Public scope and experiment record

The k-agents paper reports quantum-calibration experiments. The repository also offers simulation, so experimental provenance depends on the backend.

[Overview](https://github.com/ShuxiangCao/LeeQ/blob/main/README.md) · [License](https://github.com/ShuxiangCao/LeeQ/blob/main/LICENSE) · [Paper](https://doi.org/10.1016/j.patter.2025.101372)

## k-agents

[EvoEvolver/k_agents](https://github.com/EvoEvolver/k_agents) · Experimental decisions · Unspecified · Published experiment

Discovers, executes and evaluates calibration experiments through existing experiment libraries, retaining experimental knowledge and visual results.

Maintainer: EvoEvolver

Access path: Calibration agent → experiment selection & inspection → LeeQ → quantum experiment

### Contribution and value

Builds a calibration loop of selection, execution and visual inspection around an existing experiment library.

### Distinctions and conditions

Uses experimental knowledge for subsequent decisions; its README points to NVIDIA’s successor reference project.

### Reusable ideas

Reuse descriptions, discovery and outcome assessment of experiment skills.

### Public scope and experiment record

The paper reports physical quantum calibration. The README now points to NVIDIA’s Quantum Calibration Agent Blueprint; no license was identified in this repository.

[Overview](https://github.com/EvoEvolver/k_agents/blob/main/README.md) · [Paper](https://arxiv.org/abs/2412.07978)

## Quantum Calibration Agent Blueprint

[NVIDIA/Quantum-Calibration-Agent-Blueprint](https://github.com/NVIDIA/Quantum-Calibration-Agent-Blueprint) · Experimental decisions · Apache-2.0 · Adapter / documentation

A quantum-device calibration agent reference implementation with experiment discovery, execution, visual analysis, workflows and result storage.

Maintainer: NVIDIA

Access path: Calibration agent → registered Python experiment → user control backend → results store

### Contribution and value

Provides a reference calibration-agent structure for experiment discovery, execution, image analysis and results.

### Distinctions and conditions

User-supplied experiment scripts connect the hardware; controller integration remains explicit.

### Reusable ideas

Reuse experiment plugins and result models while keeping controller integration independent of the agent UI.

### Public scope and experiment record

An NVIDIA Apache-2.0 project; experiments integrate through supplied Python scripts. The reference interface does not imply support for every quantum controller.

[Overview](https://github.com/NVIDIA/Quantum-Calibration-Agent-Blueprint/blob/main/README.md) · [License](https://github.com/NVIDIA/Quantum-Calibration-Agent-Blueprint/blob/main/LICENSE)

## CALMS

[mcherukara/CALMS](https://github.com/mcherukara/CALMS) · Experimental decisions · BSD-3-Clause · Maintainer hardware record

A context- and tool-augmented facility assistant integrating instrument knowledge with operational functions.

Maintainer: mcherukara

Access path: User task → retrieved instrument context → Python tool calls → facility device

### Contribution and value

Combines facility-context retrieval with executable functions to connect conversation to operations.

### Distinctions and conditions

Goes beyond manual retrieval through tool calls; later APS work connects robots and nanoprobe tasks.

### Reusable ideas

Version operating knowledge together with tool signatures and device context.

### Public scope and experiment record

An earlier public implementation with a demonstration and a three-clause BSD license. Later robot and beamline work appears in the APS repository.

[Overview](https://github.com/mcherukara/CALMS/blob/main/README.md) · [License](https://github.com/mcherukara/CALMS/blob/main/LICENSE)

## CALMS · APS experimental agents

[AdvancedPhotonSource/CALMS](https://github.com/AdvancedPhotonSource/CALMS) · Experimental decisions · Unspecified · Published experiment

Teachable experiment-agent workflows for a North N9 robotic station and an X-ray nanoprobe.

Maintainer: Argonne · Advanced Photon Source

Access path: Experiment agent → teachable workflow → robot / nanoprobe commands → experiment

### Contribution and value

Connects teachable experimental workflows to robot and X-ray nanoprobe operations.

### Distinctions and conditions

Moves from a general facility assistant toward specific workflows and is maintained separately from early CALMS.

### Reusable ideas

Study how expert demonstrations become readable, executable and editable procedures.

### Public scope and experiment record

README names robot and nanoprobe command modules and demonstration videos; no license was identified. Sources use the repository’s current default branch.

[Overview](https://github.com/AdvancedPhotonSource/CALMS/blob/main/README.md) · [Paper](https://doi.org/10.1038/s41524-026-02005-0)

## Opentrons MCP

[yerbymatey/opentrons-mcp](https://github.com/yerbymatey/opentrons-mcp) · Device bridges · MIT · Adapter / documentation

Combines API-documentation search with protocol upload, run management, homing and status access for OT-2/Flex.

Maintainer: yerbymatey

Access path: Agent → MCP → Opentrons HTTP API → OT-2 / Flex

### Contribution and value

Connects robot protocols and run management to agents alongside documentation lookup.

### Distinctions and conditions

Relies on the robot’s existing HTTP service; retrieval and motion-causing tools have different roles.

### Reusable ideas

Connect protocol files, run IDs, step state and sample identity in one record.

### Public scope and experiment record

Device calls use the robot HTTP API; documentation queries and physical-action tools are distinct.

[Overview](https://github.com/yerbymatey/opentrons-mcp/blob/main/README.md) · [License](https://github.com/yerbymatey/opentrons-mcp/blob/main/LICENSE)

## plr-mcp

[di-omics/plr-mcp](https://github.com/di-omics/plr-mcp) · Device bridges · MIT · Simulation-verified

Exposes liquid handling, plate reading, thermocycling and heater-shaker operations through MCP using PyLabRobot backends.

Maintainer: di-omics

Access path: Agent → MCP → PyLabRobot → chatterbox / STAR backend

### Contribution and value

Reuses PyLabRobot device/resource models across several liquid-handling devices.

### Distinctions and conditions

Uses a higher-level abstraction with default simulator validation; a real STAR backend is a separate deployment path.

### Reusable ideas

Reuse deck and container models and add records of real liquid-handling processes.

### Public scope and experiment record

End-to-end checks use the chatterbox simulator by default. A real STAR backend and bring-up guide are provided, separately from simulation verification.

[Overview](https://github.com/di-omics/plr-mcp/blob/main/README.md) · [License](https://github.com/di-omics/plr-mcp/blob/main/LICENSE)

## OpenLabAI

[nygmeta/OpenLabAI](https://github.com/nygmeta/OpenLabAI) · Procedure composition · MIT · Maintainer hardware record

Natural-language liquid-handling workflows spanning Opentrons, Biomek, Hamilton and experiment-record integrations.

Maintainer: nygmeta

Access path: Agent → MCP workflow → robot-specific API / COM / PyLabRobot → robot

### Contribution and value

Connects several liquid-handling platforms to natural-language workflows.

### Distinctions and conditions

Backend coverage differs; tested OT-2 reads and homing do not establish all execution actions.

### Reusable ideas

Maintain capability records per action/backend and verify integration separately from workflow reuse.

### Public scope and experiment record

Maintainers report physical OT-2 reads, status, homing and protocol generation; upload/start execution tools have not yet run on hardware. Hamilton and benchtop layers remain simulated.

[Overview](https://github.com/nygmeta/OpenLabAI/blob/main/README.md) · [License](https://github.com/nygmeta/OpenLabAI/blob/main/LICENSE)

## LabscriptAI OT

[KRATSZ/labscriptai-ot](https://github.com/KRATSZ/labscriptai-ot) · Procedure composition · LabscriptAI Research Citation License v1.0 · Adapter / documentation

An Opentrons agent plugin combining protocol authoring, simulation, skills and live-runtime assistance.

Maintainer: KRATSZ

Access path: Agent plugin / Skills → protocol generation → local simulation → Opentrons

### Contribution and value

Integrates protocol writing, simulation and run assistance in an agent development workflow.

### Distinctions and conditions

Emphasizes experimental-program development and operation; its restrictive license affects commercial reuse.

### Reusable ideas

Reuse the continuous workflow from authoring and checking to execution and readback.

### Public scope and experiment record

Currently uses the LabscriptAI Research Citation License, requiring separate permission for commercial use; listed outside the standard open-source-license group.

[Overview](https://github.com/KRATSZ/labscriptai-ot/blob/main/README.md) · [License](https://github.com/KRATSZ/labscriptai-ot/blob/main/LICENSE) · [Paper](https://doi.org/10.1101/2025.09.30.679666)

## Coscientist

[gomesgroup/coscientist](https://github.com/gomesgroup/coscientist) · Experimental decisions · Apache-2.0 + Commons Clause · Published experiment

A language model coordinates literature, code and experimental tools for chemical research; an important early physical-experiment case study.

Maintainer: Carnegie Mellon · Gomes Group

Access path: Research goal → literature & code tools → laboratory API → robotic chemistry

### Contribution and value

Demonstrates a language model combining retrieval, programming and experiment tools for chemistry tasks.

### Distinctions and conditions

Contributes end-to-end research organization and experiments; the public release differs from the full paper environment.

### Reusable ideas

Reuse task decomposition and feedback design while implementing laboratory integration separately.

### Public scope and experiment record

The paper reports robotic chemistry. Public code is not the complete deployable laboratory from the paper. License: Apache-2.0 with Commons Clause.

[Overview](https://github.com/gomesgroup/coscientist/blob/main/README.md) · [License](https://github.com/gomesgroup/coscientist/blob/main/LICENSE) · [Paper](https://doi.org/10.1038/s41586-023-06792-0)

## ChemAgents

[pic-ai-robotic-chemistry/ChemAgents](https://github.com/pic-ai-robotic-chemistry/ChemAgents) · Experimental decisions · Unspecified · Published experiment

A multi-agent chemical-research system connecting experimental protocols, a robotic workcell and experiment data.

Maintainer: pic-ai-robotic-chemistry

Access path: Research agents → robot instructions → ROS / robot drivers → chemistry workstation

### Contribution and value

Connects chemical planning, robot operations and experimental data in a multi-agent workflow.

### Distinctions and conditions

Robot instructions, AGV and arm drivers live in external repositories, so the system spans several projects.

### Reusable ideas

Use dependency graphs to define each module’s inputs, outputs and device responsibilities.

### Public scope and experiment record

The repository provides paper code and experimental data, linking robot instructions and AGV drivers separately; no license was identified here.

[Overview](https://github.com/pic-ai-robotic-chemistry/ChemAgents/blob/main/README.md) · [Paper](https://doi.org/10.1021/jacs.4c17738)

## ORGANA

[ac-rad/organa](https://github.com/ac-rad/organa) · Experimental decisions · Unspecified · Published experiment

The ORGANA paper combines user intent, scene perception and experiment progress in a chemistry robot assistant; this repository mainly publishes the project website and research material.

Maintainer: AC-RAD research collaboration

Access path: User intent → perception & task planning → robot execution → experiment report

### Contribution and value

The paper uses user intent, scene perception and experiment progress to choose robot actions.

### Distinctions and conditions

The listed repository mainly contains website source, providing methods and experiment evidence rather than a complete controller release.

### Reusable ideas

Reuse the relationship among perception, experiment progress and reporting; locate a distinct release for controller code.

### Public scope and experiment record

The paper reports physical robot experiments. The README identifies this repository as website source, rather than establishing a complete robot-control release; no license was identified.

[Overview](https://github.com/ac-rad/organa/blob/main/README.md) · [Paper](https://arxiv.org/abs/2401.06949)

## CLAIRify

[ac-rad/xdl-generation](https://github.com/ac-rad/xdl-generation) · Procedure composition · MIT · Published experiment

Translates natural-language experiment steps into verifiable XDL procedures, feeding verification errors back to the model for revision.

Maintainer: AC-RAD research collaboration

Access path: Natural-language procedure → XDL generation → verification & revision → external executor

### Contribution and value

Converts experimental instructions into structured procedures and revises them using verification feedback.

### Distinctions and conditions

The principal release is the generator and data; procedure validity and robot execution are separate layers.

### Reusable ideas

Reuse the generate-verify-revise loop and connect the verifier to available device capabilities.

### Public scope and experiment record

The paper includes robot execution; this repository mainly releases the generator and data. The README directs users to develop for updated API compatibility.

[Overview](https://github.com/ac-rad/xdl-generation/blob/master/README.md) · [License](https://github.com/ac-rad/xdl-generation/blob/master/LICENSE) · [Paper](https://arxiv.org/abs/2303.14100)

## CLAIRify-Chemspeed

[ac-rad/clairify-chemspeed](https://github.com/ac-rad/clairify-chemspeed) · Procedure composition · Unspecified · Adapter / documentation

Generates Chemspyd programs from natural language, connecting protocol generation to Chemspeed automation.

Maintainer: AC-RAD research collaboration

Access path: Natural language → program generation → Chemspyd → Chemspeed platform

### Contribution and value

Connects language-to-procedure generation specifically to Chemspyd.

### Distinctions and conditions

Targets an existing device programming interface rather than a general XDL generator.

### Reusable ideas

Reuse program generation above an established experiment API and retain program/run versions.

### Public scope and experiment record

An interface example linked by the Chemspyd paper; no license was identified for this repository.

[Overview](https://github.com/ac-rad/clairify-chemspeed/blob/master/README.md) · [Paper](https://doi.org/10.1039/D4DD00046C)

## SynAgent · thin-film synthesis

[izumitkhr/synagent](https://github.com/izumitkhr/synagent) · Experimental decisions · MIT · Published experiment

Multimodal planning and hypothesis testing in a thin-film synthesis loop, reading XRD/SEM data and writing conditions for the next experiment.

Maintainer: izumitkhr

Access path: XRD / SEM MaiML data → hypothesis & skill generation → output.txt → external dLab

### Contribution and value

Updates its understanding of thin-film synthesis through predictions, feedback and alternating verification/falsification.

### Distinctions and conditions

The public program is an iteration planner exchanging files with dLab, not a collection of deposition and transport drivers.

### Reusable ideas

Reuse structured links among hypotheses, predicted outcomes, measurements and next conditions.

### Public scope and experiment record

The paper reports 18 physical experiments. Public code connects to dLab through MaiML input and output.txt, without packaging the complete deposition, transport and measurement stack.

[Overview](https://github.com/izumitkhr/synagent/blob/main/README.md) · [License](https://github.com/izumitkhr/synagent/blob/main/LICENSE) · [Paper](https://arxiv.org/abs/2609.18598)

## AutoLabs

[pnnl/autolabs](https://github.com/pnnl/autolabs) · Experimental decisions · BSD-2-Clause · Supporting artifact

Generates experiment steps and Lab Step Representation, supporting multi-agent revision and experiment-design evaluation.

Maintainer: Pacific Northwest National Laboratory

Access path: Research prompt → multi-agent revision → Lab Step Representation → simulation / evaluation

### Contribution and value

Expresses experimental designs as inspectable steps for comparison and revision.

### Distinctions and conditions

The public application emphasizes planning, simulation and evaluation rather than a complete hardware executor.

### Reusable ideas

Reuse intermediate step representations that can be checked independently and consumed by an executor.

### Public scope and experiment record

The public application emphasizes design, simulation and evaluation; physical experiments in the paper do not make this repository a complete hardware runtime.

[Overview](https://github.com/pnnl/autolabs/blob/master/README.md) · [License](https://github.com/pnnl/autolabs/blob/master/LICENSE.md) · [Paper](https://arxiv.org/abs/2509.25651)

## opcua-mcp · kukapay

[kukapay/opcua-mcp](https://github.com/kukapay/opcua-mcp) · Device bridges · MIT · Adapter / documentation

Connects OPC UA browsing and single-node or batch reads/writes to agents while retaining existing industrial servers.

Maintainer: kukapay

Access path: Agent → MCP → OPC UA client → server address space → industrial device

### Contribution and value

Adds browse/read/write tools in front of existing OPC UA device services.

### Distinctions and conditions

Primarily bridges protocols; variable units, modes and effects come from the server information model.

### Reusable ideas

Preserve the OPC UA information model and map agent arguments to nodes precisely.

### Public scope and experiment record

An OPC UA-to-MCP adapter; physical meaning depends on the server address space and information model.

[Overview](https://github.com/kukapay/opcua-mcp/blob/main/README.md) · [License](https://github.com/kukapay/opcua-mcp/blob/main/LICENSE)

## OPC UA MCP · IndustriAgents

[IndustriAgents/OPCUA-MCP](https://github.com/IndustriAgents/OPCUA-MCP) · Device bridges · MIT · Adapter / documentation

Browsing, reads, history, subscriptions, alarms and configured writes/method calls, with one local process per OPC UA endpoint.

Maintainer: IndustriAgents

Access path: Agent → local MCP process → OPC UA subscriptions / methods → endpoint

### Contribution and value

Adds subscriptions, history and alarms to industrial observation with configured write access.

### Distinctions and conditions

Goes beyond single-point access toward ongoing state; one process connects to one endpoint.

### Reusable ideas

Reuse event-driven observation while separating endpoint sessions from experiment jobs.

### Public scope and experiment record

The current README includes writes but defaults to read-only operation; shared remote multi-client deployment has separate design constraints.

[Overview](https://github.com/IndustriAgents/OPCUA-MCP/blob/main/README.md) · [License](https://github.com/IndustriAgents/OPCUA-MCP/blob/main/LICENSE)

## modbus-mcp

[kukapay/modbus-mcp](https://github.com/kukapay/modbus-mcp) · Device bridges · MIT · Adapter / documentation

Exposes register and coil reads/writes, providing a low-level route to existing PLCs, sensors and controllers.

Maintainer: kukapay

Access path: Agent → MCP → Modbus client → coils / registers → PLC / sensor

### Contribution and value

Provides simple register/coil access to existing controllers.

### Distinctions and conditions

Readable addresses do not encode physical units or intent; the device map remains essential.

### Reusable ideas

Turn register maps into capabilities with units, scaling, modes and readback rules.

### Public scope and experiment record

Communication calls are exposed; units, scaling, modes and side effects still require a device-specific register map.

[Overview](https://github.com/kukapay/modbus-mcp/blob/main/README.md) · [License](https://github.com/kukapay/modbus-mcp/blob/main/LICENSE)

## TANGO MCP

[abogani/tango-mcp](https://github.com/abogani/tango-mcp) · Device bridges · Apache-2.0 · Adapter / documentation

Discovers devices through a TANGO database and maps attributes, state and commands to MCP resources and tools, including bulk reads.

Maintainer: abogani

Access path: Agent → MCP → PyTango database / device proxy → TANGO device server

### Contribution and value

Reuses the facility database for discovery and maps attributes, state, commands and batch reads.

### Distinctions and conditions

Adapts existing TANGO semantics while device servers retain low-level control.

### Reusable ideas

Preserve original device names, attributes and state transitions to avoid duplicate modeling.

### Public scope and experiment record

Provides TANGO_HOST deployment and attribute/command paths; available operations depend on the facility’s existing device servers.

[Overview](https://github.com/abogani/tango-mcp/blob/main/README.md) · [License](https://github.com/abogani/tango-mcp/blob/main/LICENSE)

## MCP Server for EPICS

[sryu81/mcp-server-for-epics](https://github.com/sryu81/mcp-server-for-epics) · Device bridges · Unspecified · Adapter / documentation

Offers standalone-process and IOC-embedded entry points exposing EPICS PVs and control commands to agents.

Maintainer: sryu81

Access path: Agent → MCP → standalone server / IOC library → CA / PVA → process variables

### Contribution and value

Offers standalone and IOC-embedded deployment so tool access can sit near the existing control system.

### Distinctions and conditions

Deployment topology and connection ownership distinguish it; PV meaning still needs facility context.

### Reusable ideas

Compare connection ownership and state consistency inside versus outside an IOC.

### Public scope and experiment record

C++ shared-library and protocol-dispatch structure is public; no license was identified.

[Overview](https://github.com/sryu81/mcp-server-for-epics/blob/main/README.md)

## MCP2Serial

[mcp2everything/mcp2serial](https://github.com/mcp2everything/mcp2serial) · Device bridges · MIT · Adapter / documentation

Connects microcontrollers to agents through serial communication, useful as a basic bridge for custom instruments.

Maintainer: mcp2everything

Access path: Agent → MCP → serial connection → MCU firmware → attached hardware

### Contribution and value

Provides a basic serial agent interface for custom instruments.

### Distinctions and conditions

Semantics remain in firmware and serial commands, including completion and result formats.

### Reusable ideas

Use the serial bridge as a starting point and define capabilities, responses and measurement timing.

### Public scope and experiment record

The README provides Pico integration workflows; serial transport alone does not define units, device state or completion conditions.

[Overview](https://github.com/mcp2everything/mcp2serial/blob/main/README.md) · [License](https://github.com/mcp2everything/mcp2serial/blob/main/LICENSE)

## tinymcp

[golioth/tinymcp](https://github.com/golioth/tinymcp) · Device bridges · Apache-2.0 · Adapter / documentation

Exposes Golioth device RPCs as MCP tools; existing devices can publish tool schemas through the state service.

Maintainer: Golioth

Access path: Agent → MCP → Golioth management API → device RPC → embedded device

### Contribution and value

Generates tools dynamically from existing device RPC descriptions.

### Distinctions and conditions

Adds a lightweight interface while discovery and communication depend on Golioth.

### Reusable ideas

Reuse device-published capability schemas with explicit platform dependencies.

### Public scope and experiment record

Includes a Zephyr LED-control example. Server code is open source, while operation depends on the Golioth platform.

[Overview](https://github.com/golioth/tinymcp/blob/main/README.md) · [License](https://github.com/golioth/tinymcp/blob/main/LICENSE)

## Embedded Debugger MCP

[Adancurusul/embedded-debugger-mcp](https://github.com/Adancurusul/embedded-debugger-mcp) · Instrument development · MIT · Maintainer hardware record

Connects agents to debug probes for target control, memory access, breakpoints, flashing and fault inspection, supplying physical feedback during instrument-firmware development.

Maintainer: Adancurusul

Access path: Agent → MCP / CLI → probe-rs / OpenOCD → debug probe → target MCU

### Contribution and value

Connects firmware to real chip state so an agent can inspect breakpoints, memory and faults.

### Distinctions and conditions

Operates on debug targets and firmware rather than high-level scientific instrument actions.

### Reusable ideas

Build traceable loops among firmware versions, flashing, execution and measurements.

### Public scope and experiment record

Maintainers report validation on a physical ESP32-S3; native probe-rs and OpenOCD backends are configured separately.

[Overview](https://github.com/Adancurusul/embedded-debugger-mcp/blob/main/README.md) · [License](https://github.com/Adancurusul/embedded-debugger-mcp/blob/main/LICENSE)

## Saleae Logic 2 MCP

[hsoffar/saleae-logic2-mcp](https://github.com/hsoffar/saleae-logic2-mcp) · Instrument development · Apache-2.0 · Adapter / documentation

Logic-analyzer capture, protocol decoding, timing measurement and export for firmware and physical-bus debugging.

Maintainer: hsoffar

Access path: Agent → MCP → Logic 2 automation → logic analyzer → physical bus

### Contribution and value

Returns real bus captures, protocol decoding and timing results to development agents.

### Distinctions and conditions

Contributes external signal observation while the target system executes its own program.

### Reusable ideas

Compare code changes with bus traces to locate timing problems in instrument control.

### Public scope and experiment record

Requires Saleae Logic 2 with automation enabled; the application and hardware are not supplied by the open server.

[Overview](https://github.com/hsoffar/saleae-logic2-mcp/blob/main/README.md) · [License](https://github.com/hsoffar/saleae-logic2-mcp/blob/main/LICENSE)

## MicroPython MCP Bridge

[SWITCHSCIENCE/mcp-micropython-bridge](https://github.com/SWITCHSCIENCE/mcp-micropython-bridge) · Instrument development · Unspecified · Adapter / documentation

Operates ESP32/RP2040-class boards through serial or WebREPL, using device-side helper modules and HARDWARE.md for board-specific knowledge.

Maintainer: SWITCHSCIENCE

Access path: Agent → MCP → serial / WebREPL → MicroPython helpers → MCU I/O

### Contribution and value

Uses programmable firmware for board-level I/O and retains hardware descriptions.

### Distinctions and conditions

Capabilities can be extended through device-side code, spanning development and runtime interfaces.

### Reusable ideas

Manage pin maps, wiring and helpers together with firmware versions.

### Public scope and experiment record

Provides a hardware-test CLI and firmware setup instructions; no top-level license was identified.

[Overview](https://github.com/SWITCHSCIENCE/mcp-micropython-bridge/blob/main/README.md)

## ROS MCP Server

[robotmcp/ros-mcp-server](https://github.com/robotmcp/ros-mcp-server) · Device bridges · Apache-2.0 · Maintainer hardware record

Uses rosbridge to discover topics, services, actions and message types, publish control messages and read robot-sensor feedback.

Maintainer: robotmcp

Access path: Agent → MCP → rosbridge → ROS topics / services / actions → robot

### Contribution and value

Exposes ROS communication objects to agents and reuses the existing robotics ecosystem.

### Distinctions and conditions

Solves discovery and invocation while the robot stack supplies planning, timing and feedback.

### Reusable ideas

Preserve the distinct lifecycles of topics, services and actions.

### Public scope and experiment record

Robot demonstrations are included. The bridge covers ROS communication; motion capabilities and controllers remain in the robot stack.

[Overview](https://github.com/robotmcp/ros-mcp-server/blob/main/README.md) · [License](https://github.com/robotmcp/ros-mcp-server/blob/main/LICENSE)

## ROSA

[nasa-jpl/rosa](https://github.com/nasa-jpl/rosa) · Experimental decisions · Apache-2.0 · Published experiment

JPL’s natural-language ROS assistant combines system diagnostics, state queries and extensible robot-operation tools.

Maintainer: NASA · Jet Propulsion Laboratory

Access path: Language agent → extensible ROS tools → ROS 1 / ROS 2 → robot

### Contribution and value

Combines robot diagnosis, inspection and operation tools in a natural-language assistant.

### Distinctions and conditions

The framework owns interaction/reasoning, unlike a pure ROS-to-MCP adapter.

### Reusable ideas

Reuse domain tools that express robot state and operation scope.

### Public scope and experiment record

The paper and examples cover robotic applications. ROSA is an agent/tool framework; native MCP is not inferred from its purpose.

[Overview](https://github.com/nasa-jpl/rosa/blob/main/README.md) · [License](https://github.com/nasa-jpl/rosa/blob/main/LICENSE) · [Paper](https://arxiv.org/abs/2410.06472)

## device-use

[labclaw/device-use](https://github.com/labclaw/device-use) · GUI operation · Apache-2.0 · Adapter / documentation

Wraps instrument software through screen observation, planning and mouse/keyboard actions with device profiles. Relevant when an API is unavailable.

Maintainer: labclaw

Access path: Agent / VLM → observe-plan-act → mouse / keyboard → instrument software

### Contribution and value

Brings instrument software without usable APIs into an observe-and-operate loop.

### Distinctions and conditions

Depends on the visible UI and software version, with different maintenance and verification costs from SDK access.

### Reusable ideas

Use device profiles for UI state, actions and post-action result checks.

### Public scope and experiment record

Public implementation includes NMR-data and plate-reader modules. MCP tools do not establish physical-control validation for every named commercial instrument.

[Overview](https://github.com/labclaw/device-use/blob/main/README.md) · [License](https://github.com/labclaw/device-use/blob/main/LICENSE) · [Implementation](https://github.com/labclaw/device-use/blob/main/src/device_use/integrations/mcp_server.py)

## device-skills

[labclaw/device-skills](https://github.com/labclaw/device-skills) · Knowledge and artifacts · Apache-2.0 · Supporting artifact

Instrument operating knowledge and skill material accompanying device-use execution interfaces.

Maintainer: labclaw

Access path: Device operating knowledge → Agent Skills → agent → separate device-use runtime

### Contribution and value

Provides reusable instrument operating knowledge to agents.

### Distinctions and conditions

Knowledge guides operation while a separate component handles connection and execution.

### Reusable ideas

Make skills reference device versions, required tools and expected observations.

### Public scope and experiment record

Skills contain knowledge and operating instructions; listed as supporting material rather than device drivers or an independently validated hardware system.

[Overview](https://github.com/labclaw/device-skills/blob/main/README.md) · [License](https://github.com/labclaw/device-skills/blob/main/LICENSE)

## edge-mhs

[fastly/edge-mhs](https://github.com/fastly/edge-mhs) · Device bridges · Apache-2.0 · Simulation-verified

An edge gateway between agents and device services for identity, parameter constraints, quotas and audit records.

Maintainer: Fastly

Access path: Agent → MCP edge gateway → backend proxy → mock driver

### Contribution and value

Centralizes remote-access identity, argument constraints and records in an edge gateway.

### Distinctions and conditions

Currently a mock-backed reference gateway whose backend contract must be matched to a real device runtime.

### Reusable ideas

Treat the gateway as an optional deployment component while preserving independent local execution.

### Public scope and experiment record

The README identifies a reference implementation with mock backends, not an official Anthropic MHS server.

[Overview](https://github.com/fastly/edge-mhs/blob/main/README.md) · [License](https://github.com/fastly/edge-mhs/blob/main/LICENSE)

## Agent2Device Protocol

[neogyk/Agent2Device-Protocol](https://github.com/neogyk/Agent2Device-Protocol) · Instrument contracts · MIT · Concept / proposal

A protocol concept for connecting agents to laboratory devices.

Maintainer: neogyk

Access path: Protocol concept → README design notes

### Contribution and value

Provides a conceptual entry point to agent-device connectivity.

### Distinctions and conditions

The release consists of design notes, with no driver or runtime to reuse directly.

### Reusable ideas

Use to compare requirements, drawing implementation decisions from concrete code and behavior.

### Public scope and experiment record

The reviewed tree contains only README, LICENSE and an ignore file, with no protocol implementation or device driver.

[Overview](https://github.com/neogyk/Agent2Device-Protocol/blob/main/README.md) · [License](https://github.com/neogyk/Agent2Device-Protocol/blob/main/LICENSE)

## ChemCrow public release

[ur-whitelab/chemcrow-public](https://github.com/ur-whitelab/chemcrow-public) · Knowledge and artifacts · MIT · Supporting artifact

An important chemistry tool-augmented agent case for understanding orchestration and experimental-service boundaries.

Maintainer: ur-whitelab

Access path: Chemistry agent → public tool subset → external services

### Contribution and value

Shows how chemical expertise enters model workflows through tool composition.

### Distinctions and conditions

The public package lacks some paper service interfaces, so experimental scope exceeds the downloadable tool set.

### Reusable ideas

Reuse tool selection and domain-task organization while checking each available service.

### Public scope and experiment record

The paper includes experimental execution, but the README explicitly says API restrictions exclude some paper tools from the public package.

[Overview](https://github.com/ur-whitelab/chemcrow-public/blob/main/README.md) · [License](https://github.com/ur-whitelab/chemcrow-public/blob/main/LICENSE) · [Paper](https://doi.org/10.1038/s42256-024-00832-8)

## NV autonomous experiments

[takuyaisogawa/nv-autonomous-experiments](https://github.com/takuyaisogawa/nv-autonomous-experiments) · Knowledge and artifacts · MIT code / CC BY-4.0 artifacts · Supporting artifact

Public case studies, analysis code and experimental artifacts for autonomous NV-center experiments.

Maintainer: takuyaisogawa

Access path: Released case studies → analysis & trajectories → external live backend

### Contribution and value

Provides NV experiment case studies and analysis for studying decisions and feedback.

### Distinctions and conditions

The release excludes the live laboratory backend and serves as trajectory material rather than a driver.

### Reusable ideas

Reuse the links among trajectories, analyses and the experimental environment.

### Public scope and experiment record

Release and license notes explicitly omit the live-laboratory backend. Useful for experimental trajectories, not a complete NV-device control release.

[Overview](https://github.com/takuyaisogawa/nv-autonomous-experiments/blob/main/README.md) · [License](https://github.com/takuyaisogawa/nv-autonomous-experiments/blob/main/LICENSE) · [Paper](https://arxiv.org/abs/2607.25145)

## UC2 LLM microscopy workshop

[openUC2/Hackathon-UC2-LLM](https://github.com/openUC2/Hackathon-UC2-LLM) · Knowledge and artifacts · Unspecified · Supporting artifact

A teaching entry point for physical UC2 microscopes and the ImSwitch API, covering hardware, access and experimental challenges.

Maintainer: openUC2

Access path: Workshop material → Python / ImSwitch FastAPI → UC2 microscope

### Contribution and value

Uses an open microscope and explicit API to connect hardware to experimental exercises.

### Distinctions and conditions

Contributes integration material and experimental tasks rather than a complete persistent agent platform.

### Reusable ideas

Use compact reproducible experiments for adapter onboarding and acceptance.

### Public scope and experiment record

Workshop and example material rather than a complete independent agent platform; no license was identified.

[Overview](https://github.com/openUC2/Hackathon-UC2-LLM/blob/main/README.md)

