IOP Runtime 0.8.3 improves shared instrument connections and independently installed model descriptions.

- Modbus devices on one bus share a connection with separate device addresses and response timeouts. Reconfiguring an idle device preserves its neighbours' connection. Independent buses continue in parallel.
- Registration distinguishes a physical bus from an instrument address, rejects duplicate device addresses, and retains every device in shared-connection discovery results.
- Installed Python packages can supply JSON model descriptions through `ai4instruments.instrument_profiles`. Reading them does not import the package or start its SDK.
- The model catalogue supports filtering, pagination, package versions and original documentation through HTTP, CLI, Python, TypeScript and MCP. Invalid package files leave other descriptions available.
- More specific identity matches take precedence within a source tier. Equally applicable descriptions remain explicit choices. The interface can apply an installed description through existing versioned configuration.

Windows, macOS and Linux: x86_64 and ARM64. All six archives include Python and offline Runtime/Agent dependencies. Desktop installation additionally downloads native UI dependencies. Vendor SDKs and OS device drivers are installed for the instruments that need them.

中文：0.8.3 修复共享总线的连接与配置更新，完整保留总线上的仪器列表，并支持随独立安装包提供型号说明。目录可按制造商与型号查询；来源、版本及操作可直接查看和采用。桌面、浏览器和 Agent 使用同一套配置与接口。

[仪器支持包与共享总线](https://github.com/Cherish0925/AI4Instruments/blob/main/iop/instrument-packages.zh-CN.md) · [Instrument support packages](https://github.com/Cherish0925/AI4Instruments/blob/main/iop/instrument-packages.md) · [API](https://github.com/Cherish0925/AI4Instruments/blob/main/docs/runtime/http-api.md)
