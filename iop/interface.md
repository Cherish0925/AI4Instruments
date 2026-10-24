# IOP Runtime · Desktop and browser

[中文](interface.zh-CN.md) · [Download 0.8.2](https://github.com/Cherish0925/AI4Instruments/releases/tag/iop-v0.8.2) · [IOP project](README.md)

IOP Runtime is installed software that runs continuously on the laboratory computer. Its native window and browser interface connect to the same service and share instruments, platform configuration, experiments and data. Accepted experiments continue when either window closes.

| Component | Purpose |
| --- | --- |
| Runtime service | Maintain device connections, schedule operations, execute programs and save results. |
| Desktop application | A dedicated window and application menu entry; start or connect to the local service. |
| Browser interface | Use the same interface in a browser, including connections to laboratory servers. |
| Program interface | Connect agents, Python / TypeScript programs and command-line tools directly. |

## Install

Download and extract the ZIP for your operating system and CPU. Python 3.10+ and network access to download dependencies are required. Each archive includes the matching Rust executor.

On **Windows**, run from the extracted directory:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File .\install-desktop.ps1
```

The Start menu receives **IOP Runtime** and **IOP Browser**. The desktop window uses Microsoft Edge WebView2; install [WebView2 Runtime](https://developer.microsoft.com/microsoft-edge/webview2/) if it is absent.

On Windows ARM64, the installer also installs .NET 10 Desktop Runtime inside the IOP user installation for the native ARM64 window. See [Microsoft installation documentation](https://learn.microsoft.com/dotnet/core/tools/dotnet-install-script).

On **macOS / Linux**:

```sh
sh install-desktop.sh
```

macOS applications are installed under your user `Applications` directory. Linux receives application menu entries and uses Qt WebEngine / PySide6. It requires a graphical session and system GUI libraries; on Ubuntu:

```sh
sudo apt-get install libegl1 libopengl0 libxkbcommon0 libxkbcommon-x11-0 libxcb-cursor0 libxcb-icccm4 libxcb-keysyms1 libxcb-shape0 libxcb-xinerama0 libxcb-randr0 libxcb-render-util0 libxtst6 libxkbfile1 libopus0 libsnappy1v5 libminizip1t64 liblcms2-2 libwebp7 libwebpdemux2 libwebpmux3 libnss3 libasound2t64
```

On Ubuntu 22.04, use `libasound2` and `libminizip1` instead of their `t64` variants. Linux ARM64 desktop installations require Ubuntu 24.04 (glibc 2.39) or a newer compatible system for the matching [PySide6 web engine](https://pypi.org/project/PySide6-WebEngine/). Headless servers and WSL can use `install.sh` and browser access. Windows-specific instrument SDKs run with a Windows service.

The installer prints full command paths. To update, stop the existing service with its `iop stop` command, run the new installer and reopen the application. Existing `~/.iop` configuration and records are retained.

## Open and switch

| Action | Command or entry |
| --- | --- |
| Native window | IOP Runtime from the application menu, or `iop desktop` |
| Browser | IOP Browser from the application menu, or `iop open` |
| Switch interfaces | “Open in browser” / “Open desktop app” in the sidebar |
| Start the service at login | `iop service install`; see [service installation](../docs/runtime/README.md) |
| Stop the service | `iop stop` |

Both commands start the local service if necessary and otherwise connect to it. Both windows may remain open. Browser-to-desktop switching applies to the same computer with a graphical session. To use a remote service, start the desktop application on your computer:

```sh
iop --endpoint http://lab-computer:8765 desktop
```

Provide the service token through `IOP_TOKEN`. Configure the server's listening address as described in the [runtime guide](../docs/runtime/README.md).

## Pages and workflow

| Page | Work |
| --- | --- |
| Overview | Device counts, platforms, active experiments and recent results; discovery on first use. |
| Instruments & software | Discover serial, USB, VISA and registered connections; choose a driver, register a device and invoke described operations. |
| Platforms | Select devices, describe ports and physical links, view topology, save configuration and run defined initialization procedures. |
| Experiments | Submit operations or an experiment ZIP; inspect progress, parameters, returned values, results and files. |
| Resources | Inspect device and shared capacity use, edit configured capacities and inspect installed adapters. |
| Connection & settings | Chinese / English, light / dark themes, service computer, version and connection. |

Discovery lists connections visible to the computer. Registration selects the instrument's driver and operation description; platform configuration describes actual wiring. Simple workflows can be assembled from operations and dependencies in the interface. Submit an experiment ZIP for loops, feedback and analysis. Configuration import and JSON editing remain available.

Results load separately from operation history, which is paged in groups of 100. Automatic refresh preserves forms being edited. `Ctrl/Cmd + K` finds devices, platforms and experiments.

## Interface implementation

HTML, CSS and JavaScript modules ship with the installed software; no frontend development server or CDN is required. Desktop windows use the system web engine on Windows / macOS and Qt WebEngine on Linux. pywebview supplies the standard window; Windows ARM64 uses public Windows Forms and WebView2 APIs directly. See [source and verification](interface/README.md).

## Agent integration

Installers include the MCP component. Run `iop mcp-config` for this installation’s agent launcher or `iop context --start` to read laboratory setup. Connection settings can export the same description. [Agent guide](agent-setup.md).
