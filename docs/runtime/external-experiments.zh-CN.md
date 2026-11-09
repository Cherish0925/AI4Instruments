# 连续实验程序 · 0.8.5

[English](external-experiments.md) · [HTTP API](http-api.md) · [可运行示例](../../examples/iop/external-experiment/experiment.py)

实验程序保留自己的科学计算环境，实验室服务负责仪器连接、操作过程和实验数据。开始一个实验，连续提交操作或批次，分析返回结果，最后结束。Python、TypeScript、MCP 和命令行共用同一个实验编号和调度器。

```python
from ai4instruments.iop import Client

with Client() as lab:
    with lab.start_experiment(name='样品扫描', resources=['stage', 'meter'],
                              request_id='sample-42-scan-1') as run:
        print(run.id)  # 保存此编号，断开后可接回本实验。
        records = run.batch([
            {'id':'set', 'device':'stage', 'operation':'move_to',
             'arguments':{'angle_deg':15}},
            {'id':'read', 'device':'meter', 'operation':'measure'}
        ], request_id='sample-42-point-1')
        measurement = records[-1]['result']
        run.save_acquisition('point-1.json', [op['id'] for op in records],
                             conditions={'sample':'42'},
                             analysis={'accepted':measurement['power'] > 0})
        run.checkpoint({'next_point':2})
        run.save_result({'points':1})
```

内层 `with` 正常退出时结束实验，异常退出时请求取消。单独关闭客户端不结束实验。新工作使用新 request ID，相同提交重试时保留原编号。示例使用演示设备；真实操作名称、参数和单位从已登记的仪器说明读取。

## 串行、并行和共享仪器

批次内省略 `after` 表示接着上一步执行；`after=[]` 开始独立分支；`after=['a','b']` 等待两个分支。结果到参数的绑定也形成依赖。全部步骤通过检查并写入记录后才开始执行，提交要么整体接收，要么整体拒绝。执行中失败不会撤销已经发生的物理动作；已完成结果保留，未开始的步骤取消。

**相互影响的仪器和共享物理对象，应在 `start_experiment(resources=[...])` 中完整预留。** 预留贯穿调用和批次之间的间隙，直到实验结束或取消完成。未预留时，其他实验可以在两次调用或批次步骤之间使用仪器。互不影响的平台仍可并行。软件依赖表达完成顺序，精确同步由设备时钟和硬件触发实现。

`batch()` 等待完成并返回操作记录。需要立即返回时，直接使用 `POST /v1/runs/{id}/batches`，再用相同路径的 GET、`request_id` 和可选 `wait=0..25` 读取结果。每批最多 10,000 步，并受服务配置的活动操作容量约束。长实验可连续提交批次，调度器只保留尚未结束的操作。原有 `submit()` 工作流保持原语义：省略依赖表示独立步骤。

## 采集一次，判断和保存引用同一份数据

`invoke()` 返回驱动结果；`invoke_record()` 同时返回操作编号、时间和仪器配置版本。`save_acquisition()` 从服务中读取指定的已完成操作及其配置版本，保存为 JSON，**不会再次向仪器发送采集命令**。相同文件名、相同内容重试时返回原文件；不同内容使用新名称。

将真实仪器设置的读回操作一并纳入操作编号。`conditions` 保存调用方提供的样品和接线信息，不将这些文字当作实际测量。`analysis` 保存对本次采集的判断与计算结果。大型图像、数组和连续数据保留原二进制格式，通过 `upload(..., operation_ids=[...])` 或数据流接口保存，再在采集记录中引用其文件编号。实验结束后这些关联继续保留。

## 断开后继续

客户端断开后，用 `Client().run(saved_run_id)` 接回实验，通过 `info(details=False)`、`operations()` 和 `checkpoints()` 读取状态。相同操作或批次 request ID 返回之前已接收的记录，实验结束后仍可查询；相同编号配不同输入会被拒绝。客户端不会在连接失败后自动重发 POST。

服务重启会中断已经开始的实验。读取操作与进度后，显式调用 `run.resume(request_id='continuation-1')`；原实验编号和历史操作保留。外部程序决定从哪里继续，Runtime 不会重启该外部进程，也不会重复执行结果未明的物理动作。驱动配置变化需要先处理再继续。

文件传输和已接收操作结束后调用 `finish()`；放弃实验时调用 `cancel()`。停止客户端等待不意味着实验停止。

## 各入口共用同一流程

| 入口 | 连续实验 | 批量操作 | 保存采集 |
| --- | --- | --- | --- |
| Python | `start_experiment` → `finish` | `run.batch` | `run.save_acquisition` |
| TypeScript | `startExperiment` → `finish` | `run.batch` | `run.saveAcquisition` |
| MCP | `start_experiment` → `finish_experiment` | `submit_operations` | `save_acquisition` |
| 命令行 | `iop begin` → `iop finish` | `iop batch RUN steps.json --request-id ID --wait` | `iop acquisition RUN point.json OP_ID...` |

MCP 提交后立即返回，使用 `experiment` 读取完成状态和结果。Agent 可以在批次之间做研究决策，密集的数值计算由程序完成。原有 `Client.invoke()` 和不带 run ID 的 `iop call` 仍是独立单步工作流，连续实验应使用实验句柄。

## 与其他软件交接仪器

操作和预留结束后，调用 `lab.release(device)` 或 `iop release DEVICE`。服务关闭连接，保留仪器说明；后台发现和服务重启都不会重新占用它。同一 SDK 进程管理的设备一起释放和接回。`reconnect(device)` 恢复访问；为单台已释放仪器应用新配置时，也会重新接入。桌面和网页仪器面板提供相同操作。

`lab.adapters()` 和 MCP 的 `available_adapters` 返回连接参数说明。SCPI TCP 的 `config.source_address` 指定本机面向仪器的网卡 IP；串口支持波特率、数据位、校验方式、停止位和软硬件流控。无法解析的身份回复保留原文，状态为 `identity_unparsed`、通信为 `responded`；了解格式或修正配置后，可主动重新识别。
