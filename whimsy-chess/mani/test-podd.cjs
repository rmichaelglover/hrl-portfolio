const assert=require('node:assert/strict'),P=require('./podd.js'),E=require('./engine.js'),{dispatch}=require('./podd-node.cjs');
(async()=>{
 const c=E.example(),b=await P.create(c);assert.equal(b.receipt.receiptId,'dab824621b19df0909fbd419e9690db7198ed5097a8c4810e58ec375a02ccae2','Arithmetic/canonicalization regression vector');
 assert.equal((await P.verifyFull(b)).status,'full-replay-verified');assert.equal(b.states.length,41);
 for(const state of b.states)for(const row of state)assert.equal(row.map(BigInt).reduce((a,b)=>a+b,0n),1000000n);
 const renamed={...c,id:'different display name',nodes:c.nodes.map(n=>({...n,truth:1-n.truth}))};assert.equal((await P.create(renamed)).receipt.challengeId,b.receipt.challengeId,'Display name and evaluation labels cannot create a new computational identity');
 assert.notEqual((await P.create({...c,damping:.5})).receipt.challengeId,b.receipt.challengeId);
 assert.notEqual((await P.create({...c,iterations:39})).receipt.challengeId,b.receipt.challengeId);
 assert.equal(P.canonical({b:1,a:2}),P.canonical({a:2,b:1}));
 const seed='ab'.repeat(32),indices=await P.sampleIndices(b.receipt,seed,5);assert.equal(new Set(indices).size,5);assert.deepEqual(await P.sampleIndices(b.receipt,seed,5),indices);
 const audit=await P.makeAudit(b,indices);assert.equal((await P.verifyAudit(audit,indices)).status,'sampled-transitions-consistent');
 const all=Array.from({length:40},(_,i)=>i);assert.equal((await P.verifyAudit(await P.makeAudit(b,all),all)).status,'all-transitions-verified');
 for(const mutate of [x=>x.receipt.finalStateHash='0'.repeat(64),x=>x.challenge.damping='1',x=>x.states[1][0]=['500000','500000']]){const bad=structuredClone(b);mutate(bad);await assert.rejects(()=>P.verifyFull(bad));}
 for(const mutate of [x=>x.transitions[0].before.siblings[0]='0'.repeat(64),x=>x.transitions[0].before.iteration=1,x=>x.initial.state[0]=['500000','500000'],x=>x.final.state[0]=['500000','500000']]){const bad=structuredClone(audit);mutate(bad);await assert.rejects(()=>P.verifyAudit(bad,indices));}
 await assert.rejects(()=>P.verifyAudit(audit,[...indices.slice(0,-1),indices[0]]));
 await assert.rejects(()=>P.sampleIndices(b.receipt,seed,41));await assert.rejects(()=>P.sampleIndices(b.receipt,'bad',5));
 // Demonstrate why a correct suffix does not certify its checkpoint's origin.
 const falseStates=structuredClone(b.states);falseStates[1][0]=['500000','500000'];for(let i=1;i<40;i++)falseStates[i+1]=P.step(b.challenge,falseStates[i]);
 const forged=await P.commit(b.challenge,falseStates);await assert.rejects(()=>P.verifyFull(forged),/step 0/);
 assert.equal((await P.verifyAudit(await P.makeAudit(forged,[39]),[39])).status,'sampled-transitions-consistent');
 await assert.rejects(async()=>P.verifyAudit(await P.makeAudit(forged,[0]),[0]),/step 0/);
 const isolated=await P.create({...c,edges:[]});assert.deepEqual(isolated.states[0],isolated.states.at(-1));await P.verifyFull(isolated);
 const zero=await P.create({...c,edges:c.edges.map(e=>({...e,compatibility:[[0,0],[0,0]]}))});assert.deepEqual(zero.states[0],zero.states.at(-1));
 const tiny={...c,edges:c.edges.map(e=>({...e,weight:1e-9}))};await assert.rejects(()=>P.create(tiny),/quantized to zero/);
 const asymmetric={...c,edges:c.edges.map(e=>({...e,compatibility:[[1,.2],[.8,.7]]}))},a=await P.create(asymmetric),rev=await P.create({...asymmetric,edges:asymmetric.edges.map(e=>({...e,source:e.target,target:e.source,compatibility:e.compatibility[0].map((_,i)=>e.compatibility.map(row=>row[i]))}))});assert.deepEqual(a.states,rev.states);
 assert.equal((await dispatch({jsonrpc:'2.0',id:1,method:'podd_verify',params:{bundle:b}})).result.status,'full-replay-verified');
 assert.equal((await dispatch({jsonrpc:'2.0',id:2,method:'unknown',params:{}})).error.code,-32601);assert.equal((await dispatch([])).error.code,-32600);
 console.log('PoDD passed: golden vector, fixed-point sums, content identity, Merkle openings, seed selection, full replay, sampled audits, tamper rejection, forged-prefix counterexample, zero-support behavior, transpose invariance, RPC routing.');
})().catch(e=>{console.error(e);process.exitCode=1;});
