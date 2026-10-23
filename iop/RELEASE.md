IOP Runtime 0.7.0 connects agent clients to the same persistent service used by the desktop, browser, CLI and experiment programs.

- MCP stdio integration with tools for laboratory context, instrument descriptions, platform setup, experiment submission, progress, files and reconnection.
- `iop mcp-config` generates the command and arguments for the installed application. `iop context --start` starts or connects to the service and reads the laboratory configuration.
- `/v1/context` provides a compact description of instruments, platforms, available drivers, resources and remaining setup. JSON schemas for instruments, platforms and workflows are included in the installation.
- Desktop/browser settings can export the laboratory description. Existing configurations are reused; initialization remains a named experiment procedure.
- Identical instrument-registration retries reuse their connection. Startup failures retain their device configurations when other instruments are registered, and can be reconnected later.
- Selecting a remote endpoint no longer attempts to start a local service. Concurrent local startup requests wait for the shared service to become available.
- Release checks now exercise unpacked installers on all six native targets, MCP communication, and Linux ARM64 desktop/browser operation in addition to the existing targets.

Download the ZIP matching your operating system and CPU. Windows: run install-desktop.ps1 for desktop use or install.ps1 for browser/server use. macOS/Linux: run sh install-desktop.sh or sh install.sh. Python 3.10+ is required. Archives include the native Rust executor; installers create a separate Python environment and download dependencies. The Agent component is installed by default; IOP_AGENT=0 omits MCP dependencies.

Linux service packages target glibc 2.35+; ARM64 desktop requires glibc 2.39+. macOS build targets are Apple Silicon 14+ and Intel 15+. Windows offers x86_64 and ARM64 packages, with WebView2 for desktop use. See iop/product.md and iop/interface.md for platform requirements. These are ZIP/script installations; standalone signed installers and automatic updates are not included.

Finish active experiments and stop the old service before updating. Configuration and data in ~/.iop are retained. Closing an interface or agent leaves accepted experiments running; stopping the service records active experiments as interrupted.

中文：0.7.0 新增 MCP、统一实验室说明、仪器与平台配置格式接口，以及桌面和网页中的说明导出。Agent 复用已有仪器说明与平台配置，提交实验后可以退出，再通过运行编号查询。修复远端连接误启动本机服务、并发启动和失败设备配置保留问题。安装脚本默认包含 Agent 组件。中文说明：iop/product.zh-CN.md 与 iop/agent-setup.zh-CN.md。
