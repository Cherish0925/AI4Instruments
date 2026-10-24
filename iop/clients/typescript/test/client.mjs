import test from 'node:test';
import assert from 'node:assert/strict';
import {createServer} from 'node:http';
import {IOP} from '../dist/index.js';

test('retains platform, request identity, and reconnects to an accepted run',async()=>{
  const received=[];let events=0;
  const server=createServer(async(req,res)=>{
    assert.equal(req.headers.authorization,'Bearer example');
    let text='';for await(const chunk of req)text+=chunk;
    received.push({path:req.url,body:text?JSON.parse(text):null});
    res.setHeader('Content-Type','application/json');
    if(req.method==='POST')res.end(JSON.stringify({id:'run-1',state:'queued'}));
    else if(req.url.startsWith('/v1/events')){events++;res.end(JSON.stringify({events:events===1?[{sequence:7,kind:'run.completed',run_id:'run-1'}]:[],cursor:7}));}
    else if(req.url === '/v1/runs/run-1/result')res.end(JSON.stringify({read:{value:42}}));
    else res.end(JSON.stringify({id:'run-1',state:'completed',result:{read:{value:42}}}));
  });
  await new Promise(resolve=>server.listen(0,'127.0.0.1',resolve));
  try{
    const endpoint='http://127.0.0.1:'+server.address().port;
    const client=new IOP(endpoint,'example');
    const run=await client.submit([{id:'read',device:'meter',operation:'measure'}],{platform:'bench',request_id:'experiment-1'});
    assert.equal(received[0].body.platform,'bench');assert.equal(received[0].body.request_id,'experiment-1');
    assert.deepEqual(await new IOP(endpoint,'example').run(run.id).result(),{read:{value:42}});
    const stream=[];for await(const event of run.watch(6))stream.push(event);
    assert.equal(stream[0].sequence,7);assert.ok(received.some(r=>r.path.includes('after=7')));
  }finally{await new Promise(resolve=>server.close(resolve));}
});
