IOP Runtime 0.8.0 improves instrument setup, repeated program calls, parallel scheduling and the shared desktop/browser interface.

- Instrument IDs are generated automatically when omitted. Batch registration returns the outcome of each description. Saved driver configurations can be exported and reused.
- Serial, VISA, USB and configured-software discovery run concurrently. Background scan requests share one scan; other laboratory work continues. Known Windows COM/VISA aliases are grouped and cannot open duplicate SCPI drivers. USB inventory is displayed separately from configurable interfaces.
- Instrument operations stay in a side panel with readable responses, SCPI identity fields and direct access to experiment records. Large experiment results load only when requested. Short operation histories no longer show unnecessary pagination.
- SCPI text responses use buffered reads, preserve trailing data, handle split line endings and support configurable serial framing and flow control. Profile substitution preserves operation command templates.
- The scheduler commits groups of ready-operation start records before dispatch, retaining device/resource ordering. A failed start-record write releases the selected allocations for a later attempt without sending device commands.
- Python and TypeScript experiment-program calls wait for the target operation directly. The former fixed Python polling delay and repeated TypeScript event-history reads are removed. Status summaries avoid materializing full experiment results and definitions in the application.
- MCP adds background discovery and batch instrument registration. Chinese and English instrument-setup guides describe the common path from a connection to reusable model operations and experiment programs.

Three alternating measurements per version on the same Linux host gave these median execution times: 5,000 independent immediate operations, 2.995 s → 1.508 s; 200 sequential Python SDK calls over local HTTP, 10.607 s → 0.965 s; 5,000 serially dependent immediate operations, 3.347 s → 3.091 s. SQLite recording is included. These are local simulated-operation measurements, not physical instrument sampling rates. Raw data and scripts: iop/performance/.

Download the ZIP matching the operating system and CPU. Windows: install-desktop.ps1 or install.ps1. macOS/Linux: sh install-desktop.sh or sh install.sh. Python 3.10+ is required; installers create a separate environment and download dependencies. Archives include the Rust process executor. The Agent component is installed by default; IOP_AGENT=0 omits it.

Linux service packages target glibc 2.35+; ARM64 desktop requires glibc 2.39+. macOS targets are Apple Silicon 14+ and Intel 15+. Windows offers x86_64 and ARM64 packages, with WebView2 for desktop use. See iop/product.md for requirements. These remain ZIP/script installations; standalone signed installers and automatic updates are separate product work.

Finish active experiments and stop the old service before updating. Configuration and data in ~/.iop are retained. Closing an interface or Agent leaves accepted experiments running; stopping the service records active experiments as interrupted.

中文：0.8.0 增加自动 ID、批量接入、共享后台扫描、接口归组和仪器说明导出；改进仪器操作与结果展示。缓冲读取 SCPI 响应，合并调度写入，连续实验调用直接等待目标操作完成。所有入口共用原有 Runtime、驱动与平台配置。中文说明：iop/instrument-setup.zh-CN.md、iop/agent-setup.zh-CN.md、iop/product.zh-CN.md。
