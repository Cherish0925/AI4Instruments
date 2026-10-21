# IOP — Instrument Operations Protocol

**仪器操作协议**

IOP is the name of AI4Instruments' instrument interoperability effort. It connects instrument knowledge, executable operations and experimental results through shared definitions. People and agents use the same operation meanings through documentation, interfaces, scripts or tools.

IOP 将仪器知识、可执行操作和实验结果连接到同一套定义。人和 Agent 使用共同的操作含义，通过文档、界面、脚本或工具访问。

## Design scope

| Responsibility | Shared information |
| --- | --- |
| Understand the instrument / 理解仪器 | Identity, configuration, physical principles, controllable and observable capabilities, units, calibration and applicability. / 身份、配置、物理原理、可控可测能力、单位、校准与适用条件。 |
| Execute an operation / 执行操作 | Parameters, resources, execution state, timing, completion, readback and results. / 参数、资源、执行状态、时序、完成条件、读回与结果。 |
| Compose an experiment / 组织实验 | Reusable methods, dependencies, samples, observations and feedback. / 可复用方法、依赖、样品、观测与反馈。 |

Human-readable explanations and machine-readable descriptions refer to the same operation identity and version. A method retains its applicability and links to constituent operations. Knowledge and data can remain in their appropriate formats while explicit references connect them to capabilities, procedures and observations.

人工可读说明与机器可读描述引用同一操作身份和版本。方法保留适用条件，并关联其组成操作。知识和数据使用适当的格式，通过明确引用连接能力、过程和观测。

[Basic Operations, Standard Operations and Workflow Operations](operations.md) describe composition roles. Every role needs meaningful definitions, an execution path and interpretable results. The three reading levels used in the presentation organize existing work and design analysis; they do not replace these operation roles.

IOP should reuse existing drivers, control systems and data formats through explicit mappings. Compatibility is established for named capabilities and implementations, including differences that cannot be represented without extensions. Research systems retain their objectives and decision policies.

## Development

The repository currently provides an operation model and a simulated optical reference implementation. The proposed next steps are instrument descriptions, physical-device adapters, persistent execution and reusable methods across device implementations. The presentation distinguishes existing projects, design references and proposed IOP architecture.

当前仓库已有操作模型与模拟光学参考实现。下一阶段依次实现仪器描述、真实设备适配、持续执行和跨设备的方法复用。演示分别标明现有工程、设计材料与拟议的 IOP 架构。

[中文演示与资料库](agent-instruments/index.zh-CN.html#presentation/1) · [English presentation and catalogue](agent-instruments/index.en.html#presentation/1) · [Comparison data](agent-instruments/presentation.json)
