# Independent instrument drivers / 独立仪器驱动

[IOP](README.md) · [中文](README.zh-CN.md) · [Existing adapters](../docs/runtime/drivers.md)

The `process` adapter connects an executable to IOP through UTF-8 JSON lines. Rust `iop-execd` owns that process, forwards requests and cancellation, and ends the process when its response deadline expires or the service disconnects. Python supplies a worker for existing adapters. C, C++, C#, Java and other SDKs can implement the same messages in their own executable.

`process` 驱动通过 UTF-8 JSON 行连接独立程序。Rust `iop-execd` 管理进程、请求、取消通知、响应时限和退出。Python 工作进程可加载已有驱动；其他语言的厂商 SDK 使用相同消息接口。

## Use / 使用

Release archives include the matching executor. A source checkout builds it with:

```sh
cargo build --release --manifest-path iop/daemon/Cargo.toml
```

Copy `iop-execd` (`iop-execd.exe` on Windows) to `src/ai4instruments/iop/bin/` before building the Python wheel, put it on the executable path, or set `IOP_EXECD` to its full path.

```sh
iop register iop/examples/process-device.json
iop call external-stage position
```

That example is simulated. To load an existing real driver, replace the entry in `config.configuration.devices` with the model's SCPI, Modbus, HTTP or installed Python driver record. `config.command` defaults to the included Python worker and may instead name any compatible executable. `config.timeout` is the maximum time in seconds for one response; set it to accommodate the instrument's operation duration.

示例使用模拟设备。真实仪器在 `config.configuration.devices` 中填写实际驱动与连接配置。`config.command` 可指定任意兼容的可执行程序；`config.timeout` 表示单次响应允许的最长秒数，应覆盖实际仪器操作时间。

Devices sharing a serial bus or SDK can use the same `config.worker` ID and identical configuration containing all of their device records. They share one process and an automatically registered scheduling resource. Unrelated SDKs use different worker IDs and can operate concurrently.

共享总线或 SDK 的设备使用相同的 `config.worker` 与同一份完整配置，共用一个进程并自动共用调度资源；独立 SDK 使用不同进程，可以并行。不要把同一物理连接同时登记成直接驱动与独立进程驱动。

## Messages / 消息

Every request except `cancel` has an `id`. Each response returns that ID and either `result`, `error`, or `cancelled: true`. Write SDK logs to stderr. Stdout is reserved for JSON replies.

| Method | `params` | Result |
| --- | --- | --- |
| `configure` | Worker-specific configuration; the Python worker accepts `devices` | Loaded device IDs or equivalent metadata. |
| `describe` | `{"device":"meter"}` | Instrument description including `operations` and their parameters. |
| `invoke` | `{"device":"meter","operation":"measure","arguments":{}}` | Actual operation result, with units and time where applicable. |
| `cancel` | `{"id":"active-request-id"}` | Notification: no separate reply. The original invocation later reports its outcome. |

```json
{"id":"request-1","method":"invoke","params":{"device":"meter","operation":"measure","arguments":{}}}
```

```json
{"id":"request-1","result":{"value":0.125,"unit":"W","source":"device"}}
```

A worker serves one operation at a time. Its input loop must continue accepting cancellation while an SDK call runs; the included Python worker demonstrates this separation. Cancellation requests do not imply the physical action has stopped.

If a driver exits or times out without a result, IOP records an unresolved outcome and keeps affected resources unavailable. Independent devices continue. After inspecting the actual equipment state and reconnecting the worker (currently by restarting the service), the operator or agent can return the named resources to use:

```python
from ai4instruments.iop import Client
lab = Client()
print(lab.request('/v1/status')['resource_holds'])
# Supply the exact resources and the observed state for this instrument.
lab.request('/v1/resources/resolve', {
    'resources': ['device:meter', 'shared:worker:meter-sdk'],
    'observation': 'Acquisition is stopped; the device reports idle.'
})
```

The observation is recorded with the release. Old physical actions are not automatically resubmitted. This applies specifically to interrupted driver processes; normal completion and cooperative cancellation retain the usual operation records.
