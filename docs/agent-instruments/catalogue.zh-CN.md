# 项目目录

[中文 HTML](index.zh-CN.html) · [English HTML](index.en.html) · [JSON](catalogue.json)

## OpenMHP

[kushalsinha/openmhp](https://github.com/kushalsinha/openmhp) · 仪器说明 · Apache-2.0 · 模拟验证

设备描述、读写、动作、任务、租约与实验记录组成统一接口；可通过已有驱动生态接入。适合研究精简设备说明与按需发现。

公开规范与实现；supported-devices 的 7 个设备包标为 twin tested，另有 1 个人工操作模板。维护者明确尚未确认这些驱动的实机运行。

MCP / CLI / Python SDK / JSON-RPC / HTTP/SSE

[项目说明](https://github.com/kushalsinha/openmhp/blob/main/README.md) · [许可证](https://github.com/kushalsinha/openmhp/blob/main/LICENSE) · [实现入口](https://github.com/kushalsinha/openmhp/blob/main/SPEC.md) · [实现入口](https://github.com/kushalsinha/openmhp/blob/main/supported-devices/README.md) · [实现入口](https://github.com/kushalsinha/openmhp/blob/main/supported-devices/biologic-sp300/driver.py)

## Open-MHS · Abenor Labs

[Abenor-Labs/Open-MHS](https://github.com/Abenor-Labs/Open-MHS) · 仪器说明 · Apache-2.0 · 接入实现 / 文档

以 capability tag 和设备基类统一传感器、执行器及状态；提供串口机械臂适配示例。独立社区实现。

源码包含 mock 设备和串口驱动；本次材料未提供具体实机验证记录。

MCP / REST / CLI / Python / Serial

[项目说明](https://github.com/Abenor-Labs/Open-MHS/blob/main/README.md) · [许可证](https://github.com/Abenor-Labs/Open-MHS/blob/main/LICENSE) · [实现入口](https://github.com/Abenor-Labs/Open-MHS/blob/main/open_mhs/drivers/serial_robotic_arm.py) · [实现入口](https://github.com/Abenor-Labs/Open-MHS/blob/main/schema/capability_schema.json)

## Open MHS · tongriyaotxt

[tongriyaotxt/open-mhs](https://github.com/tongriyaotxt/open-mhs) · 仪器说明 · MIT · 接入实现 / 文档

设备注册、统一命令和 MCP 工具；包含机器人动作与技能执行扩展。与同名项目分别维护。

已读 MCP 调用分派代码；物理设备与 MuJoCo 示例需按各自后端区分。

MCP / REST / CLI / Python

[项目说明](https://github.com/tongriyaotxt/open-mhs/blob/main/README.md) · [许可证](https://github.com/tongriyaotxt/open-mhs/blob/main/LICENSE) · [实现入口](https://github.com/tongriyaotxt/open-mhs/blob/main/src/openmhs/mcp/server.py)

## Open MHS · SCUT-ESA

[SCUT-ESA/open-mhs](https://github.com/SCUT-ESA/open-mhs) · 仪器说明 · MIT · 维护者实机记录

统一设备接口加显式后端策略，覆盖 VISA 仪器、嵌入式 I/O 与模拟设备。属于受 MHS 启发的社区工程。

维护者列出 UNI-T UPO6102N 与 UTG2062X 的实机验证；其余摄像头、GPIO 等条目仍分别标为实验性或模拟。

MCP / REST / CLI / PyVISA

[项目说明](https://github.com/SCUT-ESA/open-mhs/blob/main/README.md) · [许可证](https://github.com/SCUT-ESA/open-mhs/blob/main/LICENSE) · [实现入口](https://github.com/SCUT-ESA/open-mhs/blob/main/src/openmhs/core/backend.py)

## Model Hardware Protocol · Cuntinum

[Cuntinum/model-hardware-protocol](https://github.com/Cuntinum/model-hardware-protocol) · 仪器说明 · Apache-2.0 · 接入实现 / 文档

以 discover、read、write、execute 组织设备驱动和共享状态。包名 khp，与 OpenMHP 不是同一项目。

公开规范、SDK 与驱动目录；README 的 production grade 定位没有在本次材料中形成跨设备实测依据。

Python SDK / TypeScript SDK / MCP / CLI

[项目说明](https://github.com/Cuntinum/model-hardware-protocol/blob/main/README.md) · [许可证](https://github.com/Cuntinum/model-hardware-protocol/blob/main/LICENSE)

## Open Agent Hardware Layer

[fredabila/oahl](https://github.com/fredabila/oahl) · 仪器说明 · MIT · 维护者实机记录

discover–reserve–execute–release 生命周期；节点、适配器与传输插件分离，可本地运行或使用可选注册与中继服务。

README 展示 Android 手机 ADB 操作；不能由此推定科研仪器的校准、长任务或读数语义已统一。

JavaScript SDK / Python SDK / WebSocket / Serial / ADB / MQTT / TCP

[项目说明](https://github.com/fredabila/oahl/blob/main/README.md) · [许可证](https://github.com/fredabila/oahl/blob/main/LICENSE)

## instrMCP

[caidish/instrMCP](https://github.com/caidish/instrMCP) · 常驻执行 · MIT · 接入实现 / 文档

把现有 Jupyter 内核中的 QCoDeS Station 暴露给 Agent，复用参数、仪器快照、数据库与测量工作流。适合已使用 QCoDeS 的实验室。

已读参数发现、缓存与 fresh 读取路径；真实连接由运行中的内核及 QCoDeS 驱动持有。

MCP / Jupyter / QCoDeS / Python / MeasureIt

[项目说明](https://github.com/caidish/instrMCP/blob/main/README.md) · [许可证](https://github.com/caidish/instrMCP/blob/main/LICENSE) · [实现入口](https://github.com/caidish/instrMCP/blob/main/instrmcp/servers/jupyter_qcodes/backend/qcodes.py)

## PUDA

[PUDAP/puda](https://github.com/PUDAP/puda) · 常驻执行 · MIT · 接入实现 / 文档

无头物理设备执行平台：消息层、分层驱动、协议运行与结果记录分离。Agent 通过 CLI 和技能编写、验证、运行实验。

已读 CLI 协议执行路径：运行前读取机器命令目录，经 NATS 分发；仓库含边缘驱动示例。

CLI / NATS / Python drivers / Agent Skills

[项目说明](https://github.com/PUDAP/puda/blob/main/README.md) · [许可证](https://github.com/PUDAP/puda/blob/main/LICENSE) · [实现入口](https://github.com/PUDAP/puda/blob/main/apps/cli/internal/cli/protocol-run.go) · [论文](https://arxiv.org/abs/2607.26464)

## Uni-Lab-OS

[deepmodeling/Uni-Lab-OS](https://github.com/deepmodeling/Uni-Lab-OS) · 过程编排 · GPL-3.0 framework + proprietary drivers · 论文实机案例

跨设备实验室编排，结合动作、资源和实验室拓扑。框架、设备适配与工作流编译的分工值得比较。

论文与驱动目录展示物理实验路径。主框架 GPL-3.0；unilabos/devices/ 单独采用 DP Technology 专有许可。

Python / ROS 2 / Action/Resource model / Workflow compiler

[项目说明](https://github.com/deepmodeling/Uni-Lab-OS/blob/main/README.md) · [许可证](https://github.com/deepmodeling/Uni-Lab-OS/blob/main/LICENSE) · [实现入口](https://github.com/deepmodeling/Uni-Lab-OS/blob/main/NOTICE) · [实现入口](https://github.com/deepmodeling/Uni-Lab-OS/blob/main/unilabos/devices/LICENSE) · [实现入口](https://github.com/deepmodeling/Uni-Lab-OS/blob/main/docs/developer_guide/add_device.md) · [论文](https://arxiv.org/abs/2512.21766)

## Osprey

[als-apg/osprey](https://github.com/als-apg/osprey) · 常驻执行 · BSD-3-Clause · 论文实机案例

面向大型科学设施的 Agent 接口，处理通道语义寻址、设施知识、控制连接与操作过程。已有 EPICS、DOOCS、TANGO 连接器。

项目论文与设施应用提供实验背景；当前实现要求每次硬件写入经人工批准。

MCP / CLI / Agent Skills / EPICS / DOOCS / TANGO

[项目说明](https://github.com/als-apg/osprey/blob/main/README.md) · [许可证](https://github.com/als-apg/osprey/blob/main/LICENSE.txt) · [实现入口](https://github.com/als-apg/osprey/blob/main/docs/source/architecture/mcp-servers.rst) · [论文](https://doi.org/10.1063/5.0306302)

## IvoryOS

[ivoryos-ai/IvoryOS](https://github.com/ivoryos-ai/IvoryOS) · 过程编排 · MIT · 论文实机案例

从已有 Python 自动化对象生成控制界面和工作流，包含可选的自然语言工作流设计功能。适合逐步接管已有设备代码。

有实验室编排论文；当前 README 未声明原生 MCP 服务，不能把 Python API 自动等同于 MCP。

Python introspection / Web application / LLM workflow design

[项目说明](https://github.com/ivoryos-ai/IvoryOS/blob/main/README.md) · [许可证](https://github.com/ivoryos-ai/IvoryOS/blob/main/LICENSE) · [实现入口](https://github.com/ivoryos-ai/IvoryOS/blob/main/ivoryos/parsers/introspection.py) · [论文](https://www.nature.com/articles/s41467-025-60514-w)

## Jumpstarter

[jumpstarter-dev/jumpstarter](https://github.com/jumpstarter-dev/jumpstarter) · 常驻执行 · Apache-2.0 · 接入实现 / 文档

共享和租用真实或虚拟被测硬件，统一电源、串口、CAN、SPI、GPIO 与 USB 控制。Agent 可沿用测试脚本的接口。

公开驱动、Python 客户端、gRPC 定义与控制器；属于可被 Agent 使用的硬件基础设施，不是专门的科学语言模型。

CLI / Python API / gRPC / Hardware leases

[项目说明](https://github.com/jumpstarter-dev/jumpstarter/blob/main/README.md) · [许可证](https://github.com/jumpstarter-dev/jumpstarter/blob/main/LICENSE)

## Lager

[lagerdata/lager](https://github.com/lagerdata/lager) · 常驻执行 · Apache-2.0 · 接入实现 / 文档

用台架 Linux 主机集中连接电源、示波器、调试探针和总线；统一 CLI 可由 Agent、人工或 CI 使用，程序可在设备旁执行。

README 与文档提供具体仪器和台架部署路径；可复用的是台架执行层。

CLI / Python Net API / Network bench control

[项目说明](https://github.com/lagerdata/lager/blob/main/README.md) · [许可证](https://github.com/lagerdata/lager/blob/main/LICENSE)

## Experiment Automation Agents

[AdvancedPhotonSource/EAA](https://github.com/AdvancedPhotonSource/EAA) · 常驻执行 · Unspecified · 论文实机案例

面向需要视觉反馈的科学实验 Agent 运行环境；支持图像工具结果、确定性工作流及实验任务管理。

有显微实验论文；README 已宣布迁移到 EAA-Pi。当前仓库未识别到顶层许可证。

MCP client / HTTP tools / Python / Agent Skills

[项目说明](https://github.com/AdvancedPhotonSource/EAA/blob/main/README.md) · [论文](https://pmc.ncbi.nlm.nih.gov/articles/PMC13633048/)

## EAA-Pi

[AdvancedPhotonSource/EAA-Pi](https://github.com/AdvancedPhotonSource/EAA-Pi) · 常驻执行 · Unspecified · 接入实现 / 文档

基于 pi-experiment-ops 的实验助手界面，终端与网页共享工作区、工具配置和实验会话。

作为 EAA 后继工程公开；实际仪器能力取决于接入的 MCP 服务，不能继承旧论文全部验证范围。

CLI / Web UI / MCP instruments / Agent Skills

[项目说明](https://github.com/AdvancedPhotonSource/EAA-Pi/blob/main/README.md)

## pi-experiment-ops

[AdvancedPhotonSource/pi-experiment-ops](https://github.com/AdvancedPhotonSource/pi-experiment-ops) · 常驻执行 · Unspecified · 接入实现 / 文档

组合实验工具、后台执行、持久终端和会话检索，为实验应用提供可复用 Agent 执行环境。

MCP 适配器连接独立仪器服务；运行环境本身不提供通用设备驱动。

Pi extension / MCP / CodeMode / CLI / Agent Skills

[项目说明](https://github.com/AdvancedPhotonSource/pi-experiment-ops/blob/main/README.md)

## LabMCP · K-Dense

[K-Dense-AI/lab-instrument-mcps](https://github.com/K-Dense-AI/lab-instrument-mcps) · 设备桥接 · Apache-2.0 · 模拟验证

单仓库仪器适配集合，覆盖电子测量、光谱、温控、泵、显微、液体处理和设施协议。组件清单单列，避免把服务器数量当作独立项目数量。

当前机器可读目录含 32 个服务器、411 个工具，全部标为 simulated；其中质谱数据和工作单工具不是直接设备控制。

MCP / CLI / VISA / TCP / Serial / Vendor APIs

[项目说明](https://github.com/K-Dense-AI/lab-instrument-mcps/blob/main/README.md) · [许可证](https://github.com/K-Dense-AI/lab-instrument-mcps/blob/main/LICENSE) · [实现入口](https://github.com/K-Dense-AI/lab-instrument-mcps/blob/main/packages/labmcp/src/labmcp/catalog.json)

## LabLink

[techmanual-ai/lablink-mcp](https://github.com/techmanual-ai/lablink-mcp) · 设备桥接 · MIT · 接入实现 / 文档

多种传输接口汇入同一 MCP 服务，便于把已有指令和脚本接给 Agent。设备语义主要仍由配置和驱动表达。

提供五类连接驱动与配置示例；通用通信能力不代表任意设备已经适配。

MCP / VISA/SCPI / SSH / REST / Serial / Python

[项目说明](https://github.com/techmanual-ai/lablink-mcp/blob/main/README.md) · [许可证](https://github.com/techmanual-ai/lablink-mcp/blob/main/LICENSE)

## scpi-mcp

[armchairdeity/mcp-server-scpi](https://github.com/armchairdeity/mcp-server-scpi) · 设备桥接 · MIT · 接入实现 / 文档

将示波器采集与测量目标封装为工具，仪器后端负责具体 SCPI。首个目标是 Rigol DS1054Z。

有 Rigol 与 mock 后端；README 明确不暴露任意原始 SCPI，且没有信号源或逻辑分析仪功能。

MCP / PyVISA / SCPI / USB/LAN

[项目说明](https://github.com/armchairdeity/mcp-server-scpi/blob/main/README.md) · [许可证](https://github.com/armchairdeity/mcp-server-scpi/blob/main/LICENSE)

## oscilloscope-mcp

[masahiro-999/oscilloscope-mcp](https://github.com/masahiro-999/oscilloscope-mcp) · 设备桥接 · MIT · 接入实现 / 文档

网络示波器设置、触发、波形读取和测量反馈；返回结构化数据、图像及可独立查看的波形页面。

README 描述实际台架与 FPGA 调试路径；设备兼容性仍按项目列出的型号确认。

MCP / SCPI / TCP

[项目说明](https://github.com/masahiro-999/oscilloscope-mcp/blob/main/README.md) · [许可证](https://github.com/masahiro-999/oscilloscope-mcp/blob/main/LICENSE)

## lecroy-mcp

[lucasgerads/lecroy-mcp](https://github.com/lucasgerads/lecroy-mcp) · 设备桥接 · AGPL-3.0 · 维护者实机记录

LeCroy 示波器控制与波形采集，使用 LAN VXI-11 或 USB。

仓库附运行演示；LAN 路径要求 VXI-11，README 明确不支持 LeCroy VICP 模式。

MCP / SCPI / VXI-11 / USB

[项目说明](https://github.com/lucasgerads/lecroy-mcp/blob/main/README.md) · [许可证](https://github.com/lucasgerads/lecroy-mcp/blob/main/LICENSE)

## siglent-scpi-mcp

[mp911de/siglent-scpi-mcp](https://github.com/mp911de/siglent-scpi-mcp) · 设备桥接 · Apache-2.0 · 维护者实机记录

Siglent 示波器和电源的类型化工具，记录实际发送的 SCPI 命令。

维护者报告一次 SDS1204X HD 与 SPD3303X-E 台架验证，包括波形缩放链；其余列出型号不能一并视为实测。

MCP / SCPI / TCP

[项目说明](https://github.com/mp911de/siglent-scpi-mcp/blob/main/README.md) · [许可证](https://github.com/mp911de/siglent-scpi-mcp/blob/main/LICENSE)

## scope-mcp

[Netlist-Studio/scope-mcp](https://github.com/Netlist-Studio/scope-mcp) · 设备桥接 · MIT · 维护者实机记录

Keysight/Agilent 示波器的设置、截图、波形下载、测量与串行解码。

README 指明实测 Agilent MSOX2024A，固件 02.43.2018020635。

MCP / PyVISA / Ethernet / SCPI

[项目说明](https://github.com/Netlist-Studio/scope-mcp/blob/main/README.md) · [许可证](https://github.com/Netlist-Studio/scope-mcp/blob/main/LICENSE)

## dwf-mcp-server

[KenosInc/dwf-mcp-server](https://github.com/KenosInc/dwf-mcp-server) · 设备桥接 · MIT · 接入实现 / 文档

Digilent WaveForms 设备的示波器、任意波形与逻辑分析接口。

开源服务依赖单独取得的专有 libdwf/运行库；不能把服务端 MIT 许可理解为整个 SDK 开源。

MCP / dwfpy / WaveForms SDK / USB

[项目说明](https://github.com/KenosInc/dwf-mcp-server/blob/main/README.md) · [许可证](https://github.com/KenosInc/dwf-mcp-server/blob/main/LICENSE)

## Instrument MCP

[zeng-andrew/instrument-mcp](https://github.com/zeng-andrew/instrument-mcp) · 设备桥接 · Unspecified · 接入实现 / 文档

集成频谱分析仪、无线综测仪、电源、温箱及逻辑分析仪，使用 YAML 描述命令并管理多仪器会话。

列出 Keysight MXA/EXA、R&S CMW500 与 DSLogic 等适配目标；未识别到许可证。

MCP / SCPI / Modbus RTU / USB / YAML commands

[项目说明](https://github.com/zeng-andrew/instrument-mcp/blob/main/README.md)

## daqmx-mcp

[BrianDavidCouch/daqmx-mcp](https://github.com/BrianDavidCouch/daqmx-mcp) · 设备桥接 · Apache-2.0 · 接入实现 / 文档

发现 NI DAQ 设备并执行有限长度的模拟电压和数字输入采集。

社区项目；当前版本没有输出、连续采集或任意属性写入。NI 驱动独立安装。

MCP / Codex plugin / NI nidaqmx

[项目说明](https://github.com/BrianDavidCouch/daqmx-mcp/blob/main/README.md) · [许可证](https://github.com/BrianDavidCouch/daqmx-mcp/blob/main/LICENSE)

## DAQiFi Core

[daqifi/daqifi-core](https://github.com/daqifi/daqifi-core) · 设备桥接 · MIT · 接入实现 / 文档

厂商公开的无线采集 SDK 与 MCP 服务，涵盖通道配置、采样、数字 I/O、PWM、模拟输出和 SD 卡记录。

README 将采集控制和记录下载连成完整路径；具体能力取决于 DAQiFi 设备型号。

MCP / .NET API / Wi-Fi / USB

[项目说明](https://github.com/daqifi/daqifi-core/blob/main/README.md) · [许可证](https://github.com/daqifi/daqifi-core/blob/main/LICENSE) · [实现入口](https://github.com/daqifi/daqifi-core/tree/main/src/Daqifi.Mcp)

## LabVIEW MCP Server Toolkit

[JanGoebel/LabVIEW-MCP-Server-Toolkit](https://github.com/JanGoebel/LabVIEW-MCP-Server-Toolkit) · 设备桥接 · MIT · 接入实现 / 文档

让已有 LabVIEW 应用以工具、资源和提示的方式暴露 VI。适合直接包装实验室现有控制程序。

开源工具包；LabVIEW 本体与仪器 VI 的依赖、许可分别存在。

MCP / HTTP / LabVIEW VIs

[项目说明](https://github.com/JanGoebel/LabVIEW-MCP-Server-Toolkit/blob/main/readme.md) · [许可证](https://github.com/JanGoebel/LabVIEW-MCP-Server-Toolkit/blob/main/LICENSE)

## LabVIEW MCP · Zühlke

[Zuehlke/labview-mcp](https://github.com/Zuehlke/labview-mcp) · 仪器开发 · MIT · 接入实现 / 文档

Agent 可读取、修改和运行 LabVIEW 程序，主要处于开发工具层；能否控制设备取决于所运行 VI。

依赖 LabVIEW 内部 lvai.LVAI 服务，README 明确它不是已发布、稳定承诺的 NI API。

MCP / gRPC / LabVIEW scripting

[项目说明](https://github.com/Zuehlke/labview-mcp/blob/main/README.md) · [许可证](https://github.com/Zuehlke/labview-mcp/blob/main/LICENSE)

## OpenFlexure-MCP

[GSIBabu/OpenFlexure-MCP](https://github.com/GSIBabu/OpenFlexure-MCP) · 设备桥接 · GPL-3.0 · 接入实现 / 文档

通过 OpenFlexure 客户端操作载物台、拍照、自动对焦、Z-stack 与扩展功能。

接入路径指向同一网络的真实 OpenFlexure 显微镜；仓库未给出系统化实测矩阵。

MCP / OpenFlexure Python client / HTTP

[项目说明](https://github.com/GSIBabu/OpenFlexure-MCP/blob/main/README.md) · [许可证](https://github.com/GSIBabu/OpenFlexure-MCP/blob/main/LICENSE)

## microscope-agent

[BioNanomics/microscope-agent](https://github.com/BioNanomics/microscope-agent) · 设备桥接 · MIT · 接入实现 / 文档

面向 Nikon Ti2-E 与 Baumer 相机的紧凑接口，读位置、移动 XY、采图；图像与实际位置及状态修订号关联。

提供 SDK 与 mock 路径；返回图像预览及完整文件。当前工具刻意不开放绝对 Z 移动。

MCP / Nikon SDK / GenICam camera

[项目说明](https://github.com/BioNanomics/microscope-agent/blob/main/README.md) · [许可证](https://github.com/BioNanomics/microscope-agent/blob/main/LICENSE)

## Agent-Lens

[aicell-lab/agent-lens](https://github.com/aicell-lab/agent-lens) · 过程编排 · MIT · 接入实现 / 文档

将显微镜控制、机器人样本转移、图像分割、相似搜索和 OME-Zarr 数据组织在一起。

公开服务注册代码与在线演示入口；主要设备调用经 Hypha 服务，未将原生 MCP 标作已确认接口。

Hypha RPC / Python / Web UI / BioEngine

[项目说明](https://github.com/aicell-lab/agent-lens/blob/main/README.md) · [许可证](https://github.com/aicell-lab/agent-lens/blob/main/LICENSE) · [实现入口](https://github.com/aicell-lab/agent-lens/blob/main/agent_lens/register_tools_service.py)

## Agentic microscope

[kyu-softmatter/agentic-microscope](https://github.com/kyu-softmatter/agentic-microscope) · 设备桥接 · MIT · 接入实现 / 文档

将研究目标转为有硬件边界与校准依据的显微镜配置，涵盖显微镜、光镊与压电平台。

已读设置、应用与回读代码。README 提醒光镊 TCP 接口的接受回执不等于动作完成，并宣布向 soft-matter-agents 迁移。

MCP / Python / Micro-Manager / Vendor SDK/TCP

[项目说明](https://github.com/kyu-softmatter/agentic-microscope/blob/main/README.md) · [许可证](https://github.com/kyu-softmatter/agentic-microscope/blob/main/LICENSE) · [实现入口](https://github.com/kyu-softmatter/agentic-microscope/blob/main/hardware/microscope.py)

## soft-matter-agents

[kyu-softmatter/soft-matter-agents](https://github.com/kyu-softmatter/soft-matter-agents) · 过程编排 · MIT · 接入实现 / 文档

显微镜、模拟、文献与桥接 Agent 的组合工程；显微镜模块是旧 Agentic microscope 的后继位置。

作为迁移入口收录；各模块不都连接物理设备，具体硬件能力仍需查 microscope_agent。

Python / Microscope agent / Agent workflows

[项目说明](https://github.com/kyu-softmatter/soft-matter-agents/blob/main/README.md) · [许可证](https://github.com/kyu-softmatter/soft-matter-agents/blob/main/LICENSE)

## AILA

[M3RG-IITD/AILA](https://github.com/M3RG-IITD/AILA) · 实验决策 · MIT · 论文实机案例

原子力显微镜实验中的语言模型助手，结合任务分解、工具调用和反馈。

Nature Communications 论文报告实机 AFM 实验；代码与基准公开，重用需匹配论文的仪器控制环境。

Python tools / LLM agents / Instrument control software

[项目说明](https://github.com/M3RG-IITD/AILA/blob/main/README.md) · [许可证](https://github.com/M3RG-IITD/AILA/blob/main/LICENSE.md) · [论文](https://www.nature.com/articles/s41467-025-64105-7)

## LLM-directed-SPM

[DIAOZHUO/LLM-directed-SPM](https://github.com/DIAOZHUO/LLM-directed-SPM) · 实验决策 · Unspecified · 论文实机案例

扫描探针显微实验中的命令生成、知识库和专门小模型；包含本地模型服务与模型训练材料。

论文描述物理扫描探针实验；仓库未识别到顶层许可证，模型训练代码与完整设备接入应分别评估。

Python / WebSocket / Small language models / spmutil

[项目说明](https://github.com/DIAOZHUO/LLM-directed-SPM/blob/main/readme.md) · [论文](https://arxiv.org/abs/2602.20669)

## Quailbot Pi

[BB-84C/quailbot-pi](https://github.com/BB-84C/quailbot-pi) · 常驻执行 · ISC · 接入实现 / 文档

将仪器工作区变为参数、动作、图像回读与多步程序的固定工具接口；操作与后续观察分别记录。Nanonis 路径依赖外部 nqctl。

公开 Pi 扩展与工作区说明；STM 论文是相关实验背景，不据此宣称该扩展独立包含全部硬件驱动。

Pi extension / CLI driver contract / Workspace JSON / Image readback

[项目说明](https://github.com/BB-84C/quailbot-pi/blob/main/README.md) · [许可证](https://github.com/BB-84C/quailbot-pi/blob/main/LICENSE) · [论文](https://arxiv.org/abs/2609.27302)

## VISION

[CFN-softbio/VISION](https://github.com/CFN-softbio/VISION) · 实验决策 · Unspecified · 论文实机案例

以语音或文字把用户意图转为束线操作代码，模块化处理转录、分类、编程与分析。

项目展示 NSLS-II 11-BM CMS 工作站部署和用户确认后执行；不是无人闭环的通用仪器协议。未识别到许可证。

Voice/text / Python code generation / Bluesky workstation

[项目说明](https://github.com/CFN-softbio/VISION/blob/main/README.md) · [论文](https://doi.org/10.1088/2632-2153/add9e4)

## LeeQ

[ShuxiangCao/LeeQ](https://github.com/ShuxiangCao/LeeQ) · 常驻执行 · BSD-3-Clause · 论文实机案例

超导量子器件的脉冲实验、扫描、校准状态与分析框架；可向 Agent 提供实验描述及图文检查接口。

k-agents 论文报告量子校准实验；仓库同时提供模拟路径，应按后端识别实验来源。

Python experiment API / Pulse control / k-agents integration

[项目说明](https://github.com/ShuxiangCao/LeeQ/blob/main/README.md) · [许可证](https://github.com/ShuxiangCao/LeeQ/blob/main/LICENSE) · [论文](https://doi.org/10.1016/j.patter.2025.101372)

## k-agents

[EvoEvolver/k_agents](https://github.com/EvoEvolver/k_agents) · 实验决策 · Unspecified · 论文实机案例

围绕已有实验库发现、执行和判断校准实验，保留实验知识与视觉结果。

论文有实机量子校准；README 已指向 NVIDIA Quantum Calibration Agent Blueprint。当前仓库未识别到许可证。

Python / Experiment agents / LeeQ

[项目说明](https://github.com/EvoEvolver/k_agents/blob/main/README.md) · [论文](https://arxiv.org/abs/2412.07978)

## Quantum Calibration Agent Blueprint

[NVIDIA/Quantum-Calibration-Agent-Blueprint](https://github.com/NVIDIA/Quantum-Calibration-Agent-Blueprint) · 实验决策 · Apache-2.0 · 接入实现 / 文档

量子器件校准 Agent 参考工程，包含实验发现、执行、图像分析、工作流和结果存储。

NVIDIA 公开 Apache-2.0 工程，实验通过用户提供的 Python 脚本接入；不能把参考界面视为已覆盖所有量子控制器。

Python experiment scripts / CLI / Web UI / HDF5 / SQLite

[项目说明](https://github.com/NVIDIA/Quantum-Calibration-Agent-Blueprint/blob/main/README.md) · [许可证](https://github.com/NVIDIA/Quantum-Calibration-Agent-Blueprint/blob/main/LICENSE)

## CALMS

[mcherukara/CALMS](https://github.com/mcherukara/CALMS) · 实验决策 · BSD-3-Clause · 维护者实机记录

上下文与工具增强的科学设施助手，将仪器知识和操作函数纳入交互。

早期公开实现附演示；许可文本为三条款 BSD。后续机器人与束线工作另见 APS 仓库。

Python tools / Retrieval / Instrument commands

[项目说明](https://github.com/mcherukara/CALMS/blob/main/README.md) · [许可证](https://github.com/mcherukara/CALMS/blob/main/LICENSE)

## CALMS · APS experimental agents

[AdvancedPhotonSource/CALMS](https://github.com/AdvancedPhotonSource/CALMS) · 实验决策 · Unspecified · 论文实机案例

面向 North N9 机器人与 X-ray nanoprobe 的可教学实验 Agent 工作流。

README 列出机器人、纳米探针命令模块及运行视频；许可证未识别，分支以仓库当前默认分支为准。

Python / Robot command functions / Beamline tools

[项目说明](https://github.com/AdvancedPhotonSource/CALMS/blob/main/README.md) · [论文](https://doi.org/10.1038/s41524-026-02005-0)

## Opentrons MCP

[yerbymatey/opentrons-mcp](https://github.com/yerbymatey/opentrons-mcp) · 设备桥接 · MIT · 接入实现 / 文档

结合 API 文档检索与机器人协议上传、运行管理、归位及状态读取，面向 OT-2/Flex。

设备调用走机器人 HTTP API；文档查询工具与会驱动机器人动作的工具分别存在。

MCP / Opentrons HTTP API

[项目说明](https://github.com/yerbymatey/opentrons-mcp/blob/main/README.md) · [许可证](https://github.com/yerbymatey/opentrons-mcp/blob/main/LICENSE)

## plr-mcp

[di-omics/plr-mcp](https://github.com/di-omics/plr-mcp) · 设备桥接 · MIT · 模拟验证

将液体处理、酶标仪、热循环仪和加热振荡器操作暴露为 MCP，复用 PyLabRobot 后端。

默认以 chatterbox 模拟器端到端验证；有真实 STAR 后端入口与接机说明，不能把模拟验证等同于实机验证。

MCP / PyLabRobot

[项目说明](https://github.com/di-omics/plr-mcp/blob/main/README.md) · [许可证](https://github.com/di-omics/plr-mcp/blob/main/LICENSE)

## OpenLabAI

[nygmeta/OpenLabAI](https://github.com/nygmeta/OpenLabAI) · 过程编排 · MIT · 维护者实机记录

自然语言液体处理工作流，包含 Opentrons、Biomek、Hamilton 与实验记录连接。

维护者报告 OT-2 读取、状态、归位与协议生成已接实机，上传/启动等执行工具尚未实机运行；Hamilton 和台式设备层为模拟。

MCP / Opentrons HTTP / Biomek COM / PyLabRobot

[项目说明](https://github.com/nygmeta/OpenLabAI/blob/main/README.md) · [许可证](https://github.com/nygmeta/OpenLabAI/blob/main/LICENSE)

## LabscriptAI OT

[KRATSZ/labscriptai-ot](https://github.com/KRATSZ/labscriptai-ot) · 过程编排 · LabscriptAI Research Citation License v1.0 · 接入实现 / 文档

面向 Opentrons 的 Agent 插件，集成协议编写、模拟、技能和实时运行辅助。

当前采用 LabscriptAI Research Citation License，商业使用须另行许可；不列入标准开源许可组。

MCP / Agent Skills / Opentrons / Local simulation

[项目说明](https://github.com/KRATSZ/labscriptai-ot/blob/main/README.md) · [许可证](https://github.com/KRATSZ/labscriptai-ot/blob/main/LICENSE) · [论文](https://doi.org/10.1101/2025.09.30.679666)

## Coscientist

[gomesgroup/coscientist](https://github.com/gomesgroup/coscientist) · 实验决策 · Apache-2.0 + Commons Clause · 论文实机案例

语言模型组织文献、程序和实验工具完成化学研究；是早期真实实验的重要案例。

论文报告机器人化学实验；公开代码不等于论文的完整可部署实验室。许可为 Apache-2.0 加 Commons Clause。

Python tools / Opentrons / Laboratory APIs

[项目说明](https://github.com/gomesgroup/coscientist/blob/main/README.md) · [许可证](https://github.com/gomesgroup/coscientist/blob/main/LICENSE) · [论文](https://doi.org/10.1038/s41586-023-06792-0)

## ChemAgents

[pic-ai-robotic-chemistry/ChemAgents](https://github.com/pic-ai-robotic-chemistry/ChemAgents) · 实验决策 · Unspecified · 论文实机案例

多 Agent 化学研究系统，连接实验协议、机器人工作站与实验数据。

仓库提供论文代码和实验数据，并把机器人指令与 AGV 驱动链接到其他仓库；本仓库未识别到许可证。

LangGraph tools / Robot instruction set / ROS drivers

[项目说明](https://github.com/pic-ai-robotic-chemistry/ChemAgents/blob/main/README.md) · [论文](https://doi.org/10.1021/jacs.4c17738)

## ORGANA

[ac-rad/organa](https://github.com/ac-rad/organa) · 实验决策 · Unspecified · 论文实机案例

ORGANA 论文中的化学机器人助手结合用户目标、场景感知与实验进度；本仓库主要发布项目网站与研究材料。

论文展示真实机器人实验；README 明确该仓库包含网站源码，没有据此确认完整机器人控制实现；许可证未识别。

Task planning / Robot perception / Laboratory operations

[项目说明](https://github.com/ac-rad/organa/blob/main/README.md) · [论文](https://arxiv.org/abs/2401.06949)

## CLAIRify

[ac-rad/xdl-generation](https://github.com/ac-rad/xdl-generation) · 过程编排 · MIT · 论文实机案例

把自然语言实验步骤转换为可检查的 XDL 过程，验证错误反馈给模型进行修订。

论文含机器人执行；本仓库主要发布生成器与数据。README 指明旧代码接口已过时，更新版本在 develop 分支。

Natural language to XDL / Verifier loop / Python

[项目说明](https://github.com/ac-rad/xdl-generation/blob/master/README.md) · [许可证](https://github.com/ac-rad/xdl-generation/blob/master/LICENSE) · [论文](https://arxiv.org/abs/2303.14100)

## CLAIRify-Chemspeed

[ac-rad/clairify-chemspeed](https://github.com/ac-rad/clairify-chemspeed) · 过程编排 · Unspecified · 接入实现 / 文档

自然语言生成 Chemspyd 程序，把协议生成连接到 Chemspeed 自动化平台。

Chemspyd 论文链接的接口示例；未识别到本仓库许可证。

Python generation / Chemspyd / Chemspeed

[项目说明](https://github.com/ac-rad/clairify-chemspeed/blob/master/README.md) · [论文](https://doi.org/10.1039/D4DD00046C)

## SynAgent · thin-film synthesis

[izumitkhr/synagent](https://github.com/izumitkhr/synagent) · 实验决策 · MIT · 论文实机案例

薄膜合成闭环中的多模态规划与假设检验，读取 XRD/SEM 数据，为下一次实验写出条件。

论文报告 18 次物理实验；公开程序通过 MaiML 输入与 output.txt 对接 dLab，未打包整套沉积、搬运与测量驱动。

Python iteration runner / MaiML / File-based platform interface / Generated skills

[项目说明](https://github.com/izumitkhr/synagent/blob/main/README.md) · [许可证](https://github.com/izumitkhr/synagent/blob/main/LICENSE) · [论文](https://arxiv.org/abs/2609.18598)

## AutoLabs

[pnnl/autolabs](https://github.com/pnnl/autolabs) · 实验决策 · BSD-2-Clause · 配套代码 / 资料

生成实验步骤与 Lab Step Representation，支持多 Agent 修订和实验设计评估。

公开应用重点是设计、模拟和评估；不能仅凭论文的物理实验将此仓库当作完整硬件执行系统。

Python / LSR export / Agent planning

[项目说明](https://github.com/pnnl/autolabs/blob/master/README.md) · [许可证](https://github.com/pnnl/autolabs/blob/master/LICENSE.md) · [论文](https://arxiv.org/abs/2509.25651)

## opcua-mcp · kukapay

[kukapay/opcua-mcp](https://github.com/kukapay/opcua-mcp) · 设备桥接 · MIT · 接入实现 / 文档

把 OPC UA 节点浏览、单点与批量读写接到 Agent，保留已有工业设备服务端。

是 OPC UA 到 MCP 的适配层；设备意义取决于服务端地址空间和信息模型。

MCP / OPC UA

[项目说明](https://github.com/kukapay/opcua-mcp/blob/main/README.md) · [许可证](https://github.com/kukapay/opcua-mcp/blob/main/LICENSE)

## OPC UA MCP · IndustriAgents

[IndustriAgents/OPCUA-MCP](https://github.com/IndustriAgents/OPCUA-MCP) · 设备桥接 · MIT · 接入实现 / 文档

浏览、读数、历史、订阅、告警与受配置约束的写入及方法调用；一个本地进程连接一个 OPC UA 端点。

README 当前已包含写入能力，但默认只读；远程共享多客户端运行仍有单独设计约束。

MCP / OPC UA / Subscriptions / History

[项目说明](https://github.com/IndustriAgents/OPCUA-MCP/blob/main/README.md) · [许可证](https://github.com/IndustriAgents/OPCUA-MCP/blob/main/LICENSE)

## modbus-mcp

[kukapay/modbus-mcp](https://github.com/kukapay/modbus-mcp) · 设备桥接 · MIT · 接入实现 / 文档

把寄存器和线圈读写暴露为工具，是连接已有 PLC、传感器与控制器的底层入口。

具备通信调用接口；寄存器单位、比例、设备模式与副作用仍需设备映射表表达。

MCP / Modbus TCP/UDP/Serial

[项目说明](https://github.com/kukapay/modbus-mcp/blob/main/README.md) · [许可证](https://github.com/kukapay/modbus-mcp/blob/main/LICENSE)

## TANGO MCP

[abogani/tango-mcp](https://github.com/abogani/tango-mcp) · 设备桥接 · Apache-2.0 · 接入实现 / 文档

从 TANGO 数据库发现设备，将属性、状态和命令映射为 MCP 资源与工具，支持批量读取。

提供具体 TANGO_HOST 部署与属性/命令路径；实际可操作范围由设施已有设备服务器决定。

MCP / PyTango / Streamable HTTP

[项目说明](https://github.com/abogani/tango-mcp/blob/main/README.md) · [许可证](https://github.com/abogani/tango-mcp/blob/main/LICENSE)

## MCP Server for EPICS

[sryu81/mcp-server-for-epics](https://github.com/sryu81/mcp-server-for-epics) · 设备桥接 · Unspecified · 接入实现 / 文档

提供独立进程和 IOC 内嵌两种入口，把 EPICS PV 和控制命令暴露给 Agent。

C++ 共享库和协议分派结构公开；未识别到许可证。

MCP / EPICS CA/PVA / IOC / stdio/HTTP

[项目说明](https://github.com/sryu81/mcp-server-for-epics/blob/main/README.md)

## MCP2Serial

[mcp2everything/mcp2serial](https://github.com/mcp2everything/mcp2serial) · 设备桥接 · MIT · 接入实现 / 文档

通过串口连接 MCU 与 Agent，适合作为自制仪器的基础通信桥。

README 给出 Pico 等接入流程；串口传输本身不定义仪器的量纲、状态或完成条件。

MCP / Serial / Raspberry Pi Pico

[项目说明](https://github.com/mcp2everything/mcp2serial/blob/main/README.md) · [许可证](https://github.com/mcp2everything/mcp2serial/blob/main/LICENSE)

## tinymcp

[golioth/tinymcp](https://github.com/golioth/tinymcp) · 设备桥接 · Apache-2.0 · 接入实现 / 文档

将 Golioth 设备 RPC 及其描述动态暴露为 MCP 工具，已有设备可通过状态服务发布工具 schema。

包含 Zephyr LED 控制示例；服务代码开源，但运行依赖 Golioth 平台，不能当作纯离线通用设备协议。

MCP / Golioth management API / Device RPC

[项目说明](https://github.com/golioth/tinymcp/blob/main/README.md) · [许可证](https://github.com/golioth/tinymcp/blob/main/LICENSE)

## Embedded Debugger MCP

[Adancurusul/embedded-debugger-mcp](https://github.com/Adancurusul/embedded-debugger-mcp) · 仪器开发 · MIT · 维护者实机记录

让 Agent 连接调试探针、控制目标、读写内存、设断点、刷写与检查故障，为仪器固件开发提供物理反馈。

维护者声明在真实 ESP32-S3 上验证；原生 probe-rs 和 OpenOCD 后端分开配置。

MCP / CLI / Agent Skills / probe-rs / OpenOCD/GDB

[项目说明](https://github.com/Adancurusul/embedded-debugger-mcp/blob/main/README.md) · [许可证](https://github.com/Adancurusul/embedded-debugger-mcp/blob/main/LICENSE)

## Saleae Logic 2 MCP

[hsoffar/saleae-logic2-mcp](https://github.com/hsoffar/saleae-logic2-mcp) · 仪器开发 · Apache-2.0 · 接入实现 / 文档

逻辑分析仪的采集、协议解码、时序测量和导出接口，用于固件与真实总线调试。

依赖已开启自动化接口的 Saleae Logic 2；该软件和硬件不随开源服务提供。

MCP / Logic 2 automation API

[项目说明](https://github.com/hsoffar/saleae-logic2-mcp/blob/main/README.md) · [许可证](https://github.com/hsoffar/saleae-logic2-mcp/blob/main/LICENSE)

## MicroPython MCP Bridge

[SWITCHSCIENCE/mcp-micropython-bridge](https://github.com/SWITCHSCIENCE/mcp-micropython-bridge) · 仪器开发 · Unspecified · 接入实现 / 文档

通过串口或 WebREPL 操作 ESP32/RP2040 等，利用设备侧 helper 模块和 HARDWARE.md 保存板级知识。

提供实机测试 CLI 和固件接入说明；未识别到顶层许可证。

MCP / USB Serial / WebREPL / MicroPython

[项目说明](https://github.com/SWITCHSCIENCE/mcp-micropython-bridge/blob/main/README.md)

## ROS MCP Server

[robotmcp/ros-mcp-server](https://github.com/robotmcp/ros-mcp-server) · 设备桥接 · Apache-2.0 · 维护者实机记录

经 rosbridge 发现主题、服务、动作与消息类型，发布控制消息并读取机器人传感器反馈。

仓库附机器人演示；适配覆盖 ROS 通信层，具体运动能力和控制器仍在机器人自身系统中。

MCP / rosbridge / ROS 1 / ROS 2

[项目说明](https://github.com/robotmcp/ros-mcp-server/blob/main/README.md) · [许可证](https://github.com/robotmcp/ros-mcp-server/blob/main/LICENSE)

## ROSA

[nasa-jpl/rosa](https://github.com/nasa-jpl/rosa) · 实验决策 · Apache-2.0 · 论文实机案例

JPL 的 ROS 自然语言助手，结合系统诊断、状态查询与可扩展机器人操作工具。

论文与示例覆盖机器人应用；ROSA 是 Agent 工具框架，不能由名称推断具有原生 MCP。

LangChain tools / ROS 1 / ROS 2

[项目说明](https://github.com/nasa-jpl/rosa/blob/main/README.md) · [许可证](https://github.com/nasa-jpl/rosa/blob/main/LICENSE) · [论文](https://arxiv.org/abs/2410.06472)

## device-use

[labclaw/device-use](https://github.com/labclaw/device-use) · 界面操作 · Apache-2.0 · 接入实现 / 文档

用屏幕观察、规划和鼠标键盘操作包装仪器软件，配套设备 profile。适用于 API 缺失时的替代接入研究。

公开实现含 NMR 数据处理与酶标仪模块；MCP 工具存在不等于全部列出的商业仪器都已完成物理控制验证。

Python / GUI automation / MCP / VLM backends

[项目说明](https://github.com/labclaw/device-use/blob/main/README.md) · [许可证](https://github.com/labclaw/device-use/blob/main/LICENSE) · [实现入口](https://github.com/labclaw/device-use/blob/main/src/device_use/integrations/mcp_server.py)

## device-skills

[labclaw/device-skills](https://github.com/labclaw/device-skills) · 知识与资料 · Apache-2.0 · 配套代码 / 资料

仪器操作知识与技能材料，与 device-use 的执行接口配套。

技能是知识与操作说明；独立收录为配套资料，不计作设备驱动或独立实机系统。

Agent Skills / Device operating knowledge

[项目说明](https://github.com/labclaw/device-skills/blob/main/README.md) · [许可证](https://github.com/labclaw/device-skills/blob/main/LICENSE)

## edge-mhs

[fastly/edge-mhs](https://github.com/fastly/edge-mhs) · 设备桥接 · Apache-2.0 · 模拟验证

在 Agent 与设备服务之间加入边缘网关，处理身份、参数约束、配额与审计。

README 将其定位为参考实现并使用 mock 后端；不是 Anthropic 官方 MHS 服务端。

MCP gateway / Fastly Compute

[项目说明](https://github.com/fastly/edge-mhs/blob/main/README.md) · [许可证](https://github.com/fastly/edge-mhs/blob/main/LICENSE)

## Agent2Device Protocol

[neogyk/Agent2Device-Protocol](https://github.com/neogyk/Agent2Device-Protocol) · 仪器说明 · MIT · 构想 / 提案

讨论 Agent 与实验设备连接的协议构想。

查阅仓库树只有 README、LICENSE 与忽略文件，没有协议实现或设备驱动。

Design notes

[项目说明](https://github.com/neogyk/Agent2Device-Protocol/blob/main/README.md) · [许可证](https://github.com/neogyk/Agent2Device-Protocol/blob/main/LICENSE)

## ChemCrow public release

[ur-whitelab/chemcrow-public](https://github.com/ur-whitelab/chemcrow-public) · 知识与资料 · MIT · 配套代码 / 资料

化学工具增强 Agent 的重要案例，可用于理解工具编排和实验服务边界。

论文有实验执行，但 README 明确公共包因 API 限制不包含论文所有工具；不据论文补写未公开的硬件接口。

Python / LangChain tools

[项目说明](https://github.com/ur-whitelab/chemcrow-public/blob/main/README.md) · [许可证](https://github.com/ur-whitelab/chemcrow-public/blob/main/LICENSE) · [论文](https://doi.org/10.1038/s42256-024-00832-8)

## NV autonomous experiments

[takuyaisogawa/nv-autonomous-experiments](https://github.com/takuyaisogawa/nv-autonomous-experiments) · 知识与资料 · MIT code / CC BY-4.0 artifacts · 配套代码 / 资料

NV 中心自主实验的公共案例、分析代码与实验资料。

许可和发布说明明确未包含 live-laboratory backend；可研究实验轨迹，不能直接当作完整 NV 设备控制软件。

Python / MATLAB / Case-study artifacts

[项目说明](https://github.com/takuyaisogawa/nv-autonomous-experiments/blob/main/README.md) · [许可证](https://github.com/takuyaisogawa/nv-autonomous-experiments/blob/main/LICENSE) · [论文](https://arxiv.org/abs/2607.25145)

## UC2 LLM microscopy workshop

[openUC2/Hackathon-UC2-LLM](https://github.com/openUC2/Hackathon-UC2-LLM) · 知识与资料 · Unspecified · 配套代码 / 资料

围绕真实 UC2 显微镜和 ImSwitch API 的教学入口，包括设备构成、接入与实验挑战。

是课程与示例资料，不是独立完整的 Agent 平台；未识别到许可证。

ImSwitch FastAPI / Python

[项目说明](https://github.com/openUC2/Hackathon-UC2-LLM/blob/main/README.md)

