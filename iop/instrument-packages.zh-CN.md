# 仪器支持包

[English](instrument-packages.md) · [型号说明](instruments/README.md) · [驱动接口](drivers.md) · [实验平台](platforms.zh-CN.md)

IOP 0.8.3 可从已安装的 Python 包读取型号说明。包可以同时提供设备枚举、仪器驱动和型号说明；核心服务继续负责调度、配置与实验记录。

| 内容 | 包的入口 | 读取方式 |
| --- | --- | --- |
| 仪器驱动 | `ai4instruments.drivers` | 按名称加载驱动类 |
| SDK 设备枚举 | `ai4instruments.discovery` | 在独立进程中调用枚举函数 |
| 型号说明 | `ai4instruments.instrument_profiles` | 直接读取包内 JSON，不导入包或启动 SDK |

## 查找与采用

```sh
iop instrument-catalog --manufacturer Stanford_Research_Systems --model SR830
iop instrument-catalog --id srs-sr830 --details
```

结果给出操作名称、原始资料、说明来源和包版本。默认每页 50 项，用返回的 `next_offset` 继续读取。Python、TypeScript 和 HTTP 提供相同查询；MCP 的 `instrument_profiles` 默认返回摘要，设置 `details=true` 才读取操作定义。

在仪器详情点击“补充型号操作”，选择已安装的说明，再点击“用于这台仪器”。此操作保留已有操作、补充缺少的操作并保存配置版本。有已受理实验的仪器完成工作后再修改；其他仪器的实验继续。

自动匹配优先使用实验室保存的说明，其次是安装包，再次是内置说明。同一来源层级中，更具体的型号、序列号或固件条件优先。两个说明同样匹配时，保留候选供选择，通用 SCPI 操作仍可使用。读取目录不会向仪器发送命令。

## 制作一个包

包内包含以下文件：

| 文件 | 内容 |
| --- | --- |
| `pyproject.toml` | 安装信息与入口 |
| `my_lab_instruments/__init__.py` | 可以为空 |
| `my_lab_instruments/instruments/*.json` | 符合型号说明格式的 JSON 文件 |

```toml
[build-system]
requires = ["setuptools>=70.1"]
build-backend = "setuptools.build_meta"

[project]
name = "my-lab-instruments"
version = "0.1.0"
requires-python = ">=3.10"

[project.entry-points."ai4instruments.instrument_profiles"]
models = "my_lab_instruments:instruments"

[tool.setuptools.package-data]
my_lab_instruments = ["instruments/*.json"]
```

入口值的冒号左侧是 Python 包，右侧是资源目录；点号表示目录层级。它不是需要执行的函数。JSON 使用[型号说明格式](schema/instrument-profile.schema.json)，可参考仓库已有的 [SR830 说明](instruments/srs-sr830.json)。命令、单位和完成条件来自对应型号的编程手册。

使用 IOP 安装环境中的 Python 执行 `python -m pip install .`，完成当前实验后重启服务。安装环境的 Python 路径可从 `iop mcp-config` 的 `command` 读取。发行包中的内置说明不受第三方文件解析错误影响；出错的包和文件会显示在目录查询的 `errors` 中。

## 共用 Modbus 总线

一条 RS-485 总线或一个 TCP 网关可以登记多台仪器，每台说明使用各自的 `config.device_id`。相同总线地址与站号只登记一次；操作使用该仪器的站号。

TCP 支持完整的 0–255 标识字段，包括直连 TCP 设备使用的 0 和 255；串口仪器使用 1–247 的独立地址。具体值遵循仪器或网关手册，参见 [Modbus TCP 实现指南](https://www.modbus.org/file/secure/messagingimplementationguide.pdf)。

同一进程内的 Modbus 设备共用连接，按总线安排请求。修改空闲仪器的名称或操作说明，不关闭其他仪器正在使用的连接。不同总线可并行。串口的波特率、数据位、停止位和校验方式保持一致；每台设备可使用自己的响应超时。读写失败不会自动重发原请求。

需要独立进程时，将同一总线的仪器放在同一个 `process` worker 中；多个进程无法共同持有一个独占串口。仪器列表按设备显示，连接详情列出该总线上的全部已登记仪器。
