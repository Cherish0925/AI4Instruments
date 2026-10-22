# Instrument descriptions and drivers · 仪器说明与驱动

[中文安装](README.zh-CN.md) · [Installation](README.md)

A description names an instrument's operations and their inputs. A driver performs those operations and reports when they have finished. The runtime keeps connections and schedules calls. / 仪器说明列出操作与输入，驱动执行并报告完成，常驻服务保持连接并安排调用。

## SCPI

Copy [scpi-meter.json](../../examples/iop/scpi-meter.json), replace the address and model-specific commands, then register it with `iop register device.json`. / 复制示例，按型号手册修改地址与命令后登记。

```json
{
  "id": "power-meter",
  "driver": "scpi",
  "resources": ["measurement-channel"],
  "config": {
    "name": "Optical power meter",
    "transport": "tcp",
    "host": "192.168.1.50",
    "port": 5025,
    "timeout": 5,
    "termination": "\n",
    "operations": {
      "read_power": {
        "description": "Read optical power",
        "parameters": {},
        "query": "MEAS:POW?",
        "result": {"type": "number", "unit": "W"}
      },
      "set_wavelength": {
        "parameters": {"nm": {"type":"number","minimum":400,"maximum":1100,"unit":"nm"}},
        "write": "SENS:CORR:WAV {nm}",
        "completion": {"query":"*OPC?","equals":"1","timeout":30}
      }
    }
  }
}
```

These commands and ranges illustrate the format; use those specified for the actual model. The driver formats named parameters into a command, reads query responses and optionally polls completion. Numeric results include their configured unit and acquisition timestamp. / 示例中的命令和范围需要替换为实际型号的定义。

| Transport / 连接 | `config` fields / 字段 |
| --- | --- |
| TCP | `transport: "tcp"`, `host`, `port` (default 5025) |
| Serial / 串口 | `transport: "serial"`, `port: "COM4"` or `/dev/ttyUSB0`, `baudrate` (default 9600) |
| VISA | `transport: "visa"`, `resource: "USB0::...::INSTR"`; optional `backend: "@py"` |

All support `timeout` in seconds and `termination`. Text encoding defaults to ASCII. VISA support depends on the installed vendor library or pyvisa-py backend and its transport dependencies.

Built-in `identify`, `query` and `write` operations provide `*IDN?`, a raw text query and a raw text write. A write result with `sent: true` means the command was sent. A named operation with `completion` also waits for its specified device response. Motion or acquisition completion must follow the actual device's documented status mechanism. This SCPI driver handles text; binary image and waveform transfers belong in model-specific drivers.

内置 `identify`、`query`、`write` 分别读取身份、查询文本和写入文本。`sent: true` 表示命令已发送；定义 `completion` 的操作还会等待相应设备回复。运动、稳定和采集完成的含义按仪器手册定义。二进制图像与波形传输使用对应型号驱动。

## Modbus TCP and RTU

Use `driver: "modbus"`. TCP configuration specifies `host`, `port` (default 502) and `device_id` (default 1). RTU specifies `transport: "serial"`, `port`, `baudrate`, `parity` and `stopbits`. Logical devices on the same bus share a connection and an automatically named scheduling resource. Install the `devices` extra for PyModbus.

使用 `modbus` 驱动，可接入寄存器与线圈接口的温控器、PLC、电源、传感器和执行器。同一总线上的逻辑设备共用连接，并自动按总线顺序通信。地址使用协议中的零起始地址；寄存器表中的编号需要按型号手册转换。

Built-ins: `read_holding_registers`, `read_input_registers`, `read_coils`, `read_discrete_inputs`, `write_register`, `write_registers`, `write_coil`. Named operations select a `function`, fixed `arguments`, a `scale`, `offset` and optional `unit`. Scalar reads can use signed 16-bit interpretation. Named writes can map a physical `value_parameter` back to a register value. Multi-register floating-point formats require a model-specific driver.

See [modbus-temperature.json](../../examples/iop/modbus-temperature.json). A write acknowledgement reports receipt by the device; reaching a temperature, position or flow target requires subsequent measurements in the experiment program or a device-specific operation. The adapter sets communication retries to zero so an unanswered write is not automatically repeated.

写入应答表示设备已收到请求。达到温度、位置或流量目标，需要实验程序继续读取或由专用操作等待完成。说明文件中的地址、比例和单位均需与真实型号对应。

