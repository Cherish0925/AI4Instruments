# IOP — Instrument Operation Protocol

**仪器操作协议**

IOP defines the physical meaning, execution and evidence of instrument operations. People and software use the same definitions; methods compose operations; device adapters connect them to physical equipment.

IOP 定义仪器操作的物理含义、执行方式与结果依据。人和程序使用共同定义，方法组合这些操作，设备适配器把操作落实到真实仪器。

## Platform architecture / 平台架构

The [runtime architecture](runtime/architecture.md) specifies the target Rust core, Python driver and experiment processes, TypeScript clients and SQL records, with the migration from the current Python implementation.

[常驻服务架构](runtime/architecture.zh-CN.md)说明 Rust 核心、Python 驱动与实验进程、TypeScript 客户端、SQL 记录的分工，以及从当前 Python 实现逐步推进的顺序。

IOP is organized into four components: **instrument descriptions, a persistent service, experiment programs and experiment records**. The three mechanism families in the comparative study explain existing approaches; these four components define our system architecture.

IOP 按四个部分组织：**仪器说明、常驻服务、实验程序、实验记录**。前文的三个机制岛屿用于归纳已有方案；这里的四部分定义我们的系统架构。

| Component / 组成 | Responsibility / 职责 |
| --- | --- |
| Instrument descriptions / 仪器说明 | Principles, operating knowledge, capabilities, quantities, operations, affected resources and completion conditions. / 原理、使用知识、能力、物理量、操作、作用资源与完成条件。 |
| Persistent service / 常驻服务 | Device registration and connections, resource ownership, dependency scheduling, managed experiment workers, state and events. / 设备注册与连接、资源占用、依赖调度、实验工作进程、状态与事件。 |
| Experiment programs / 实验程序 | Versioned methods, dependencies, loops, conditions, parameters and analysis. / 版本化的方法、步骤依赖、循环、条件、参数与分析。 |
| Experiment records / 实验记录 | Research and experiment identities, runs, operation histories, observations, data and their context. / 研究与实验身份、运行、操作历史、观测、数据及其上下文。 |

Each experimental platform has one service responsible for its registered devices. Drivers bind each device identity to its capabilities and endpoint. People and agents submit experiment packages or individual operations through the service. The service manages experiment workers and device connections, so experiments retain their identity and execution state across caller disconnects. Multiple platforms coordinate through their respective services.

每个实验平台由一个常驻服务管理已注册设备。驱动将设备身份、能力与连接地址绑定起来。人和 Agent 通过服务提交实验包或单步操作。服务管理实验工作进程及设备连接，调用者断开后，实验仍保留执行身份与状态。多个平台通过各自的服务协作。

Runtime names the software system that executes experiments. Persistent daemon processes host the platform service. The service can manage one instrument or several, with separate driver and experiment workers. Device operations pass through the service; fitting and analysis may run in a client or a worker. Programs submit derived results together with references to their input data.

Runtime 指实验运行系统。常驻服务由持续运行的守护进程承载，可管理一台仪器或整个平台。服务内部可分设驱动进程与实验工作进程。设备操作经服务安排，拟合和分析可以在客户端或工作进程中完成。程序将分析结果与输入数据引用一并提交保存。

A method identifier and version describe a reusable procedure. Each submission receives a run_id; each operation within that run receives its own operation_id. Observations and files retain links to the actual execution and the definitions it used.

方法标识与版本说明可复用的实验步骤。每次提交产生 run_id，其中每项实际操作产生 operation_id。观测与数据文件同时关联实际执行及使用的定义。

## Scheduling / 调度

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
| Run / 实验运行 | One experiment submission with fixed parameters, versions and devices. / 一次实验提交，包含参数、版本、设备与多项操作。 |
| Operation instance / 操作实例 | One execution of an operation within a run, with state, events and observations. / 一次实验运行中的具体操作，包含状态、事件与观测。 |
| Observation / 观测 | Physical readings with units, acquisition times, conditions and provenance. / 带单位、采集时间、条件与来源的物理读数。 |

Knowledge materials explain an operation's principles, applicability and practical use through explicit identity and version references. Human-readable instructions and machine-readable descriptions remain linked. A result connects to the execution and observations that support it.

原理、适用条件与使用经验通过身份和版本关联到操作定义；人工可读说明与机器可读描述保持对应。每个结果关联到产生它的执行与支持它的观测。

## Existing mechanisms / 已有机制

The comparative study follows one hierarchy: existing designs → shared mechanisms → IOP. Capability models contribute descriptions and driver mappings. Execution rules contribute task lifecycles and measurement records. Discovery and resource coordination contribute equipment identities, reservations and access paths.

研究采用一条固定关系：具体方案 → 共同机制 → IOP。能力模型提供描述与驱动映射；执行规则提供任务生命周期与测量记录；发现和资源协作提供设备身份、占用与访问路径。

Compatibility is defined per capability: inputs retain physical meaning, completion follows device readback, and results retain units and acquisition context. SiLA 2, OPC UA/LADS, W3C WoT and existing drivers provide mapping foundations. API, CLI, MCP and human interfaces can share the same operation model.

兼容性按能力建立：输入保留物理含义，完成条件依赖设备读回，结果保留单位与采集条件。SiLA 2、OPC UA/LADS、W3C WoT 及已有驱动提供映射基础；API、CLI、MCP 与人工界面共享操作模型。

## Development / 建设

[IOP Runtime 0.3.0](runtime/README.md) implements the platform service: device registration and discovery, persistent experiment packages, dependency/resource scheduling, HTTP and Python clients, and linked records. It includes SCPI TCP/serial/VISA, Modbus TCP/RTU and HTTP drivers, a custom-driver interface and simulated multi-instrument experiments. Previously started work becomes interrupted after a service restart; automatic recovery of physical actions is not implemented.

[IOP 常驻服务 0.3.0](runtime/README.zh-CN.md) 已实现设备登记与发现、持续运行的实验程序包、依赖与资源调度、HTTP 与 Python 客户端和关联记录。提供 SCPI TCP / 串口 / VISA、Modbus TCP / RTU 和 HTTP 驱动、自定义驱动接口及多仪器模拟实验。服务重启后，之前已经开始的实验标为中断，保留数据；物理动作的自动恢复尚未实现。

The architecture above describes the broader IOP design. The runtime guide specifies the implemented behavior of this release. / 上文说明 IOP 整体设计，本版实际行为以常驻服务文档为准。

[中文 IOP](agent-instruments/index.zh-CN.html#presentation/1) · [English IOP](agent-instruments/index.en.html#presentation/1) · [Content and mechanisms](agent-instruments/presentation.json)
