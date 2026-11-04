# 把实验室接入研究系统

IOP Runtime 常驻在操纵仪器的计算机上。插件把选定的实验室接入研究系统；Skill 写明操作方法；MCP 提供可调用的工具。实验由实验室服务执行，关闭对话或更新插件不会取消已经接收的实验。

[English](README.md) · [图解与安装（HTML）](guide.zh-CN.html) · [下载 IOP](https://github.com/Cherish0925/AI4Instruments/releases/latest) · [服务接口](../../docs/runtime/http-api.md)

## 选择实验室

在实验室电脑安装 Runtime。在**执行 Agent 工具的那台电脑**上使用 IOP 0.8.4 的命令；如果终端找不到 `iop`，用安装器显示的完整路径。

| 部署方式 | 操作 |
| --- | --- |
| 本机仪器 | `iop connect --name bench --local`。有多套服务时用 `--lab-home 路径` 指定实验室数据目录。 |
| 通过 SSH 使用另一台实验室电脑 | `iop connect --name bench --ssh lab-server --remote-iop /opt/iop/venv/bin/iop`。使用已设好的非交互 SSH 账户；远端自定义路径按 POSIX shell 传递。程序包路径属于远端运行 MCP 的电脑。 |
| 已有 IOP REST 服务 | `iop connect --name bench --remote https://lab.example.org --token-env BENCH_IOP_TOKEN`。工具执行端安装 IOP 桥接程序，由宿主注入该名称对应的凭据。地址填服务根地址。程序包和下载路径属于桥接电脑。 |
| 只接受 HTTP MCP 的云端产品 | 实验室管理员设置独立的 `IOP_MCP_TOKEN`，运行 `iop mcp-http --port 8766`。通过 HTTPS 反向代理接入 `/mcp`，提交 Bearer 凭据。网关只监听本机回环地址，代理向上游发送 `Host: 127.0.0.1:8766`。只支持 OAuth 的宿主需另配网关。HTTP 不开放读写网关本机路径的两个文件工具。 |

命令输出各宿主的安装路径，不操作仪器。一个名字绑定一个实验室；另一套实验室用另一个名字。更新时运行 `iop connect --name bench`，沿用原连接。站点配置和实验数据仍由实验室保存。

## 在宿主中安装

| 宿主 | 安装与更新 |
| --- | --- |
| Codex | `codex plugin marketplace add "<marketplace>"`，再执行 `codex plugin add bench@iop-bench`。直接注册 MCP 可使用输出中的 `codex_toml`。Git 来源可用 `codex plugin marketplace upgrade ai4instruments` 刷新，再安装新版插件。 |
| Claude Code | `claude plugin marketplace add "<marketplace>"`，再执行 `claude plugin install bench@iop-bench`。重新生成连接包后执行 `claude plugin update bench@iop-bench`，重新加载插件。 |
| Agentic Research OS | 将 `research_os` 对应目录放进目标 Session 的工作目录，在 Extensions 中以 **plugin** 安装，名称用实验室名；激活安装得到的版本。升级时以当前版本为起点安装，再激活新版本。 |
| 求是引擎 | 把 `qiushi` 对应目录作为 **MCP 包**导入目标用户的研究空间；需上传 ZIP 时选 `qiushi_zip`。现有 Linux 执行后端通过 `run_shell` 使用 `bench tools` 和 `bench call 工具名 JSON`；用同一包安装器更新。 |
| 其他 stdio MCP 宿主 | 在 `mcp` 对应的 JSON 文件中取出可执行程序与参数数组，一并注册。连接远端 REST 时让宿主向子进程传递指定的凭据变量。 |
| 其他科研程序 | 可直接使用 REST、Python 或 TypeScript。IOP 服务接口在 `/v1`；独立的 HTTP MCP 网关在 `/mcp`。 |

**从 GitHub 安装。** 如果宿主能在 PATH 中找到 `iop`，直接在 Codex 或 Claude Code 添加 `Cherish0925/AI4Instruments` 插件源，安装 `iop-lab@ai4instruments`。它使用该进程的 IOP 连接。桌面程序找不到 PATH，或一个账号需要区分多个实验室时，使用上面的具名连接。托管部署应给执行工作进程分配相应实验室和凭据；插件本身不隔离租户。

**分别更新。** 更新插件不会重启 Runtime、替换驱动或移走实验记录。原连接包保留，供已经打开的客户端使用。升级 Runtime 时，等已接收的实验结束，再运行新版本对应平台的安装器。已有 0.8.3 用户也可解压独立连接器 ZIP，运行 `python install.py --name bench`；可使用 IOP 自带的 Python，或用 `--iop-python 路径` 指定。HTTP MCP 网关从 0.8.4 提供。

## 第一次使用

读取 `lab_context`，再用 `describe_instrument` 查询所选设备的操作、参数和单位。接线、样品或校准条件无法从机器读出时，由了解现场的人补齐。提交前选定 `request_id`，保存实验室名和返回的实验 ID；重连后以 `experiment(run_id, include_result=true)` 读取结果。只有在原提交的回复丢失时，才用相同请求 ID 重发相同内容。