## HTTP JSON

Use `driver: "http"` with `config.base_url`, optional `headers` and `timeout`. Each operation specifies `method`, `path`, optional `query` and `body`, and optional `result_path` as a list of JSON keys or indices.

`${parameter}` in JSON bodies preserves the input's JSON type. `{parameter}` in a URL path is URL-encoded. An operation returns the response together with the selected value, time and optional unit. See [http-sensor.json](../../examples/iop/http-sensor.json). Asynchronous HTTP jobs require an experiment to poll the device's status operation; a successful request alone does not imply physical completion.

HTTP 驱动适用于已有 JSON 接口的仪器和设备服务器。参数、路径和返回字段写在仪器说明中。设备返回异步任务时，由实验程序继续查询其状态。

## Automatic registration / 自动登记

`config.json` can contain discovery `profiles`. Each profile requires a transport and exact metadata matches. Placeholders in its device record are filled from the discovered connection. / 发现规则按连接类型及字段精确匹配，用发现的地址与序列号生成设备记录。

```json
{
  "match": {"transport":"serial","vid":1234,"pid":5678},
  "device": {
    "id":"meter-{serial_number}",
    "driver":"scpi",
    "config":{"transport":"serial","port":"{address}","baudrate":9600}
  }
}
```

Use values actually returned by `iop discover`; the numbers above are placeholders. A scan runs every `discovery_interval` seconds (default 30), and `iop discover` requests a scan immediately. A matching installed profile registers a new device once and retains it in the configuration. A discovery entry describes a connection, not necessarily an instrument. Existing device IDs are not automatically rebound to a changed address; update their configuration and restart.

使用 `iop discover` 返回的真实字段值。服务默认每 30 秒发现一次，已登记的设备不重复添加。设备地址发生变化时，修改配置并重启。

## Python driver / Python 驱动

Implement these methods in an installed Python module:

```python
from ai4instruments.iop.drivers import Driver

class TemperatureProbe(Driver):
    def describe(self):
        return {
            "name": "Temperature probe",
            "mode": "hardware",
            "driver_version": "1.0",
            "operations": {
                "read_temperature": {
                    "description": "Read the probe temperature in kelvin",
                    "parameters": {}
                }
            }
        }

    def invoke(self, operation, arguments, cancelled):
        # Call your SDK here and return a JSON-compatible result.
        # Return only when this operation's documented completion occurs.
        raise NotImplementedError("Connect the probe SDK")

    def close(self):
        # Release the connection held by this driver.
        pass
```

Register with `{"id":"probe","driver":"my_instruments:TemperatureProbe","config":{}}`. The example intentionally leaves the SDK call to the device implementation. A complete runnable simulated driver is provided in [custom_driver.py](../../examples/iop/custom_driver.py). Install or place that module on the service's Python import path before registering it.

`self.id` identifies the instrument, `self.config` contains driver settings, and `self.registry` provides registered driver objects. Calls to the same device are serialized; different devices may execute on different threads. Driver methods must return JSON-compatible values with units and acquisition context where appropriate. Use bounded communication timeouts and implement the `cancelled` event according to the device. `close()` releases persistent connections.

将驱动安装在服务使用的 Python 环境中，再以 `module:Class` 登记。同一设备不会同时执行两次调用，不同设备可以在不同线程中执行。返回值使用可序列化为 JSON 的内容，并保留单位与采集信息。通信设置明确的超时时间，按设备行为响应取消请求，`close()` 关闭连接。

The parameter model supports `number`, `integer`, `string`, `boolean`, `array`, `object`, `minimum`, `maximum`, `enum`, `default`, `required` and descriptive `unit`. Required defaults to true; fields with a default may be omitted. Undeclared arguments are rejected. This is the runtime's current parameter format, not a complete JSON Schema implementation.

参数格式支持以上字段；有默认值的参数可以省略，未声明的参数不传入设备。数组可定义 `items`、`minItems` 和 `maxItems`；复杂数据的含义由驱动说明。

## Sources / 依赖文档

- [pySerial port discovery](https://pyserial.readthedocs.io/en/latest/tools.html)
- [PyVISA resource discovery and communication](https://pyvisa.readthedocs.io/en/latest/introduction/communication.html)
- [PyModbus client](https://pymodbus.readthedocs.io/en/v3.11.1/source/client.html)
- [Python SQLite](https://docs.python.org/3/library/sqlite3.html)
