IOP Runtime 0.8.4 connects research hosts to a named laboratory. The same instrument service owns experiments, configuration and data after the host disconnects or a connector is updated.

- Run `iop connect --name bench --local` to prepare Codex and Claude Code marketplaces, a Research OS plugin, a Qiushi command package, and direct MCP settings. Use `--ssh` for a remote lab, or `--remote` plus a host credential reference for a REST bridge.
- For clients that accept only MCP over HTTP, `iop mcp-http` serves Streamable HTTP at `/mcp` on loopback. Set `IOP_MCP_TOKEN`; use an HTTPS proxy for clients on another machine.
- The separate IOP Connect ZIP supports existing 0.8.3 stdio installations. Generating a connector does not stop an experiment or change a driver. Upgrade the service itself when it is idle.
- Windows, macOS and Linux archives still include the runtime Python and Agent dependencies for x86_64 and ARM64.

中文：0.8.4 可按实验室名称生成四种宿主的安装包与通用 MCP 设置。更新连接器不重启仪器服务。云端宿主可通过单独的 HTTP MCP 网关接入。

[中文安装说明](https://github.com/Cherish0925/AI4Instruments/blob/main/iop/connect/README.zh-CN.md) · [Installation guide](https://github.com/Cherish0925/AI4Instruments/blob/main/iop/connect/README.md)
