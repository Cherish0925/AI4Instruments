# 实验执行

[IOP Runtime](README.zh-CN.md) · [English](execution.md) · [接口](../docs/runtime/http-api.md)

一个实验可以同时使用实体仪器、计算程序和远端服务。IOP 按步骤依赖、设备能力与可用资源安排执行；程序包表达循环、条件、反馈与研究方法。

## 顺序、并行和数据

没有依赖的步骤可以并行。`after` 指定顺序，`bindings` 把已经完成的步骤结果传入下一步，并自动建立相应依赖。

```json
{
  "name": "计算并处理结果",
  "steps": [
    {"id":"first","device":"processor","operation":"calculate","arguments":{"x":3}},
    {"id":"second","device":"processor","operation":"calculate",
     "bindings":{"x":{"step":"first","path":["value"]}}}
  ]
}
```

这里的 `processor` 是已登记、提供 `calculate(x)` 的对象。`path` 按对象字段或数组下标提取结果；省略 `path` 表示整个结果。传入下一步前，服务按该操作的参数说明检查类型与范围。需要自适应循环、模型拟合或更复杂的程序逻辑时，提交实验程序包。

每台设备默认同时执行一个操作。独立软件任务或确实支持并发的驱动可以在说明中声明 `concurrency`。共享总线、样品、控制器等仍使用共同的 `resources` 名称。

## 可计数资源

使用 Python 或浏览器“运行资源”配置容量：

```python
from ai4instruments.iop import Client
lab = Client()
lab.configure_resources({"cpu": 16, "gpu": 2, "solver": 3})
```

操作用 `requirements` 声明需要的数量，例如 `{"cpu":4,"solver":1}`。服务一次取得全部所需资源；等待中的操作不占用部分资源。上面的配置允许最多三项这样的求解任务共同运行。名称由实验室定义，也可以用 `gpu-0`、`gpu-1` 表示独立设备。

资源需求可以写在驱动说明、具体操作或实验步骤中。同一资源取其中最大的数量。资源数量用于任务安排；计算程序内部的线程数、显存与 GPU 选择由该程序配置。

`resources` 与 `requirements` 写在整个实验上时，表示跨步骤保留。工作流会同时纳入它使用的设备；程序包须在提交时列全设备与数量。实验内部的操作使用已经保留的份额，不重复占用。需要共同执行的两个步骤各用两个计算份额，整次实验应保留四份。

## 持续运行

服务受理后返回 `run_id`。提交者断开连接后，工作流与已上传程序包继续运行。运行中的程序包可以不断提交新操作，完成的操作转入 SQLite；内存只保留其尚未结束的操作。历史按页读取：

```python
run = lab.run(run_id)
page = run.operations(after=0, limit=200)
next_page = run.operations(after=page["cursor"], limit=200)
for event in run.watch():
    print(event["kind"])
```

事件接口支持等待新事件返回，客户端无需不断请求完整实验记录。服务重新启动后，尚未开始的实验继续排队；中断的实验保存已经完成的记录。设备动作不会因重启而自动重放。

`workers` 控制同时执行的操作数，`package_workers` 控制实验程序数。`config.json` 中的 `max_active_runs` 和 `max_active_operations` 默认分别为 10000 与 100000；达到容量时，新请求返回 HTTP 503，已受理的工作继续执行。驱动的 `concurrency` 和资源数量仍分别生效。

## 数据文件

小型结构化结果随操作返回。图像、波形、数组与其他大文件保存在实验输出目录，数据库记录名称、大小和所属实验。文件上传、下载按块传输：

```python
record = run.upload("measurement.h5", "raw/measurement.h5")
run.download(record["id"], "downloaded.h5")
```

直接驱动收到的第三个参数兼容 `threading.Event`，同时提供 `run_id`、`operation_id`、`output_dir`、`file(name)` 与 `progress(fraction, message)`。驱动可以写入操作自己的目录并报告进度。

## 计算程序与远端任务

`command` 适配器运行普通可执行程序，`process` 适配器保持厂商 SDK 会话，`http` 适配器连接同步接口或异步任务服务。接入细节见[软件与驱动扩展](software.zh-CN.md)。

Rust 组件管理实验程序、命令程序及独立 SDK 进程。普通程序的输出直接写入文件；取消、超时或上层连接关闭时结束其进程树。仪器动作的完成状态由相应驱动报告。

一个运行服务负责本机登记的资源。远端 IOP 也可通过 HTTP 任务适配器接入；每个服务分别安排自己的设备，跨服务的实验顺序由上层程序表达。跨主机的同时采样仍需设备时钟与触发机制。
