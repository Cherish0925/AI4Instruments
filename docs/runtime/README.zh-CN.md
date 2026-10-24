# IOP 常驻服务

[English](README.md) · [服务架构](architecture.zh-CN.md) · [HTTP 接口](http-api.md) · [仪器驱动](drivers.md) · [源码](../../src/ai4instruments/iop)

0.8.0 新增 [MCP 与 Agent 接入](../../iop/agent-setup.zh-CN.md)、统一实验室说明和仪器配置恢复。[软件形态与系统支持](../../iop/product.zh-CN.md)。

IOP Runtime 是安装在仪器所在计算机上的常驻软件。它保持设备连接，接收实验程序，安排串行与并行操作，保存参数、读数、结果和文件。人和 Agent 使用同一套 HTTP 接口、Python 客户端和命令行；浏览器可以查看设备、提交实验和读取结果。

**0.8.0 已实现：** 后台服务、设备登记与发现、依赖调度、跨步骤设备占用、实验程序包执行、实验记录、Python 客户端、网页界面和各系统的登录自启动入口。

Rust 管理 SDK、计算程序和实验程序的进程执行，Python 处理 HTTP 与工作流调度，TypeScript 提供完整客户端。见[当前架构](architecture.zh-CN.md)。

**0.5.0 新增：** 依赖就绪调度、跨步骤结果传递、可计数资源、通用命令程序、异步 HTTP 任务、驱动包入口、进度事件和文件流式上传。[实验执行](../../iop/execution.zh-CN.md) · [软件与驱动扩展](../../iop/software.zh-CN.md)。进入 [IOP 工程](../../iop/README.zh-CN.md)或[配置实验平台](../../iop/platforms.zh-CN.md)。

**0.6.0 新增：** 独立桌面窗口、桌面与浏览器切换、系统应用菜单入口，以及重新设计的设备、平台、实验与资源界面。[桌面与网页使用说明](../../iop/interface.zh-CN.md)。

## 安装与启动

需要 Python 3.10 或更新版本。下载本仓库 ZIP 并解压，在解压目录运行：

```sh
python -m pip install ".[devices]"
iop init
iop start
iop open
```

如果系统使用 `python3`，将上述 `python` 换成 `python3`。如果 `iop` 未加入命令路径，使用 `python -m ai4instruments.iop` 代替它。

独立安装到用户目录：Linux、macOS、WSL 执行 `sh install.sh`；Windows 执行 `powershell -NoProfile -ExecutionPolicy Bypass -File .\install.ps1`。脚本创建独立 Python 环境，安装后打印该环境的启动命令。服务器无需图形桌面，可以只使用命令行和 HTTP。

下载的 IOP 软件包也可以直接安装其中的 wheel：

安装脚本自动选择 `dist/` 中适合当前系统的 wheel。

`[devices]` 安装串口、VISA、USB 发现和 Modbus 相关依赖。仅使用 TCP 仪器、模拟设备或已有驱动时，可以省略它。Python 服务使用标准库；原生执行组件包含在发行包中。

| 系统 | 后台运行 | `iop service install` |
| --- | --- | --- |
| Linux | 独立后台进程 | systemd 用户服务 |
| Windows | 独立后台进程 | 当前用户登录时启动的计划任务 |
| macOS | 独立后台进程 | 当前用户的 launchd LaunchAgent |
| WSL | Linux 后台进程 | 启用 systemd 时使用用户服务 |

`iop start` 启动后不依赖当前终端。希望登录后自动运行时，先执行 `iop stop`，等 `iop status` 显示服务已停止，再执行 `iop service install`。卸载自启动用 `iop service uninstall`，数据保留。Linux 无人登录的服务器可由管理员将同一条 `iop serve` 命令配置为系统服务，或为该用户启用 systemd lingering。Windows 计划任务和 macOS LaunchAgent 在用户登录后运行。

