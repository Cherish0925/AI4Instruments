# AI4Instruments

### Instruments as programmable partners in scientific discovery

**AI design and implementation + AI development and use.**

AI4Instruments explores how scientific instruments can be designed, developed and operated with AI as a continuing participant. The aim is to expand what experiments can be performed: expose useful hardware capabilities, make observations interpretable, compose operations across instruments, and turn experimental experience into better apparatus and better research.

**By Shuxing Yang** · [中文介绍](README.zh-CN.md) · [Paper: PDF](paper/AI4Instruments.pdf) · [Paper: HTML](paper/AI4Instruments.html) · [Readable manuscript](paper/manuscript.md)

## Why this project exists

An instrument's hardware may support more than its application exposes. A laboratory may have every device needed for an experiment, yet lack compatible interfaces, synchronised timing, reliable readback or a coherent record of what happened. Researchers spend time repairing these gaps instead of testing ideas.

Connecting existing equipment to an AI system is an essential first step. AI4Instruments carries the question through the whole instrument lifecycle: **what should be built, what should be programmable, what should be observable, and what should change after the next experiment?**

| Perspective | Starting point | Main question |
| --- | --- | --- |
| **Instruments4AI** | Available instruments, manuals, SDKs and interfaces | How can AI use this apparatus to conduct an experiment? |
| **AI4Instruments** | Scientific questions and the design of the apparatus itself | How can AI help create, develop and use better experimental capabilities? |

These perspectives work together. Existing equipment provides a practical starting point; experimental evidence guides deeper changes to software, firmware, circuits and mechanics.

## Three levels, open to development

![Operation hierarchy](assets/operation-hierarchy.svg)

| Level | Meaning | Example |
| --- | --- | --- |
| **Basic Operations** | Elementary control and observation at a declared hardware abstraction level | Set an exposure, read an axis position, acquire a signal. |
| **Standard Operations** | Reusable experimental procedures with explicit assumptions and observations | Capture an image, transfer liquid, execute a thermal programme. |
| **Workflow Operations** | Serial, parallel and adaptive composition across an experiment | Synthesis → processing → characterisation → next experiment. |

The foundation is **a complete set of basic operations**. Completeness is checked against a declared capability inventory, including adjustable quantities, observations, modes and timing. Missing capabilities remain visible. The goal is clear, nonredundant meaning; valid operations can still compete for the same physical resource.

A reusable procedure remains inspectable and replaceable. Capability descriptions say what an instrument can do. Evidence records say what has been observed. The current research objective decides what is worth doing next. An established workflow should help a new investigation without defining its limits.

## Start here

| If you want to… | Read or run |
| --- | --- |
| Understand the argument | [Paper manuscript](paper/manuscript.md), [PDF](paper/AI4Instruments.pdf), or [standalone HTML](paper/AI4Instruments.html) |
| Design an operation interface | [Operation model](docs/operations.md) |
| Develop an instrument from the hardware upward | [Instrument lifecycle](docs/instrument-design.md) |
| Explore optics, chemistry, biology and materials examples | [Experimental designs](docs/examples.md) |
| Inspect a working software example | [Simulated optical alignment](examples/README.md) |
| Compare established standards and research | [Related work](docs/related-work.md) |
| Choose a concrete contribution | [Research agenda](docs/research-agenda.md) and [contribution guide](CONTRIBUTING.md) |

## Run the reference

Python 3.10 or newer; no runtime dependencies or installation required.

```bash
python examples/optical_alignment.py --output runs/optical-alignment
python -m unittest discover -s tests -v
```

The simulated bench has two positioning axes and a detector. Seven Basic Operations compose into three Standard Operations and one Workflow Operation. The axes move concurrently; acquisition waits for both observed positions. An external search objective selects the next setting from measured feedback.

Each run writes a capability manifest, a JSONL trajectory and a summary. With the default seed, the demonstration performs 22 evaluations and changes simulated measured power from 23.734040 to 99.979081 µW. The [example documentation](examples/README.md) explains the model, clocks, provenance, assumptions and extension points.

## What this repository contains

```text
paper/       Manuscript, bibliography, standalone HTML and typeset PDF
assets/      Original diagrams used in the paper and documentation
docs/        Operation model, instrument design, examples and research agenda
src/         Small Python reference for operations, traces and composition
examples/    Executable simulated optical experiment and capability manifest
tests/       Behavioural tests for the reference implementation
scripts/     Reproducible paper build
```

Version 0.1.0 establishes the design framework and a simulated executable reference. The next experimental milestone is to characterise real-device adapters against explicit capability inventories and demonstrate a procedure transferred across apparatus. Progress is measured by experimental capability and evidence, as described in the [research agenda](docs/research-agenda.md).

## Build and share the paper

The PDF and HTML contain the same manuscript. The HTML is self-contained, including its figures and styles; download it and open it in a browser. Its text, references and figures remain available offline. The PDF is ready to share or print. Both list **Shuxing Yang** as the sole author, without an affiliation.

```bash
python -m pip install -r requirements-paper.txt
python scripts/build_paper.py
```

For HTML alone, run `python scripts/build_paper.py --html-only`; this uses only the Python standard library. The PDF uses ReportLab and embeds DejaVu Serif when available, with a built-in serif fallback.

## Contribute and reuse

A useful contribution may be one documented instrument capability, an adapter, a controller implementation, an experimental procedure, an informative trajectory or a measured instrument improvement. Begin with the scientific question, identify what is implemented, and provide the evidence another researcher needs to use it.

Code is available under the [MIT License](LICENSE). The paper, documentation and original figures are licensed under [CC BY 4.0](LICENSE-docs.md). Citation metadata is in [CITATION.cff](CITATION.cff).
