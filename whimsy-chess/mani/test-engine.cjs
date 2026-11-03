const assert=require('node:assert/strict');
const E=require('./engine.js');
const c=E.example(),r=E.run(c);
assert.equal(r.baselineAccuracy,4/6);assert.equal(r.finalAccuracy,1);assert.ok(r.finalConsistency>r.baselineConsistency);
for(const p of r.probabilities){assert.ok(p.every(v=>Number.isFinite(v)&&v>=0));assert.ok(Math.abs(p.reduce((a,b)=>a+b,0)-1)<1e-12);}
assert.deepEqual(E.run(c),r,'Replay must be deterministic');
const noEdges={...c,edges:[]};assert.deepEqual(E.run(noEdges).probabilities,c.nodes.map(n=>n.prior));
const zero={...c,edges:c.edges.map(e=>({...e,compatibility:[[0,0],[0,0]]}))};assert.deepEqual(E.run(zero).probabilities,c.nodes.map(n=>n.prior));
const paused={...c,damping:0};assert.deepEqual(E.run(paused).probabilities,c.nodes.map(n=>n.prior));
const transposed={...c,edges:c.edges.map(e=>({...e,source:e.target,target:e.source,compatibility:e.compatibility[0].map((_,i)=>e.compatibility.map(row=>row[i]))}))};assert.deepEqual(E.run(transposed),r);
assert.throws(()=>E.run({...c,nodes:[...c.nodes,c.nodes[0]]}));assert.throws(()=>E.run({...c,edges:[...c.edges,c.edges[0]]}));
assert.throws(()=>E.run({...c,iterations:Infinity}));assert.throws(()=>E.run({...c,nodes:c.nodes.map(n=>({...n,prior:[NaN,1]}))}));
for(const total of [0,1,9,10,99,100,10000,Number.MAX_SAFE_INTEGER]){const a=E.allocation(total);assert.equal(a.miner+a.science+a.sanctuary,total);assert.ok(Object.values(a).every(Number.isSafeInteger));}
assert.deepEqual(E.allocation(100),{miner:80,science:10,sanctuary:10});assert.throws(()=>E.allocation(-1));assert.throws(()=>E.allocation(1.5));
console.log('Passed: reproducibility, normalization, held-out synthetic labels, fallback behavior, transpose invariance, validation, allocation conservation.');
