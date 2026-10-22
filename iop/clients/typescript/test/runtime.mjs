import test from 'node:test';
import assert from 'node:assert/strict';
import {spawn, execFileSync} from 'node:child_process';
import {mkdtemp, readFile, writeFile, rm} from 'node:fs/promises';
import {tmpdir} from 'node:os';
import {join, resolve} from 'node:path';
import {fileURLToPath} from 'node:url';
import {IOP} from '../dist/index.js';

test('TypeScript experiment package calls the running service and streams results', {timeout:30000}, async()=>{
  const root = fileURLToPath(new URL('../../../../', import.meta.url));
  const home = await mkdtemp(join(tmpdir(),'iop-typescript-'));
  const python = process.env.IOP_TEST_PYTHON || 'python3';
  const env = {...process.env, PYTHONPATH:join(root,'src')};
  let child, client;
  try {
    const program = `import {IOP} from './iop.mjs';
const client = new IOP(process.env.IOP_ENDPOINT, process.env.IOP_TOKEN);
const run = client.run(process.env.IOP_RUN_ID);
const result = await run.invoke('stage','position');
await run.upload('samples.bin',new Blob([new Uint8Array(1048577).fill(42)]));
await run.saveResult({angle:result.angle_actual});
`;
    await writeFile(join(home,'experiment.mjs'),program);
    await writeFile(join(home,'iop.mjs'),await readFile(new URL('../dist/index.js', import.meta.url)));
    execFileSync(python,['-c',`import json,zipfile,sys
from pathlib import Path
p=Path(sys.argv[1])
with zipfile.ZipFile(p/'package.zip','w') as z:
 z.writestr('package.json',json.dumps({'command':['node','experiment.mjs']}))
 for name in ('experiment.mjs','iop.mjs'): z.write(p/name,name)
`,home],{env});
    child = spawn(python,['-u','-c',`import sys
from ai4instruments.iop.config import initialize,save_json,home_path
from ai4instruments.iop.cli import serve
p=home_path(sys.argv[1]); c=initialize(p,True,0);c['discovery_interval']=0;save_json(p/'config.json',c)
serve(p)
`,home],{env,stdio:['ignore','pipe','pipe']});
    let errors = '';
    child.stderr.on('data',data=>{errors += data.toString();});
    const endpoint = await new Promise((resolve,reject)=>{
      let output = '';
      child.stdout.on('data',data=>{output += data.toString(); const found=output.match(/http:\/\/127\.0\.0\.1:\d+/);if(found)resolve(found[0]);});
      child.once('exit',code=>reject(Error('Service exited: '+code+' '+errors)));
    });
    const config = JSON.parse(await readFile(join(home,'config.json'),'utf8'));
    client = new IOP(endpoint,config.token);
    await client.configureResources({cpu:4});
    assert.ok((await client.adapters()).some(item=>item.name==='command'));
    const run = await client.submitPackage(new Uint8Array(await readFile(join(home,'package.zip'))),{resources:['stage']});
    assert.deepEqual(await run.result(),{angle:0});
    const file = (await run.files()).find(item=>item.name==='output/samples.bin');
    assert.equal(file.size,1048577);
    const response = await run.download(file.id);
    const bytes = new Uint8Array(await response.arrayBuffer());
    assert.equal(bytes.length,1048577); assert.equal(bytes[bytes.length-1],42);
    const events=[]; for await (const event of run.watch()) events.push(event);
    assert.ok(events.some(event=>event.kind==='operation.completed'));
    assert.ok(events.some(event=>event.kind==='run.completed'));
  } finally {
    if (client) await client.request('/v1/shutdown',{}).catch(()=>{});
    if (child && child.exitCode===null) await new Promise(resolve=>{
      const timer=setTimeout(()=>child.kill(),3000);
      child.once('exit',()=>{clearTimeout(timer);resolve();});
    });
    await rm(home,{recursive:true,force:true});
  }
});
