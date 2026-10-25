# IOP Runtime · 桌面与网页

[English](interface.md) · [下载 0.8.3](https://github.com/Cherish0925/AI4Instruments/releases/tag/iop-v0.8.3) · [IOP 工程](README.zh-CN.md)

IOP Runtime 是安装在实验室计算机上的常驻软件。桌面窗口和浏览器是它的两个操作入口：连接相同的服务，使用相同的仪器、平台配置、实验和数据。窗口关闭后，已经提交的实验继续运行。

| 组成 | 作用 |
| --- | --- |
| 运行服务 | 保持设备连接，安排串行与并行操作，执行实验程序，保存结果。 |
| 桌面应用 | 独立窗口、系统应用菜单入口，直接连接或启动本机服务。 |
| 网页界面 | 在浏览器中使用同一套操作界面，也可连接实验室服务器。 |
| 程序接口 | Agent、Python / TypeScript 程序与命令行直接调用服务。 |

## 安装

下载与操作系统和 CPU 相符的 ZIP，解压。需要 Python 3.10+ 和可下载依赖的网络。Windows、macOS 与 Linux 的发行包均包含对应架构的 Rust 执行程序。

**Windows**，在解压目录运行：

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File .\install-desktop.ps1
```

安装后，在开始菜单找到 **IOP Runtime** 和 **IOP Browser**。桌面窗口使用 Microsoft Edge WebView2；如果系统没有安装它，先安装 [WebView2 Runtime](https://developer.microsoft.com/microsoft-edge/webview2/)。

Windows ARM64 的安装脚本还会把 .NET 10 Desktop Runtime 安装到 IOP 用户目录，供原生 ARM64 窗口使用。[Microsoft 安装说明](https://learn.microsoft.com/dotnet/core/tools/dotnet-install-script)。

**macOS / Linux**：

```sh
sh install-desktop.sh
```

macOS 应用位于当前用户的 `Applications` 目录；Linux 写入当前用户的应用菜单。Linux 桌面使用 Qt WebEngine / PySide6，需要图形会话和系统图形库。Ubuntu 可安装：

```sh
sudo apt-get install libegl1 libopengl0 libxkbcommon0 libxkbcommon-x11-0 libxcb-cursor0 libxcb-icccm4 libxcb-keysyms1 libxcb-shape0 libxcb-xinerama0 libxcb-randr0 libxcb-render-util0 libxtst6 libxkbfile1 libopus0 libsnappy1v5 libminizip1t64 liblcms2-2 libwebp7 libwebpdemux2 libwebpmux3 libnss3 libasound2t64
```

Ubuntu 22.04 使用 `libasound2` 与 `libminizip1`，分别替代 `libasound2t64` 与 `libminizip1t64`。Linux ARM64 桌面使用 Ubuntu 24.04（glibc 2.39）或更新的兼容系统，以安装对应的 [PySide6 网页引擎](https://pypi.org/project/PySide6-WebEngine/)。无桌面的服务器和 WSL 可以使用 `install.sh` 安装运行服务，从浏览器访问。Windows 专用仪器 SDK 使用 Windows 端服务。

安装脚本打印完整命令路径；同一目录可以再次运行安装脚本升级。更新前用旧安装的 `iop stop` 停止服务，安装后重新打开应用。默认的 `~/.iop` 配置与实验记录继续保留。

## 打开与切换

| 操作 | 命令或入口 |
| --- | --- |
| 桌面窗口 | 应用菜单中的 IOP Runtime，或 `iop desktop` |
| 浏览器 | 应用菜单中的 IOP Browser，或 `iop open` |
| 两种界面间切换 | 左侧底部“在浏览器中打开” / “打开桌面应用” |
| 开机后登录时启动服务 | `iop service install`，详见[服务安装](../docs/runtime/README.zh-CN.md) |
| 停止运行服务 | `iop stop` |

`iop desktop` 和 `iop open` 会启动尚未运行的本机服务；已经运行时直接连接。浏览器与桌面可以同时打开。浏览器中的桌面切换按钮适用于同一台有图形会话的计算机；连接服务器时，在自己的电脑启动桌面客户端并指定服务器地址：

```sh
iop --endpoint http://lab-computer:8765 desktop
```

通过 `IOP_TOKEN` 提供该服务的连接令牌。服务器监听地址的设置见[客户端和服务器](../docs/runtime/README.zh-CN.md#客户端和服务器)。

## 页面与工作流程

| 页面 | 具体用途 |
| --- | --- |
| 概览 | 查看仪器数、实验平台、当前执行和最近结果。首次使用从设备发现开始。 |
| 仪器与软件 | 查看串口、USB、VISA 和已登记连接；选择驱动、填写地址并登记；按仪器说明填写参数与执行操作。 |
| 实验平台 | 选择设备，设置端口与物理连接，查看连接图，保存平台配置；执行已定义的初始化过程。 |
| 实验任务 | 提交操作流程或实验 ZIP，查看步骤进度、参数、返回值、结果和文件。 |
| 运行资源 | 查看设备与共享资源的使用数量，调整已配置的资源容量，查看驱动包。 |
| 连接与设置 | 切换中文 / 英文、浅色 / 深色主题，查看服务所在计算机、版本与连接。 |

设备发现列出计算机可见的连接。登记时仍需选择与仪器匹配的驱动和操作说明；仪器的物理接线由平台配置表达。简单实验可以用界面选择操作和前置步骤，循环、反馈和分析逻辑可以直接提交实验程序 ZIP。JSON 导入与编辑保留在对应配置入口。

结果与操作记录分开读取，操作历史每次加载 100 条。界面自动刷新，正在填写的表单不会被刷新覆盖。`Ctrl/Cmd + K` 可查找设备、平台和实验。

## 界面工程

界面是随软件安装的 HTML、CSS 与 JavaScript 模块，无需前端服务器或 CDN。Windows / macOS 使用系统网页引擎，Linux 使用 Qt WebEngine。常规桌面窗口由 pywebview 提供，Windows ARM64 通过公开的 Windows Forms 与 WebView2 接口创建窗口。[源码与运行检查](interface/README.md)。

## Agent 接入

安装脚本默认包含 MCP 组件。用 `iop mcp-config` 获取当前安装的 Agent 连接配置；用 `iop context --start` 读取实验室配置。“连接与设置”页面可导出实验室说明。[完整接入说明](agent-setup.zh-CN.md)。
