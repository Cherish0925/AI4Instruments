# IOP TypeScript client

Requires Node.js 20+ or a browser with Fetch, AbortSignal.timeout and crypto.randomUUID. Build from source with `npm ci && npm run build`; install a release archive with `npm install ./ai4instruments-iop-0.8.1.tgz`.

```typescript
import { IOP } from '@ai4instruments/iop';
const lab = new IOP('http://127.0.0.1:8765', process.env.IOP_TOKEN);
console.log(await lab.platforms());
const run = await lab.submit([
  {id:'read', device:'meter', operation:'measure'}
], {platform:'materials-bench'});
console.log(await run.result());
```

`Run.wait({signal})` stops waiting when its signal is aborted. Use `Run.cancel()` to request cancellation of the experiment itself. `Run.watch(cursor)` resumes ordered event retrieval. Both clients support platform setup, operations, experiment packages, events, results and files. `lab.submitPackage(bytes, options)` uploads a ZIP; `run.invoke()` issues an operation from an already-running experiment package; `run.saveResult(value)` saves its result. `run.upload(name, blob)` streams a file and `run.download(id)` returns a Fetch response whose body can be streamed. `run.operations(cursor, limit)` pages through persistent history.

`lab.configureResources({cpu:16, solver:2})` sets capacities; a workflow step or submission can declare `requirements`. Steps can use `bindings` to transfer a previous result into an argument. `lab.adapters()` lists installed drivers and `lab.reconnect(device)` reconnects an idle device.

The integration test uploads a Node.js experiment package to an actual IOP service, calls an instrument operation, uploads a binary file and reads its result and events.
