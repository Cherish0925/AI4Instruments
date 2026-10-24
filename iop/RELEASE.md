IOP Runtime 0.8.1 connects discovery, instrument identity and saved model operations.

- Discover LXI SCPI-raw, HiSLIP and VXI-11 announcements alongside USB, serial and VISA resources.
- Read instrument manufacturer, model, serial number and firmware; automatically register recognized SCPI endpoints.
- Reuse identity across rediscovery and address changes. Read identities through the scheduler for existing connections, and verify saved identity when reconnecting.
- Match exact manufacturer/model descriptions and load named operations. The bundled catalogue covers selected operations for SR830 and eight RIGOL DP800 models; add local descriptions through CLI, HTTP, MCP or the shared interface.
- Enumerate installed NI-DAQmx and Basler pypylon SDK devices. SDK and VISA discovery run in separate processes; installed discovery plugins can return identity, channels and driver configurations.
- Save discovery history and expose specific remaining setup fields to Agents. Desktop and browser show identity, source, interface information and documentation together.

Downloads: six OS/architecture archives and the TypeScript client. Archives contain the Python wheel and Rust executor. Run `install-desktop.ps1` on Windows or `sh install-desktop.sh` on macOS/Linux for the desktop application; use `install.ps1` / `install.sh` for browser/server operation. Python 3.10+ and an internet connection for dependencies are required.

Stop the previous service after experiments finish, then run the new installer. Existing configuration and records are retained.

中文：0.8.1 将发现连接、读取仪器身份、保存型号操作连成同一流程，增加 LXI 网络发现、NI-DAQmx/pypylon 枚举与发现扩展。桌面、网页和 Agent 共用身份、连接、资料与未完成设置。内置型号操作覆盖 SR830 与 8 个 RIGOL DP800 型号的部分功能；其他型号使用通用接口或安装对应说明与驱动。USB 转串口名称不会作为仪器身份，物理接线和样品关系仍由平台配置记录。

[中文接入说明](https://github.com/Cherish0925/AI4Instruments/blob/main/iop/instrument-setup.zh-CN.md) · [English setup](https://github.com/Cherish0925/AI4Instruments/blob/main/iop/instrument-setup.md) · [Model descriptions and SDK extensions](https://github.com/Cherish0925/AI4Instruments/tree/main/iop/instruments)
