# IOP examples · 仪器与实验实例

[中文使用说明](../../docs/runtime/README.zh-CN.md) · [User guide](../../docs/runtime/README.md)

| Example | Purpose / 用途 | Runs without hardware / 无仪器运行 |
| --- | --- | --- |
| `multi-instrument/` | Temperature, measured dosing, weighing and acquisition / 温控、反馈加液、称量与信号采集 | Yes, explicitly simulated / 是，标明模拟 |
| `parallel.json` | Parallel preparation and dependent acquisition / 并行准备与顺序采集 | `iop init --demo` |
| `polarization/` | Repeated scan, retained device setup and CSV / 扫描、持续设备占用与 CSV | `iop init --demo` |
| `scpi-meter.json` | SCPI instrument description / SCPI 仪器说明 | Replace address and model commands / 需真实地址与型号命令 |
| `modbus-temperature.json` | Modbus named operations and units / Modbus 具名操作与单位 | Replace device register map / 需真实寄存器定义 |
| `http-sensor.json` | HTTP device operations / HTTP 仪器操作 | Replace device endpoints / 需真实接口地址 |
| `custom_driver.py` | Installed-driver extension / 自定义驱动扩展 | Simulated probe / 模拟探头 |

Start the service, register the general laboratory example, and submit its program:

```sh
iop init
iop start
iop register examples/iop/multi-instrument/devices.json
iop package examples/iop/multi-instrument --resources bath balance pump daq sample --wait
```

The scheduler and client are unchanged across these examples. A physical instrument uses the same operation calls once its driver implements the corresponding units, behavior and completion. / 这些实例共用同一调度器和客户端。真实仪器由驱动提供相应操作、单位、行为与完成条件。
