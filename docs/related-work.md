# Related work

AI4Instruments connects three established lines of work: instrument interoperability, programmable experimental control, and autonomous research. Its emphasis is the instrument lifecycle: how hardware, firmware, software, operation descriptions and experimental evidence can develop together when AI systems are intended users and contributors to instrument design.

## Interfaces and experimental control

| Project or standard | Established contribution | Connection to AI4Instruments |
|---|---|---|
| [SiLA 2](https://sila-standard.com/standards/) | Discoverable laboratory services organized into Features, Commands, Parameters and Properties. | A suitable existing transport and capability vocabulary. Operation descriptions can expose the declared experimental meaning and scope of these interfaces. |
| [OPC UA LADS](https://reference.opcfoundation.org/specs/OPC-30500-1/full) | A laboratory device information model spanning hardware and functional views, state machines, program execution, results and maintenance. | Provides useful structure for device state, experimental lifecycle and results. AI4Instruments can map operations onto these objects. |
| [EPICS](https://epics-controls.org/about-epics/) | Distributed scientific control using local input/output controllers and networked Channel Access or pvAccess. | Supplies a mature foundation for distributed control and observation. Local control remains close to the equipment. |
| [Bluesky](https://blueskyproject.io/bluesky/v1.13.1/index.html) | Experiment orchestration, streaming data and metadata, reusable procedures and interruption handling. | Existing plans can implement Standard Operations and Workflow Operations while preserving their parameters and execution records. |
| [Ophyd](https://blueskyproject.io/ophyd/) | Device abstractions with methods such as `trigger`, `read` and `set`, grouping control channels into logical devices. | Demonstrates that common operation semantics can span distinct control systems. Device-specific capabilities remain available through explicit descriptions. |
| [GenICam](https://www.emva.org/wp-content/uploads/GenICam_Standard_v2_1_1.pdf) | Machine-readable camera descriptions connecting features to registers, with typed access and separate configuration and transport modules. | A concrete precedent for linking a useful operation to its underlying electronic representation. It also shows why feature availability and dependencies belong in an instrument description. |
| [ARTIQ](https://m-labs.hk/artiq/manual/rtio.html) | Kernels and real-time I/O that schedule hardware events on a timeline and timestamp input events. | Demonstrates how precise experimental timing can be expressed in programs and executed locally. Planning an experiment and producing its timed signals are different computational tasks. |

These systems already cover substantial parts of interoperability and automation. A useful contribution from AI4Instruments is to make their relationship to hardware capability, abstraction level, composition and evidence explicit. Replacing every existing driver or protocol would add integration work without necessarily expanding experimental capability.

## AI access to physical devices

The [agent–instrument study](agent-instruments/README.md) provides a source-linked comparison of protocols, runtimes and physical-device adapters, with [Chinese](agent-instruments/index.zh-CN.html?raw=1) and [English](agent-instruments/index.en.html?raw=1) offline HTML, structured project data, license distinctions and implementation evidence. It includes MHS, the AIP design reference, community OpenMHP/Open-MHS projects, MCP bridges and experimental systems across microscopy, quantum laboratories, chemistry, robotics and measurement benches.

Anthropic's [Model Hardware Standard research preview](https://www.anthropic.com/news/model-hardware-standard-research-preview), announced on 27 August 2026, describes standardized drivers, device discovery, physical metadata and access through MCP, command-line tools and APIs. It also describes multi-instrument coordination and scripts for operations that should execute locally. The announcement presents an early partner preview preceding planned open sourcing.

This is closely related work. AI4Instruments develops the broader design question of how instruments should be conceived, constructed and revised for autonomous experimentation, together with explicit Basic Operations, reusable Standard Operations, open-ended Workflow Operations and evidence connecting their revisions to measured performance.

## Autonomous research systems

[Coscientist](https://www.nature.com/articles/s41586-023-06792-0) connects language-model reasoning with documentation, programming and chemical experiments. It establishes a concrete link between an agent's ability to understand laboratory software and its ability to conduct physical work.

[End-to-end autonomous scientific discovery on a real optical platform](https://arxiv.org/abs/2604.27092) reports extended investigations by Qiushi Discovery Engine involving program execution, optical measurements and revision of research plans. Its optical setting motivates the need for adaptable instrument operations across a continuing investigation, rather than a single fixed measurement sequence.

[A-Lab](https://www.nature.com/articles/s41586-023-06734-w) combines robotic solid-state synthesis with computational and learning methods for choosing and interpreting experiments. Its [2026 correction](https://www.nature.com/articles/s41586-025-09992-y) revises material identification and novelty claims; the current title refers to inorganic materials. Here it is relevant as an integrated synthesis and characterization system.

[A mobile robotic chemist](https://www.nature.com/articles/s41586-020-2442-2) demonstrates an alternative route: a mobile robot operates laboratory stations while a Bayesian search selects experiments. This broadens the meaning of instrument access. A physical intermediary can connect equipment to an autonomous workflow even when its original interface was designed for human operation.

## The research direction

The next step is to study how these capabilities reinforce one another across the instrument lifecycle. An experimental failure can reveal a missing observation; the missing observation can motivate a sensor or firmware change; that change can enable a new Basic Operation; a new procedure can then be composed and evaluated. The relevant unit of progress is the experimentally demonstrated capability gained through this cycle.

The terms **Instruments4AI** and **AI4Instruments** describe complementary design emphases. Existing equipment can be integrated immediately while new instruments are designed for richer programmability, observation and revision. Both routes contribute to laboratories that can share executable methods and interpretable evidence across vendors and disciplines.

Bibliographic metadata is maintained in [references.json](../paper/references.json). Web documentation was consulted on 15 October 2026.
