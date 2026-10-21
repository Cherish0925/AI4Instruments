# Data model / 数据模型

All records are UTF-8 JSON. Stable project IDs join `catalogue.json`, `landscape.json`, `graph.json` and `context.json`. Chinese and English prose use `{ "zh": "…", "en": "…" }`. Schemas: [catalogue](catalogue.schema.json), [landscape](landscape.schema.json), [graph](graph.schema.json).

全部记录采用 UTF-8 JSON；稳定的项目 ID 串联事实、分析、图谱与基础生态。中英文正文采用同一条记录中的 `zh` / `en` 字段。

## Source files / 源数据

| File | Ownership / 内容 |
| --- | --- |
| `catalogue.json` | Project identity, description, interfaces, public scope, evidence, licensing, sources and review date / 工程事实、公开范围、接口、证据、许可及来源。 |
| `context.json` | Standards/foundations, component inventories, naming distinctions and scope / 标准、基础生态、组件及范围。 |
| `landscape.json` | Actors, domains, approaches, unique project profiles, documented dependencies, development links, insights and design choices / 主体、领域、路线、逐项分析、依赖、后续发展和设计决策。 |
| `guide.*.md` | Design chapters and experimental examples / 接口设计章节与实验示例。 |

`landscape.profiles[].route` assigns a primary contribution route, not an exclusive capability or a quality rank. `domain` identifies the main application or cross-domain design. `path` is an explanatory sequence in the reviewed material, not an executable procedure. `path_scope: research` identifies a paper-system path that may extend beyond the public repository.

`route` 是主要贡献分类，不表示唯一能力或优劣排名；`domain` 是主要应用领域。`path` 解释材料中的接入关系，不是可执行程序；`path_scope: research` 表示论文系统路径，范围可能大于公开仓库。

Actor IDs normally match GitHub namespaces. Namespaced repositories establish public maintenance, while separately cited institutional sources establish affiliations. The five additional protocol/standards actors use explicit IDs. An actor’s `projects` and `standards` are identifiers, not copies of records.

## Graph / 图谱

`graph.json` is generated. It contains `nodes` and directed `edges`.

| Node prefix | Kind | Reference |
| --- | --- | --- |
| `p:` | `project` | `catalogue.projects[].id` |
| `a:` | `actor` | `landscape.actors[].id` |
| `r:` | `route` | `landscape.routes[].id` |
| `d:` | `domain` | Key in `landscape.domains` |
| `s:` | `standard` | `context.standards[].id` |
| `f:` | `foundation` | Key in `landscape.extra_foundations` |

| Edge kind | Direction and meaning / 方向与含义 |
| --- | --- |
| `maintained_by` | Project → public maintainer namespace / 工程 → 维护命名空间。 |
| `publishes` | Actor → protocol or standard / 主体 → 发布或维护的协议标准。 |
| `uses` | Project → foundation it integrates or reuses / 工程 → 接入或复用的基础接口。 |
| `successor` | Earlier project → documented subsequent project / 较早工程 → 有来源的后续工程。 |
| `documents` | Operating knowledge → associated implementation / 操作知识 → 对应实现。 |
| `related` | Project → documented related work / 工程 → 有来源的相关发展。 |
| `classified_route` | Project → primary contribution route / 工程 → 主要贡献路线。 |
| `classified_domain` | Project → primary domain / 工程 → 主要作用领域。 |

Every edge carries `basis`, `sources` and an optional bilingual `note`. `documented` marks a relationship supported by cited material; `analysis` marks an editorial classification. The graph contains 177 documented relationships and 146 classifications in this edition. Dependency edges do not change a project’s hardware-evidence label. A grouped foundation node does not imply implementation of every standard it contains; use the edge note and project path.

每条边包含依据类型、来源和可选备注。本版本有 177 条来源关系、146 条分析分类。依赖关系与实机证据独立记录；同类基础生态的合并节点按备注限定实际接入范围。

Edge IDs are generated per build; use `(source, target, kind)` to identify a relationship across editions. Node IDs and project IDs are stable.

## Generated files / 生成文件

The builder produces `graph.json`, `sources.json`, `catalogue.csv`, both catalogue Markdown files, both profile Markdown files and both HTML editions. `sources.json` deduplicates URLs and retains subjects, roles and the latest review date recorded for that URL.

Each HTML has a `script#research-data[type="application/json"]` object:

```javascript
const data = JSON.parse(document.querySelector('#research-data').textContent);
const project = data.catalogue.projects.find(p => p.id === 'instrmcp');
const profile = data.landscape.profiles.find(p => p.id === project.id);
const links = data.graph.edges.filter(e => e.source === 'p:' + project.id);
```

The bundle contains `catalogue`, `context`, `landscape`, `graph`, `sources`, `presentation` and `documents`. `sources` is the record array; the standalone `sources.json` wraps it with a review date. `documents` contains the full original texts authored for this module, schemas and the synthetic contract example. External papers and manuals remain linked sources.

## Rebuild checks / 构建检查

The builder checks unique IDs, profile coverage, valid actor/route references, bilingual contribution fields, graph endpoints and source presence on documented edges. When editing the reader, check section navigation, deep links, filters, comparison, graph selection, downloads and mobile overflow in both languages.

The diagram on the opening page is an analytical role model. The relationship graph is a navigable view of the complete `graph.json`; dense neighborhoods show six neighbors per side while the paginated evidence list retains every adjacent edge.

## Presentation hierarchy

`presentation.json` holds bilingual slide titles, speaker notes, the full-catalogue role grouping and the direct protocol comparison set. `groups` partitions the existing eight routes by primary system responsibility. `protocol_comparison.groups` separately groups comparable instrument-interface designs by their main mechanism. These are editorial classifications, not protocol inheritance or confirmed compatibility.

References beginning `p:` identify catalogue projects; `s:` identify standards/design records. MHS and AIP use `s:` and are not among the 73 project records. Agent2Device is retained under `unassigned_concepts` because its public description does not establish a sufficiently detailed mechanism. Projects can span several responsibilities; primary assignments avoid duplicate counts. The reading hierarchy and Basic/Standard/Workflow Operations describe different dimensions.

The HTML bundle includes the `presentation` object. `#presentation/3` opens the direct comparison inventory; `#presentation/6?route=bridge` opens the full-ecosystem island with its bridge records expanded.
