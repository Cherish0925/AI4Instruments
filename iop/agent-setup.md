# Agent setup / Agent 配置实验平台

[IOP](README.md) · [中文](README.zh-CN.md) · [Platform schema](schema/platform.schema.json) · [HTTP API](../docs/runtime/http-api.md)

Codex, Claude Code, DeepSeek Harness, Qiushi Engine and other clients can use the same CLI, HTTP API or SDK. The service operates independently of the chosen model or harness. This guide describes the available interface; it does not claim a separately published plugin for each product.

1. Connect to the instrument computer's service. Read `/v1/status`, `/v1/devices`, `/v1/discovery` and `/v1/platforms`.
2. Match discovered connections to instrument models, documentation and installed drivers. Register usable devices. An enumerated USB port does not identify the full operation set.
3. Read the actual platform wiring and experiment requirements. Create a platform description containing device IDs, port connections, shared physical resources and initialization procedures. Ask the operator for physical connections that cannot be observed electronically.
4. Preview the description with `POST /v1/platforms/preview`. Save it with `POST /v1/platforms` and the current `expected_revision` (0 for a new platform).
5. Submit the `initialize` procedure when its actions are intended. Query the resulting run and readings. Saving a configuration does not invoke it.
6. Submit an experiment with `platform`, `steps` and the resources to retain across steps, or upload a package. Keep its `run_id`; query or reconnect later. Reuse `request_id` when retrying the same submission.

人或 Agent 首次接入时，需要将可见设备、实际接线、仪器说明与实验要求对应起来。USB/串口扫描通常无法获知样品、光路、管路或触发线的实际连接。已有配置可以直接读取与复用，不必每次实验重新配置。

云端 Agent 使用可达的服务地址，读取并保留运行编号；长实验交给服务运行。本地或远端的客户端关闭后，已经受理的实验继续。更换模型或 Harness 不要求重新打开仪器连接。

## Python

```python
import json
from pathlib import Path
from ai4instruments.iop import Client
lab = Client()  # IOP_ENDPOINT and IOP_TOKEN can select a remote service.
definition = json.loads(Path('platform.json').read_text())
lab.request('/v1/platforms/preview', {'definition': definition})
platform = lab.configure_platform(definition, expected_revision=0)
run = lab.procedure(platform['id'], 'initialize')
print(run.id, run.result())
```

## TypeScript

Build or install the packaged client from [clients/typescript](clients/typescript/). The package has no runtime dependencies and uses the standard Fetch API.

```typescript
import { IOP } from '@ai4instruments/iop';
const lab = new IOP(process.env.IOP_ENDPOINT, process.env.IOP_TOKEN);
const platforms = await lab.platforms();
const run = await lab.submit([
  { id: 'read', device: 'meter', operation: 'measure' }
], { platform: 'materials-bench' });
console.log(run.id);
console.log(await run.result());
```

Remote connections must reach the instrument service; the default listener is local to its computer. Configure the service's `host` and its existing connection token for the laboratory network, or use the laboratory's existing remote connection. No cloud account is required to run IOP locally.
