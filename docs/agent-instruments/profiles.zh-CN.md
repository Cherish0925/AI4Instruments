# 工程说明与比较

## OpenMHP

[kushalsinha/openmhp](https://github.com/kushalsinha/openmhp) · 仪器说明 · Apache-2.0 · 模拟验证

设备描述、读写、动作、任务、租约与实验记录组成统一接口；可通过已有驱动生态接入。适合研究精简设备说明与按需发现。

维护主体：kushalsinha

接入关系：Agent → MCP / CLI / SDK → OpenMHP jobs & leases → device adapter

### 贡献与价值

把一次工具调用扩展为有身份、资源占用、事件和结果的设备任务。

### 差异与适用条件

相较单设备 MCP 桥，重点在共同生命周期与按需能力描述；当前设备包的证据主要来自孪生测试。

### 可复用部分

借鉴任务、租约与结果结构；逐型号补齐真实读回和运行记录。

### 公开范围与实验记录

公开规范与实现；supported-devices 的 7 个设备包标为 twin tested，另有 1 个人工操作模板。维护者明确尚未确认这些驱动的实机运行。

[项目说明](https://github.com/kushalsinha/openmhp/blob/main/README.md) · [许可证](https://github.com/kushalsinha/openmhp/blob/main/LICENSE) · [实现入口](https://github.com/kushalsinha/openmhp/blob/main/SPEC.md) · [实现入口](https://github.com/kushalsinha/openmhp/blob/main/supported-devices/README.md) · [实现入口](https://github.com/kushalsinha/openmhp/blob/main/supported-devices/biologic-sp300/driver.py)

## Open-MHS · Abenor Labs

[Abenor-Labs/Open-MHS](https://github.com/Abenor-Labs/Open-MHS) · 仪器说明 · Apache-2.0 · 接入实现 / 文档

以 capability tag 和设备基类统一传感器、执行器及状态；提供串口机械臂适配示例。独立社区实现。

维护主体：Abenor-Labs

接入关系：Agent → MCP / REST → capability tags → serial robotic-arm driver

### 贡献与价值

用能力标签与基类，把不同设备的传感、动作和状态组织成可发现的接口。

### 差异与适用条件

重点是设备表示与串口适配示例，规模与验证范围不同于完整的实验室执行系统。

### 可复用部分

研究能力标签怎样映射到驱动方法，并为每个标签定义返回语义。

### 公开范围与实验记录

源码包含 mock 设备和串口驱动；本次材料未提供具体实机验证记录。

[项目说明](https://github.com/Abenor-Labs/Open-MHS/blob/main/README.md) · [许可证](https://github.com/Abenor-Labs/Open-MHS/blob/main/LICENSE) · [实现入口](https://github.com/Abenor-Labs/Open-MHS/blob/main/open_mhs/drivers/serial_robotic_arm.py) · [实现入口](https://github.com/Abenor-Labs/Open-MHS/blob/main/schema/capability_schema.json)

## Open MHS · tongriyaotxt

[tongriyaotxt/open-mhs](https://github.com/tongriyaotxt/open-mhs) · 仪器说明 · MIT · 接入实现 / 文档

设备注册、统一命令和 MCP 工具；包含机器人动作与技能执行扩展。与同名项目分别维护。

维护主体：tongriyaotxt

接入关系：Agent → MCP dispatch → command / skill execution → robot backend

### 贡献与价值

在注册和命令接口之上加入可组合的机器人动作与技能。

### 差异与适用条件

与其他 Open-MHS 同名但代码独立；机器人后端与 MuJoCo 路径应分别评估。

### 可复用部分

参考命令分派与动作组合；把具体后端能力写进设备描述。

### 公开范围与实验记录

已读 MCP 调用分派代码；物理设备与 MuJoCo 示例需按各自后端区分。

[项目说明](https://github.com/tongriyaotxt/open-mhs/blob/main/README.md) · [许可证](https://github.com/tongriyaotxt/open-mhs/blob/main/LICENSE) · [实现入口](https://github.com/tongriyaotxt/open-mhs/blob/main/src/openmhs/mcp/server.py)

## Open MHS · SCUT-ESA

[SCUT-ESA/open-mhs](https://github.com/SCUT-ESA/open-mhs) · 仪器说明 · MIT · 维护者实机记录

统一设备接口加显式后端策略，覆盖 VISA 仪器、嵌入式 I/O 与模拟设备。属于受 MHS 启发的社区工程。

维护主体：SCUT-ESA

接入关系：Agent → MCP / REST / CLI → explicit backend → VISA device

### 贡献与价值

把统一接口落到可选择的后端，并公布两个具体型号的接机结果。

### 差异与适用条件

实机记录覆盖指定 UNI-T 示波器与信号源；其他 I/O 条目有不同状态。

### 可复用部分

借鉴后端选择和型号级验证表，避免把模拟与实机混在同一状态。

### 公开范围与实验记录

维护者列出 UNI-T UPO6102N 与 UTG2062X 的实机验证；其余摄像头、GPIO 等条目仍分别标为实验性或模拟。

[项目说明](https://github.com/SCUT-ESA/open-mhs/blob/main/README.md) · [许可证](https://github.com/SCUT-ESA/open-mhs/blob/main/LICENSE) · [实现入口](https://github.com/SCUT-ESA/open-mhs/blob/main/src/openmhs/core/backend.py)

## Model Hardware Protocol · Cuntinum

[Cuntinum/model-hardware-protocol](https://github.com/Cuntinum/model-hardware-protocol) · 仪器说明 · Apache-2.0 · 接入实现 / 文档

以 discover、read、write、execute 组织设备驱动和共享状态。包名 khp，与 OpenMHP 不是同一项目。

维护主体：Cuntinum

接入关系：Agent → MCP / Python / TypeScript → khp driver & state bus → device

### 贡献与价值

以少量读、写、执行、发现操作和共享状态组织设备接口。

### 差异与适用条件

与 OpenMHP 的任务/租约组织不同；应比较具体状态传播与驱动行为，而非相近名称。

### 可复用部分

比较四类操作是否足够表达设备模式、异步任务与外部状态变化。

### 公开范围与实验记录

公开规范、SDK 与驱动目录；README 的 production grade 定位没有在本次材料中形成跨设备实测依据。

[项目说明](https://github.com/Cuntinum/model-hardware-protocol/blob/main/README.md) · [许可证](https://github.com/Cuntinum/model-hardware-protocol/blob/main/LICENSE)

## Open Agent Hardware Layer

[fredabila/oahl](https://github.com/fredabila/oahl) · 仪器说明 · MIT · 维护者实机记录

discover–reserve–execute–release 生命周期；节点、适配器与传输插件分离，可本地运行或使用可选注册与中继服务。

维护主体：fredabila

接入关系：Agent SDK → OAHL node & reservation → transport plugin → physical device

### 贡献与价值

把设备节点、适配器、传输与占用生命周期分开，支持本地和可选远程发现。

### 差异与适用条件

公开演示是手机 ADB 操作；测量单位、校准和科学数据仍需领域层补充。

### 可复用部分

参考可插拔传输和设备占用机制，再增加测量对象与过程语义。

### 公开范围与实验记录

README 展示 Android 手机 ADB 操作；不能由此推定科研仪器的校准、长任务或读数语义已统一。

[项目说明](https://github.com/fredabila/oahl/blob/main/README.md) · [许可证](https://github.com/fredabila/oahl/blob/main/LICENSE)

## instrMCP

[caidish/instrMCP](https://github.com/caidish/instrMCP) · 常驻执行 · MIT · 接入实现 / 文档

把现有 Jupyter 内核中的 QCoDeS Station 暴露给 Agent，复用参数、仪器快照、数据库与测量工作流。适合已使用 QCoDeS 的实验室。

维护主体：caidish

接入关系：Agent → MCP → live Jupyter kernel → QCoDeS Station → instrument driver

### 贡献与价值

直接复用实验室已经初始化的内核、仪器连接与测量状态。

### 差异与适用条件

与另起设备服务器相比，连接所有权留在现有 QCoDeS 会话；新鲜读数与缓存有明确路径。

### 可复用部分

适合渐进接入已有实验室；继续定义内核重启、任务身份和共享资源行为。

### 公开范围与实验记录

已读参数发现、缓存与 fresh 读取路径；真实连接由运行中的内核及 QCoDeS 驱动持有。

[项目说明](https://github.com/caidish/instrMCP/blob/main/README.md) · [许可证](https://github.com/caidish/instrMCP/blob/main/LICENSE) · [实现入口](https://github.com/caidish/instrMCP/blob/main/instrmcp/servers/jupyter_qcodes/backend/qcodes.py)

## PUDA

[PUDAP/puda](https://github.com/PUDAP/puda) · 常驻执行 · MIT · 接入实现 / 文档

无头物理设备执行平台：消息层、分层驱动、协议运行与结果记录分离。Agent 通过 CLI 和技能编写、验证、运行实验。

维护主体：PUDAP

接入关系：Agent CLI / Skills → protocol runner → NATS → edge driver → machine

### 贡献与价值

将通信、驱动、实验过程和结果记录分开，Agent 可以操作无头执行平台。

### 差异与适用条件

相较单设备服务，更关心跨组件分发与运行环境；CLI 是主要 Agent 入口。

### 可复用部分

参考边缘驱动与实验运行器的边界，以及过程文件到结果记录的对应关系。

### 公开范围与实验记录

已读 CLI 协议执行路径：运行前读取机器命令目录，经 NATS 分发；仓库含边缘驱动示例。

[项目说明](https://github.com/PUDAP/puda/blob/main/README.md) · [许可证](https://github.com/PUDAP/puda/blob/main/LICENSE) · [实现入口](https://github.com/PUDAP/puda/blob/main/apps/cli/internal/cli/protocol-run.go) · [论文](https://arxiv.org/abs/2607.26464)

## Uni-Lab-OS

[deepmodeling/Uni-Lab-OS](https://github.com/deepmodeling/Uni-Lab-OS) · 过程编排 · GPL-3.0 framework + proprietary drivers · 论文实机案例

跨设备实验室编排，结合动作、资源和实验室拓扑。框架、设备适配与工作流编译的分工值得比较。

维护主体：deepmodeling

接入关系：Agent / workflow → action-resource model → ROS 2 → device modules

### 贡献与价值

把动作、资源和实验室拓扑放进统一编排模型，支持跨设备实验。

### 差异与适用条件

需要理解实验室布局和设备角色；框架与设备目录的许可不同。

### 可复用部分

借鉴资源图与工作流编译，同时为适配器定义独立可复用边界。

### 公开范围与实验记录

论文与驱动目录展示物理实验路径。主框架 GPL-3.0；unilabos/devices/ 单独采用 DP Technology 专有许可。

[项目说明](https://github.com/deepmodeling/Uni-Lab-OS/blob/main/README.md) · [许可证](https://github.com/deepmodeling/Uni-Lab-OS/blob/main/LICENSE) · [实现入口](https://github.com/deepmodeling/Uni-Lab-OS/blob/main/NOTICE) · [实现入口](https://github.com/deepmodeling/Uni-Lab-OS/blob/main/unilabos/devices/LICENSE) · [实现入口](https://github.com/deepmodeling/Uni-Lab-OS/blob/main/docs/developer_guide/add_device.md) · [论文](https://arxiv.org/abs/2512.21766)

## Osprey

[als-apg/osprey](https://github.com/als-apg/osprey) · 常驻执行 · BSD-3-Clause · 论文实机案例

面向大型科学设施的 Agent 接口，处理通道语义寻址、设施知识、控制连接与操作过程。已有 EPICS、DOOCS、TANGO 连接器。

维护主体：Berkeley Lab · ALS 加速器物理组

接入关系：Agent / MCP / CLI → semantic channel lookup → facility connector → EPICS / TANGO / DOOCS

### 贡献与价值

让 Agent 在大量设施通道中按设备意义查找与调用，复用设施知识。

### 差异与适用条件

比直接 PV/属性读写桥多出设施上下文与工作流组织；现有写入流程含人工批准。

### 可复用部分

研究语义寻址怎样连接到真实通道，以及设施知识如何随运行记录更新。

### 公开范围与实验记录

项目论文与设施应用提供实验背景；当前实现要求每次硬件写入经人工批准。

[项目说明](https://github.com/als-apg/osprey/blob/main/README.md) · [许可证](https://github.com/als-apg/osprey/blob/main/LICENSE.txt) · [实现入口](https://github.com/als-apg/osprey/blob/main/docs/source/architecture/mcp-servers.rst) · [论文](https://doi.org/10.1063/5.0306302)

## IvoryOS

[ivoryos-ai/IvoryOS](https://github.com/ivoryos-ai/IvoryOS) · 过程编排 · MIT · 论文实机案例

从已有 Python 自动化对象生成控制界面和工作流，包含可选的自然语言工作流设计功能。适合逐步接管已有设备代码。

维护主体：ivoryos-ai

接入关系：Python automation objects → introspection → UI / workflow → existing device methods

### 贡献与价值

从已有 Python 对象提取可操作功能，降低把脚本变成可组合实验的成本。

### 差异与适用条件

通过对象内省接入，而非要求先重写统一驱动；自然语言设计是可选能力。

### 可复用部分

借鉴渐进接入方式，并给自动提取的方法补齐物理含义和结果字段。

### 公开范围与实验记录

有实验室编排论文；当前 README 未声明原生 MCP 服务，不能把 Python API 自动等同于 MCP。

[项目说明](https://github.com/ivoryos-ai/IvoryOS/blob/main/README.md) · [许可证](https://github.com/ivoryos-ai/IvoryOS/blob/main/LICENSE) · [实现入口](https://github.com/ivoryos-ai/IvoryOS/blob/main/ivoryos/parsers/introspection.py) · [论文](https://www.nature.com/articles/s41467-025-60514-w)

## Jumpstarter

[jumpstarter-dev/jumpstarter](https://github.com/jumpstarter-dev/jumpstarter) · 常驻执行 · Apache-2.0 · 接入实现 / 文档

共享和租用真实或虚拟被测硬件，统一电源、串口、CAN、SPI、GPIO 与 USB 控制。Agent 可沿用测试脚本的接口。

维护主体：jumpstarter-dev

接入关系：Agent / test / CI → CLI / Python → lease & exporter → hardware interfaces

### 贡献与价值

把共享硬件变成可租用、可编程的测试资源，统一人工、CI 与 Agent 的入口。

### 差异与适用条件

核心是硬件资源与测试基础设施；实验推理和科学量语义位于其上层。

### 可复用部分

借鉴设备占用、远程导出和复现测试环境。

### 公开范围与实验记录

公开驱动、Python 客户端、gRPC 定义与控制器；属于可被 Agent 使用的硬件基础设施，不是专门的科学语言模型。

[项目说明](https://github.com/jumpstarter-dev/jumpstarter/blob/main/README.md) · [许可证](https://github.com/jumpstarter-dev/jumpstarter/blob/main/LICENSE)

## Lager

[lagerdata/lager](https://github.com/lagerdata/lager) · 常驻执行 · Apache-2.0 · 接入实现 / 文档

用台架 Linux 主机集中连接电源、示波器、调试探针和总线；统一 CLI 可由 Agent、人工或 CI 使用，程序可在设备旁执行。

维护主体：lagerdata

接入关系：Agent / CI CLI → bench Linux box → named Net → instrument channel

### 贡献与价值

用命名测试点抽象实际仪器通道，并把脚本放到台架主机执行。

### 差异与适用条件

相较直接写厂商指令，程序面向供电轨、总线和探针；换仪器时可保留测试点名称。

### 可复用部分

借鉴物理连接命名与本地过程执行，记录测试点到通道的版本映射。

### 公开范围与实验记录

README 与文档提供具体仪器和台架部署路径；可复用的是台架执行层。

[项目说明](https://github.com/lagerdata/lager/blob/main/README.md) · [许可证](https://github.com/lagerdata/lager/blob/main/LICENSE)

## Experiment Automation Agents

[AdvancedPhotonSource/EAA](https://github.com/AdvancedPhotonSource/EAA) · 常驻执行 · Unspecified · 论文实机案例

面向需要视觉反馈的科学实验 Agent 运行环境；支持图像工具结果、确定性工作流及实验任务管理。

维护主体：Argonne · Advanced Photon Source

接入关系：Experiment agent → image-aware tools → instrument services → experiment

### 贡献与价值

把图像结果、工作流与实验会话纳入同一 Agent 环境。

### 差异与适用条件

研究贡献在视觉实验运行方式；仓库已指向 EAA-Pi，应沿迁移关系阅读。

### 可复用部分

研究实验上下文和视觉工具结果怎样跨步骤保留。

### 公开范围与实验记录

有显微实验论文；README 已宣布迁移到 EAA-Pi。当前仓库未识别到顶层许可证。

[项目说明](https://github.com/AdvancedPhotonSource/EAA/blob/main/README.md) · [论文](https://pmc.ncbi.nlm.nih.gov/articles/PMC13633048/)

## EAA-Pi

[AdvancedPhotonSource/EAA-Pi](https://github.com/AdvancedPhotonSource/EAA-Pi) · 常驻执行 · Unspecified · 接入实现 / 文档

基于 pi-experiment-ops 的实验助手界面，终端与网页共享工作区、工具配置和实验会话。

维护主体：Argonne · Advanced Photon Source

接入关系：Terminal / web UI → pi-experiment-ops → MCP instrument server → device

### 贡献与价值

终端和网页共用实验工作区，使不同交互入口使用同一工具与会话。

### 差异与适用条件

它是应用入口；仪器驱动来自下游 MCP 服务，旧 EAA 实验结果不能自动转移。

### 可复用部分

借鉴界面与执行环境的分离，保留可替换的 Agent 前端。

### 公开范围与实验记录

作为 EAA 后继工程公开；实际仪器能力取决于接入的 MCP 服务，不能继承旧论文全部验证范围。

[项目说明](https://github.com/AdvancedPhotonSource/EAA-Pi/blob/main/README.md)

## pi-experiment-ops

[AdvancedPhotonSource/pi-experiment-ops](https://github.com/AdvancedPhotonSource/pi-experiment-ops) · 常驻执行 · Unspecified · 接入实现 / 文档

组合实验工具、后台执行、持久终端和会话检索，为实验应用提供可复用 Agent 执行环境。

维护主体：Argonne · Advanced Photon Source

接入关系：Pi agent → extension / CodeMode → persistent tools → MCP services

### 贡献与价值

为实验 Agent 提供后台运行、持久终端、会话检索及工具执行组件。

### 差异与适用条件

相比 EAA-Pi 的界面，这里提供可复用运行组件；具体硬件由外部服务承担。

### 可复用部分

借鉴会话生命周期与仪器任务生命周期的分离。

### 公开范围与实验记录

MCP 适配器连接独立仪器服务；运行环境本身不提供通用设备驱动。

[项目说明](https://github.com/AdvancedPhotonSource/pi-experiment-ops/blob/main/README.md)

## LabMCP · K-Dense

[K-Dense-AI/lab-instrument-mcps](https://github.com/K-Dense-AI/lab-instrument-mcps) · 设备桥接 · Apache-2.0 · 模拟验证

单仓库仪器适配集合，覆盖电子测量、光谱、温控、泵、显微、液体处理和设施协议。组件清单单列，避免把服务器数量当作独立项目数量。

维护主体：K-Dense

接入关系：Agent → MCP server package → device protocol adapter → simulated backend

### 贡献与价值

把多个设备连接器按一致方式组织、安装和发现，形成可扩展的适配仓库。

### 差异与适用条件

覆盖面来自 32 个组件；当前目录全部为模拟状态，不能作为 32 类实机验证。

### 可复用部分

借鉴组件清单、工具命名和型号级贡献流程，用实机记录逐步扩展。

### 公开范围与实验记录

当前机器可读目录含 32 个服务器、411 个工具，全部标为 simulated；其中质谱数据和工作单工具不是直接设备控制。

[项目说明](https://github.com/K-Dense-AI/lab-instrument-mcps/blob/main/README.md) · [许可证](https://github.com/K-Dense-AI/lab-instrument-mcps/blob/main/LICENSE) · [实现入口](https://github.com/K-Dense-AI/lab-instrument-mcps/blob/main/packages/labmcp/src/labmcp/catalog.json)

## LabLink

[techmanual-ai/lablink-mcp](https://github.com/techmanual-ai/lablink-mcp) · 设备桥接 · MIT · 接入实现 / 文档

多种传输接口汇入同一 MCP 服务，便于把已有指令和脚本接给 Agent。设备语义主要仍由配置和驱动表达。

维护主体：techmanual-ai

接入关系：Agent → MCP → configured transport → VISA / SSH / REST / Serial / Python

### 贡献与价值

用一个服务汇合多种实验室已有通信入口，减少逐协议接线成本。

### 差异与适用条件

传输通用性较强；设备的量、模式和操作结果仍由命令配置与驱动解释。

### 可复用部分

作为异构设备接入层，另行建立共同的测量与动作语义。

### 公开范围与实验记录

提供五类连接驱动与配置示例；通用通信能力不代表任意设备已经适配。

[项目说明](https://github.com/techmanual-ai/lablink-mcp/blob/main/README.md) · [许可证](https://github.com/techmanual-ai/lablink-mcp/blob/main/LICENSE)

## scpi-mcp

[armchairdeity/mcp-server-scpi](https://github.com/armchairdeity/mcp-server-scpi) · 设备桥接 · MIT · 接入实现 / 文档

将示波器采集与测量目标封装为工具，仪器后端负责具体 SCPI。首个目标是 Rigol DS1054Z。

维护主体：armchairdeity

接入关系：Agent → goal-level scope tools → Rigol backend → PyVISA / SCPI

### 贡献与价值

把采集目标封装成示波器工具，减少 Agent 直接拼接底层命令。

### 差异与适用条件

采用有边界的设备操作面，首个目标为 Rigol DS1054Z；不是任意 SCPI 透传。

### 可复用部分

比较目标级操作与原始指令的分工，为稳定测量过程建立模板。

### 公开范围与实验记录

有 Rigol 与 mock 后端；README 明确不暴露任意原始 SCPI，且没有信号源或逻辑分析仪功能。

[项目说明](https://github.com/armchairdeity/mcp-server-scpi/blob/main/README.md) · [许可证](https://github.com/armchairdeity/mcp-server-scpi/blob/main/LICENSE)

## oscilloscope-mcp

[masahiro-999/oscilloscope-mcp](https://github.com/masahiro-999/oscilloscope-mcp) · 设备桥接 · MIT · 接入实现 / 文档

网络示波器设置、触发、波形读取和测量反馈；返回结构化数据、图像及可独立查看的波形页面。

维护主体：masahiro-999

接入关系：Agent → MCP acquisition tools → SCPI over TCP → oscilloscope

### 贡献与价值

把示波器设置、触发与波形结果组织成 Agent 可读的反馈。

### 差异与适用条件

除数值外提供图像和独立波形页面，适合观察信号形状的调试任务。

### 可复用部分

借鉴波形摘要与完整数据同时返回的方式。

### 公开范围与实验记录

README 描述实际台架与 FPGA 调试路径；设备兼容性仍按项目列出的型号确认。

[项目说明](https://github.com/masahiro-999/oscilloscope-mcp/blob/main/README.md) · [许可证](https://github.com/masahiro-999/oscilloscope-mcp/blob/main/LICENSE)

## lecroy-mcp

[lucasgerads/lecroy-mcp](https://github.com/lucasgerads/lecroy-mcp) · 设备桥接 · AGPL-3.0 · 维护者实机记录

LeCroy 示波器控制与波形采集，使用 LAN VXI-11 或 USB。

维护主体：lucasgerads

接入关系：Agent → MCP → VXI-11 / USB SCPI → LeCroy oscilloscope

### 贡献与价值

提供 LeCroy 示波器的具体连接与波形采集路径。

### 差异与适用条件

协议选择影响能否接通：该实现使用 VXI-11 / USB，不支持 VICP。

### 可复用部分

为适配器同时记录品牌、型号、传输与模式，避免仅按品牌匹配。

### 公开范围与实验记录

仓库附运行演示；LAN 路径要求 VXI-11，README 明确不支持 LeCroy VICP 模式。

[项目说明](https://github.com/lucasgerads/lecroy-mcp/blob/main/README.md) · [许可证](https://github.com/lucasgerads/lecroy-mcp/blob/main/LICENSE)

## siglent-scpi-mcp

[mp911de/siglent-scpi-mcp](https://github.com/mp911de/siglent-scpi-mcp) · 设备桥接 · Apache-2.0 · 维护者实机记录

Siglent 示波器和电源的类型化工具，记录实际发送的 SCPI 命令。

维护主体：mp911de

接入关系：Agent → typed MCP tools → logged SCPI / TCP → scope & supply

### 贡献与价值

同时覆盖示波器和电源，并把实际指令留在记录中。

### 差异与适用条件

实测型号与波形缩放链有具体记录，便于定位数据解释错误。

### 可复用部分

借鉴从原始波形到物理单位的转换记录及台架复现材料。

### 公开范围与实验记录

维护者报告一次 SDS1204X HD 与 SPD3303X-E 台架验证，包括波形缩放链；其余列出型号不能一并视为实测。

[项目说明](https://github.com/mp911de/siglent-scpi-mcp/blob/main/README.md) · [许可证](https://github.com/mp911de/siglent-scpi-mcp/blob/main/LICENSE)

## scope-mcp

[Netlist-Studio/scope-mcp](https://github.com/Netlist-Studio/scope-mcp) · 设备桥接 · MIT · 维护者实机记录

Keysight/Agilent 示波器的设置、截图、波形下载、测量与串行解码。

维护主体：Netlist-Studio

接入关系：Agent → MCP → PyVISA / Ethernet SCPI → Keysight / Agilent scope

### 贡献与价值

集中提供截图、波形、测量和解码，形成较完整的示波器操作面。

### 差异与适用条件

给出实测型号与固件版本；可据此判断兼容范围，而非依赖品牌标签。

### 可复用部分

建立带固件版本的驱动兼容表和测量结果格式。

### 公开范围与实验记录

README 指明实测 Agilent MSOX2024A，固件 02.43.2018020635。

[项目说明](https://github.com/Netlist-Studio/scope-mcp/blob/main/README.md) · [许可证](https://github.com/Netlist-Studio/scope-mcp/blob/main/LICENSE)

## dwf-mcp-server

[KenosInc/dwf-mcp-server](https://github.com/KenosInc/dwf-mcp-server) · 设备桥接 · MIT · 接入实现 / 文档

Digilent WaveForms 设备的示波器、任意波形与逻辑分析接口。

维护主体：KenosInc

接入关系：Agent → MCP → dwfpy → WaveForms SDK → Digilent device

### 贡献与价值

复用 WaveForms SDK，让同一设备的模拟与数字功能进入工具接口。

### 差异与适用条件

SDK 封装减少底层开发，但运行仍需要独立的厂商库。

### 可复用部分

清楚分开开源适配层、厂商运行库与设备能力描述。

### 公开范围与实验记录

开源服务依赖单独取得的专有 libdwf/运行库；不能把服务端 MIT 许可理解为整个 SDK 开源。

[项目说明](https://github.com/KenosInc/dwf-mcp-server/blob/main/README.md) · [许可证](https://github.com/KenosInc/dwf-mcp-server/blob/main/LICENSE)

## Instrument MCP

[zeng-andrew/instrument-mcp](https://github.com/zeng-andrew/instrument-mcp) · 设备桥接 · Unspecified · 接入实现 / 文档

集成频谱分析仪、无线综测仪、电源、温箱及逻辑分析仪，使用 YAML 描述命令并管理多仪器会话。

维护主体：zeng-andrew

接入关系：Agent → MCP sessions → YAML commands → SCPI / Modbus / USB devices

### 贡献与价值

用配置描述命令并管理多仪器会话，覆盖射频与环境测试设备。

### 差异与适用条件

核心差异是配置式适配；命令映射仍需给出单位、返回解析和型号约束。

### 可复用部分

研究哪些差异可配置化，哪些必须保留在驱动代码中。

### 公开范围与实验记录

列出 Keysight MXA/EXA、R&S CMW500 与 DSLogic 等适配目标；未识别到许可证。

[项目说明](https://github.com/zeng-andrew/instrument-mcp/blob/main/README.md)

## daqmx-mcp

[BrianDavidCouch/daqmx-mcp](https://github.com/BrianDavidCouch/daqmx-mcp) · 设备桥接 · Apache-2.0 · 接入实现 / 文档

发现 NI DAQ 设备并执行有限长度的模拟电压和数字输入采集。

维护主体：BrianDavidCouch

接入关系：Agent → MCP / plugin → nidaqmx → NI DAQ input channels

### 贡献与价值

把 NI 设备发现与有限长度输入采集做成紧凑工具集。

### 差异与适用条件

范围明确聚焦输入；输出、连续采集与任意属性写入不在当前实现内。

### 可复用部分

为采集任务定义长度、时钟、输入类型和完成条件。

### 公开范围与实验记录

社区项目；当前版本没有输出、连续采集或任意属性写入。NI 驱动独立安装。

[项目说明](https://github.com/BrianDavidCouch/daqmx-mcp/blob/main/README.md) · [许可证](https://github.com/BrianDavidCouch/daqmx-mcp/blob/main/LICENSE)

## DAQiFi Core

[daqifi/daqifi-core](https://github.com/daqifi/daqifi-core) · 设备桥接 · MIT · 接入实现 / 文档

厂商公开的无线采集 SDK 与 MCP 服务，涵盖通道配置、采样、数字 I/O、PWM、模拟输出和 SD 卡记录。

维护主体：DAQiFi

接入关系：Agent → MCP → DAQiFi .NET SDK → Wi-Fi / USB device

### 贡献与价值

由设备厂商在同一 SDK 上提供 Agent 接口，贯通配置、采集与记录下载。

### 差异与适用条件

与外部社区包装不同，MCP 与设备 SDK 同仓维护；能力仍按型号区分。

### 可复用部分

借鉴厂商维护驱动与开放工具接口共同演进的方式。

### 公开范围与实验记录

README 将采集控制和记录下载连成完整路径；具体能力取决于 DAQiFi 设备型号。

[项目说明](https://github.com/daqifi/daqifi-core/blob/main/README.md) · [许可证](https://github.com/daqifi/daqifi-core/blob/main/LICENSE) · [实现入口](https://github.com/daqifi/daqifi-core/tree/main/src/Daqifi.Mcp)

## LabVIEW MCP Server Toolkit

[JanGoebel/LabVIEW-MCP-Server-Toolkit](https://github.com/JanGoebel/LabVIEW-MCP-Server-Toolkit) · 设备桥接 · MIT · 接入实现 / 文档

让已有 LabVIEW 应用以工具、资源和提示的方式暴露 VI。适合直接包装实验室现有控制程序。

维护主体：JanGoebel

接入关系：Agent → MCP HTTP toolkit → exposed VI → existing device code

### 贡献与价值

让实验室直接暴露已有 VI，保留已经工作的仪器控制程序。

### 差异与适用条件

处理的是运行接口；与修改 VI 内部图形程序的开发工具不同。

### 可复用部分

定义 VI 的参数、物理影响和结果定义，再包装成可发现能力。

### 公开范围与实验记录

开源工具包；LabVIEW 本体与仪器 VI 的依赖、许可分别存在。

[项目说明](https://github.com/JanGoebel/LabVIEW-MCP-Server-Toolkit/blob/main/readme.md) · [许可证](https://github.com/JanGoebel/LabVIEW-MCP-Server-Toolkit/blob/main/LICENSE)

## LabVIEW MCP · Zühlke

[Zuehlke/labview-mcp](https://github.com/Zuehlke/labview-mcp) · 仪器开发 · MIT · 接入实现 / 文档

Agent 可读取、修改和运行 LabVIEW 程序，主要处于开发工具层；能否控制设备取决于所运行 VI。

维护主体：Zühlke

接入关系：Agent → MCP → gRPC lvai.LVAI → LabVIEW program editing / running

### 贡献与价值

把 LabVIEW 程序本身纳入 Agent 的读取、修改与运行循环。

### 差异与适用条件

它改变的是控制软件；真实设备能力取决于 VI，接口还依赖内部 LabVIEW 服务。

### 可复用部分

区分开发期编辑与运行期仪器操作，分别保存程序版本和实验记录。

### 公开范围与实验记录

依赖 LabVIEW 内部 lvai.LVAI 服务，README 明确它不是已发布、稳定承诺的 NI API。

[项目说明](https://github.com/Zuehlke/labview-mcp/blob/main/README.md) · [许可证](https://github.com/Zuehlke/labview-mcp/blob/main/LICENSE)

## OpenFlexure-MCP

[GSIBabu/OpenFlexure-MCP](https://github.com/GSIBabu/OpenFlexure-MCP) · 设备桥接 · GPL-3.0 · 接入实现 / 文档

通过 OpenFlexure 客户端操作载物台、拍照、自动对焦、Z-stack 与扩展功能。

维护主体：GSIBabu

接入关系：Agent → MCP → OpenFlexure Python client → microscope HTTP API

### 贡献与价值

在现有开源显微镜控制 API 上提供移动、成像与对焦工具。

### 差异与适用条件

接入依赖已联网的 OpenFlexure 系统，主要新增的是 Agent 调用面。

### 可复用部分

借鉴对焦与 Z-stack 等过程级能力，而不只暴露单步电机命令。

### 公开范围与实验记录

接入路径指向同一网络的真实 OpenFlexure 显微镜；仓库未给出系统化实测矩阵。

[项目说明](https://github.com/GSIBabu/OpenFlexure-MCP/blob/main/README.md) · [许可证](https://github.com/GSIBabu/OpenFlexure-MCP/blob/main/LICENSE)

## microscope-agent

[BioNanomics/microscope-agent](https://github.com/BioNanomics/microscope-agent) · 设备桥接 · MIT · 接入实现 / 文档

面向 Nikon Ti2-E 与 Baumer 相机的紧凑接口，读位置、移动 XY、采图；图像与实际位置及状态修订号关联。

维护主体：BioNanomics

接入关系：Agent → MCP → Nikon / GenICam adapter → stage & camera

### 贡献与价值

将图像、真实位置与状态修订号关联，让后续判断知道观察来自哪个配置。

### 差异与适用条件

比仅返回图片的工具多出测量上下文；开放的运动范围有明确约束。

### 可复用部分

把图像与位置、曝光、配置版本作为同一次观测返回。

### 公开范围与实验记录

提供 SDK 与 mock 路径；返回图像预览及完整文件。当前工具刻意不开放绝对 Z 移动。

[项目说明](https://github.com/BioNanomics/microscope-agent/blob/main/README.md) · [许可证](https://github.com/BioNanomics/microscope-agent/blob/main/LICENSE)

## Agent-Lens

[aicell-lab/agent-lens](https://github.com/aicell-lab/agent-lens) · 过程编排 · MIT · 接入实现 / 文档

将显微镜控制、机器人样本转移、图像分割、相似搜索和 OME-Zarr 数据组织在一起。

维护主体：KTH / SciLifeLab · AICell Lab

接入关系：Agent / web UI → Hypha services → microscope & sample handling → OME-Zarr / BioEngine

### 贡献与价值

把显微采集、样品转移、分析服务和图像数据组织成一套工作平台。

### 差异与适用条件

价值在服务协同和数据组织；接入主线是 Hypha，而非以 MCP 为唯一中心。

### 可复用部分

借鉴采集、分析与数据浏览共用同一实验对象的设计。

### 公开范围与实验记录

公开服务注册代码与在线演示入口；主要设备调用经 Hypha 服务，未将原生 MCP 标作已确认接口。

[项目说明](https://github.com/aicell-lab/agent-lens/blob/main/README.md) · [许可证](https://github.com/aicell-lab/agent-lens/blob/main/LICENSE) · [实现入口](https://github.com/aicell-lab/agent-lens/blob/main/agent_lens/register_tools_service.py)

## Agentic microscope

[kyu-softmatter/agentic-microscope](https://github.com/kyu-softmatter/agentic-microscope) · 设备桥接 · MIT · 接入实现 / 文档

将研究目标转为有硬件边界与校准依据的显微镜配置，涵盖显微镜、光镊与压电平台。

维护主体：kyu-softmatter

接入关系：Research goal → MCP configuration → calibrated device settings → apply & readback

### 贡献与价值

把研究目标转成校准范围内的显微配置，并检查应用后的实际状态。

### 差异与适用条件

强调配置含义与实际回读，覆盖显微镜、光镊和压电平台；代码向后继仓库迁移。

### 可复用部分

建立目标参数、设备参数和观测状态之间可检查的映射。

### 公开范围与实验记录

已读设置、应用与回读代码。README 提醒光镊 TCP 接口的接受回执不等于动作完成，并宣布向 soft-matter-agents 迁移。

[项目说明](https://github.com/kyu-softmatter/agentic-microscope/blob/main/README.md) · [许可证](https://github.com/kyu-softmatter/agentic-microscope/blob/main/LICENSE) · [实现入口](https://github.com/kyu-softmatter/agentic-microscope/blob/main/hardware/microscope.py)

## soft-matter-agents

[kyu-softmatter/soft-matter-agents](https://github.com/kyu-softmatter/soft-matter-agents) · 过程编排 · MIT · 接入实现 / 文档

显微镜、模拟、文献与桥接 Agent 的组合工程；显微镜模块是旧 Agentic microscope 的后继位置。

维护主体：kyu-softmatter

接入关系：Agent workflow → microscope_agent / simulation / literature modules → configured backend

### 贡献与价值

把显微控制、模拟与文献模块组合成软物质实验工作流。

### 差异与适用条件

研究能力分布在多个模块；只有实际设备模块承担物理控制。

### 可复用部分

借鉴模块分工与迁移关系，分别记录模拟、知识和实机执行的产物。

### 公开范围与实验记录

作为迁移入口收录；各模块不都连接物理设备，具体硬件能力仍需查 microscope_agent。

[项目说明](https://github.com/kyu-softmatter/soft-matter-agents/blob/main/README.md) · [许可证](https://github.com/kyu-softmatter/soft-matter-agents/blob/main/LICENSE)

## AILA

[M3RG-IITD/AILA](https://github.com/M3RG-IITD/AILA) · 实验决策 · MIT · 论文实机案例

原子力显微镜实验中的语言模型助手，结合任务分解、工具调用和反馈。

维护主体：IIT Delhi · M3RG

接入关系：Research request → planning & feedback agents → AFM control tools → AFM experiment

### 贡献与价值

把任务分解、工具执行与反馈判断用于实际 AFM 实验，并提供评测材料。

### 差异与适用条件

主要贡献是实验任务上的 Agent 组织与表现；不是跨厂商 AFM 互操作规范。

### 可复用部分

借鉴真实任务、仪器环境与失败类型共同构成的评测方式。

### 公开范围与实验记录

Nature Communications 论文报告实机 AFM 实验；代码与基准公开，重用需匹配论文的仪器控制环境。

[项目说明](https://github.com/M3RG-IITD/AILA/blob/main/README.md) · [许可证](https://github.com/M3RG-IITD/AILA/blob/main/LICENSE.md) · [论文](https://www.nature.com/articles/s41467-025-64105-7)

## LLM-directed-SPM

[DIAOZHUO/LLM-directed-SPM](https://github.com/DIAOZHUO/LLM-directed-SPM) · 实验决策 · Unspecified · 论文实机案例

扫描探针显微实验中的命令生成、知识库和专门小模型；包含本地模型服务与模型训练材料。

维护主体：DIAOZHUO

接入关系：User task → domain model & knowledge → WebSocket / spmutil → scanning probe microscope

### 贡献与价值

把扫描探针知识、命令生成和专门小模型结合，研究领域模型如何操作仪器。

### 差异与适用条件

与只调用通用大模型的桥接不同，公开材料包含模型训练与本地服务。

### 可复用部分

研究领域知识应放进模型、技能还是设备描述，并用同一实验任务比较。

### 公开范围与实验记录

论文描述物理扫描探针实验；仓库未识别到顶层许可证，模型训练代码与完整设备接入应分别评估。

[项目说明](https://github.com/DIAOZHUO/LLM-directed-SPM/blob/main/readme.md) · [论文](https://arxiv.org/abs/2602.20669)

## Quailbot Pi

[BB-84C/quailbot-pi](https://github.com/BB-84C/quailbot-pi) · 常驻执行 · ISC · 接入实现 / 文档

将仪器工作区变为参数、动作、图像回读与多步程序的固定工具接口；操作与后续观察分别记录。Nanonis 路径依赖外部 nqctl。

维护主体：BB-84C

接入关系：Pi agent → workspace contract → instrument CLI / nqctl → Nanonis backend

### 贡献与价值

用固定工作区说明组织参数、动作、图像与多步程序，分开记录动作和观察。

### 差异与适用条件

以 CLI 与工作区文件承接仪器能力；Nanonis 驱动仍由外部 nqctl 提供。

### 可复用部分

借鉴工作区作为实验状态与操作知识载体，明确外部驱动版本。

### 公开范围与实验记录

公开 Pi 扩展与工作区说明；STM 论文是相关实验背景，不据此宣称该扩展独立包含全部硬件驱动。

[项目说明](https://github.com/BB-84C/quailbot-pi/blob/main/README.md) · [许可证](https://github.com/BB-84C/quailbot-pi/blob/main/LICENSE) · [论文](https://arxiv.org/abs/2609.27302)

## VISION

[CFN-softbio/VISION](https://github.com/CFN-softbio/VISION) · 实验决策 · Unspecified · 论文实机案例

以语音或文字把用户意图转为束线操作代码，模块化处理转录、分类、编程与分析。

维护主体：Brookhaven · CFN 团队

接入关系：Voice / text → classification & code generation → Bluesky workstation → beamline

### 贡献与价值

将自然语言意图转成已有束线环境可执行的操作代码。

### 差异与适用条件

重点在自然交互与模块化任务转换；确定性执行由 Bluesky 等既有系统承担。

### 可复用部分

借鉴意图到可审阅实验计划的转换，并保留生成代码与运行结果。

### 公开范围与实验记录

项目展示 NSLS-II 11-BM CMS 工作站部署和用户确认后执行；不是无人闭环的通用仪器协议。未识别到许可证。

[项目说明](https://github.com/CFN-softbio/VISION/blob/main/README.md) · [论文](https://doi.org/10.1088/2632-2153/add9e4)

## LeeQ

[ShuxiangCao/LeeQ](https://github.com/ShuxiangCao/LeeQ) · 常驻执行 · BSD-3-Clause · 论文实机案例

超导量子器件的脉冲实验、扫描、校准状态与分析框架；可向 Agent 提供实验描述及图文检查接口。

维护主体：ShuxiangCao

接入关系：Experiment agent / Python → LeeQ experiment & sweep → pulse backend → quantum device

### 贡献与价值

提供可被 Agent 发现和执行的量子实验对象、扫描、校准状态与结果分析。

### 差异与适用条件

它是实验与控制基础，而 k-agents 等负责选择和评价实验。

### 可复用部分

借鉴可组合实验对象，以及实验描述与结果检查接口。

### 公开范围与实验记录

k-agents 论文报告量子校准实验；仓库同时提供模拟路径，应按后端识别实验来源。

[项目说明](https://github.com/ShuxiangCao/LeeQ/blob/main/README.md) · [许可证](https://github.com/ShuxiangCao/LeeQ/blob/main/LICENSE) · [论文](https://doi.org/10.1016/j.patter.2025.101372)

## k-agents

[EvoEvolver/k_agents](https://github.com/EvoEvolver/k_agents) · 实验决策 · Unspecified · 论文实机案例

围绕已有实验库发现、执行和判断校准实验，保留实验知识与视觉结果。

维护主体：EvoEvolver

接入关系：Calibration agent → experiment selection & inspection → LeeQ → quantum experiment

### 贡献与价值

围绕已有实验库建立选择、执行和视觉判断的校准循环。

### 差异与适用条件

把实验知识用于下一步决策；当前 README 指向 NVIDIA 后继参考工程。

### 可复用部分

借鉴实验技能的描述、发现与校准结果判断。

### 公开范围与实验记录

论文有实机量子校准；README 已指向 NVIDIA Quantum Calibration Agent Blueprint。当前仓库未识别到许可证。

[项目说明](https://github.com/EvoEvolver/k_agents/blob/main/README.md) · [论文](https://arxiv.org/abs/2412.07978)

## Quantum Calibration Agent Blueprint

[NVIDIA/Quantum-Calibration-Agent-Blueprint](https://github.com/NVIDIA/Quantum-Calibration-Agent-Blueprint) · 实验决策 · Apache-2.0 · 接入实现 / 文档

量子器件校准 Agent 参考工程，包含实验发现、执行、图像分析、工作流和结果存储。

维护主体：NVIDIA

接入关系：Calibration agent → registered Python experiment → user control backend → results store

### 贡献与价值

提供实验发现、执行、图像分析与结果存储的校准 Agent 参考结构。

### 差异与适用条件

用户提供实验脚本完成设备接入；平台知名度不能替代具体控制器适配。

### 可复用部分

借鉴实验插件与结果模型，让控制器接入独立于 Agent 界面。

### 公开范围与实验记录

NVIDIA 公开 Apache-2.0 工程，实验通过用户提供的 Python 脚本接入；不能把参考界面视为已覆盖所有量子控制器。

[项目说明](https://github.com/NVIDIA/Quantum-Calibration-Agent-Blueprint/blob/main/README.md) · [许可证](https://github.com/NVIDIA/Quantum-Calibration-Agent-Blueprint/blob/main/LICENSE)

## CALMS

[mcherukara/CALMS](https://github.com/mcherukara/CALMS) · 实验决策 · BSD-3-Clause · 维护者实机记录

上下文与工具增强的科学设施助手，将仪器知识和操作函数纳入交互。

维护主体：mcherukara

接入关系：User task → retrieved instrument context → Python tool calls → facility device

### 贡献与价值

将设施知识检索与可执行操作函数结合，减少纯对话与实际操作的脱节。

### 差异与适用条件

相较纯手册问答，它能调用工具；后续 APS 版本进一步连接机器人与纳米探针。

### 可复用部分

让操作知识与工具签名、设备上下文一起版本化。

### 公开范围与实验记录

早期公开实现附演示；许可文本为三条款 BSD。后续机器人与束线工作另见 APS 仓库。

[项目说明](https://github.com/mcherukara/CALMS/blob/main/README.md) · [许可证](https://github.com/mcherukara/CALMS/blob/main/LICENSE)

## CALMS · APS experimental agents

[AdvancedPhotonSource/CALMS](https://github.com/AdvancedPhotonSource/CALMS) · 实验决策 · Unspecified · 论文实机案例

面向 North N9 机器人与 X-ray nanoprobe 的可教学实验 Agent 工作流。

维护主体：Argonne · Advanced Photon Source

接入关系：Experiment agent → teachable workflow → robot / nanoprobe commands → experiment

### 贡献与价值

把可教学的实验流程连接到机器人与 X-ray nanoprobe 操作。

### 差异与适用条件

重点由通用设施助手转向具体实验流程；发布内容与早期 CALMS 分仓维护。

### 可复用部分

研究专家示范如何形成可读、可执行并可修改的实验过程。

### 公开范围与实验记录

README 列出机器人、纳米探针命令模块及运行视频；许可证未识别，分支以仓库当前默认分支为准。

[项目说明](https://github.com/AdvancedPhotonSource/CALMS/blob/main/README.md) · [论文](https://doi.org/10.1038/s41524-026-02005-0)

## Opentrons MCP

[yerbymatey/opentrons-mcp](https://github.com/yerbymatey/opentrons-mcp) · 设备桥接 · MIT · 接入实现 / 文档

结合 API 文档检索与机器人协议上传、运行管理、归位及状态读取，面向 OT-2/Flex。

维护主体：yerbymatey

接入关系：Agent → MCP → Opentrons HTTP API → OT-2 / Flex

### 贡献与价值

把机器人协议与运行管理直接接到 Agent，同时提供相关文档查询。

### 差异与适用条件

依赖机器人已有 HTTP 服务；知识检索与真正驱动动作的工具承担不同职责。

### 可复用部分

把协议文件、运行 ID、步骤状态和样品信息连成同一记录。

### 公开范围与实验记录

设备调用走机器人 HTTP API；文档查询工具与会驱动机器人动作的工具分别存在。

[项目说明](https://github.com/yerbymatey/opentrons-mcp/blob/main/README.md) · [许可证](https://github.com/yerbymatey/opentrons-mcp/blob/main/LICENSE)

## plr-mcp

[di-omics/plr-mcp](https://github.com/di-omics/plr-mcp) · 设备桥接 · MIT · 模拟验证

将液体处理、酶标仪、热循环仪和加热振荡器操作暴露为 MCP，复用 PyLabRobot 后端。

维护主体：di-omics

接入关系：Agent → MCP → PyLabRobot → chatterbox / STAR backend

### 贡献与价值

复用 PyLabRobot 的设备和资源模型，一次连接多类液体处理设备。

### 差异与适用条件

抽象层较高，默认验证来自模拟器；真实 STAR 后端是独立部署路径。

### 可复用部分

沿用既有甲板和容器模型，为真实液体过程补充运行记录。

### 公开范围与实验记录

默认以 chatterbox 模拟器端到端验证；有真实 STAR 后端入口与接机说明，不能把模拟验证等同于实机验证。

[项目说明](https://github.com/di-omics/plr-mcp/blob/main/README.md) · [许可证](https://github.com/di-omics/plr-mcp/blob/main/LICENSE)

## OpenLabAI

[nygmeta/OpenLabAI](https://github.com/nygmeta/OpenLabAI) · 过程编排 · MIT · 维护者实机记录

自然语言液体处理工作流，包含 Opentrons、Biomek、Hamilton 与实验记录连接。

维护主体：nygmeta

接入关系：Agent → MCP workflow → robot-specific API / COM / PyLabRobot → robot

### 贡献与价值

尝试把不同液体处理平台接到共同的自然语言工作流中。

### 差异与适用条件

各后端进度不一致；已实测的 OT-2 读取与归位不能代表所有执行动作。

### 可复用部分

按动作和后端维护能力矩阵，将接机与工作流复用分别验证。

### 公开范围与实验记录

维护者报告 OT-2 读取、状态、归位与协议生成已接实机，上传/启动等执行工具尚未实机运行；Hamilton 和台式设备层为模拟。

[项目说明](https://github.com/nygmeta/OpenLabAI/blob/main/README.md) · [许可证](https://github.com/nygmeta/OpenLabAI/blob/main/LICENSE)

## LabscriptAI OT

[KRATSZ/labscriptai-ot](https://github.com/KRATSZ/labscriptai-ot) · 过程编排 · LabscriptAI Research Citation License v1.0 · 接入实现 / 文档

面向 Opentrons 的 Agent 插件，集成协议编写、模拟、技能和实时运行辅助。

维护主体：KRATSZ

接入关系：Agent plugin / Skills → protocol generation → local simulation → Opentrons

### 贡献与价值

把写协议、模拟和运行辅助放进同一 Agent 开发流程。

### 差异与适用条件

更偏实验程序开发与使用体验；其限制性许可影响商业复用。

### 可复用部分

借鉴编写、检查、执行、回读之间的连续工作流。

### 公开范围与实验记录

当前采用 LabscriptAI Research Citation License，商业使用须另行许可；不列入标准开源许可组。

[项目说明](https://github.com/KRATSZ/labscriptai-ot/blob/main/README.md) · [许可证](https://github.com/KRATSZ/labscriptai-ot/blob/main/LICENSE) · [论文](https://doi.org/10.1101/2025.09.30.679666)

## Coscientist

[gomesgroup/coscientist](https://github.com/gomesgroup/coscientist) · 实验决策 · Apache-2.0 + Commons Clause · 论文实机案例

语言模型组织文献、程序和实验工具完成化学研究；是早期真实实验的重要案例。

维护主体：Carnegie Mellon · Gomes Group

接入关系：Research goal → literature & code tools → laboratory API → robotic chemistry

### 贡献与价值

展示语言模型如何组合检索、编程和实验工具完成化学任务。

### 差异与适用条件

价值在端到端研究组织与实验展示；公共发布与论文完整实验环境不同。

### 可复用部分

借鉴研究任务的工具分解和实验反馈设计，另行落实实验室接入。

### 公开范围与实验记录

论文报告机器人化学实验；公开代码不等于论文的完整可部署实验室。许可为 Apache-2.0 加 Commons Clause。

[项目说明](https://github.com/gomesgroup/coscientist/blob/main/README.md) · [许可证](https://github.com/gomesgroup/coscientist/blob/main/LICENSE) · [论文](https://doi.org/10.1038/s41586-023-06792-0)

## ChemAgents

[pic-ai-robotic-chemistry/ChemAgents](https://github.com/pic-ai-robotic-chemistry/ChemAgents) · 实验决策 · Unspecified · 论文实机案例

多 Agent 化学研究系统，连接实验协议、机器人工作站与实验数据。

维护主体：pic-ai-robotic-chemistry

接入关系：Research agents → robot instructions → ROS / robot drivers → chemistry workstation

### 贡献与价值

将化学任务规划、机器人操作和实验数据连接为多 Agent 研究流程。

### 差异与适用条件

机器人指令集、AGV 和机械臂驱动分布在外部仓库，系统边界跨多个工程。

### 可复用部分

用依赖图明确每个模块的输入、输出和设备责任。

### 公开范围与实验记录

仓库提供论文代码和实验数据，并把机器人指令与 AGV 驱动链接到其他仓库；本仓库未识别到许可证。

[项目说明](https://github.com/pic-ai-robotic-chemistry/ChemAgents/blob/main/README.md) · [论文](https://doi.org/10.1021/jacs.4c17738)

## ORGANA

[ac-rad/organa](https://github.com/ac-rad/organa) · 实验决策 · Unspecified · 论文实机案例

ORGANA 论文中的化学机器人助手结合用户目标、场景感知与实验进度；本仓库主要发布项目网站与研究材料。

维护主体：AC-RAD 研究合作团队

接入关系：User intent → perception & task planning → robot execution → experiment report

### 贡献与价值

论文把用户意图、场景感知和实验进度用于机器人下一步决策。

### 差异与适用条件

所列公开仓库主要是网站源码；可学习系统方法与实验证据，不能据此取得完整控制软件。

### 可复用部分

借鉴感知、实验进度与报告之间的关系，控制实现需另找明确发布。

### 公开范围与实验记录

论文展示真实机器人实验；README 明确该仓库包含网站源码，没有据此确认完整机器人控制实现；许可证未识别。

[项目说明](https://github.com/ac-rad/organa/blob/main/README.md) · [论文](https://arxiv.org/abs/2401.06949)

## CLAIRify

[ac-rad/xdl-generation](https://github.com/ac-rad/xdl-generation) · 过程编排 · MIT · 论文实机案例

把自然语言实验步骤转换为可检查的 XDL 过程，验证错误反馈给模型进行修订。

维护主体：AC-RAD 研究合作团队

接入关系：Natural-language procedure → XDL generation → verification & revision → external executor

### 贡献与价值

把实验步骤转换为可检查的结构化过程，并用验证反馈修正生成结果。

### 差异与适用条件

主要公开贡献是生成器与数据；过程语言的有效性与机器人执行能力是两层。

### 可复用部分

借鉴生成、验证和修订循环，同时把设备可用能力接入验证器。

### 公开范围与实验记录

论文含机器人执行；本仓库主要发布生成器与数据。README 指明旧代码接口已过时，更新版本在 develop 分支。

[项目说明](https://github.com/ac-rad/xdl-generation/blob/master/README.md) · [许可证](https://github.com/ac-rad/xdl-generation/blob/master/LICENSE) · [论文](https://arxiv.org/abs/2303.14100)

## CLAIRify-Chemspeed

[ac-rad/clairify-chemspeed](https://github.com/ac-rad/clairify-chemspeed) · 过程编排 · Unspecified · 接入实现 / 文档

自然语言生成 Chemspyd 程序，把协议生成连接到 Chemspeed 自动化平台。

维护主体：AC-RAD 研究合作团队

接入关系：Natural language → program generation → Chemspyd → Chemspeed platform

### 贡献与价值

将语言到实验程序的转换具体连接到 Chemspyd 接口。

### 差异与适用条件

相较通用 XDL 生成，面向一个既有设备编程接口，迁移依赖平台能力。

### 可复用部分

借鉴在成熟实验 API 之上生成程序，并保存程序与运行版本。

### 公开范围与实验记录

Chemspyd 论文链接的接口示例；未识别到本仓库许可证。

[项目说明](https://github.com/ac-rad/clairify-chemspeed/blob/master/README.md) · [论文](https://doi.org/10.1039/D4DD00046C)

## SynAgent · thin-film synthesis

[izumitkhr/synagent](https://github.com/izumitkhr/synagent) · 实验决策 · MIT · 论文实机案例

薄膜合成闭环中的多模态规划与假设检验，读取 XRD/SEM 数据，为下一次实验写出条件。

维护主体：izumitkhr

接入关系：XRD / SEM MaiML data → hypothesis & skill generation → output.txt → external dLab

### 贡献与价值

用预测、实验反馈和证实/证伪交替更新对薄膜合成的理解。

### 差异与适用条件

公开程序是逐轮规划器，靠数据文件与 dLab 交换条件；不是沉积与搬运驱动集合。

### 可复用部分

借鉴假设、预期结果、实测结果和下一轮条件的结构化关联。

### 公开范围与实验记录

论文报告 18 次物理实验；公开程序通过 MaiML 输入与 output.txt 对接 dLab，未打包整套沉积、搬运与测量驱动。

[项目说明](https://github.com/izumitkhr/synagent/blob/main/README.md) · [许可证](https://github.com/izumitkhr/synagent/blob/main/LICENSE) · [论文](https://arxiv.org/abs/2609.18598)

## AutoLabs

[pnnl/autolabs](https://github.com/pnnl/autolabs) · 实验决策 · BSD-2-Clause · 配套代码 / 资料

生成实验步骤与 Lab Step Representation，支持多 Agent 修订和实验设计评估。

维护主体：Pacific Northwest National Laboratory

接入关系：Research prompt → multi-agent revision → Lab Step Representation → simulation / evaluation

### 贡献与价值

把实验设计输出为可检查的步骤表示，便于比较方案和迭代修订。

### 差异与适用条件

公共应用偏规划、模拟与评估；真实设备执行不是该发布的完整交付。

### 可复用部分

借鉴中间步骤表示，让规划输出能被独立检查与后续执行器消费。

### 公开范围与实验记录

公开应用重点是设计、模拟和评估；不能仅凭论文的物理实验将此仓库当作完整硬件执行系统。

[项目说明](https://github.com/pnnl/autolabs/blob/master/README.md) · [许可证](https://github.com/pnnl/autolabs/blob/master/LICENSE.md) · [论文](https://arxiv.org/abs/2509.25651)

## opcua-mcp · kukapay

[kukapay/opcua-mcp](https://github.com/kukapay/opcua-mcp) · 设备桥接 · MIT · 接入实现 / 文档

把 OPC UA 节点浏览、单点与批量读写接到 Agent，保留已有工业设备服务端。

维护主体：kukapay

接入关系：Agent → MCP → OPC UA client → server address space → industrial device

### 贡献与价值

在已有 OPC UA 设备服务前增加浏览和读写工具，利用现有工业接入。

### 差异与适用条件

主要完成协议桥接；变量的单位、模式与作用由服务端信息模型决定。

### 可复用部分

优先保留 OPC UA 信息模型，把 Agent 参数准确映射到节点。

### 公开范围与实验记录

是 OPC UA 到 MCP 的适配层；设备意义取决于服务端地址空间和信息模型。

[项目说明](https://github.com/kukapay/opcua-mcp/blob/main/README.md) · [许可证](https://github.com/kukapay/opcua-mcp/blob/main/LICENSE)

## OPC UA MCP · IndustriAgents

[IndustriAgents/OPCUA-MCP](https://github.com/IndustriAgents/OPCUA-MCP) · 设备桥接 · MIT · 接入实现 / 文档

浏览、读数、历史、订阅、告警与受配置约束的写入及方法调用；一个本地进程连接一个 OPC UA 端点。

维护主体：IndustriAgents

接入关系：Agent → local MCP process → OPC UA subscriptions / methods → endpoint

### 贡献与价值

把订阅、历史与告警加入 Agent 的工业状态观察，并提供配置化写入。

### 差异与适用条件

比只读写单点更关注持续状态；一个进程对应一个端点。

### 可复用部分

借鉴事件驱动观察，并把端点会话与上层实验任务分开。

### 公开范围与实验记录

README 当前已包含写入能力，但默认只读；远程共享多客户端运行仍有单独设计约束。

[项目说明](https://github.com/IndustriAgents/OPCUA-MCP/blob/main/README.md) · [许可证](https://github.com/IndustriAgents/OPCUA-MCP/blob/main/LICENSE)

## modbus-mcp

[kukapay/modbus-mcp](https://github.com/kukapay/modbus-mcp) · 设备桥接 · MIT · 接入实现 / 文档

把寄存器和线圈读写暴露为工具，是连接已有 PLC、传感器与控制器的底层入口。

维护主体：kukapay

接入关系：Agent → MCP → Modbus client → coils / registers → PLC / sensor

### 贡献与价值

为大量已有控制器提供简单的寄存器与线圈访问入口。

### 差异与适用条件

底层地址可读写不代表量纲与设备意图已描述；映射表仍是关键知识。

### 可复用部分

把寄存器表提升为带单位、比例、模式和读回规则的能力描述。

### 公开范围与实验记录

具备通信调用接口；寄存器单位、比例、设备模式与副作用仍需设备映射表表达。

[项目说明](https://github.com/kukapay/modbus-mcp/blob/main/README.md) · [许可证](https://github.com/kukapay/modbus-mcp/blob/main/LICENSE)

## TANGO MCP

[abogani/tango-mcp](https://github.com/abogani/tango-mcp) · 设备桥接 · Apache-2.0 · 接入实现 / 文档

从 TANGO 数据库发现设备，将属性、状态和命令映射为 MCP 资源与工具，支持批量读取。

维护主体：abogani

接入关系：Agent → MCP → PyTango database / device proxy → TANGO device server

### 贡献与价值

复用设施数据库发现设备，并映射属性、状态、命令和批量读取。

### 差异与适用条件

在已有 TANGO 语义上适配，设备服务器继续承担底层控制。

### 可复用部分

保留设备名、属性与状态转换的原始含义，减少重复建模。

### 公开范围与实验记录

提供具体 TANGO_HOST 部署与属性/命令路径；实际可操作范围由设施已有设备服务器决定。

[项目说明](https://github.com/abogani/tango-mcp/blob/main/README.md) · [许可证](https://github.com/abogani/tango-mcp/blob/main/LICENSE)

## MCP Server for EPICS

[sryu81/mcp-server-for-epics](https://github.com/sryu81/mcp-server-for-epics) · 设备桥接 · Unspecified · 接入实现 / 文档

提供独立进程和 IOC 内嵌两种入口，把 EPICS PV 和控制命令暴露给 Agent。

维护主体：sryu81

接入关系：Agent → MCP → standalone server / IOC library → CA / PVA → process variables

### 贡献与价值

提供独立服务与 IOC 内嵌两种部署位置，使工具入口贴近现有控制系统。

### 差异与适用条件

部署拓扑与连接所有权是主要差异；PV 的科学含义仍需设施上下文。

### 可复用部分

比较在 IOC 内部和外部持有连接的代价与状态一致性。

### 公开范围与实验记录

C++ 共享库和协议分派结构公开；未识别到许可证。

[项目说明](https://github.com/sryu81/mcp-server-for-epics/blob/main/README.md)

## MCP2Serial

[mcp2everything/mcp2serial](https://github.com/mcp2everything/mcp2serial) · 设备桥接 · MIT · 接入实现 / 文档

通过串口连接 MCU 与 Agent，适合作为自制仪器的基础通信桥。

维护主体：mcp2everything

接入关系：Agent → MCP → serial connection → MCU firmware → attached hardware

### 贡献与价值

让自制仪器从串口获得基本 Agent 入口，接入门槛较低。

### 差异与适用条件

协议语义留在固件与串口命令中，需要自行定义完成状态与结果格式。

### 可复用部分

把串口桥作为起点，补齐设备能力、命令响应和测量时间。

### 公开范围与实验记录

README 给出 Pico 等接入流程；串口传输本身不定义仪器的量纲、状态或完成条件。

[项目说明](https://github.com/mcp2everything/mcp2serial/blob/main/README.md) · [许可证](https://github.com/mcp2everything/mcp2serial/blob/main/LICENSE)

## tinymcp

[golioth/tinymcp](https://github.com/golioth/tinymcp) · 设备桥接 · Apache-2.0 · 接入实现 / 文档

将 Golioth 设备 RPC 及其描述动态暴露为 MCP 工具，已有设备可通过状态服务发布工具 schema。

维护主体：Golioth

接入关系：Agent → MCP → Golioth management API → device RPC → embedded device

### 贡献与价值

从已有设备 RPC 描述动态生成工具，复用设备管理平台。

### 差异与适用条件

新增入口较轻，但设备发现和通信依赖 Golioth 平台。

### 可复用部分

借鉴设备发布能力 schema 的方式，明确平台服务的依赖边界。

### 公开范围与实验记录

包含 Zephyr LED 控制示例；服务代码开源，但运行依赖 Golioth 平台，不能当作纯离线通用设备协议。

[项目说明](https://github.com/golioth/tinymcp/blob/main/README.md) · [许可证](https://github.com/golioth/tinymcp/blob/main/LICENSE)

## Embedded Debugger MCP

[Adancurusul/embedded-debugger-mcp](https://github.com/Adancurusul/embedded-debugger-mcp) · 仪器开发 · MIT · 维护者实机记录

让 Agent 连接调试探针、控制目标、读写内存、设断点、刷写与检查故障，为仪器固件开发提供物理反馈。

维护主体：Adancurusul

接入关系：Agent → MCP / CLI → probe-rs / OpenOCD → debug probe → target MCU

### 贡献与价值

把编译后的固件与真实芯片状态连接，让 Agent 能观察断点、内存与故障。

### 差异与适用条件

操作对象是调试目标与固件，不等同于实验用的高层仪器动作。

### 可复用部分

建立固件版本、刷写、运行与测量反馈之间的可追踪循环。

### 公开范围与实验记录

维护者声明在真实 ESP32-S3 上验证；原生 probe-rs 和 OpenOCD 后端分开配置。

[项目说明](https://github.com/Adancurusul/embedded-debugger-mcp/blob/main/README.md) · [许可证](https://github.com/Adancurusul/embedded-debugger-mcp/blob/main/LICENSE)

## Saleae Logic 2 MCP

[hsoffar/saleae-logic2-mcp](https://github.com/hsoffar/saleae-logic2-mcp) · 仪器开发 · Apache-2.0 · 接入实现 / 文档

逻辑分析仪的采集、协议解码、时序测量和导出接口，用于固件与真实总线调试。

维护主体：hsoffar

接入关系：Agent → MCP → Logic 2 automation → logic analyzer → physical bus

### 贡献与价值

把真实数字总线采样、协议解码和时序结果反馈给开发 Agent。

### 差异与适用条件

价值在观察外部信号；设备程序的执行仍由被测系统完成。

### 可复用部分

将源代码变化与总线轨迹对照，定位仪器控制链中的时序问题。

### 公开范围与实验记录

依赖已开启自动化接口的 Saleae Logic 2；该软件和硬件不随开源服务提供。

[项目说明](https://github.com/hsoffar/saleae-logic2-mcp/blob/main/README.md) · [许可证](https://github.com/hsoffar/saleae-logic2-mcp/blob/main/LICENSE)

## MicroPython MCP Bridge

[SWITCHSCIENCE/mcp-micropython-bridge](https://github.com/SWITCHSCIENCE/mcp-micropython-bridge) · 仪器开发 · Unspecified · 接入实现 / 文档

通过串口或 WebREPL 操作 ESP32/RP2040 等，利用设备侧 helper 模块和 HARDWARE.md 保存板级知识。

维护主体：SWITCHSCIENCE

接入关系：Agent → MCP → serial / WebREPL → MicroPython helpers → MCU I/O

### 贡献与价值

让 Agent 通过可编程固件直接操作板级 I/O，并保留硬件说明。

### 差异与适用条件

硬件能力可以通过设备侧代码扩展；它同时涉及开发接口和运行接口。

### 可复用部分

把引脚、接线和设备侧 helper 与固件版本一同管理。

### 公开范围与实验记录

提供实机测试 CLI 和固件接入说明；未识别到顶层许可证。

[项目说明](https://github.com/SWITCHSCIENCE/mcp-micropython-bridge/blob/main/README.md)

## ROS MCP Server

[robotmcp/ros-mcp-server](https://github.com/robotmcp/ros-mcp-server) · 设备桥接 · Apache-2.0 · 维护者实机记录

经 rosbridge 发现主题、服务、动作与消息类型，发布控制消息并读取机器人传感器反馈。

维护主体：robotmcp

接入关系：Agent → MCP → rosbridge → ROS topics / services / actions → robot

### 贡献与价值

把 ROS 图中的通信对象直接呈现给 Agent，复用既有机器人生态。

### 差异与适用条件

解决发现和调用；运动规划、控制频率和执行反馈仍由机器人栈提供。

### 可复用部分

保留 topic、service、action 的不同生命周期，不压成同一种同步调用。

### 公开范围与实验记录

仓库附机器人演示；适配覆盖 ROS 通信层，具体运动能力和控制器仍在机器人自身系统中。

[项目说明](https://github.com/robotmcp/ros-mcp-server/blob/main/README.md) · [许可证](https://github.com/robotmcp/ros-mcp-server/blob/main/LICENSE)

## ROSA

[nasa-jpl/rosa](https://github.com/nasa-jpl/rosa) · 实验决策 · Apache-2.0 · 论文实机案例

JPL 的 ROS 自然语言助手，结合系统诊断、状态查询与可扩展机器人操作工具。

维护主体：NASA · Jet Propulsion Laboratory

接入关系：Language agent → extensible ROS tools → ROS 1 / ROS 2 → robot

### 贡献与价值

将机器人状态分析、信息查询与操作工具放入自然语言助手。

### 差异与适用条件

Agent 工具框架本身承担交互与推理，与纯 ROS 到 MCP 的适配角色不同。

### 可复用部分

借鉴领域工具如何表达机器人状态和可操作范围。

### 公开范围与实验记录

论文与示例覆盖机器人应用；ROSA 是 Agent 工具框架，不能由名称推断具有原生 MCP。

[项目说明](https://github.com/nasa-jpl/rosa/blob/main/README.md) · [许可证](https://github.com/nasa-jpl/rosa/blob/main/LICENSE) · [论文](https://arxiv.org/abs/2410.06472)

## device-use

[labclaw/device-use](https://github.com/labclaw/device-use) · 界面操作 · Apache-2.0 · 接入实现 / 文档

用屏幕观察、规划和鼠标键盘操作包装仪器软件，配套设备 profile。适用于 API 缺失时的替代接入研究。

维护主体：labclaw

接入关系：Agent / VLM → observe-plan-act → mouse / keyboard → instrument software

### 贡献与价值

把没有可用 API 的仪器软件纳入屏幕观察和操作循环。

### 差异与适用条件

接口依赖可见界面与软件版本，适合与 SDK 路径比较维护和验证成本。

### 可复用部分

使用设备 profile 记录界面状态、操作步骤和动作后的结果检查。

### 公开范围与实验记录

公开实现含 NMR 数据处理与酶标仪模块；MCP 工具存在不等于全部列出的商业仪器都已完成物理控制验证。

[项目说明](https://github.com/labclaw/device-use/blob/main/README.md) · [许可证](https://github.com/labclaw/device-use/blob/main/LICENSE) · [实现入口](https://github.com/labclaw/device-use/blob/main/src/device_use/integrations/mcp_server.py)

## device-skills

[labclaw/device-skills](https://github.com/labclaw/device-skills) · 知识与资料 · Apache-2.0 · 配套代码 / 资料

仪器操作知识与技能材料，与 device-use 的执行接口配套。

维护主体：labclaw

接入关系：Device operating knowledge → Agent Skills → agent → separate device-use runtime

### 贡献与价值

把仪器操作知识作为可复用材料交给 Agent。

### 差异与适用条件

知识材料指导怎么操作；设备连接与执行由另一个组件完成。

### 可复用部分

让技能引用明确设备版本、所需工具和预期观测结果。

### 公开范围与实验记录

技能是知识与操作说明；独立收录为配套资料，不计作设备驱动或独立实机系统。

[项目说明](https://github.com/labclaw/device-skills/blob/main/README.md) · [许可证](https://github.com/labclaw/device-skills/blob/main/LICENSE)

## edge-mhs

[fastly/edge-mhs](https://github.com/fastly/edge-mhs) · 设备桥接 · Apache-2.0 · 模拟验证

在 Agent 与设备服务之间加入边缘网关，处理身份、参数约束、配额与审计。

维护主体：Fastly

接入关系：Agent → MCP edge gateway → backend proxy → mock driver

### 贡献与价值

将远程访问的身份、参数约束与记录集中在边缘网关。

### 差异与适用条件

当前是基于 mock 的参考网关，后端合约仍需对应真实设备运行器。

### 可复用部分

把网关当作可选部署组件，保持仪器本地执行接口独立。

### 公开范围与实验记录

README 将其定位为参考实现并使用 mock 后端；不是 Anthropic 官方 MHS 服务端。

[项目说明](https://github.com/fastly/edge-mhs/blob/main/README.md) · [许可证](https://github.com/fastly/edge-mhs/blob/main/LICENSE)

## Agent2Device Protocol

[neogyk/Agent2Device-Protocol](https://github.com/neogyk/Agent2Device-Protocol) · 仪器说明 · MIT · 构想 / 提案

讨论 Agent 与实验设备连接的协议构想。

维护主体：neogyk

接入关系：Protocol concept → README design notes

### 贡献与价值

提供 Agent 到设备连接问题的概念入口。

### 差异与适用条件

当前发布是设计笔记，没有驱动与运行器可供直接复用。

### 可复用部分

仅用于比较需求表述；实现依据需来自有具体代码和行为的工程。

### 公开范围与实验记录

查阅仓库树只有 README、LICENSE 与忽略文件，没有协议实现或设备驱动。

[项目说明](https://github.com/neogyk/Agent2Device-Protocol/blob/main/README.md) · [许可证](https://github.com/neogyk/Agent2Device-Protocol/blob/main/LICENSE)

## ChemCrow public release

[ur-whitelab/chemcrow-public](https://github.com/ur-whitelab/chemcrow-public) · 知识与资料 · MIT · 配套代码 / 资料

化学工具增强 Agent 的重要案例，可用于理解工具编排和实验服务边界。

维护主体：ur-whitelab

接入关系：Chemistry agent → public tool subset → external services

### 贡献与价值

展示化学领域知识怎样通过工具组合进入语言模型的研究流程。

### 差异与适用条件

公共包缺少论文中部分服务接口，论文实验范围大于可下载工具范围。

### 可复用部分

借鉴工具选择与领域任务组织，并逐项查阅可公开复用的服务。

### 公开范围与实验记录

论文有实验执行，但 README 明确公共包因 API 限制不包含论文所有工具；不据论文补写未公开的硬件接口。

[项目说明](https://github.com/ur-whitelab/chemcrow-public/blob/main/README.md) · [许可证](https://github.com/ur-whitelab/chemcrow-public/blob/main/LICENSE) · [论文](https://doi.org/10.1038/s42256-024-00832-8)

## NV autonomous experiments

[takuyaisogawa/nv-autonomous-experiments](https://github.com/takuyaisogawa/nv-autonomous-experiments) · 知识与资料 · MIT code / CC BY-4.0 artifacts · 配套代码 / 资料

NV 中心自主实验的公共案例、分析代码与实验资料。

维护主体：takuyaisogawa

接入关系：Released case studies → analysis & trajectories → external live backend

### 贡献与价值

提供 NV 自主实验的案例和分析材料，帮助研究实验决策与反馈。

### 差异与适用条件

发布说明排除了在线实验后端，适合作为实验轨迹资料而非驱动。

### 可复用部分

借鉴轨迹、分析与实验环境之间的对应关系。

### 公开范围与实验记录

许可和发布说明明确未包含 live-laboratory backend；可研究实验轨迹，不能直接当作完整 NV 设备控制软件。

[项目说明](https://github.com/takuyaisogawa/nv-autonomous-experiments/blob/main/README.md) · [许可证](https://github.com/takuyaisogawa/nv-autonomous-experiments/blob/main/LICENSE) · [论文](https://arxiv.org/abs/2607.25145)

## UC2 LLM microscopy workshop

[openUC2/Hackathon-UC2-LLM](https://github.com/openUC2/Hackathon-UC2-LLM) · 知识与资料 · Unspecified · 配套代码 / 资料

围绕真实 UC2 显微镜和 ImSwitch API 的教学入口，包括设备构成、接入与实验挑战。

维护主体：openUC2

接入关系：Workshop material → Python / ImSwitch FastAPI → UC2 microscope

### 贡献与价值

用开放显微镜和明确 API 给出从设备到实验任务的教学路径。

### 差异与适用条件

贡献是接入材料与实验任务，不是完整常驻 Agent 平台。

### 可复用部分

用小型可复现实验作为新适配器的入门和验收任务。

### 公开范围与实验记录

是课程与示例资料，不是独立完整的 Agent 平台；未识别到许可证。

[项目说明](https://github.com/openUC2/Hackathon-UC2-LLM/blob/main/README.md)

