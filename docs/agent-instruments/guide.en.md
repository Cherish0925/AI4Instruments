# Agents and physical instruments

AI4Instruments · Protocols, interfaces and open projects · 2026-10-20

## 01 · What to build

The useful common foundation lets different agents discover devices, understand capabilities, submit experiments, observe physical outcomes and use that experience in subsequent decisions. Its value is transferable experimental capability: what survives a change of model, instrument or laboratory, and what must be established again?

Existing projects demonstrate several integration routes: MCP wrappers over drivers, CLIs controlling local runtimes, plans submitted to established control systems, GUI operation of instrument software, and robots manipulating laboratory apparatus. These routes can coexist. Describing capabilities already available in a laboratory is often more useful than rebuilding its device access.

The central design problem is connecting requests to physical facts. A server receiving a command, a device accepting a setting, execution ending and an experimental objective being achieved are distinct events. Successful transport establishes only part of that chain.

## 02 · Names and status

| Name | What the available material establishes | Useful contribution |
| --- | --- | --- |
| **MHS** | Anthropic’s Model Hardware Standard is presented as a research preview with an application entry point; the announcement places open sourcing in a later phase. | Common drivers, discovery, physical descriptions and MCP / CLI / API access. |
| **AIP** | The Agent–Instrument Protocol PRD v1.1 supplied for this discussion; a corresponding public implementation has not been verified. | Persistent execution, typed quantities and activities, class profiles, observation provenance, resource relationships and recovery. |
| **OpenMHP** | Independent public specification and code; its supported-device packages are currently primarily twin-tested. | A compact tool surface, on-demand descriptions, actions, jobs, leases, method packages and run records. |
| **Several Open-MHS projects** | Community projects maintained by different authors. Inspiration does not establish official status or verified compatibility. | Compare each device model, adapter and hardware record separately. |
| **LAP** | A Lab Agent Protocol design paper, explicitly without normative or implemented status. | Combining InstrumentCard, reservations, tasks and measurement results. |
| **MCP** | A general agent/tool protocol with public SDKs and a Tasks extension. | Discovery, structured arguments, resources, capability negotiation and asynchronous results. |

