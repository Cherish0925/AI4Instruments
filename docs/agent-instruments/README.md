# Agents and physical instruments

[中文](README.zh-CN.md) · [Chinese HTML](index.zh-CN.html?raw=1) · [English HTML](index.en.html?raw=1)

A source-linked study of interfaces through which AI agents discover, operate and observe physical instruments. It connects protocol design to actual drivers, runtimes, experiments and licensing.

The collection contains **73 project and supporting-material records**, **14 protocol or foundation entries**, and **40 separately listed components**. Review date: **2026-10-20**. Download either HTML file and open it locally for search, filters and data export without a server or network connection.

## Read

| Purpose | File |
| --- | --- |
| Chinese analysis and design recommendations | [guide.zh-CN.md](guide.zh-CN.md) |
| English analysis and design recommendations | [guide.en.md](guide.en.md) |
| Complete readable catalogues | [中文](catalogue.zh-CN.md) · [English](catalogue.en.md) |
| Bilingual project records | [catalogue.json](catalogue.json) · [CSV](catalogue.csv) |
| Protocols, foundations, components and scope boundaries | [context.json](context.json) |
| Primary-source index | [sources.json](sources.json) |
| Machine-readable field definitions | [catalogue.schema.json](catalogue.schema.json) |
| Illustrative device/measurement contract | [examples/](examples/README.md) |

The HTML files are the integrated reading editions: system responsibilities, project selection, protocol comparisons, design analysis, experimental examples and reusable records. The catalogue schema, measurement-contract example and both analysis texts are embedded and can be exported offline. Protocols are grouped by their role; each entry retains its own implementation and publication status.

## How records are evaluated

Sources are maintainer repositories and documentation, official protocol material and original papers. Discovery lists identify leads; they do not establish technical claims. Selected implementation paths were inspected for connection ownership, actual device calls, simulation boundaries and result handling. Source-file hashes record the reviewed copies where available; they identify snapshots and are not a substitute for an upstream release or commit.

Experimental status and licensing are independent:

| Field | Meaning |
| --- | --- |
| `experiment` | A linked publication reports a physical experiment; the release may cover only part of that system. |
| `hardware` | Maintainers identify a physical device test or demonstration. |
| `adapter` | A concrete adapter or integration path is documented; this label does not assert hardware validation. |
| `simulation` | The project explicitly reports simulator or twin validation. |
| `artifact` | Supporting code, skills, data, workshop material or a partial research release. |
| `proposal` | A concept without a device implementation in the reviewed repository. |

`mcp` and `skills` record documented interfaces; `not_documented` means that this review did not establish their availability. It does not mean the interface cannot exist. “Open-source license” applies to the listed repository scope, not automatically to required vendor SDKs, model services or laboratory hardware. Restricted, mixed and unidentified licenses have separate groups.

This was a source and implementation review, not a hardware test campaign. Component inventories do not increase independent-project counts. Related repositories and migrations are linked explicitly; ordinary forks are deduplicated. AIP is identified as a supplied design reference, without presenting the source PRD as a public software release.

## Update and rebuild

Edit `catalogue.json`, `context.json` and the two guide Markdown files. Keep the same project IDs and meanings across languages. Add source URLs to every material factual change. Record tested model, firmware, backend and scope when upgrading a hardware-evidence label.

From the repository root:

```bash
python docs/agent-instruments/build.py
```

The build uses only Python’s standard library. It regenerates both self-contained HTML files, Markdown catalogues, CSV and `sources.json`. Project descriptions remain readable in HTML without JavaScript; JavaScript supplies filtering and export. The embedded JSON is in `script#research-data[type="application/json"]`; its `documents` field holds the analysis texts, catalogue schema and contract example.

When adding a project, check for an actual physical-device path, an existing upstream entry, a separate license file and a simulator-only demonstration. If a useful project lacks a complete control release, retain it as a clearly scoped reference rather than extending its claims. Change records belong in [CHANGELOG.md](CHANGELOG.md).

## Attribution

Original research prose and catalogue annotations follow the repository’s [CC BY 4.0 documentation license](../../LICENSE-docs.md); build code follows [MIT](../../LICENSE). Upstream software retains its own license. LabMCP component names, protocol identifiers and tool counts are indexed from its Apache-2.0 catalogue, with links to the [original source](https://github.com/K-Dense-AI/lab-instrument-mcps/blob/main/packages/labmcp/src/labmcp/catalog.json). OpenMHP component status comes from its [supported-device index](https://github.com/kushalsinha/openmhp/blob/main/supported-devices/README.md).

The offline font is a renamed subset of Noto Sans CJK SC under the [SIL Open Font License](assets/FONT_LICENSE.txt). No third-party manual or article is bundled in full.
