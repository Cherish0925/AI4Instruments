# 智能体与真实仪器

[English](README.md) · [中文 HTML](index.zh-CN.html?raw=1) · [English HTML](index.en.html?raw=1)

研究 AI / LLM Agent 如何发现、连接、驱动和观察真实仪器。资料把协议设计与实际驱动、执行系统、实验案例及许可证放在同一条可追溯的接入路径中。

当前收录 **73 项工程与配套资料**、**14 项协议与基础生态**、**40 个单列组件**。核查日期：**2026-10-20**。下载 HTML 后可直接打开，离线检索、筛选与导出数据。

| 想了解的内容 | 文件 |
| --- | --- |
| 协议地位、接口分工与设计建议 | [中文分析](guide.zh-CN.md) · [English](guide.en.md) |
| 全部项目的可读记录 | [中文目录](catalogue.zh-CN.md) · [English](catalogue.en.md) |
| 中英双语项目数据 | [JSON](catalogue.json) · [CSV](catalogue.csv) |
| 协议、基础生态、设备组件与范围边界 | [context.json](context.json) |
| 原始来源索引 | [sources.json](sources.json) |
| 数据字段定义 | [catalogue.schema.json](catalogue.schema.json) |
| 设备与测量契约示例 | [examples/](examples/README.md) |

MHS 官方研究预览、用户提供的 AIP 设计、社区 Open-MHS/OpenMHP 工程、LAP 设计论文，与已有 MCP、SiLA 2、LADS、WoT 生态分别标明，不按相似名称合并。

## 如何判断与使用

项目记录分别回答：有什么接口；调用落到什么设备路径；公开过哪种实验或实现证据；哪些代码可以按什么许可复用；原始资料在哪里。

“论文实机案例”来自原始论文，“维护者实机记录”来自项目说明或演示；“接入实现 / 文档”不等于实机通过；“模拟验证”不等于相应硬件已经运行。配套资料和设计提案有独立标记。MCP / Skills 未确认表示本次材料没有建立其存在，不表示确定不存在。

许可证与实验状态独立筛选。开源服务可能依赖专有 SDK；公开仓库也可能没有许可证或限制商业使用。组件数量和 fork 不重复计为独立工程。实机状态引用作者或维护者记录，本次没有操作这些设备。

## 更新

修改 `catalogue.json`、`context.json` 和两份 `guide` 文件，保留一致的项目 ID、字段含义和来源。新的实机记录应写明型号、固件、后端与验证范围。随后在仓库根目录运行：

```bash
python docs/agent-instruments/build.py
```

标准库构建器会生成中英 HTML、目录 Markdown、CSV 和来源索引。HTML 内嵌全部结构化记录；不开启 JavaScript 也可阅读，开启后支持筛选和导出。详细字段语义与维护方法见 [English README](README.md)，更新记录见 [CHANGELOG.md](CHANGELOG.md)。

原创说明采用仓库的 CC BY 4.0 许可，构建代码采用 MIT，第三方项目保留各自许可。离线字体的许可位于 [FONT_LICENSE.txt](assets/FONT_LICENSE.txt)。
