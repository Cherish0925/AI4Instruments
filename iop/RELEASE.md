IOP Runtime 0.8.2 connects instrument configuration, continuing experiments and data transfer.

- Discovery publishes completed providers and identified instruments incrementally. Driver availability, discovery presence and recent communication are reported separately.
- Agent context defaults to a concise overview with detail URLs, device pagination and an event cursor. Subsequent reads can request changes without repeating measurement results.
- Instrument configurations retain versions and can be edited or restored while idle, from the shared interface, HTTP, CLI, Python, TypeScript or MCP.
- Programs can save progress and continue under the original run ID after interruption. Stable operation IDs retain completed results. Each attempt retains its terminal output.
- Binary streams retain ordered batches with format/channel descriptions, idempotent retries and artifact downloads. File transfer runs outside the instrument scheduler lock.
- Installed Python drivers can use the Rust supervisor through `execution.mode=process`. Startup, operation and cancellation deadlines are separate.
- Six OS/architecture archives include a pinned Python distribution and offline Runtime/Agent dependencies. Core installation no longer requires a system Python or dependency downloads. Desktop installers additionally download native UI dependencies.

Windows, macOS and Linux: x86_64 and ARM64. Use `install.ps1` / `sh install.sh`, or the corresponding `install-desktop` script. The installer stops an idle previous service; complete or cancel accepted experiments before upgrading. Laboratory configuration and records are retained. Vendor SDKs and OS device drivers are installed for the instruments that need them.

中文：0.8.2 改进连续使用：发现结果逐项显示，Agent 按需读取说明和变化，仪器配置可以在线编辑并保留版本，程序可以从保存的进度继续，连续数据按序分块保存。Windows、macOS、Linux 的六个发行包内置 Python 和核心依赖。桌面、浏览器、命令行和 Agent 继续使用同一个运行服务。

[持续实验与接入说明](https://github.com/Cherish0925/AI4Instruments/blob/main/iop/continuity.zh-CN.md) · [Continuing experiments](https://github.com/Cherish0925/AI4Instruments/blob/main/iop/continuity.md) · [API](https://github.com/Cherish0925/AI4Instruments/blob/main/docs/runtime/http-api.md) · [Scheduling measurements](https://github.com/Cherish0925/AI4Instruments/blob/main/iop/performance/README.md)
