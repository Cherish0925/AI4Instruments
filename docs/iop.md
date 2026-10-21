# IOP — Instrument Operations Protocol

**仪器操作协议**

IOP defines the physical meaning, execution and evidence of instrument operations. People and software use the same definitions; methods compose operations; device adapters connect them to physical equipment.

IOP 定义仪器操作的物理含义、执行方式与结果依据。人和程序使用共同定义，方法组合这些操作，设备适配器把操作落实到真实仪器。

## Operation model / 操作模型

| Object / 对象 | Meaning / 含义 |
| --- | --- |
| Instrument / 仪器 | Physical identity, capabilities and resources. / 物理身份、能力与资源。 |
| Operation / 操作 | Inputs, units, effects, completion criteria and outputs. / 输入、单位、作用、完成条件与输出。 |
| Method / 方法 | Applicability, procedure and analysis using named operations. / 以明确操作组成的适用条件、过程与分析方法。 |
| Binding / 设备绑定 | Mapping to drivers, vendor commands and existing control systems. / 到驱动、厂商命令及现有控制系统的映射。 |
| Run / 执行实例 | A particular execution with fixed parameters, versions, resources, state and events. / 带固定参数、版本、资源、状态与事件的一次执行。 |
| Observation / 观测 | Physical readings with units, acquisition times, conditions and provenance. / 带单位、采集时间、条件与来源的物理读数。 |

Knowledge materials explain an operation's principles, applicability and practical use through explicit identity and version references. Human-readable instructions and machine-readable descriptions remain linked. A result connects to the execution and observations that support it.

原理、适用条件与使用经验通过身份和版本关联到操作定义；人工可读说明与机器可读描述保持对应。每个结果关联到产生它的执行与支持它的观测。

## Existing mechanisms / 已有机制

The comparative study follows one hierarchy: existing designs → shared mechanisms → IOP. Capability models contribute descriptions and driver mappings. Execution contracts contribute task lifecycles and measurement records. Discovery and resource coordination contribute equipment identities, reservations and access paths.

研究采用一条固定关系：具体方案 → 共同机制 → IOP。能力模型提供描述与驱动映射；执行契约提供任务生命周期与测量记录；发现和资源协作提供设备身份、占用与访问路径。

Compatibility is defined per capability: inputs retain physical meaning, completion follows device readback, and results retain units and acquisition context. SiLA 2, OPC UA/LADS, W3C WoT and existing drivers provide mapping foundations. API, CLI, MCP and human interfaces can share the same operation model.

兼容性按能力建立：输入保留物理含义，完成条件依赖设备读回，结果保留单位与采集条件。SiLA 2、OPC UA/LADS、W3C WoT 及已有驱动提供映射基础；API、CLI、MCP 与人工界面共享操作模型。

## Development / 建设

The repository currently contains an [operation composition model](operations.md) and a simulated optical reference implementation. The next validation target is one polarization-scan method running on two physical equipment configurations with equivalent angle definitions, completion criteria and interpretable measurement records.

仓库当前提供[操作组合模型](operations.md)与模拟光学参考实现。下一验证目标是在两套真实设备组合上运行同一个偏振扫描方法，保持角度定义、完成判据和测量记录含义的一致。

[中文 IOP](agent-instruments/index.zh-CN.html#presentation/1) · [English IOP](agent-instruments/index.en.html#presentation/1) · [Content and mechanisms](agent-instruments/presentation.json)
