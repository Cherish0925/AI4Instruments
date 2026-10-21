# AI and physical instruments: landscape and project comparisons

[中文](README.zh-CN.md) · [Chinese HTML](index.zh-CN.html?raw=1) · [English HTML](index.en.html?raw=1)

A source-linked study of how AI / LLM agents discover, operate and observe physical instruments, connecting participants, interfaces, runtimes, experimental results and reusable engineering.

This edition contains **73 project and research-artifact records, 70 maintainer/standards actors, 190 graph nodes, 323 relationships and 316 source addresses**, plus **14 standards/foundation entries and 40 device components**. Edition date: **2026-10-21**; individual records retain their own review dates.

Download either HTML file and open it locally. Fonts, diagrams, text and structured records are embedded, supporting offline search, pagination, comparison and export.

## IOP: from existing designs to a shared operation model

The argument uses three fixed levels: **existing designs → shared mechanisms → the IOP operation model**. A polarization scan connects capability definitions, execution, observations and device adaptation.

- Pages 1–2: the hierarchy and the physical operation.
- Pages 3–9: the objects, execution paths and distinctions of MHS, three independent Open-MHS projects, Cuntinum MHP, AIP, OpenMHP, LAP and OAHL.
- Pages 10–12: capability models, execution/result contracts, discovery/resource coordination, and their relationship to SiLA 2, OPC UA/LADS and W3C WoT.
- Pages 13–18: IOP object relationships, a shared operation definition, execution/readback, cross-device mappings, instrument packages and validation targets.

Chapter navigation and a chapter-specific outline support keyboard navigation, direct page selection and fullscreen. Sources accompany relevant pages. Nine designs with concrete mechanisms inform the synthesis; the Agent2Device concept is listed separately. The wider project catalogue remains available in the other sections.

[English IOP](index.en.html#presentation/1) · [中文 IOP](index.zh-CN.html#presentation/1) · [Content and mechanism data](presentation.json)

## Nine reading sections

| Section | Question |
| --- | --- |
| IOP | Which approaches are directly comparable, which mechanisms do they share, and how can they inform IOP? |
| Landscape | How do device bridges, contracts, persistent execution, procedures, experimental decisions, instrument development, GUI operation and knowledge resources fit together? |
| Relationships | Who maintains what; which foundations does a project use; how have projects developed or migrated? |
| Approaches | What problem does each route solve, what does it produce, and how should it be compared and verified? |
| Participants | What have research groups, industry teams, collaborative organizations, user accounts and standards actors contributed? |
| Projects and comparison | How does each project connect, contribute and differ, and what can be reused? Compare up to three projects side by side. |
| Standards and components | Where do shared semantics, agent interfaces, execution foundations and device packages belong? |
| Design choices | How should capabilities, execution ownership, observations, procedures and ecosystem collaboration be designed? |
| Sources and data | Where is the evidence, and how can the collection be exported and reused? |

Use the sidebar, previous/next controls and section numbers to navigate. Profiles have individual addresses; directories and sources are paginated. URL fragments such as `#projects/instrmcp` and `#relations/s:mcp` locate specific content.

## Files and data

| Content | File |
| --- | --- |
| Complete interactive editions | [中文](index.zh-CN.html) · [English](index.en.html) |
| Per-project contributions, distinctions and reuse analysis | [中文](profiles.zh-CN.md) · [English](profiles.en.md) |
| Interface design and experimental examples | [中文](guide.zh-CN.md) · [English](guide.en.md) |
| Project facts | [catalogue.json](catalogue.json) · [CSV](catalogue.csv) · [中文 catalogue](catalogue.zh-CN.md) · [English](catalogue.en.md) |
| Actors, routes, profiles and design decisions | [landscape.json](landscape.json) |
| Typed, source-linked relationships | [graph.json](graph.json) |
| Standards, foundations, components and scope | [context.json](context.json) |
| Original-source index | [sources.json](sources.json) |
| Field and relationship semantics | [data-model.md](data-model.md) |
| JSON Schema | [Projects](catalogue.schema.json) · [Landscape](landscape.schema.json) · [Graph](graph.schema.json) |
| Illustrative device/measurement contract | [examples/](examples/README.md) |

The opening diagram explains functional responsibilities. The relationship graph records actual maintenance, integration, reuse and development links. It distinguishes `documented` relationships from `analysis` classifications. For grouped foundation nodes, edge notes identify the actual integration scope: OPC UA access, for example, is distinguished from implementing the LADS information model.

Each project preserves its public release scope, licensing and experimental evidence. Published physical experiments, maintainer hardware records, adapter implementations, simulations, supporting artifacts and proposals are separate evidence categories. The system described in a paper and the material delivered by its linked repository are recorded separately.

The 70 actors comprise 65 repository-maintainer namespaces and five protocol/standards actors. User accounts are not assumed to represent sole developers, and organization accounts are not automatically classified as companies. Verified institutional context has separate primary sources. Routes, contribution comparisons and design choices are analysis of the material.

## Update and rebuild

Edit `catalogue.json`, `context.json`, `landscape.json` and both guide Markdown files. Preserve stable IDs and bilingual fields. A new entry needs its project facts, maintainer, contribution analysis, access path and sources. Add foundation relationships only when supported by concrete documentation or implementation.

From the repository root:

```bash
python docs/agent-instruments/build.py
```

The builder uses Python’s standard library and generates both HTML files, project profiles, Markdown catalogues, CSV, graph and source index. Layout is in `reader.py` and `assets/reader.css`; interaction is in `assets/reader.js`. All static text remains readable without JavaScript.

The HTML’s `script#research-data` contains the complete dataset. Its `documents` field includes both language editions of design text and project profiles, schemas, CSV and the contract example. See [data-model.md](data-model.md) for data relationships and [CHANGELOG.md](CHANGELOG.md) for updates.

## Attribution

Original prose and catalogue annotations follow [CC BY 4.0](../../LICENSE-docs.md); build code follows [MIT](../../LICENSE). Upstream software retains its own license. LabMCP component names, protocol identifiers and tool counts are indexed from its Apache-2.0 [catalogue](https://github.com/K-Dense-AI/lab-instrument-mcps/blob/main/packages/labmcp/src/labmcp/catalog.json). OpenMHP component status comes from its [supported-device index](https://github.com/kushalsinha/openmhp/blob/main/supported-devices/README.md).

The embedded font is a renamed subset of Noto Sans CJK SC under the [SIL Open Font License](assets/FONT_LICENSE.txt). Original papers and manuals are linked.

IOP content and mechanism synthesis are in `presentation.py`; layout is in `assets/presentation.css`. The build generates `presentation.json` and embeds it in both HTML editions.
