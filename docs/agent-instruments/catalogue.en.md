# Project catalogue

[中文 HTML](index.zh-CN.html) · [English HTML](index.en.html) · [JSON](catalogue.json)

## OpenMHP

[kushalsinha/openmhp](https://github.com/kushalsinha/openmhp) · Device protocols · Apache-2.0 · Simulation-verified

A device contract covering descriptors, reads, writes, actions, jobs, leases and run records, with bridges to existing drivers. Useful for studying a compact device interface and on-demand discovery.

Published specification and implementation. Seven supported-device packages are marked twin tested, plus one manual-operation template; maintainers explicitly distinguish these from hardware-tested drivers.

MCP / CLI / Python SDK / JSON-RPC / HTTP/SSE

[Overview](https://github.com/kushalsinha/openmhp/blob/main/README.md) · [License](https://github.com/kushalsinha/openmhp/blob/main/LICENSE) · [Implementation](https://github.com/kushalsinha/openmhp/blob/main/SPEC.md) · [Implementation](https://github.com/kushalsinha/openmhp/blob/main/supported-devices/README.md) · [Implementation](https://github.com/kushalsinha/openmhp/blob/main/supported-devices/biologic-sp300/driver.py)

## Open-MHS · Abenor Labs

[Abenor-Labs/Open-MHS](https://github.com/Abenor-Labs/Open-MHS) · Device protocols · Apache-2.0 · Adapter / documentation

Capability tags and a device base class describe sensors, actuators and state, with a serial robotic-arm adapter. An independent community implementation.

Source includes mock devices and a serial driver; the reviewed material does not document a named hardware validation run.

MCP / REST / CLI / Python / Serial

[Overview](https://github.com/Abenor-Labs/Open-MHS/blob/main/README.md) · [License](https://github.com/Abenor-Labs/Open-MHS/blob/main/LICENSE) · [Implementation](https://github.com/Abenor-Labs/Open-MHS/blob/main/open_mhs/drivers/serial_robotic_arm.py) · [Implementation](https://github.com/Abenor-Labs/Open-MHS/blob/main/schema/capability_schema.json)

## Open MHS · tongriyaotxt

[tongriyaotxt/open-mhs](https://github.com/tongriyaotxt/open-mhs) · Device protocols · MIT · Adapter / documentation

Device registration, common commands and MCP tools, extended with robot motion and skill execution. Maintained separately from other similarly named projects.

MCP dispatch code reviewed. Physical-device and MuJoCo examples must be assessed by their individual backends.

MCP / REST / CLI / Python

[Overview](https://github.com/tongriyaotxt/open-mhs/blob/main/README.md) · [License](https://github.com/tongriyaotxt/open-mhs/blob/main/LICENSE) · [Implementation](https://github.com/tongriyaotxt/open-mhs/blob/main/src/openmhs/mcp/server.py)

## Open MHS · SCUT-ESA

[SCUT-ESA/open-mhs](https://github.com/SCUT-ESA/open-mhs) · Device protocols · MIT · Maintainer hardware record

A common device interface with explicit backend policies for VISA instruments, embedded I/O and simulators. A community project inspired by MHS.

Maintainers report real-hardware verification for UNI-T UPO6102N and UTG2062X; other camera and GPIO adapters have separate experimental or simulation status.

MCP / REST / CLI / PyVISA

[Overview](https://github.com/SCUT-ESA/open-mhs/blob/main/README.md) · [License](https://github.com/SCUT-ESA/open-mhs/blob/main/LICENSE) · [Implementation](https://github.com/SCUT-ESA/open-mhs/blob/main/src/openmhs/core/backend.py)

## Model Hardware Protocol · Cuntinum

[Cuntinum/model-hardware-protocol](https://github.com/Cuntinum/model-hardware-protocol) · Device protocols · Apache-2.0 · Adapter / documentation

Organizes drivers and shared state around discover, read, write and execute. Distributed as khp; distinct from OpenMHP.

Public specification, SDKs and driver directory. The README’s production-grade description is not treated as evidence of cross-device validation.

Python SDK / TypeScript SDK / MCP / CLI

[Overview](https://github.com/Cuntinum/model-hardware-protocol/blob/main/README.md) · [License](https://github.com/Cuntinum/model-hardware-protocol/blob/main/LICENSE)

## Open Agent Hardware Layer

[fredabila/oahl](https://github.com/fredabila/oahl) · Device protocols · MIT · Maintainer hardware record

A discover–reserve–execute–release lifecycle separating nodes, adapters and transports, with local operation or optional registry and relay services.

README demonstrates Android phone operation through ADB; this does not establish a shared scientific calibration, long-job or measurement model.

JavaScript SDK / Python SDK / WebSocket / Serial / ADB / MQTT / TCP

[Overview](https://github.com/fredabila/oahl/blob/main/README.md) · [License](https://github.com/fredabila/oahl/blob/main/LICENSE)

## instrMCP

[caidish/instrMCP](https://github.com/caidish/instrMCP) · Execution & orchestration · MIT · Adapter / documentation

Exposes a QCoDeS Station inside an existing Jupyter kernel, reusing parameters, snapshots, databases and measurement workflows. A direct route for QCoDeS laboratories.

Parameter discovery, caching and fresh-read code reviewed. The running kernel and QCoDeS drivers own the actual device connections.

MCP / Jupyter / QCoDeS / Python / MeasureIt

[Overview](https://github.com/caidish/instrMCP/blob/main/README.md) · [License](https://github.com/caidish/instrMCP/blob/main/LICENSE) · [Implementation](https://github.com/caidish/instrMCP/blob/main/instrmcp/servers/jupyter_qcodes/backend/qcodes.py)

## PUDA

[PUDAP/puda](https://github.com/PUDAP/puda) · Execution & orchestration · MIT · Adapter / documentation

A headless physical-device runtime separating messaging, layered drivers, protocol execution and result records. Agents author, validate and run experiments through a CLI and skills.

CLI execution path reviewed: it obtains the machine command catalogue before dispatch through NATS; the repository includes an edge-driver example.

CLI / NATS / Python drivers / Agent Skills

[Overview](https://github.com/PUDAP/puda/blob/main/README.md) · [License](https://github.com/PUDAP/puda/blob/main/LICENSE) · [Implementation](https://github.com/PUDAP/puda/blob/main/apps/cli/internal/cli/protocol-run.go) · [Paper](https://arxiv.org/abs/2607.26464)

## Uni-Lab-OS

[deepmodeling/Uni-Lab-OS](https://github.com/deepmodeling/Uni-Lab-OS) · Execution & orchestration · GPL-3.0 framework + proprietary drivers · Published experiment

Cross-device laboratory orchestration combining actions, resources and laboratory topology. Useful for comparing framework, adapter and workflow-compiler responsibilities.

The paper and driver tree describe physical laboratory operation. The framework is GPL-3.0; unilabos/devices/ is separately covered by a DP Technology proprietary license.

Python / ROS 2 / Action/Resource model / Workflow compiler

[Overview](https://github.com/deepmodeling/Uni-Lab-OS/blob/main/README.md) · [License](https://github.com/deepmodeling/Uni-Lab-OS/blob/main/LICENSE) · [Implementation](https://github.com/deepmodeling/Uni-Lab-OS/blob/main/NOTICE) · [Implementation](https://github.com/deepmodeling/Uni-Lab-OS/blob/main/unilabos/devices/LICENSE) · [Implementation](https://github.com/deepmodeling/Uni-Lab-OS/blob/main/docs/developer_guide/add_device.md) · [Paper](https://arxiv.org/abs/2512.21766)

## Osprey

[als-apg/osprey](https://github.com/als-apg/osprey) · Execution & orchestration · BSD-3-Clause · Published experiment

An agent interface for large scientific facilities: semantic channel addressing, facility knowledge, control connectors and operational workflows. Includes EPICS, DOOCS and TANGO connectors.

Project publications and facility applications supply experimental context; the current implementation requires human approval for every hardware write.

MCP / CLI / Agent Skills / EPICS / DOOCS / TANGO

[Overview](https://github.com/als-apg/osprey/blob/main/README.md) · [License](https://github.com/als-apg/osprey/blob/main/LICENSE.txt) · [Implementation](https://github.com/als-apg/osprey/blob/main/docs/source/architecture/mcp-servers.rst) · [Paper](https://doi.org/10.1063/5.0306302)

## IvoryOS

[ivoryos-ai/IvoryOS](https://github.com/ivoryos-ai/IvoryOS) · Execution & orchestration · MIT · Published experiment

Turns existing Python automation objects into controls and workflows, with optional natural-language workflow design. Useful for progressively exposing existing device code.

A laboratory-orchestration paper is available. The current README does not document a native MCP server; a Python API is recorded separately.

Python introspection / Web application / LLM workflow design

[Overview](https://github.com/ivoryos-ai/IvoryOS/blob/main/README.md) · [License](https://github.com/ivoryos-ai/IvoryOS/blob/main/LICENSE) · [Implementation](https://github.com/ivoryos-ai/IvoryOS/blob/main/ivoryos/parsers/introspection.py) · [Paper](https://www.nature.com/articles/s41467-025-60514-w)

## Jumpstarter

[jumpstarter-dev/jumpstarter](https://github.com/jumpstarter-dev/jumpstarter) · Execution & orchestration · Apache-2.0 · Adapter / documentation

Shares and leases physical or virtual devices under test, with power, UART, CAN, SPI, GPIO and USB drivers. Agents can use the same interfaces as test scripts.

Public drivers, Python client, gRPC definitions and controller. Agent-accessible hardware infrastructure rather than a specialized scientific language model.

CLI / Python API / gRPC / Hardware leases

[Overview](https://github.com/jumpstarter-dev/jumpstarter/blob/main/README.md) · [License](https://github.com/jumpstarter-dev/jumpstarter/blob/main/LICENSE)

## Lager

[lagerdata/lager](https://github.com/lagerdata/lager) · Execution & orchestration · Apache-2.0 · Adapter / documentation

A bench Linux host connects supplies, scopes, debug probes and buses. A common CLI serves agents, humans and CI; programs can execute next to the devices.

README and documentation describe concrete instruments and bench deployment. The reusable contribution is the bench execution layer.

CLI / Python Net API / Network bench control

[Overview](https://github.com/lagerdata/lager/blob/main/README.md) · [License](https://github.com/lagerdata/lager/blob/main/LICENSE)

## Experiment Automation Agents

[AdvancedPhotonSource/EAA](https://github.com/AdvancedPhotonSource/EAA) · Execution & orchestration · Unspecified · Published experiment

An experiment-agent runtime emphasizing visual feedback, image tool results, deterministic workflows and experiment task management.

A microscopy experiment publication is available; the README announces migration to EAA-Pi. No top-level license was identified.

MCP client / HTTP tools / Python / Agent Skills

[Overview](https://github.com/AdvancedPhotonSource/EAA/blob/main/README.md) · [Paper](https://pmc.ncbi.nlm.nih.gov/articles/PMC13633048/)

## EAA-Pi

[AdvancedPhotonSource/EAA-Pi](https://github.com/AdvancedPhotonSource/EAA-Pi) · Execution & orchestration · Unspecified · Adapter / documentation

An experiment-assistant interface built on pi-experiment-ops; terminal and web views share workspaces, tools and experiment sessions.

Published as EAA’s successor. Instrument capability depends on connected MCP servers; validation from the earlier paper is not automatically transferred.

CLI / Web UI / MCP instruments / Agent Skills

[Overview](https://github.com/AdvancedPhotonSource/EAA-Pi/blob/main/README.md)

## pi-experiment-ops

[AdvancedPhotonSource/pi-experiment-ops](https://github.com/AdvancedPhotonSource/pi-experiment-ops) · Execution & orchestration · Unspecified · Adapter / documentation

Combines experiment tools, background execution, persistent terminals and transcript search into a reusable agent runtime for experiment applications.

Its MCP adapter connects separate instrument services; the runtime itself does not provide universal device drivers.

Pi extension / MCP / CodeMode / CLI / Agent Skills

[Overview](https://github.com/AdvancedPhotonSource/pi-experiment-ops/blob/main/README.md)

## LabMCP · K-Dense

[K-Dense-AI/lab-instrument-mcps](https://github.com/K-Dense-AI/lab-instrument-mcps) · Measurement & benches · Apache-2.0 · Simulation-verified

A monorepo of instrument adapters spanning electronic measurement, spectroscopy, temperature control, pumps, microscopy, liquid handling and facility protocols. Components are listed separately.

The machine-readable catalogue lists 32 servers and 411 tools, all marked simulated. Mass-spectrometry data and worklist tools are not direct device control.

MCP / CLI / VISA / TCP / Serial / Vendor APIs

[Overview](https://github.com/K-Dense-AI/lab-instrument-mcps/blob/main/README.md) · [License](https://github.com/K-Dense-AI/lab-instrument-mcps/blob/main/LICENSE) · [Implementation](https://github.com/K-Dense-AI/lab-instrument-mcps/blob/main/packages/labmcp/src/labmcp/catalog.json)

## LabLink

[techmanual-ai/lablink-mcp](https://github.com/techmanual-ai/lablink-mcp) · Measurement & benches · MIT · Adapter / documentation

Brings several transports into one MCP server so agents can use existing commands and scripts. Device semantics remain primarily in configuration and drivers.

Five connection-driver families and configuration examples are documented; generic connectivity does not imply support for every device.

MCP / VISA/SCPI / SSH / REST / Serial / Python

[Overview](https://github.com/techmanual-ai/lablink-mcp/blob/main/README.md) · [License](https://github.com/techmanual-ai/lablink-mcp/blob/main/LICENSE)

## scpi-mcp

[armchairdeity/mcp-server-scpi](https://github.com/armchairdeity/mcp-server-scpi) · Measurement & benches · MIT · Adapter / documentation

Wraps oscilloscope capture and measurement goals as tools, leaving SCPI details to instrument backends. The first target is the Rigol DS1054Z.

Rigol and mock backends are documented; the README explicitly excludes arbitrary raw SCPI, waveform-generator and logic-analyzer functions.

MCP / PyVISA / SCPI / USB/LAN

[Overview](https://github.com/armchairdeity/mcp-server-scpi/blob/main/README.md) · [License](https://github.com/armchairdeity/mcp-server-scpi/blob/main/LICENSE)

## oscilloscope-mcp

[masahiro-999/oscilloscope-mcp](https://github.com/masahiro-999/oscilloscope-mcp) · Measurement & benches · MIT · Adapter / documentation

Network oscilloscope configuration, triggering, waveform acquisition and measurement feedback, returning structured data, images and standalone waveform views.

The README describes bench operation and FPGA debugging workflows; compatibility remains model-specific.

MCP / SCPI / TCP

[Overview](https://github.com/masahiro-999/oscilloscope-mcp/blob/main/README.md) · [License](https://github.com/masahiro-999/oscilloscope-mcp/blob/main/LICENSE)

## lecroy-mcp

[lucasgerads/lecroy-mcp](https://github.com/lucasgerads/lecroy-mcp) · Measurement & benches · AGPL-3.0 · Maintainer hardware record

LeCroy oscilloscope control and waveform acquisition over LAN VXI-11 or USB.

A running demonstration is included. The documented LAN path requires VXI-11 and explicitly excludes LeCroy VICP.

MCP / SCPI / VXI-11 / USB

[Overview](https://github.com/lucasgerads/lecroy-mcp/blob/main/README.md) · [License](https://github.com/lucasgerads/lecroy-mcp/blob/main/LICENSE)

## siglent-scpi-mcp

[mp911de/siglent-scpi-mcp](https://github.com/mp911de/siglent-scpi-mcp) · Measurement & benches · Apache-2.0 · Maintainer hardware record

Typed tools for Siglent oscilloscopes and supplies, recording the SCPI commands applied.

Maintainers report one SDS1204X HD and SPD3303X-E bench session, including waveform scaling; other listed models are not all hardware-tested.

MCP / SCPI / TCP

[Overview](https://github.com/mp911de/siglent-scpi-mcp/blob/main/README.md) · [License](https://github.com/mp911de/siglent-scpi-mcp/blob/main/LICENSE)

## scope-mcp

[Netlist-Studio/scope-mcp](https://github.com/Netlist-Studio/scope-mcp) · Measurement & benches · MIT · Maintainer hardware record

Configuration, screenshots, waveform download, measurements and serial decoding for Keysight/Agilent oscilloscopes.

README identifies testing on an Agilent MSOX2024A with firmware 02.43.2018020635.

MCP / PyVISA / Ethernet / SCPI

[Overview](https://github.com/Netlist-Studio/scope-mcp/blob/main/README.md) · [License](https://github.com/Netlist-Studio/scope-mcp/blob/main/LICENSE)

## dwf-mcp-server

[KenosInc/dwf-mcp-server](https://github.com/KenosInc/dwf-mcp-server) · Measurement & benches · MIT · Adapter / documentation

Oscilloscope, arbitrary-waveform and logic-analysis interfaces for Digilent WaveForms devices.

The open server depends on separately obtained proprietary libdwf/runtime components; its MIT license does not cover the vendor SDK.

MCP / dwfpy / WaveForms SDK / USB

[Overview](https://github.com/KenosInc/dwf-mcp-server/blob/main/README.md) · [License](https://github.com/KenosInc/dwf-mcp-server/blob/main/LICENSE)

## Instrument MCP

[zeng-andrew/instrument-mcp](https://github.com/zeng-andrew/instrument-mcp) · Measurement & benches · Unspecified · Adapter / documentation

Combines spectrum analyzers, radio testers, supplies, chambers and a logic analyzer using YAML command definitions and multi-instrument sessions.

Lists targets including Keysight MXA/EXA, R&S CMW500 and DSLogic; no license was identified.

MCP / SCPI / Modbus RTU / USB / YAML commands

[Overview](https://github.com/zeng-andrew/instrument-mcp/blob/main/README.md)

## daqmx-mcp

[BrianDavidCouch/daqmx-mcp](https://github.com/BrianDavidCouch/daqmx-mcp) · Measurement & benches · Apache-2.0 · Adapter / documentation

Discovers NI DAQ devices and performs finite analog-voltage and digital-input acquisition.

A community project. The current version has no outputs, continuous acquisition or arbitrary property writes; NI drivers are installed separately.

MCP / Codex plugin / NI nidaqmx

[Overview](https://github.com/BrianDavidCouch/daqmx-mcp/blob/main/README.md) · [License](https://github.com/BrianDavidCouch/daqmx-mcp/blob/main/LICENSE)

## DAQiFi Core

[daqifi/daqifi-core](https://github.com/daqifi/daqifi-core) · Measurement & benches · MIT · Adapter / documentation

Vendor-published wireless DAQ SDK and MCP server covering channels, sampling, digital I/O, PWM, analog outputs and SD-card logging.

The README connects acquisition control to recorded-data retrieval; capabilities depend on the DAQiFi device model.

MCP / .NET API / Wi-Fi / USB

[Overview](https://github.com/daqifi/daqifi-core/blob/main/README.md) · [License](https://github.com/daqifi/daqifi-core/blob/main/LICENSE) · [Implementation](https://github.com/daqifi/daqifi-core/tree/main/src/Daqifi.Mcp)

## LabVIEW MCP Server Toolkit

[JanGoebel/LabVIEW-MCP-Server-Toolkit](https://github.com/JanGoebel/LabVIEW-MCP-Server-Toolkit) · Measurement & benches · MIT · Adapter / documentation

Exposes VIs in existing LabVIEW applications as tools, resources and prompts. A direct way to wrap established laboratory control programs.

The toolkit is open source; LabVIEW itself and instrument VI dependencies have separate licensing.

MCP / HTTP / LabVIEW VIs

[Overview](https://github.com/JanGoebel/LabVIEW-MCP-Server-Toolkit/blob/main/readme.md) · [License](https://github.com/JanGoebel/LabVIEW-MCP-Server-Toolkit/blob/main/LICENSE)

## LabVIEW MCP · Zühlke

[Zuehlke/labview-mcp](https://github.com/Zuehlke/labview-mcp) · Measurement & benches · MIT · Adapter / documentation

Lets agents read, modify and run LabVIEW programs. Primarily a development interface; physical control depends on the invoked VI.

Depends on the internal lvai.LVAI service, which the README identifies as an unpublished NI API without a stability commitment.

MCP / gRPC / LabVIEW scripting

[Overview](https://github.com/Zuehlke/labview-mcp/blob/main/README.md) · [License](https://github.com/Zuehlke/labview-mcp/blob/main/LICENSE)

## OpenFlexure-MCP

[GSIBabu/OpenFlexure-MCP](https://github.com/GSIBabu/OpenFlexure-MCP) · Microscopy & beamlines · GPL-3.0 · Adapter / documentation

Uses the OpenFlexure client for stage motion, capture, autofocus, z-stacks and extension calls.

Targets an OpenFlexure microscope on the local network; the repository does not supply a systematic hardware test matrix.

MCP / OpenFlexure Python client / HTTP

[Overview](https://github.com/GSIBabu/OpenFlexure-MCP/blob/main/README.md) · [License](https://github.com/GSIBabu/OpenFlexure-MCP/blob/main/LICENSE)

## microscope-agent

[BioNanomics/microscope-agent](https://github.com/BioNanomics/microscope-agent) · Microscopy & beamlines · MIT · Adapter / documentation

A compact interface for Nikon Ti2-E and a Baumer camera: position reads, XY motion and imaging, linking frames to actual stage position and revision counters.

SDK and mock paths return image previews and full files. Absolute Z motion is deliberately absent from the exposed tools.

MCP / Nikon SDK / GenICam camera

[Overview](https://github.com/BioNanomics/microscope-agent/blob/main/README.md) · [License](https://github.com/BioNanomics/microscope-agent/blob/main/LICENSE)

## Agent-Lens

[aicell-lab/agent-lens](https://github.com/aicell-lab/agent-lens) · Microscopy & beamlines · MIT · Adapter / documentation

Combines microscope control, robotic sample transfer, segmentation, similarity search and OME-Zarr data handling.

Public service-registration code and a live-demo entry point; device calls primarily use Hypha services. Native MCP is not recorded as verified.

Hypha RPC / Python / Web UI / BioEngine

[Overview](https://github.com/aicell-lab/agent-lens/blob/main/README.md) · [License](https://github.com/aicell-lab/agent-lens/blob/main/LICENSE) · [Implementation](https://github.com/aicell-lab/agent-lens/blob/main/agent_lens/register_tools_service.py)

## Agentic microscope

[kyu-softmatter/agentic-microscope](https://github.com/kyu-softmatter/agentic-microscope) · Microscopy & beamlines · MIT · Adapter / documentation

Translates research goals into microscope configurations grounded in hardware limits and calibrations, spanning microscopy, optical tweezers and piezo stages.

Configuration, application and readback code reviewed. The README distinguishes tweezers command acceptance from physical completion and announces migration to soft-matter-agents.

MCP / Python / Micro-Manager / Vendor SDK/TCP

[Overview](https://github.com/kyu-softmatter/agentic-microscope/blob/main/README.md) · [License](https://github.com/kyu-softmatter/agentic-microscope/blob/main/LICENSE) · [Implementation](https://github.com/kyu-softmatter/agentic-microscope/blob/main/hardware/microscope.py)

## soft-matter-agents

[kyu-softmatter/soft-matter-agents](https://github.com/kyu-softmatter/soft-matter-agents) · Microscopy & beamlines · MIT · Adapter / documentation

Combines microscope, simulation, literature and bridge agents; the microscope module is the successor location for Agentic microscope.

Included as a migration target; not every module operates physical devices. Inspect microscope_agent for hardware capabilities.

Python / Microscope agent / Agent workflows

[Overview](https://github.com/kyu-softmatter/soft-matter-agents/blob/main/README.md) · [License](https://github.com/kyu-softmatter/soft-matter-agents/blob/main/LICENSE)

## AILA

[M3RG-IITD/AILA](https://github.com/M3RG-IITD/AILA) · Microscopy & beamlines · MIT · Published experiment

A language-model assistant for atomic-force-microscope experiments, combining task decomposition, tools and feedback.

The Nature Communications paper reports physical AFM experiments. Code and benchmarks are public; reuse requires a matching instrument-control environment.

Python tools / LLM agents / Instrument control software

[Overview](https://github.com/M3RG-IITD/AILA/blob/main/README.md) · [License](https://github.com/M3RG-IITD/AILA/blob/main/LICENSE.md) · [Paper](https://www.nature.com/articles/s41467-025-64105-7)

## LLM-directed-SPM

[DIAOZHUO/LLM-directed-SPM](https://github.com/DIAOZHUO/LLM-directed-SPM) · Microscopy & beamlines · Unspecified · Published experiment

Command generation, knowledge retrieval and specialized small models for scanning-probe experiments, with local model services and training material.

The paper describes physical scanning-probe experiments. No top-level license was identified; model-training code and complete device integration should be assessed separately.

Python / WebSocket / Small language models / spmutil

[Overview](https://github.com/DIAOZHUO/LLM-directed-SPM/blob/main/readme.md) · [Paper](https://arxiv.org/abs/2602.20669)

## Quailbot Pi

[BB-84C/quailbot-pi](https://github.com/BB-84C/quailbot-pi) · Microscopy & beamlines · ISC · Adapter / documentation

Turns instrument workspaces into a fixed tool surface for parameters, actions, image readbacks and multi-step programs. Actions and subsequent observations are recorded separately; Nanonis uses an external nqctl driver.

Public Pi extension and workspace contract. The STM paper supplies related experimental context, not evidence that this extension includes every hardware driver.

Pi extension / CLI driver contract / Workspace JSON / Image readback

[Overview](https://github.com/BB-84C/quailbot-pi/blob/main/README.md) · [License](https://github.com/BB-84C/quailbot-pi/blob/main/LICENSE) · [Paper](https://arxiv.org/abs/2609.27302)

## VISION

[CFN-softbio/VISION](https://github.com/CFN-softbio/VISION) · Microscopy & beamlines · Unspecified · Published experiment

Translates spoken or written requests into beamline-operation code, with modules for transcription, classification, programming and analysis.

The project shows deployment at NSLS-II 11-BM CMS, executing after user confirmation. It is not a universal unattended instrument protocol; no license was identified.

Voice/text / Python code generation / Bluesky workstation

[Overview](https://github.com/CFN-softbio/VISION/blob/main/README.md) · [Paper](https://doi.org/10.1088/2632-2153/add9e4)

## LeeQ

[ShuxiangCao/LeeQ](https://github.com/ShuxiangCao/LeeQ) · Quantum experiments · BSD-3-Clause · Published experiment

Pulse experiments, sweeps, calibration state and analysis for superconducting devices, with experiment descriptions and text/visual inspection hooks for agents.

The k-agents paper reports quantum-calibration experiments. The repository also offers simulation, so experimental provenance depends on the backend.

Python experiment API / Pulse control / k-agents integration

[Overview](https://github.com/ShuxiangCao/LeeQ/blob/main/README.md) · [License](https://github.com/ShuxiangCao/LeeQ/blob/main/LICENSE) · [Paper](https://doi.org/10.1016/j.patter.2025.101372)

## k-agents

[EvoEvolver/k_agents](https://github.com/EvoEvolver/k_agents) · Quantum experiments · Unspecified · Published experiment

Discovers, executes and evaluates calibration experiments through existing experiment libraries, retaining experimental knowledge and visual results.

The paper reports physical quantum calibration. The README now points to NVIDIA’s Quantum Calibration Agent Blueprint; no license was identified in this repository.

Python / Experiment agents / LeeQ

[Overview](https://github.com/EvoEvolver/k_agents/blob/main/README.md) · [Paper](https://arxiv.org/abs/2412.07978)

## Quantum Calibration Agent Blueprint

[NVIDIA/Quantum-Calibration-Agent-Blueprint](https://github.com/NVIDIA/Quantum-Calibration-Agent-Blueprint) · Quantum experiments · Apache-2.0 · Adapter / documentation

A quantum-device calibration agent reference implementation with experiment discovery, execution, visual analysis, workflows and result storage.

An NVIDIA Apache-2.0 project; experiments integrate through supplied Python scripts. The reference interface does not imply support for every quantum controller.

Python experiment scripts / CLI / Web UI / HDF5 / SQLite

[Overview](https://github.com/NVIDIA/Quantum-Calibration-Agent-Blueprint/blob/main/README.md) · [License](https://github.com/NVIDIA/Quantum-Calibration-Agent-Blueprint/blob/main/LICENSE)

## CALMS

[mcherukara/CALMS](https://github.com/mcherukara/CALMS) · Microscopy & beamlines · BSD-3-Clause · Maintainer hardware record

A context- and tool-augmented facility assistant integrating instrument knowledge with operational functions.

An earlier public implementation with a demonstration and a three-clause BSD license. Later robot and beamline work appears in the APS repository.

Python tools / Retrieval / Instrument commands

[Overview](https://github.com/mcherukara/CALMS/blob/main/README.md) · [License](https://github.com/mcherukara/CALMS/blob/main/LICENSE)

## CALMS · APS experimental agents

[AdvancedPhotonSource/CALMS](https://github.com/AdvancedPhotonSource/CALMS) · Microscopy & beamlines · Unspecified · Published experiment

Teachable experiment-agent workflows for a North N9 robotic station and an X-ray nanoprobe.

README names robot and nanoprobe command modules and demonstration videos; no license was identified. Sources use the repository’s current default branch.

Python / Robot command functions / Beamline tools

[Overview](https://github.com/AdvancedPhotonSource/CALMS/blob/main/README.md) · [Paper](https://doi.org/10.1038/s41524-026-02005-0)

## Opentrons MCP

[yerbymatey/opentrons-mcp](https://github.com/yerbymatey/opentrons-mcp) · Chemistry & liquid handling · MIT · Adapter / documentation

Combines API-documentation search with protocol upload, run management, homing and status access for OT-2/Flex.

Device calls use the robot HTTP API; documentation queries and physical-action tools are distinct.

MCP / Opentrons HTTP API

[Overview](https://github.com/yerbymatey/opentrons-mcp/blob/main/README.md) · [License](https://github.com/yerbymatey/opentrons-mcp/blob/main/LICENSE)

## plr-mcp

[di-omics/plr-mcp](https://github.com/di-omics/plr-mcp) · Chemistry & liquid handling · MIT · Simulation-verified

Exposes liquid handling, plate reading, thermocycling and heater-shaker operations through MCP using PyLabRobot backends.

End-to-end checks use the chatterbox simulator by default. A real STAR backend and bring-up guide are provided, separately from simulation verification.

MCP / PyLabRobot

[Overview](https://github.com/di-omics/plr-mcp/blob/main/README.md) · [License](https://github.com/di-omics/plr-mcp/blob/main/LICENSE)

## OpenLabAI

[nygmeta/OpenLabAI](https://github.com/nygmeta/OpenLabAI) · Chemistry & liquid handling · MIT · Maintainer hardware record

Natural-language liquid-handling workflows spanning Opentrons, Biomek, Hamilton and experiment-record integrations.

Maintainers report physical OT-2 reads, status, homing and protocol generation; upload/start execution tools have not yet run on hardware. Hamilton and benchtop layers remain simulated.

MCP / Opentrons HTTP / Biomek COM / PyLabRobot

[Overview](https://github.com/nygmeta/OpenLabAI/blob/main/README.md) · [License](https://github.com/nygmeta/OpenLabAI/blob/main/LICENSE)

## LabscriptAI OT

[KRATSZ/labscriptai-ot](https://github.com/KRATSZ/labscriptai-ot) · Chemistry & liquid handling · LabscriptAI Research Citation License v1.0 · Adapter / documentation

An Opentrons agent plugin combining protocol authoring, simulation, skills and live-runtime assistance.

Currently uses the LabscriptAI Research Citation License, requiring separate permission for commercial use; listed outside the standard open-source-license group.

MCP / Agent Skills / Opentrons / Local simulation

[Overview](https://github.com/KRATSZ/labscriptai-ot/blob/main/README.md) · [License](https://github.com/KRATSZ/labscriptai-ot/blob/main/LICENSE) · [Paper](https://doi.org/10.1101/2025.09.30.679666)

## Coscientist

[gomesgroup/coscientist](https://github.com/gomesgroup/coscientist) · Chemistry & liquid handling · Apache-2.0 + Commons Clause · Published experiment

A language model coordinates literature, code and experimental tools for chemical research; an important early physical-experiment case study.

The paper reports robotic chemistry. Public code is not the complete deployable laboratory from the paper. License: Apache-2.0 with Commons Clause.

Python tools / Opentrons / Laboratory APIs

[Overview](https://github.com/gomesgroup/coscientist/blob/main/README.md) · [License](https://github.com/gomesgroup/coscientist/blob/main/LICENSE) · [Paper](https://doi.org/10.1038/s41586-023-06792-0)

## ChemAgents

[pic-ai-robotic-chemistry/ChemAgents](https://github.com/pic-ai-robotic-chemistry/ChemAgents) · Chemistry & liquid handling · Unspecified · Published experiment

A multi-agent chemical-research system connecting experimental protocols, a robotic workcell and experiment data.

The repository provides paper code and experimental data, linking robot instructions and AGV drivers separately; no license was identified here.

LangGraph tools / Robot instruction set / ROS drivers

[Overview](https://github.com/pic-ai-robotic-chemistry/ChemAgents/blob/main/README.md) · [Paper](https://doi.org/10.1021/jacs.4c17738)

## ORGANA

[ac-rad/organa](https://github.com/ac-rad/organa) · Chemistry & liquid handling · Unspecified · Published experiment

A chemistry robot assistant combines user goals, scene perception and experiment progress to organize multi-step experiments and reporting.

The project and paper demonstrate physical robot experiments; repository contents and the external deployment environment are distinct. No license was identified.

Task planning / Robot perception / Laboratory operations

[Overview](https://github.com/ac-rad/organa/blob/main/README.md) · [Paper](https://arxiv.org/abs/2401.06949)

## CLAIRify

[ac-rad/xdl-generation](https://github.com/ac-rad/xdl-generation) · Chemistry & liquid handling · MIT · Published experiment

Translates natural-language experiment steps into verifiable XDL procedures, feeding verification errors back to the model for revision.

The paper includes robot execution; this repository mainly releases the generator and data. The README directs users to develop for updated API compatibility.

Natural language to XDL / Verifier loop / Python

[Overview](https://github.com/ac-rad/xdl-generation/blob/master/README.md) · [License](https://github.com/ac-rad/xdl-generation/blob/master/LICENSE) · [Paper](https://arxiv.org/abs/2303.14100)

## CLAIRify-Chemspeed

[ac-rad/clairify-chemspeed](https://github.com/ac-rad/clairify-chemspeed) · Chemistry & liquid handling · Unspecified · Adapter / documentation

Generates Chemspyd programs from natural language, connecting protocol generation to Chemspeed automation.

An interface example linked by the Chemspyd paper; no license was identified for this repository.

Python generation / Chemspyd / Chemspeed

[Overview](https://github.com/ac-rad/clairify-chemspeed/blob/master/README.md) · [Paper](https://doi.org/10.1039/D4DD00046C)

## SynAgent · thin-film synthesis

[izumitkhr/synagent](https://github.com/izumitkhr/synagent) · Chemistry & liquid handling · MIT · Published experiment

Multimodal planning and hypothesis testing in a thin-film synthesis loop, reading XRD/SEM data and writing conditions for the next experiment.

The paper reports 18 physical experiments. Public code connects to dLab through MaiML input and output.txt, without packaging the complete deposition, transport and measurement stack.

Python iteration runner / MaiML / File-based platform interface / Generated skills

[Overview](https://github.com/izumitkhr/synagent/blob/main/README.md) · [License](https://github.com/izumitkhr/synagent/blob/main/LICENSE) · [Paper](https://arxiv.org/abs/2609.18598)

## AutoLabs

[pnnl/autolabs](https://github.com/pnnl/autolabs) · Chemistry & liquid handling · BSD-2-Clause · Supporting code / material

Generates experiment steps and Lab Step Representation, supporting multi-agent revision and experiment-design evaluation.

The public application emphasizes design, simulation and evaluation; physical experiments in the paper do not make this repository a complete hardware runtime.

Python / LSR export / Agent planning

[Overview](https://github.com/pnnl/autolabs/blob/master/README.md) · [License](https://github.com/pnnl/autolabs/blob/master/LICENSE.md) · [Paper](https://arxiv.org/abs/2509.25651)

## opcua-mcp · kukapay

[kukapay/opcua-mcp](https://github.com/kukapay/opcua-mcp) · Industry & facilities · MIT · Adapter / documentation

Connects OPC UA browsing and single-node or batch reads/writes to agents while retaining existing industrial servers.

An OPC UA-to-MCP adapter; physical meaning depends on the server address space and information model.

MCP / OPC UA

[Overview](https://github.com/kukapay/opcua-mcp/blob/main/README.md) · [License](https://github.com/kukapay/opcua-mcp/blob/main/LICENSE)

## OPC UA MCP · IndustriAgents

[IndustriAgents/OPCUA-MCP](https://github.com/IndustriAgents/OPCUA-MCP) · Industry & facilities · MIT · Adapter / documentation

Browsing, reads, history, subscriptions, alarms and configured writes/method calls, with one local process per OPC UA endpoint.

The current README includes writes but defaults to read-only operation; shared remote multi-client deployment has separate design constraints.

MCP / OPC UA / Subscriptions / History

[Overview](https://github.com/IndustriAgents/OPCUA-MCP/blob/main/README.md) · [License](https://github.com/IndustriAgents/OPCUA-MCP/blob/main/LICENSE)

## modbus-mcp

[kukapay/modbus-mcp](https://github.com/kukapay/modbus-mcp) · Industry & facilities · MIT · Adapter / documentation

Exposes register and coil reads/writes, providing a low-level route to existing PLCs, sensors and controllers.

Communication calls are exposed; units, scaling, modes and side effects still require a device-specific register map.

MCP / Modbus TCP/UDP/Serial

[Overview](https://github.com/kukapay/modbus-mcp/blob/main/README.md) · [License](https://github.com/kukapay/modbus-mcp/blob/main/LICENSE)

## TANGO MCP

[abogani/tango-mcp](https://github.com/abogani/tango-mcp) · Industry & facilities · Apache-2.0 · Adapter / documentation

Discovers devices through a TANGO database and maps attributes, state and commands to MCP resources and tools, including bulk reads.

Provides TANGO_HOST deployment and attribute/command paths; available operations depend on the facility’s existing device servers.

MCP / PyTango / Streamable HTTP

[Overview](https://github.com/abogani/tango-mcp/blob/main/README.md) · [License](https://github.com/abogani/tango-mcp/blob/main/LICENSE)

## MCP Server for EPICS

[sryu81/mcp-server-for-epics](https://github.com/sryu81/mcp-server-for-epics) · Industry & facilities · Unspecified · Adapter / documentation

Offers standalone-process and IOC-embedded entry points exposing EPICS PVs and control commands to agents.

C++ shared-library and protocol-dispatch structure is public; no license was identified.

MCP / EPICS CA/PVA / IOC / stdio/HTTP

[Overview](https://github.com/sryu81/mcp-server-for-epics/blob/main/README.md)

## MCP2Serial

[mcp2everything/mcp2serial](https://github.com/mcp2everything/mcp2serial) · Embedded & debugging · MIT · Adapter / documentation

Connects microcontrollers to agents through serial communication, useful as a basic bridge for custom instruments.

The README provides Pico integration workflows; serial transport alone does not define units, device state or completion conditions.

MCP / Serial / Raspberry Pi Pico

[Overview](https://github.com/mcp2everything/mcp2serial/blob/main/README.md) · [License](https://github.com/mcp2everything/mcp2serial/blob/main/LICENSE)

## tinymcp

[golioth/tinymcp](https://github.com/golioth/tinymcp) · Embedded & debugging · Apache-2.0 · Adapter / documentation

Exposes Golioth device RPCs as MCP tools; existing devices can publish tool schemas through the state service.

Includes a Zephyr LED-control example. Server code is open source, while operation depends on the Golioth platform.

MCP / Golioth management API / Device RPC

[Overview](https://github.com/golioth/tinymcp/blob/main/README.md) · [License](https://github.com/golioth/tinymcp/blob/main/LICENSE)

## Embedded Debugger MCP

[Adancurusul/embedded-debugger-mcp](https://github.com/Adancurusul/embedded-debugger-mcp) · Embedded & debugging · MIT · Maintainer hardware record

Connects agents to debug probes for target control, memory access, breakpoints, flashing and fault inspection, supplying physical feedback during instrument-firmware development.

Maintainers report validation on a physical ESP32-S3; native probe-rs and OpenOCD backends are configured separately.

MCP / CLI / Agent Skills / probe-rs / OpenOCD/GDB

[Overview](https://github.com/Adancurusul/embedded-debugger-mcp/blob/main/README.md) · [License](https://github.com/Adancurusul/embedded-debugger-mcp/blob/main/LICENSE)

## Saleae Logic 2 MCP

[hsoffar/saleae-logic2-mcp](https://github.com/hsoffar/saleae-logic2-mcp) · Embedded & debugging · Apache-2.0 · Adapter / documentation

Logic-analyzer capture, protocol decoding, timing measurement and export for firmware and physical-bus debugging.

Requires Saleae Logic 2 with automation enabled; the application and hardware are not supplied by the open server.

MCP / Logic 2 automation API

[Overview](https://github.com/hsoffar/saleae-logic2-mcp/blob/main/README.md) · [License](https://github.com/hsoffar/saleae-logic2-mcp/blob/main/LICENSE)

## MicroPython MCP Bridge

[SWITCHSCIENCE/mcp-micropython-bridge](https://github.com/SWITCHSCIENCE/mcp-micropython-bridge) · Embedded & debugging · Unspecified · Adapter / documentation

Operates ESP32/RP2040-class boards through serial or WebREPL, using device-side helper modules and HARDWARE.md for board-specific knowledge.

Provides a hardware-test CLI and firmware setup instructions; no top-level license was identified.

MCP / USB Serial / WebREPL / MicroPython

[Overview](https://github.com/SWITCHSCIENCE/mcp-micropython-bridge/blob/main/README.md)

## ROS MCP Server

[robotmcp/ros-mcp-server](https://github.com/robotmcp/ros-mcp-server) · Robotics · Apache-2.0 · Maintainer hardware record

Uses rosbridge to discover topics, services, actions and message types, publish control messages and read robot-sensor feedback.

Robot demonstrations are included. The bridge covers ROS communication; motion capabilities and controllers remain in the robot stack.

MCP / rosbridge / ROS 1 / ROS 2

[Overview](https://github.com/robotmcp/ros-mcp-server/blob/main/README.md) · [License](https://github.com/robotmcp/ros-mcp-server/blob/main/LICENSE)

## ROSA

[nasa-jpl/rosa](https://github.com/nasa-jpl/rosa) · Robotics · Apache-2.0 · Published experiment

JPL’s natural-language ROS assistant combines system diagnostics, state queries and extensible robot-operation tools.

The paper and examples cover robotic applications. ROSA is an agent/tool framework; native MCP is not inferred from its purpose.

LangChain tools / ROS 1 / ROS 2

[Overview](https://github.com/nasa-jpl/rosa/blob/main/README.md) · [License](https://github.com/nasa-jpl/rosa/blob/main/LICENSE) · [Paper](https://arxiv.org/abs/2410.06472)

## device-use

[labclaw/device-use](https://github.com/labclaw/device-use) · GUI & operating knowledge · Apache-2.0 · Adapter / documentation

Wraps instrument software through screen observation, planning and mouse/keyboard actions with device profiles. Relevant when an API is unavailable.

Public implementation includes NMR-data and plate-reader modules. MCP tools do not establish physical-control validation for every named commercial instrument.

Python / GUI automation / MCP / VLM backends

[Overview](https://github.com/labclaw/device-use/blob/main/README.md) · [License](https://github.com/labclaw/device-use/blob/main/LICENSE) · [Implementation](https://github.com/labclaw/device-use/blob/main/src/device_use/integrations/mcp_server.py)

## device-skills

[labclaw/device-skills](https://github.com/labclaw/device-skills) · GUI & operating knowledge · Apache-2.0 · Supporting code / material

Instrument operating knowledge and skill material accompanying device-use execution interfaces.

Skills contain knowledge and operating instructions; listed as supporting material rather than device drivers or an independently validated hardware system.

Agent Skills / Device operating knowledge

[Overview](https://github.com/labclaw/device-skills/blob/main/README.md) · [License](https://github.com/labclaw/device-skills/blob/main/LICENSE)

## edge-mhs

[fastly/edge-mhs](https://github.com/fastly/edge-mhs) · Device protocols · Apache-2.0 · Simulation-verified

An edge gateway between agents and device services for identity, parameter constraints, quotas and audit records.

The README identifies a reference implementation with mock backends, not an official Anthropic MHS server.

MCP gateway / Fastly Compute

[Overview](https://github.com/fastly/edge-mhs/blob/main/README.md) · [License](https://github.com/fastly/edge-mhs/blob/main/LICENSE)

## Agent2Device Protocol

[neogyk/Agent2Device-Protocol](https://github.com/neogyk/Agent2Device-Protocol) · Device protocols · MIT · Concept / proposal

A protocol concept for connecting agents to laboratory devices.

The reviewed tree contains only README, LICENSE and an ignore file, with no protocol implementation or device driver.

Design notes

[Overview](https://github.com/neogyk/Agent2Device-Protocol/blob/main/README.md) · [License](https://github.com/neogyk/Agent2Device-Protocol/blob/main/LICENSE)

## ChemCrow public release

[ur-whitelab/chemcrow-public](https://github.com/ur-whitelab/chemcrow-public) · Chemistry & liquid handling · MIT · Supporting code / material

An important chemistry tool-augmented agent case for understanding orchestration and experimental-service boundaries.

The paper includes experimental execution, but the README explicitly says API restrictions exclude some paper tools from the public package.

Python / LangChain tools

[Overview](https://github.com/ur-whitelab/chemcrow-public/blob/main/README.md) · [License](https://github.com/ur-whitelab/chemcrow-public/blob/main/LICENSE) · [Paper](https://doi.org/10.1038/s42256-024-00832-8)

## NV autonomous experiments

[takuyaisogawa/nv-autonomous-experiments](https://github.com/takuyaisogawa/nv-autonomous-experiments) · Quantum experiments · MIT code / CC BY-4.0 artifacts · Supporting code / material

Public case studies, analysis code and experimental artifacts for autonomous NV-center experiments.

Release and license notes explicitly omit the live-laboratory backend. Useful for experimental trajectories, not a complete NV-device control release.

Python / MATLAB / Case-study artifacts

[Overview](https://github.com/takuyaisogawa/nv-autonomous-experiments/blob/main/README.md) · [License](https://github.com/takuyaisogawa/nv-autonomous-experiments/blob/main/LICENSE) · [Paper](https://arxiv.org/abs/2607.25145)

## UC2 LLM microscopy workshop

[openUC2/Hackathon-UC2-LLM](https://github.com/openUC2/Hackathon-UC2-LLM) · Microscopy & beamlines · Unspecified · Supporting code / material

A teaching entry point for physical UC2 microscopes and the ImSwitch API, covering hardware, access and experimental challenges.

Workshop and example material rather than a complete independent agent platform; no license was identified.

ImSwitch FastAPI / Python

[Overview](https://github.com/openUC2/Hackathon-UC2-LLM/blob/main/README.md)

