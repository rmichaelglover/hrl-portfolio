/* Michael Glover's Maestro / Mani research workspace. */
(function(root,factory){const api=factory();if(typeof module==='object'&&module.exports)module.exports=api;else root.ManiEngine=api;})(globalThis,function(){
'use strict';
const VERSION='maestro-mani-1';
function validate(x){
 const fail=m=>{throw Error(m);};
 if(!x||typeof x!=='object')fail('Expected a challenge object.');
 if(typeof x.id!=='string'||!x.id.trim()||x.id.length>100)fail('Provide a challenge id (1–100 characters).');
 if(!Array.isArray(x.labels)||x.labels.length<2||x.labels.length>16||x.labels.some(v=>typeof v!=='string'||!v||v.length>60)||new Set(x.labels).size!==x.labels.length)fail('Provide 2–16 distinct label names.');
 if(!Array.isArray(x.nodes)||x.nodes.length<2||x.nodes.length>128)fail('Provide 2–128 nodes.');
 const ids=new Set();
 for(const n of x.nodes){
  if(!n||typeof n.id!=='string'||!n.id||n.id.length>80||ids.has(n.id))fail('Node ids must be distinct, nonempty strings.');ids.add(n.id);
  if(!Array.isArray(n.prior)||n.prior.length!==x.labels.length||n.prior.some(v=>!Number.isFinite(v)||v<0||v>1)||Math.abs(n.prior.reduce((a,b)=>a+b,0)-1)>1e-6)fail('Each prior must be a probability vector summing to 1.');
  if(n.truth!==undefined&&(!Number.isInteger(n.truth)||n.truth<0||n.truth>=x.labels.length))fail('Truth labels must be valid label indices.');
 }
 if(!Array.isArray(x.edges)||x.edges.length>2048)fail('Provide at most 2048 edges.');
 const seen=new Set();
 for(const e of x.edges){
  if(!e||!ids.has(e.source)||!ids.has(e.target)||e.source===e.target)fail('Edges must join two different known nodes.');
  const key=JSON.stringify([e.source,e.target].sort());if(seen.has(key))fail('Duplicate undirected edge.');seen.add(key);
  if(!Number.isFinite(e.weight)||e.weight<=0||e.weight>10)fail('Edge weights must be in (0, 10].');
  if(!Array.isArray(e.compatibility)||e.compatibility.length!==x.labels.length||e.compatibility.some(row=>!Array.isArray(row)||row.length!==x.labels.length||row.some(v=>!Number.isFinite(v)||v<0||v>10)))fail('Each edge needs a nonnegative label-by-label compatibility matrix (entries ≤10).');
 }
 if(!Number.isInteger(x.iterations)||x.iterations<1||x.iterations>100)fail('Iterations must be 1–100.');
 if(!Number.isFinite(x.damping)||x.damping<0||x.damping>1)fail('Damping must be between 0 and 1.');
 // Retain only specified fields: unknown metadata cannot alter the solver or receipt.
 return {id:x.id,labels:[...x.labels],nodes:x.nodes.map(n=>({id:n.id,prior:[...n.prior],...(n.truth===undefined?{}:{truth:n.truth})})),edges:x.edges.map(e=>({source:e.source,target:e.target,weight:e.weight,compatibility:e.compatibility.map(row=>[...row])})),iterations:x.iterations,damping:x.damping};
}
const argmax=v=>v.indexOf(Math.max(...v));
function accuracy(c,p){const known=c.nodes.map((n,i)=>n.truth===undefined?null:Number(argmax(p[i])===n.truth)).filter(v=>v!==null);return known.length?known.reduce((a,b)=>a+b,0)/known.length:null;}
function consistency(c,p){const ix=new Map(c.nodes.map((n,i)=>[n.id,i]));let total=0,weight=0;for(const e of c.edges){const a=p[ix.get(e.source)],b=p[ix.get(e.target)];let v=0;for(let i=0;i<a.length;i++)for(let j=0;j<b.length;j++)v+=a[i]*e.compatibility[i][j]*b[j];total+=e.weight*v;weight+=e.weight;}return weight?total/weight:0;}
function run(input){
 const c=validate(input),index=new Map(c.nodes.map((n,i)=>[n.id,i])),neighbors=c.nodes.map(()=>[]);
 for(const e of c.edges){neighbors[index.get(e.source)].push({j:index.get(e.target),weight:e.weight,m:e.compatibility,transpose:false});neighbors[index.get(e.target)].push({j:index.get(e.source),weight:e.weight,m:e.compatibility,transpose:true});}
 let p=c.nodes.map(n=>[...n.prior]);const initial=p.map(v=>[...v]),trace=[];
 for(let t=0;t<c.iterations;t++){
  let delta=0;
  const next=p.map((v,i)=>{
   if(!neighbors[i].length)return [...v];
   const support=v.map((_,a)=>neighbors[i].reduce((s,e)=>s+e.weight*p[e.j].reduce((z,pb,b)=>z+pb*(e.transpose?e.m[b][a]:e.m[a][b]),0),0));
   const weighted=v.map((pa,a)=>pa*support[a]),sum=weighted.reduce((a,b)=>a+b,0);
   if(sum<=Number.EPSILON)return [...v];
   const mixed=v.map((pa,a)=>(1-c.damping)*pa+c.damping*weighted[a]/sum),norm=mixed.reduce((a,b)=>a+b,0);
   const out=mixed.map(v=>v/norm);delta=Math.max(delta,...out.map((x,a)=>Math.abs(x-v[a])));return out;
  });
  p=next;trace.push({iteration:t+1,delta,consistency:consistency(c,p)});if(delta<1e-10)break;
 }
 return {version:VERSION,probabilities:p,assignments:p.map(argmax),iterations:trace.length,trace,baselineConsistency:consistency(c,initial),finalConsistency:consistency(c,p),baselineAccuracy:accuracy(c,initial),finalAccuracy:accuracy(c,p)};
}
function allocation(total){if(!Number.isSafeInteger(total)||total<0)throw Error('Allocation requires a nonnegative safe integer.');const science=Math.floor(total/10),sanctuary=Math.floor(total/10);return {miner:total-science-sanctuary,science,sanctuary};}
function example(){const same=[[1,.08],[.08,1]];return {id:'synthetic-cell-neighborhood-01',labels:['State A','State B'],nodes:[{id:'cell-1',prior:[.9,.1],truth:0},{id:'cell-2',prior:[.35,.65],truth:0},{id:'cell-3',prior:[.85,.15],truth:0},{id:'cell-4',prior:[.1,.9],truth:1},{id:'cell-5',prior:[.6,.4],truth:1},{id:'cell-6',prior:[.15,.85],truth:1}],edges:[[0,1],[1,2],[0,2],[3,4],[4,5],[3,5]].map(([a,b])=>({source:'cell-'+(a+1),target:'cell-'+(b+1),weight:1,compatibility:same.map(r=>[...r])})),iterations:40,damping:.6};}
return {VERSION,validate,run,allocation,example};
});
