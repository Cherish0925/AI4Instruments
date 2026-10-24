# IOP · Agent 接入

[English](agent-setup.md) · [软件与平台](product.zh-CN.md) · [HTTP API](../docs/runtime/http-api.md) · [平台格式](schema/platform.schema.json)

Codex、Claude Code、DeepSeek Harness、Qiushi Engine 等研究软件可以通过 MCP、CLI、HTTP 或 Python / TypeScript 客户端使用 IOP。各入口连接同一个运行服务，复用同一份仪器说明、平台配置和实验记录。

## 第一次连接

发行包安装脚本默认安装 Agent 组件。用安装后的 `iop` 命令生成连接配置：

```sh
iop mcp-config
```

将其中的 `command` 和 `args` 填入 Agent 软件的 MCP 服务配置。输出使用常见的 `mcpServers` JSON 结构；采用其他配置格式的客户端使用相同的命令和参数。路径对应当前安装位置，输出不包含服务令牌。

Agent 软件随后启动 `iop mcp`。它连接本机服务，尚未运行时自动启动。关闭 Agent 或 MCP 进程后，服务与已经受理的实验继续运行。首先调用 `lab_context`，即可获取已有平台、仪器操作名称、已安装驱动、可见连接、资源使用和仍待配置的部分。

使用终端的 Agent 可以直接执行：

```sh
iop context --start
```

需要重新扫描连接时添加 `--refresh`；平时读取当前扫描结果。桌面和网页的“连接与设置”也可以导出同一份实验室说明。

从源码安装时，在 IOP 的 Python 环境中安装 `.[agent]`。发行包安装时设置 `IOP_AGENT=0` 可以省略 MCP 依赖。Python 3.10 使用仍维护的 MCP SDK 1.x，Python 3.11+ 使用 SDK 2.x；两条路径均由运行检查覆盖。[SDK 文档](https://py.sdk.modelcontextprotocol.io/)。

## 初始化与日常实验

1. 读取 `lab_context`，先复用已有仪器和平台。
2. 新仪器接入时，根据型号和资料选择已安装驱动；读取 `configuration_schema("device")`，再调用 `register_instrument`。重复提交相同配置会复用原连接。
3. 用 `configure_platform` 保存设备、实际连接、共享对象与初始化过程；修改时带上当前版本号。只向人询问已有资料和设备无法提供的物理信息。
4. 实验需要初始化时执行已保存的过程。仅保存配置不执行设备动作，也不要求每次连接都重新初始化。
5. 提交实验步骤或程序包，保存返回的运行编号，随后查询进度与结果。同一提交遇到连接中断时，重试使用原来的 `request_id`。

单台仪器可以直接使用；多个设备一起构成实验系统时，用平台说明它们的关系。步骤依赖表达先后顺序，共享资源表达需要统一安排使用的样品、腔体、总线等对象。独立设备由服务并行执行。

## MCP 工具

| 工具 | 用途 |
| --- | --- |
| `lab_context` | 读取实验室现状；可选择重新扫描连接 |
| `describe_instrument` | 读取单台仪器的操作、参数和单位 |
| `configuration_schema` | 读取仪器、平台或实验步骤的 JSON 格式 |
| `register_instrument` | 用已安装驱动登记连接 |
| `register_instruments` | 批量保存仪器说明，分别返回每项结果；ID 可省略 |
| `discover_instruments` | 启动后台扫描，或读取已有结果 |
| `configure_platform` | 保存或预览平台说明 |
| `configure_resources` | 设置资源可用数量 |
| `run_procedure` | 执行已保存的初始化或其他过程 |
| `submit_experiment` | 提交具有串并行依赖的仪器操作 |
| `submit_program` | 将 Agent 所在计算机上的目录或 ZIP 上传给服务运行 |
| `experiment` | 读取状态、分页操作记录、文件和结果 |
| `cancel_experiment` | 请求取消实验 |
| `reconnect_instrument` | 重新连接设备或此前无法加载的 SDK |
| `resolve_resources` | 记录设备当前状态，恢复使用被中断操作占用的资源 |
| `download_file` | 将实验文件保存到 Agent 所在计算机 |

MCP 资源 `iop://laboratory` 提供相同的实验室说明。提交工具立即返回，不需要等待整个实验结束。操作记录每页最多 100 条，下一次查询使用返回的 cursor；大型数据通过文件获取。

## 连接远端实验室

```sh
iop --endpoint http://lab-computer:8765 mcp-config
```

在 Agent 软件的环境或凭据配置中设置 `IOP_TOKEN`。MCP 进程运行在 Agent 所在计算机，将工作发送到可达的仪器服务；选择远端地址后不会额外启动本机服务。服务器监听设置见[安装说明](../docs/runtime/README.zh-CN.md)。

## Python 与 TypeScript

```python
from ai4instruments.iop import Client
lab = Client()  # 使用环境变量或本机配置中的连接信息。
print(lab.context()['platforms'])
print(lab.schema('workflow'))
```

```typescript
import { IOP } from '@ai4instruments/iop';
const lab = new IOP(process.env.IOP_ENDPOINT, process.env.IOP_TOKEN);
const context = await lab.context();
const schema = await lab.schema('workflow');
```

HTTP 接口为 `GET /v1/context` 和 `GET /v1/schemas/{name}`。具体仪器的完整操作说明位于 `GET /v1/devices/{id}`，按任务需要读取。

## 多设备接入与连续调用

首次扫描用 `discover_instruments()`，随后用 `discover_instruments(refresh=false)` 读取进度。串口、VISA、USB 清单分开识别；操作语言和型号能力来自仪器说明、已安装驱动及制造商资料。使用 `register_instruments(definitions)` 一次接入多台设备，读取每项返回的 ID 和错误。设备 ID 不需要人填写。

实验程序中的 Python `run.invoke()` 与 TypeScript `run.invoke()` 等待目标操作完成后立即获得结果。互不依赖的操作可以并发提交；同设备、共享总线和平台资源由服务安排。已知整段步骤时用一次工作流提交表达 `after` 与 `bindings`，避免 Agent 逐步发送单条指令。涉及反馈决策的循环放在实验程序内。

[仪器接入说明](instrument-setup.zh-CN.md) · [实测方法与结果](performance/README.md)
