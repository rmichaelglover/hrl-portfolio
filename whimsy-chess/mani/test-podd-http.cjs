const assert=require('node:assert/strict'),{server}=require('./podd-node.cjs'),E=require('./engine.js');
(async()=>{const s=server();await new Promise(resolve=>s.listen(0,'127.0.0.1',resolve));const url='http://127.0.0.1:'+s.address().port+'/rpc';try{
 async function call(method,params){const response=await fetch(url,{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({jsonrpc:'2.0',id:1,method,params})});assert.equal(response.status,200);return response.json();}
 const b=(await call('podd_create',{challenge:E.example()})).result;assert.equal((await call('podd_verify',{bundle:b})).result.status,'full-replay-verified');
 const seed='12'.repeat(32),selection=(await call('podd_sample',{receipt:b.receipt,seed,count:3})).result,audit=(await call('podd_open',{bundle:b,indices:selection.indices})).result;
 assert.equal((await call('podd_verifyAudit',{audit,expectedIndices:selection.indices})).result.status,'sampled-transitions-consistent');
 assert.equal((await fetch(url,{method:'POST',headers:{'Content-Type':'application/json',Origin:'https://example.com'},body:'{}'})).status,403);
 assert.equal((await fetch(url)).status,404);assert.equal((await fetch(url,{method:'POST',body:'{}'})).status,415);
 const invalid=await fetch(url,{method:'POST',headers:{'Content-Type':'application/json'},body:'{'});assert.equal(invalid.status,400);assert.equal((await invalid.json()).error.code,-32700);
 assert.equal((await call('podd_sample',{receipt:{...b.receipt,iterations:1000000000},seed,count:3})).error.code,-32602);
 console.log('HTTP passed: all five RPC methods, browser-origin rejection, method/content-type checks, parse errors, bounded sample input.');
 }finally{await new Promise(resolve=>s.close(resolve));}})().catch(e=>{console.error(e);process.exitCode=1;});
