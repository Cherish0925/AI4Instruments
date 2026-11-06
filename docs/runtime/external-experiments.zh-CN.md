# 外部实验程序

[English](external-experiments.md) · [HTTP API](http-api.md) · [可运行示例](../../examples/iop/external-experiment/experiment.py)

外部 Python、TypeScript 程序可以保留原来的科学计算环境，在同一个 run ID 下连续操作仪器、保存数据并结束实验。它与 Runtime 托管程序共用调度器、资源预留和实验记录。以下接口属于 0.8.4 之后的源码改动，已发布的 0.8.4 安装包尚不包含。

```python
import json
from ai4instruments.iop import Client

client = Client()
# 新实验使用新编号；提交重试时保留原编号。
run = client.start_experiment(name='扫描', request_id='sample-42-scan-1',
                              resources=['stage', 'meter'])
print(run.id)
run.invoke('stage', 'move_to', {'angle_deg':15}, request_id=run.id + '-move-1')
measurement = run.invoke_record('meter', 'measure', request_id=run.id + '-read-1')
run.save_file('point.json', json.dumps(measurement['result']),
              operation_ids=[measurement['id']])
run.checkpoint({'next_point':2})
run.save_result({'points':1})
run.finish()
```

`invoke()` 返回仪器结果。`invoke_record()` 返回同一份结果及其 operation ID、run ID、时间和仪器配置版本。后续判断与保存引用这份数据；再次调用仪器会产生新的测量。`save_file(..., operation_ids=[...])` 和 `upload(..., operation_ids=[...])` 可将文件关联到本实验已完成的操作，关联在实验结束及服务重启后保留。

相互影响的仪器与共享资源应在开始时完整预留。预留贯穿调用间隙，到 `finish()` 或取消完成后释放；独立仪器仍可并行。未预留时，每次操作仍经过调度，但两次调用之间可能插入其他实验。等待资源的实验可以接收操作，操作随实验一起等待。

先完成文件传输并等待已接受的操作结束，再调用 `finish()`。仍有待执行或执行中操作时，返回 `operations_pending`。重复结束已完成的实验只返回原记录。客户端断开不会自动结束实验或释放预留；放弃实验时调用 `cancel()`。仪器操作失败按现有失败流程结束实验。

## 换连接后继续

```python
run = Client().run(saved_run_id)
print(run.info(details=False))
print(run.operations())
print(run.checkpoints())
```

只有客户端断开时，直接接回仍在进行的实验。丢失操作响应时，用相同的 `request_id` 和输入重试，返回原操作，不重复执行物理动作；实验已结束也可以这样查询。相同编号配不同输入会被拒绝。

服务重启会将已开始的实验标记为中断。读取操作与进度后，显式调用 `run.resume(request_id='continuation-1')`；原 run ID 和历史操作保留，外部程序自行决定从哪里继续。Runtime 不会重启外部 Python 进程，也不会重放原来的调用。仪器结果未明或配置已改变时，需要先处理再继续。用原编号查询中断操作，仍返回中断状态。

## 其他入口

TypeScript 提供 `client.startExperiment(options)`、`run.invokeRecord(...)`、`run.finish()` 及原有进度与继续方法。二进制上传通过 `run.upload(name, blob, undefined, [operation.id])` 关联操作。

MCP 提供 `start_experiment`、`invoke_operation`、`save_experiment_file` 和 `finish_experiment`。提交操作立即返回；依赖其结果的后续操作，应先通过 `experiment` 读取完成状态。原有工作流和程序包入口继续可用。

```sh
iop begin --name Scan --request-id sample-42-scan-1 --resources stage
iop call stage position --run-id RUN_ID --request-id RUN_ID-read-1
iop finish RUN_ID
```

原来的 `Client.invoke()` 和不带 run ID 的 `iop call` 仍执行独立单步工作流。连续实验应使用实验句柄调用。
