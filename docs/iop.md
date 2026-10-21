# IOP — Instrument Operations Protocol

**仪器操作协议**

IOP defines the physical meaning, execution and evidence of instrument operations. People and software use the same definitions; methods compose operations; device adapters connect them to physical equipment.

IOP 定义仪器操作的物理含义、执行方式与结果依据。人和程序使用共同定义，方法组合这些操作，设备适配器把操作落实到真实仪器。

## Platform architecture / 平台架构

IOP is organized into four components: **instrument descriptions, a persistent runtime, experiment programs and experiment records**. The three mechanism families in the comparative study explain existing approaches; these four components define our system architecture.

IOP 按四个部分组织：**仪器说明、常驻运行时、实验程序、实验记录**。前文的三个机制岛屿用于归纳已有方案；这里的四部分定义我们的系统架构。

| Component / 组成 | Responsibility / 职责 |
| --- | --- |
| Instrument descriptions / 仪器说明 | Principles, operating knowledge, capabilities, quantities, operations, affected resources and completion conditions. / 原理、使用知识、能力、物理量、操作、作用资源与完成条件。 |
| Persistent runtime / 常驻运行时 | Device registration and connections, resource ownership, dependency scheduling, managed experiment workers, state and events. / 设备注册与连接、资源占用、依赖调度、实验工作进程、状态与事件。 |
| Experiment programs / 实验程序 | Versioned methods, dependencies, loops, conditions, parameters and analysis. / 版本化的方法、步骤依赖、循环、条件、参数与分析。 |
| Experiment records / 实验记录 | Research and experiment identities, runs, operation histories, observations, data and their context. / 研究与实验身份、运行、操作历史、观测、数据及其上下文。 |

Each experimental platform has one service responsible for its registered devices. Drivers bind each device identity to its capabilities and endpoint. People and agents submit experiment packages or individual operations through the service. The service manages experiment workers and device connections, so experiments retain their identity and execution state across caller disconnects. Multiple platforms coordinate through their respective services.

每个实验平台由一个常驻服务管理已注册设备。驱动将设备身份、能力与连接地址绑定起来。人和 Agent 通过服务提交实验包或单步操作。服务管理实验工作进程及设备连接，调用者断开后，实验仍保留执行身份与状态。多个平台通过各自的服务协作。

### Scheduling / 调度

The method declares dependencies; the instrument description declares physical effects, read/write access, occupied resources and observable completion. An operation becomes eligible when its dependencies are complete and all required resources are available. The scheduler acquires the declared resource set together and orders incompatible requests. Compatible operations can run concurrently.

方法声明步骤依赖，仪器说明声明物理影响、读写方式、占用资源与可观测的完成条件。前置步骤完成且所需资源全部可用时，操作进入执行；调度器一次取得声明的资源集合，对不兼容的请求排序，允许兼容操作并行。

A run can reserve resources across several steps while the scheduler also coordinates operations within that run. In a polarization scan, retain the axis, optical path and detector until the scan point is acquired. Stage movement and detector setup can proceed together; acquisition starts after both complete. This prevents another experiment from changing the optical state between positioning and measurement. Communication channels are held for the required exchange; physical motion can continue while other devices operate. Device clocks and hardware triggers handle precision synchronization.

实验可跨步骤保留资源，调度器同时协调实验内部的操作。偏振扫描中，当前扫描点持续占用转轴、光路与探测器，直到采集完成。转台移动与探测器设置可同时推进，采集等待二者完成，避免其他实验在设角与测量之间改变光学状态。通信通道按实际通信需求占用；运动期间其他可用设备继续工作。精确同步由设备时钟与硬件触发完成。

### Records and continuation / 留档与持续执行

The service links project_id → experiment_id → run_id → operation_id → observations and artifacts. At acceptance it fixes package, parameter, driver and description versions. Requests enter the durable journal before dispatch; subsequent events record execution state, actual readings and data references. Completed, failed, stopped and partial runs remain queryable. After a service restart, unfinished operations are reconciled against device readback before scheduling continues.

服务关联 project_id → experiment_id → run_id → operation_id → 观测与数据文件。任务受理时固定实验包、参数、驱动与说明版本。请求先进入持久记录，再下发设备；后续事件记录执行状态、实际读数和数据引用。完成、失败、停止和部分结果均保留。服务重启后，依据记录与设备读回核对未完成操作，再继续调度。

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

The comparative study follows one hierarchy: existing designs → shared mechanisms → IOP. Capability models contribute descriptions and driver mappings. Execution rules contribute task lifecycles and measurement records. Discovery and resource coordination contribute equipment identities, reservations and access paths.

研究采用一条固定关系：具体方案 → 共同机制 → IOP。能力模型提供描述与驱动映射；执行规则提供任务生命周期与测量记录；发现和资源协作提供设备身份、占用与访问路径。

Compatibility is defined per capability: inputs retain physical meaning, completion follows device readback, and results retain units and acquisition context. SiLA 2, OPC UA/LADS, W3C WoT and existing drivers provide mapping foundations. API, CLI, MCP and human interfaces can share the same operation model.

兼容性按能力建立：输入保留物理含义，完成条件依赖设备读回，结果保留单位与采集条件。SiLA 2、OPC UA/LADS、W3C WoT 及已有驱动提供映射基础；API、CLI、MCP 与人工界面共享操作模型。

## Development / 建设

The repository currently contains an [operation composition model](operations.md) and a simulated optical reference implementation. The next implementation target is a platform service with device registration, persistent runs, dependency/resource scheduling and linked records, followed by one polarization-scan method operating across two physical equipment configurations.

仓库当前提供[操作组合模型](operations.md)与模拟光学参考实现。下一实现目标是具备设备注册、持久运行、依赖与资源调度、关联记录的平台常驻服务，再使同一个偏振扫描方法在两套真实设备组合上运行。

[中文 IOP](agent-instruments/index.zh-CN.html#presentation/1) · [English IOP](agent-instruments/index.en.html#presentation/1) · [Content and mechanisms](agent-instruments/presentation.json)
