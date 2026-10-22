# 实验平台配置

[English](platforms.md) · [IOP](README.zh-CN.md) · [配置结构](schema/platform.schema.json)

一个服务管理所在计算机的设备；平台描述这些设备如何组成实验系统。设备可属于多个平台，同一设备与共享资源仍由同一个调度器管理。

## 三种关系

| 关系 | 写在哪里 | 对执行的影响 |
| --- | --- | --- |
| 物理连接：光路、管路、电信号、触发、样品关系 | 平台 `connections` | 提供端口与连接信息；不会仅凭连接名称发送命令或自动推断同步。 |
| 共享设备、样品、总线、容器、空间 | 平台 `resources` | 使用同一资源的冲突操作排队。资源 ID 在同一服务中全局一致。 |
| 本次实验的先后步骤 | 实验或初始化过程 `steps[].after` | 前置步骤完成后执行；互不冲突的分支并行。 |

`resources[].devices` 声明哪些设备涉及同一资源。可用 `operations` 限定涉及它的操作，例如 `{"stage":["move_to"],"meter":["measure"]}`，让探测器配置与转台运动仍可并行。不填写时，该设备的所有操作都使用该资源。

实验的顶层 `resources` 保留跨步骤需要的设备和共同对象，直到该实验结束。仅有操作级排队不足以保护“改变条件—等待稳定—测量”这一完整过程。

## 运行两个平台

以下步骤使用 `iop init --demo` 提供的模拟设备。已有真实设备配置时，请另选 `--home` 目录。

```sh
iop init --demo
iop start
iop platform apply iop/examples/platform.json
iop platform apply iop/examples/independent-platform.json
iop platform initialize materials-bench --wait
iop run iop/examples/experiment.json --wait
iop open
```

第二个平台使用 `aux`，可与第一个平台并行。其他实验室的配置从实际已登记设备开始：

```sh
iop discover
iop register devices.json
iop platform draft my-bench --devices camera stage meter --output my-bench.json
```

人或 Agent 在生成的 JSON 中填写连接、共享资源和初始化步骤，再执行：

```sh
iop platform preview my-bench.json
iop platform apply my-bench.json
iop platform initialize my-bench --wait
```

`preview` 返回解析后的配置，不保存、不操作设备。`apply` 保存配置；`initialize` 才提交初始化实验。初始化使用相同的依赖调度、停止方式与实验记录。

多仪器程序也可使用平台配置：

```sh
iop register examples/iop/multi-instrument/devices.json
iop platform apply iop/examples/liquid-platform.json
iop platform initialize liquid-bench --wait
iop package examples/iop/multi-instrument --platform liquid-bench --resources bath balance pump daq --wait
```

这个例子包含温控、天平、泵与数据采集，使用测量反馈决定后续加液量。

## 版本与持续使用

`iop platform show my-bench` 返回当前配置版本。修改已有平台时传入该版本，例如 `iop platform apply my-bench.json --revision 1`；保存后生成版本 2。`iop platform history my-bench` 返回历史版本。

影响相关设备的实验结束后再修改配置。每次实验保存提交时的平台说明与版本，后来的修改不会改变旧记录。共享资源即使由不同平台引用，或由未指定平台的直接调用使用，也进入同一个资源调度。

Python 示例：

```python
from ai4instruments.iop import Client
lab = Client()
run = lab.submit([
    {"id": "move", "device": "stage", "operation": "move_to", "arguments": {"angle_deg": 20}},
    {"id": "read", "device": "meter", "operation": "measure", "after": ["move"]},
], platform="materials-bench", resources=["stage", "meter"])
print(run.id)
# 可退出当前程序；之后用 lab.run(run_id) 查询。
```

远端 Agent 使用可达的服务地址及连接令牌。实验包由服务在仪器计算机上运行，长实验无需维持云端请求连接。数据处理可在本地或远端完成，设备操作始终经常驻服务安排。
