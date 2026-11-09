IOP Runtime 0.8.5 keeps an adaptive experiment, its instrument operations and acquired data together across client connections.

- Begin one external experiment from Python, TypeScript, MCP or CLI. Reservations span successive calls; explicit finish releases them. Reconnect through the same run ID and continue from saved progress after a service interruption.
- Submit operation batches with sequential defaults, explicit parallel branches, dependency joins and result bindings. Each operation retains its own result and configuration revision. Identical batch request IDs return existing operations.
- Save an acquisition directly from completed operations, their instrument configuration versions, declared conditions and analysis. Saving does not trigger a new measurement.
- Reuse HTTP connections and return short operations in the submission response. Dense programs need fewer client round trips.
- Read whole-quoted SCPI identity replies. Preserve unfamiliar replies without repeatedly treating them as communication failures.
- Release idle connections for another application, including shared SDK workers. Released devices remain released across discovery and service restarts. Reconnect from SDK, MCP, CLI or the instrument panel.
- Select a local TCP source address and query SCPI serial/VISA connection parameters through the adapter interface.

中文：连续实验共用一个编号；批量操作按依赖串并行；判断和保存引用同一次采集；仪器连接可以明确交接给其他软件。具体变化来自真实实验记录中的调用、数据关联、身份识别和连接反馈。

[中文使用说明](https://github.com/Cherish0925/AI4Instruments/blob/main/docs/runtime/external-experiments.zh-CN.md) · [Usage guide](https://github.com/Cherish0925/AI4Instruments/blob/main/docs/runtime/external-experiments.md) · [Calling-pattern measurements](https://github.com/Cherish0925/AI4Instruments/blob/main/iop/performance/README.md)

The software checks use simulated drivers and protocol servers. The original laboratory comparison has not been rerun with this release.