[MHS announcement](https://www.anthropic.com/news/model-hardware-standard-research-preview) · [MHS website](https://modelhardwarestandard.com/) · [OpenMHP specification](https://github.com/kushalsinha/openmhp/blob/main/SPEC.md) · [LAP paper](https://arxiv.org/html/2606.03755v1) · [MCP Tasks](https://tasks.extensions.modelcontextprotocol.io/)

Acronyms do not establish institutional affiliation. The two MHP projects here are maintained by kushalsinha and Cuntinum. AIP is also used by unrelated identity, communication and workflow projects. Catalogue entries identify authors and full repository addresses.

MCP schemas can represent units, ranges and device-specific fields, and asynchronous tasks already have an extension. Instrument integration needs agreed meanings, device-side implementations and verifiable behavior. Adding fields alone is insufficient, as is changing transport alone.

## 03 · Responsibilities along the integration path

| Layer | Responsibility | Existing material |
| --- | --- | --- |
| **Research and reasoning** | Objectives, experiment selection, interpretation and program generation. | Coscientist, AILA, SynAgent, quantum calibration agents. |
| **Agent access** | Discovery, invocation, knowledge access and result delivery. | MCP, CLI, Python APIs, Skills. |
| **Instrument contract** | Capabilities, units, modes, state, physical outcomes, jobs and resources. | AIP design, OpenMHP, public MHS material, SiLA 2, LADS, WoT. |
| **Execution and orchestration** | Connection ownership, long experiments, coordination and records. | QCoDeS/Jupyter, Bluesky, Osprey, PUDA, Uni-Lab-OS, IvoryOS. |
| **Device access** | Actual calls and model/firmware differences. | SCPI/VISA, EPICS, TANGO, ROS, vendor SDKs, serial, GUI. |
| **Physical apparatus** | Motion, excitation, acquisition, triggers and physical feedback. | Instruments, controllers, sensors, samples and connections. |

Organize knowledge, control and data separately. Manuals and skills explain operation; the control interface submits work and reports state; large waveforms, images and datasets travel through files or data services, entering agent context through references and summaries. Sampling, throughput and deployment determine the data channel; Arrow Flight is not required for every instrument.

Hard real-time triggers, servos and acquisition timing belong in instruments, FPGAs or local control programs. Agents select objectives and procedures, checking feedback at meaningful points. The MHS announcement’s example of turning exploratory laser alignment into a deterministic program illustrates this division.

## 04 · Where to start reading

| Existing environment or question | Read first | Contract work that remains |
| --- | --- | --- |
| QCoDeS instruments and Jupyter measurements | instrMCP; AIP design | Fresh versus cached values, durable jobs and shared-resource boundaries. |
| Portable device descriptions and operations | OpenMHP; the Open-MHS projects; WoT; SiLA 2; LADS | Required class capabilities, optional features and version compatibility. |
| Facilities using EPICS / TANGO / DOOCS | Osprey; TANGO MCP; EPICS MCP; VISION | Channel semantics, facility context, plan execution and records. |
| Multi-device experiments and edge execution | PUDA; Uni-Lab-OS; IvoryOS | Topology, contention, sample movement and job recovery. |
| Scopes, DAQ, supplies and embedded development | LabLink; scope-mcp; Siglent MCP; DAQiFi; Embedded Debugger | Waveform scaling, triggers, timing, configuration and firmware. |
| Microscopy, optomechanics and visual feedback | OpenFlexure-MCP; microscope-agent; Agentic microscope; EAA family | Image/position linkage, exposure, calibration and physical readback. |
| Liquid handling and chemistry robots | Opentrons MCP; plr-mcp; OpenLabAI; ChemAgents | Deck/sample identity, units, consumables and recovery boundaries. |
| Quantum and scanning-probe experiments | LeeQ; NVIDIA QCA; Quailbot Pi; AILA | Calibration state, experiment knowledge, feedback assessment and external drivers. |
| GUI-only software | device-use; vendor automation interfaces | UI versions, post-action verification and data provenance; check for an existing SDK first. |

Open licensing, hardware validation and deployability are independent dimensions. A permissively licensed project may have only simulator tests; an experimental paper may release only planning or analysis code. Coscientist’s Commons Clause, LabscriptAI’s commercial-use restriction and Uni-Lab-OS’s framework/driver license split affect reuse. License and experimental-status filters are therefore separate.

Assess ecosystem standing through independent adoption, tested device models, manufacturer-maintained adapters, versioned contracts and interoperability tests. Stars, names and a demonstration cannot substitute for these. MHS’s institutional collaborations are relevant, but the public material does not establish that one instrument protocol has already become a globally unified standard.

## 05 · A minimal useful contract

These are design recommendations for AI4Instruments. The accompanying JSON is an illustrative draft.

| Object | Information to retain | Practical purpose |
| --- | --- | --- |
| **Device / capability** | Stable identity, model, driver/firmware, capability revision, controllable and observable quantities. | Discover what can be done and recognize version changes. |
| **Quantity / observation** | Value, unit, time, provenance and validity; calibration and uncertainty where relevant. | Distinguish setpoints, measurements, caches and derived values; never replace unknown with zero. |
| **Operation** | Arguments, preconditions, expected effects, repeatability and actual readback. | Resolve uncertain physical outcomes after communication failures. |
| **Job / activity** | Durable identity, state, progress, cancellation semantics, termination reason and result references. | Track experiments beyond a conversation; distinguish requested cancellation from an actual stop. |
| **Resource** | Shared physical object, ownership scope, exclusions and conflict handling. | Express whether channels can operate concurrently, beyond a single global lock. |
| **Event / record** | Ordered sequence, time, causality, run and device identities. | Reconstruct events after reconnection, including manual interventions. |
| **Artifact / dataset** | Reference, format, integrity information, axes/units, acquisition configuration and provenance. | Keep bulk data outside text responses and trace analysis to raw acquisition. |

A device-class profile should require only genuinely interchangeable core capabilities. Optional capabilities and namespaces express everything else. Two supplies that set voltage may differ in ramps, triggers, protection states and readback speed. Generality rests on an explicit shared subset.

AIP’s richer state and activity model is instructive, but its implementation cost belongs in each driver: which states are readable, which are only tracked, and which cannot be determined? A common interface should preserve those differences instead of implying identical observability.

A task identifier in process memory does not establish durability. Specify who owns the connection after process exit, how records persist and how restart reconciles with actual device state. An MCP task, a runtime job and an instrument’s internal program can be mapped, but do not inherently share a lifecycle.

## 06 · Three concrete experiments

### Optical alignment: link observation to action

**Basic Operations** read optical power, capture camera frames and move mirrors or stages, returning units, positions and timestamps. **Standard Operations** move within a defined range, wait for settling, sample and fit. **Workflow Operations** calibrate coordinates, find a peak, track drift, preserve optical-layout revisions and compare runs.

The agent submits an objective and procedure parameters; a local program controls scan timing. Each power measurement must correspond to the actual position at acquisition. If motion produces only an acknowledgement without position confirmation, preserve “accepted, position unconfirmed.” LabMCP’s power-meter component offers an interface reference; its simulated status is not hardware validation.

### Long scans: preserve experimental identity across disconnection

The agent submits a plan and receives a job ID from a persistent execution layer that owns connections and data writing. A reconnected interface uses that ID to retrieve events and results. If the scan stops at point 47, retain the first 46 points, the actual completion state of the current point and the termination reason. Partial data is not a complete scan.

Communication timeout, execution failure and an unmet scientific objective need separate meanings. When an action was sent but its response was lost, inspect state and events before choosing another action. Network retry policy must not decide whether to repeat a physical operation.

### Liquid handling: samples are resources

Moving from a protocol to robot actions requires explicit liquids, wells, containers, tips, volumes and units. Simulation can check syntax and paths before execution; real liquid properties, aspiration height and residual volume remain experimental conditions.

If a dispense response is lost, another call may add liquid twice. Reconcile through the robot run, events and completed steps. HTTP retries alone cannot make such operations reliable.

## 07 · Turn the research into reusable engineering

Start with a small experiment with clear physical readback, reuse existing drivers and describe its Basic Operations completely. Package useful procedures as readable, executable Standard Operations, then compose Workflow Operations. Preserve implementations and data so new research can change the procedure instead of relying only on a fixed black box.

| Stage | Deliverable | Evidence of completion |
| --- | --- | --- |
| **Device contract** | Capabilities, quantities, observations, outcomes and version rules. | Two device models share a core profile while optional features accurately preserve differences. |
| **Execution service** | Connection ownership, long jobs, events and dataset references. | Actual state remains explainable after session loss, process restart or device rejection. |
| **Procedure reuse** | Readable plans, replaceable algorithms and configuration/data snapshots. | Different agent entry points execute the same procedure while retaining consistent raw records. |
| **Ecosystem collaboration** | Driver templates, profile registration, contribution rules and compatibility tests. | Independent laboratories integrate from documentation and contribute device/firmware-specific reproduction records. |

Retain failed, unknown and partially completed trajectories. They reveal missing hardware readbacks, controller changes and procedures worth improving. This connects Instruments4AI integration back to AI4Instruments instrument design and continued development.

## 08 · Read and maintain the collection

Read the naming and responsibility maps first, then filter by existing equipment. Inspect interfaces, the physical path, experimental status, license and implementation entry points. Compare the missing mappings to the laboratory’s current runtime. There is no need to fork every project: retain upstream links, creating a branch or fork when making an actual contribution.

Project records and protocol/component context live in `catalogue.json` and `context.json`. Both HTML files embed those same datasets. `sources.json` indexes sources; `catalogue.schema.json` defines the fields; `build.py` uses the Python standard library to rebuild both languages, catalogues and indexes. Download either HTML file for offline search; primary materials remain accessible through source links.

Review date: 2026-10-20. Sources include public repositories, official documentation, papers and selected implementation paths. Physical-validation status cites author or maintainer records. Components and forks are not counted as independent projects. Future changes should record the specific new evidence and status transitions so the collection remains traceable.
