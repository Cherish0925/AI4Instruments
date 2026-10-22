# IOP TypeScript client

Requires Node.js 20+ or a browser with Fetch, AbortSignal.timeout and crypto.randomUUID. Build from source with `npm ci && npm run build`; install a release archive with `npm install ./ai4instruments-iop-0.4.0.tgz`.

```typescript
import { IOP } from '@ai4instruments/iop';
const lab = new IOP('http://127.0.0.1:8765', process.env.IOP_TOKEN);
console.log(await lab.platforms());
const run = await lab.submit([
  {id:'read', device:'meter', operation:'measure'}
], {platform:'materials-bench'});
console.log(await run.result());
```

`Run.wait({signal})` stops waiting when its signal is aborted. Use `Run.cancel()` to request cancellation of the experiment itself. `Run.watch(cursor)` resumes ordered event retrieval. The Python SDK remains available for experiment-package upload and file management; the TypeScript client currently covers platform setup, operations, runs and events.
