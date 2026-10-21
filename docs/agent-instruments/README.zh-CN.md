# AI 与真实仪器：领域全景与工程比较

[English](README.md) · [中文 HTML](index.zh-CN.html?raw=1) · [English HTML](index.en.html?raw=1)

研究 AI / LLM Agent 怎样发现、连接、驱动和观察真实仪器，追踪参与者、接口、执行系统、实验结果与可复用工程之间的关系。

当前版本包含 **73 项工程与研究资料、70 个维护者及标准主体、190 个图谱节点、323 条关系、316 个来源地址**，另有 **14 组标准与基础生态、40 个设备组件**。版本日期：**2026-10-21**；具体材料的核查日期保留在条目中。

下载任一 HTML 后直接打开。字体、图谱、正文与结构化资料均已内嵌，离线支持检索、分页、比较和导出。

## IOP：从具体方案到共同操作模型

正文按固定的三级关系展开：**一级是具体方案，二级是共同机制，三级是 IOP 的操作模型**。以偏振扫描贯穿能力定义、执行、观测与设备适配。

- 第 1–2 页：三级关系与物理操作。
- 第 3–9 页：MHS、三个独立 Open-MHS 工程、Cuntinum MHP、AIP、OpenMHP、LAP、OAHL 的对象、执行路径与设计区别。
- 第 10–12 页：设备能力模型、操作执行与结果契约、设备发现与资源协作，以及 SiLA 2、OPC UA/LADS、W3C WoT 的位置。
- 第 13–18 页：IOP 对象关系、共同操作定义、执行读回、跨设备映射、仪器包与验证目标。

章节导航与页内目录保持一致；支持方向键、页面选择与全屏。来源位于相关页面下方。九项具备具体机制的方案进入归纳；Agent2Device 概念材料在目录中单列。完整工程资料仍在后续栏目中查询。

[中文 IOP](index.zh-CN.html#presentation/1) · [English IOP](index.en.html#presentation/1) · [正文与机制数据](presentation.json)

## 九个阅读栏目

| 栏目 | 回答的问题 |
| --- | --- |
| IOP | 哪些同类方案值得直接比较；如何归纳机制并综合为 IOP 的设计？ |
| 领域全景 | 设备桥接、仪器契约、常驻执行、过程编排、实验决策、仪器开发、界面操作与知识资料如何分工？ |
| 关系图谱 | 谁维护什么；工程接入或复用了什么；哪些项目有后续发展关系？ |
| 技术路线 | 每条路线解决什么问题，交付什么能力，怎样比较与验证？ |
| 参与者 | 研究机构、产业团队、协作组织、用户账号和标准主体分别做了什么？ |
| 工程与比较 | 每项怎样连接、贡献在哪里、区别是什么、哪些部分可以复用？支持至多三项并排比较。 |
| 标准与组件 | 共同语义、Agent 接口、执行基础与设备组件各自处于什么位置？ |
| 设计推演 | 怎样选择能力模型、执行所有权、观测数据、过程表达和生态协作方式？ |
| 来源与数据 | 事实和关系依据在哪里，怎样导出和继续使用？ |

左侧目录、上一栏目、下一栏目及页码用于导航；各工程有独立详情地址，名单与来源单独分页。页面地址的 `#projects/instrmcp`、`#relations/s:mcp` 等片段可直接定位内容。

## 文件与数据

| 内容 | 文件 |
| --- | --- |
| 完整交互阅读版 | [中文](index.zh-CN.html) · [English](index.en.html) |
| 逐项贡献、差异与复用分析 | [中文](profiles.zh-CN.md) · [English](profiles.en.md) |
| 接口设计与实验示例 | [中文](guide.zh-CN.md) · [English](guide.en.md) |
| 工程事实记录 | [catalogue.json](catalogue.json) · [CSV](catalogue.csv) · [中文目录](catalogue.zh-CN.md) · [English](catalogue.en.md) |
| 参与者、路线、项目分析与设计决策 | [landscape.json](landscape.json) |
| 有类型、有来源的关系图谱 | [graph.json](graph.json) |
| 标准、基础生态、设备组件与范围 | [context.json](context.json) |
| 原始来源索引 | [sources.json](sources.json) |
| 字段与关系语义 | [data-model.md](data-model.md) |
| JSON Schema | [工程](catalogue.schema.json) · [领域数据](landscape.schema.json) · [图谱](graph.schema.json) |
| 设备与测量契约示例 | [examples/](examples/README.md) |

首页图解释功能分工；关系图展示具体工程的维护、接入、复用和迁移。图谱区分 `documented` 来源记录与 `analysis` 分析分类。合并显示的基础生态节点在关系备注中指明实际接入范围，例如 OPC UA 接入与 LADS 信息模型实现分别说明。

每个工程同时保留发布范围、许可证和实验依据。“论文实机案例”“维护者实机记录”“接入实现 / 文档”“模拟验证”“配套代码 / 资料”“构想 / 提案”是不同的证据类型。公开论文中的整套实验系统与所链接仓库的实际交付范围分别记录。

70 个主体包含 65 个工程维护命名空间和 5 个协议、标准主体；用户账号不等同于独立开发者，组织账号不自动归为企业。已确认的机构背景另附原始来源。路线、贡献比较与设计建议属于基于材料的分析。

## 更新与重建

编辑 `catalogue.json`、`context.json`、`landscape.json` 和两份 `guide` 文件，保持稳定 ID 和双语字段。新的工程需同时补齐项目事实、维护主体、贡献说明、接入路径和来源；图谱依赖随明确的实现材料更新。

在仓库根目录运行：

```bash
python docs/agent-instruments/build.py
```

构建器只使用 Python 标准库，生成两份 HTML、工程说明、目录 Markdown、CSV、图谱和来源索引。版式在 `reader.py` 与 `assets/reader.css`，交互在 `assets/reader.js`。不启用 JavaScript 时仍能读取全部静态正文。

HTML 的 `script#research-data` 保存全部数据；`documents` 字段包含中英文设计正文与工程说明、字段规范、CSV 和契约示例。维护数据关系见 [data-model.md](data-model.md)，更新记录见 [CHANGELOG.md](CHANGELOG.md)。

原创说明采用仓库的 [CC BY 4.0](../../LICENSE-docs.md)，构建代码采用 [MIT](../../LICENSE)，第三方项目保留各自许可。离线字体采用 [SIL Open Font License](assets/FONT_LICENSE.txt)。

IOP 正文与机制归纳位于 `presentation.py`，版式位于 `assets/presentation.css`，构建时生成 `presentation.json` 并内嵌两份 HTML。