WSL 只能使用已经提供给 WSL 的设备；Windows 专用 SDK 可让服务直接运行在 Windows，WSL 中的实验程序经 HTTP 连接。USB 转接方式见 [Microsoft WSL USB 文档](https://learn.microsoft.com/en-us/windows/wsl/connect-usb)。

## 五分钟运行一个实验

在尚未登记真实仪器的配置中，启动前添加三个模拟设备：

```sh
iop init --demo
iop start
iop devices
iop run examples/iop/parallel.json --wait
iop package examples/iop/polarization --resources stage meter optical-path --wait
```

单点实验同时移动转台、设置探测器，二者完成后才采集。扫描程序逐点执行，保存 `scan.csv`、`result.json` 和程序输出。默认扫描七个角度；全部读数标明 `simulation`。

修改扫描参数：

```sh
iop package examples/iop/polarization --resources stage meter optical-path --parameters '{"angles_deg":[0,15,30,45]}'
```

Windows 命令行的引号处理可能不同，跨系统调用优先使用下面的 Python 客户端。

```python
from ai4instruments.iop import Client

lab = Client()
run = lab.submit_package(
    "examples/iop/polarization",
    project="polarization-study",
    resources=["stage", "meter", "optical-path"],
    parameters={"angles_deg": [0, 15, 30, 45]},
)
print(run.id)           # 保存此编号，稍后继续查询
print(run.result())    # 等待并读取结果
for file in run.files():
    print(file["id"], file["name"], file["size"])
```

提交成功后，客户端退出或网络断开，服务中的实验继续。重新连接后，用 `Client().run(run_id).info()` 查询；用 `run.files()` 列出文件，`run.download(file_id, "scan.csv")` 下载数据。

## 通用结构与多仪器实验

服务的核心对象是设备、具名操作、实验程序、依赖关系、共享资源和数据。调度器不包含光学、化学或某一型号的专用逻辑。设备差异放在驱动和仪器说明中；实验差异放在程序包中。

| 层次 | 已实现的内容 |
| --- | --- |
| 通信与驱动 | SCPI TCP / 串口 / VISA、Modbus TCP / RTU、HTTP JSON、自定义 Python 驱动 |
| 仪器说明 | 操作名称、参数、单位、范围、资源与驱动定义的完成条件 |
| 常驻服务 | 设备登记、发现、依赖调度、程序进程、数据保存与读取 |
| 实验程序 | 任意 Python 逻辑、循环、反馈、拟合和分析；其他语言也可通过 HTTP 调用 |

温控、称量、加液和信号采集的完整组合实例：

```sh
iop register examples/iop/multi-instrument/devices.json
iop package examples/iop/multi-instrument --resources bath balance pump daq sample --wait
```

该实例同时准备恒温设备、天平和采集设备；随后按实际返回的质量逐次计算加液量；每次加液后并行读取温度、质量与信号，最后保存 CSV。它使用明确标记的模拟设备，便于在没有仪器的计算机上运行。替换为真实设备时，驱动需提供对应操作及其单位、完成含义。

SCPI、Modbus 和 HTTP 接入代码均为实际通信实现。分别提供[功率计](../../examples/iop/scpi-meter.json)、[温控器](../../examples/iop/modbus-temperature.json)和[环境传感器](../../examples/iop/http-sensor.json)说明格式。显微镜、相机、机器人、质谱仪、流式设备及专有总线通过厂商 SDK 或现有控制软件接入同一驱动接口；本版没有预置这些设备所有型号的驱动。

## 仪器怎样接入

```sh
iop discover
iop register examples/iop/scpi-meter.json
iop devices
```

先将示例中的地址、单位、命令和完成条件改成仪器手册提供的内容，再登记。

| 接入方式 | 当前实现 |
| --- | --- |
| 系统可见的 USB 设备 | Linux sysfs、Windows PnP、macOS system_profiler 枚举 |
| 串口设备 | pySerial 枚举端口、厂商编号、产品编号与序列号 |
| VISA 资源 | PyVISA 通过已安装的 VISA 后端枚举 |
| SCPI 仪器 | 持续 TCP、串口或 VISA 连接；文本查询、写入、具名操作与完成状态读取 |
| Modbus 仪器 | TCP / RTU；寄存器与线圈读取和写入、具名操作、数值缩放、共用总线排序 |
| HTTP 仪器 | 按说明调用 JSON 端点，传递参数并提取返回值 |
| 厂商 SDK、相机、运动控制、已有平台 | 安装 `module:Class` 形式的 Python 驱动 |
| 自动登记 | 已配置的发现规则匹配连接信息，生成设备记录 |

**发现连接后，还需要对应的仪器说明和驱动，才能知道它能做什么、命令怎样发送、怎样判断动作完成。** USB 列表也会包含键盘、集线器等非仪器设备。网络仪器使用配置的地址，VISA 后端也可返回它支持发现的网络资源。

新增型号通常只增加驱动或说明文件，不需要修改调度器、实验记录或客户端。驱动调用本机可用的 SDK，因此操作系统、CPU 架构和厂商驱动仍需相互匹配。具体格式见[仪器驱动](drivers.md)。

## 串行、并行与设备占用

调度器同时处理两件事：**前一步是否完成；需要的设备和共享资源是否可用。**

| 情况 | 执行方式 |
| --- | --- |
| 不同设备、没有依赖 | 在可用工作线程中并行 |
| 同一设备的多个请求 | 默认顺序执行；驱动声明 `concurrency` 后按其数量安排 |
| 步骤的 `after` 指向前置步骤 | 前置步骤全部完成后执行 |
| 多项操作使用同一光路、样品或运动区域 | 给它们声明同一个共享资源名 |
| 一次扫描不能被其他实验插入 | 提交时在 `resources` 中列出整次实验需要的设备与共享资源 |
| 同时有很多实验 | 超出工作数的请求排队；互不占用设备的实验可以继续 |

整次实验所需的资源一起取得，避免两个实验各占一半设备并互相等待。实验内部仍可并行操作不同设备。程序包若声明整次占用，必须一次列出它使用的所有设备。工作流只要声明整次占用，服务就会将所有步骤使用的设备一并纳入。

未声明整次占用的实验，设备在每项操作完成后交给后续请求。这适合独立读数；扫描、配液、样品转移等连续过程应声明整次占用。所有调用者需要经同一服务访问同一设备，调度器才能统一安排它们。

取消会停止未开始的步骤、通知正在执行的驱动，并结束实验程序进程。正在执行的设备调用返回后才释放占用。驱动应提供明确的返回时间和动作完成含义；精确同步与高速反馈由设备控制器、时钟和硬件触发完成。

## 实验程序包

程序包是一个包含 `package.json` 和程序文件的目录，也可以是 ZIP。提交后，服务保存原包、创建实验目录，在独立进程中启动程序。拟合、优化、数据处理和下一步实验决策都可以写在该程序中。

```json
{"name":"polarization-scan","version":"1.0","command":["{python}","experiment.py"]}
```

`{python}` 使用服务当前的 Python 环境；也可以填写已安装的其他程序及参数。程序依赖安装在服务所在环境中。程序包以服务用户身份执行，是该实验平台安装并运行的实验软件。

程序内部：

```python
import os
from pathlib import Path
from ai4instruments.iop import Client

run = Client().current_run()
angle = run.invoke("stage", "move_to", {"angle_deg": 15})
reading = run.invoke("meter", "measure")
Path(os.environ["IOP_RUN_DIR"], "reading.txt").write_text(str(reading))
run.save_result({"position": angle, "reading": reading})
```

需要并行时，用线程同时调用 `run.invoke`；各调用仍由服务按设备安排。完整实例见[扫描程序](../../examples/iop/polarization/experiment.py)。不上传程序包时，可以直接提交 JSON 工作流；外部程序也可使用 `Client.invoke` 进行单步操作。外部程序自身退出后，其尚未提交的逻辑不会自动搬到服务中；需要持续执行的整个研究过程应作为程序包提交。

## 数据与持续运行

默认数据目录为 `~/.iop`，通过 `IOP_HOME` 或 `iop --home /path/to/data ...` 更改。`--home` 和 `--endpoint` 位于子命令之前。

| 文件 | 内容 |
| --- | --- |
| `config.json` | 服务地址、工作数、设备、发现规则与连接令牌 |
| `records.sqlite3` | 实验、操作、按顺序记录的事件及文件索引 |
| `runs/<run_id>/experiment.json` | 提交的实验定义与参数 |
| `runs/<run_id>/package.zip` | 提交的原程序包 |
| `runs/<run_id>/run.json` | 完成、失败、取消或中断后的实验记录 |
| `runs/<run_id>/output/` | 数据文件与结果 |
| `runs/<run_id>/stdout.txt`、`stderr.txt` | 实验程序输出 |
| `service.log` | 后台服务输出 |

每次提交有独立 `run_id`，每项操作有独立 `operation_id`。实验保存提交时的设备说明，事件保存开始、结束、错误与返回结果。调用方可提供 `request_id`；同一请求重发返回原记录，不重复执行。

服务重新启动时，尚未开始的任务继续排队；已经开始但没有完整结束记录的任务标为 `interrupted`，保留已有数据。该版本不会自动重放这些物理动作。重启后确认设备位置与实验进度，再提交下一次实验。

默认同时执行 8 项设备操作、4 个实验程序包，可在 `config.json` 中修改 `workers` 和 `package_workers` 后重启。并发数应按计算机性能、设备响应和实验需要设置。调度服务不会自行修改实验算法、设备参数或完成条件。

## 客户端和服务器

默认只监听 `127.0.0.1:8765`。其他计算机需要访问时，设置服务的 `host` 为相应网卡地址；客户端提供服务地址与 `config.json` 中的令牌：

```python
lab = Client("http://lab-computer:8765", token="平台令牌")
```

也可以设置 `IOP_ENDPOINT` 和 `IOP_TOKEN`。页面用 `iop open` 打开，连接信息由本机配置传入。HTTP API 见[接口文档](http-api.md)。不同计算机可分别运行服务，实验程序按设备所在平台连接；本版资源调度范围为一个服务实例。

## 源码与开发

源码安装后，普通命令程序和独立 SDK 需要编译原生组件：

```sh
cargo build --release --locked --manifest-path iop/daemon/Cargo.toml
```

将生成的 `iop-execd`（Windows 为 `iop-execd.exe`）放入命令路径，或把环境变量 `IOP_EXECD` 设置为它的绝对路径。发行包已包含该程序。


```sh
python -m pip install -e .
python -m unittest discover -s tests -v
python -m pip wheel --no-deps . --wheel-dir dist
```

持续集成覆盖 Linux、Windows、macOS 和 Python 3.10、3.12。自动检查包括并行执行、同设备排序、跨步骤占用、重启记录、程序包执行、HTTP 客户端和本地 TCP 仪器通信。真实型号的命令与完成行为由对应驱动进一步验证。
