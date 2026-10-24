<p>
  <img src="assets/readme-header.png" alt="From Instruments4AI to AI4Instruments — AI design and implementation + AI development and use." width="1280">
</p>

0.8.0 新增 MCP 接入、统一实验室说明、配置格式接口与设备恢复。Agent 直接复用已有仪器和平台配置。[软件形态、系统支持与职责分工](iop/product.zh-CN.md)。

[阅读论文](paper/manuscript.md) · [PDF](paper/AI4Instruments.pdf) · [Operations](docs/operations.md) · [运行示例](examples/README.md) · [参与讨论](https://github.com/Cherish0925/AI4Instruments/discussions/1) · [English](README.md)

## IOP Runtime · 仪器运行服务

**安装常驻仪器服务，配置实验平台，让人和 Agent 提交程序开展实验。** 一台计算机可以管理多个平台，共享设备由同一个服务安排使用。

[IOP 工程入口](iop/README.zh-CN.md) · [下载 0.8.0](https://github.com/Cherish0925/AI4Instruments/releases/tag/iop-v0.8.0) · [安装](docs/runtime/README.zh-CN.md) · [配置实验平台](iop/platforms.zh-CN.md) · [Agent 接入](iop/agent-setup.zh-CN.md)

0.8.0 提供[桌面与网页界面](iop/interface.zh-CN.md)：设备登记、平台连接图、实验操作、结果与文件。常驻服务统一安排执行；桌面、浏览器和 Agent 共用配置与记录。[整体架构](docs/runtime/architecture.zh-CN.md)。

AI4Instruments 探索一套面向 AI 的仪器方法论、设计规范与开放生态，让 AI 参与科学与工程仪器的构思、规划设计、生产制造、软硬件开发、实验使用与持续改进，贯穿仪器的整个生命周期。

目标是扩展真实物理世界中可以开展的研究，支持长期自主与自治实验，让不同实验室的知识与能力能够互通、积累和发展。**科学研究的进步、仪器能力的发展，以及 AI 从真实实验经验中学习和改进**，可以在这个过程中相互促进。这些原则面向不同科学与工程领域、不同仪器形态，以及不同类型的 AI 系统。


## 从使用仪器，到创造实验的可能性

**Instruments4AI** 从现有设备出发：建立电控与编程路径，准备手册、SDK 和例程，组织工具与知识，将设备连接成串并行实验，再为不同课题编写程序和工作流。

**AI4Instruments** 将问题推进到仪器本身：应该让哪些物理量可以被控制，哪些结果可以被观察，哪些机械、电路、芯片、控制器、固件和软件的变化能够带来更好的实验？

两者可以衔接。实验使用暴露新的需求，仪器开发创造新的实验可能性。AI 可以贯穿立项、规划设计、制造实现、软硬件协同、表征校准、实验研究和下一轮改进。

<details>
<summary>图解：从适配已有仪器，到设计与实验共同演进</summary>

![从仪器适配到持续开发](assets/design-transition.svg)

</details>

## 通用性来自共同结构

共同结构是：**干预 → 物理响应 → 观察 → 下一步实验决策。** 它可以作用于元件、单台设备、综合实验平台和跨实验室合作。每个层级保留理解其行为所需的物理细节。

参与其中的 AI 可以是语言模型 Agent、机器视觉系统、学习控制器、优化算法，以及它们的组合。不同仪器不必拥有相同的命令表，但需要能够描述、理解、组合和继续开发自己的能力。

| 操作角色 | 核心作用 |
| --- | --- |
| **Basic Operations** | 在明确的硬件抽象层级上，完整、清晰地表达最基础的控制与观察能力。 |
| **Standard Operations** | 将基础能力组织成可复用的实验过程，保留实现、适用条件和实际证据。 |
| **Workflow Operations** | 跨物理对象、设备、时间与地点，组织串行、并行、持续与反馈驱动的实验。 |

基础目标是 **a complete set of basic operations**。能力清单需要对应实际硬件、可控量、可观测量、状态和时序关系。研究还应发现未被利用的自由度、缺失的观察，以及需要通过新硬件实现的能力，使清单本身继续发展。

三类 Operations 表示组合角色。面对新问题，可以复用已有过程，也可以查看其内部实现、修改、重新组合或直接从基础操作创造新的过程；必要时进一步改进仪器本身。

操作描述说明能力，实验记录保存证据，当前研究目标决定如何评价和选择实验。已经形成的操作与工作流应当帮助新的研究，同时为新的问题和方法保留空间。

## 从底层开发到长期研究

电路提供控制与感知的物理实现，编程表达这些能力如何被使用。开放控制器、芯片、固件和电路层级的知识与开发接口，可以让研究系统改变时序、采集、驱动和处理方式，探索原有应用软件没有覆盖的能力。机械、材料与具体物理作用也需要进入同一个设计视野。

真实实验轨迹连接问题、仪器版本、干预、原始观察、分析与决策。这些信息既可以推进科学认识，也可以用于仪器改进、物理建模、感知、编程和研究策略的学习。兼容的能力描述与可理解的证据，还可以支持不同实验室迁移过程、比较结果、结合彼此的专长开展研究。

<details>
<summary>图解：实验经验如何推进科学、仪器与模型</summary>

![实验、知识、模型与仪器之间的关系](assets/experimental-learning.svg)

</details>

## 从这里开始

| 想了解的问题 | 对应内容 |
| --- | --- |
| 整体思想与论证 | [论文正文](paper/manuscript.md)、[PDF](paper/AI4Instruments.pdf)、[下载 HTML](paper/AI4Instruments.html?raw=1) |
| 如何描述、组合和扩展操作 | [Operations](docs/operations.md) |
| AI 如何参与仪器全生命周期 | [仪器设计](docs/instrument-design.md) |
| 通用原则如何落到实际实验 | [实验关系与实例](docs/examples.md) |
| IOP 如何组织平台的设备、实验与记录 | [IOP 定义](docs/iop.md) · [IOP 原理与结构](docs/agent-instruments/index.zh-CN.html?raw=1#presentation/1) · [English](docs/agent-instruments/index.en.html?raw=1#presentation/1) |
| Agent 怎样连接与操作真实仪器 | [仪器接口与生态全景](docs/agent-instruments/README.zh-CN.md) · [中文 HTML](docs/agent-instruments/index.zh-CN.html?raw=1) · [English HTML](docs/agent-instruments/index.en.html?raw=1) |
| 与已有标准和研究的联系 | [相关工作](docs/related-work.md) |
| 哪些进展值得推进与验证 | [研究议程](docs/research-agenda.md) |
| 如何查看可执行实现 | [模拟光学示例](examples/README.md) |

论文保存在 `paper/`，技术说明在 `docs/`，可执行示例在 `src/` 和 `examples/`。具体示例可以不断扩展，项目的适用范围由上述共同原则定义。

## 运行与贡献

仓库中的模拟光学示例展示命令、观察、串并行组合与反馈之间的关系，便于阅读和修改。Python 3.10 及以上即可运行，无运行时第三方依赖：

```bash
python examples/optical_alignment.py --output runs/optical-alignment
python -m unittest discover -s tests -v
```

运行后会得到能力清单、JSONL 实验轨迹和结果摘要。完整模型与扩展方式见[示例说明](examples/README.md)。

欢迎围绕思想、仪器描述、物理设计、控制程序、新操作、实验与数据开展贡献，见[贡献指南](CONTRIBUTING.md)。软件采用 [MIT](LICENSE) 许可，论文、文字文档与原创图示采用 [CC BY 4.0](LICENSE-docs.md) 许可。

---

<sub>Shuxing Yang · [作者说明](docs/author-note.md#中文) · [引用](CITATION.cff) · [English](README.md)</sub>
