const assert=require('node:assert/strict');
const {mesh,initial,evolve}=require('./engine.js');
for(const [kind,count,max] of [['square',9,4],['rectangle',9,4],['triangle',18,3],['cube',27,6],['tetra',162,4]]){
 const m=mesh(kind,3);assert.equal(m.cells.length,count);assert.equal(Math.max(...m.neighbors.map(n=>n.length)),max);
 for(const [i,list] of m.neighbors.entries()){assert.equal(new Set(list).size,list.length);assert(!list.includes(i));for(const j of list)assert(m.neighbors[j].includes(i));}
 const boundary=[...m.facets.values()].filter(a=>a.length===1).length;
 assert.equal(boundary,m.dim===2?12:kind==='cube'?54:108);
 const visited=new Set([0]),queue=[0];for(let i=0;i<queue.length;i++)for(const j of m.neighbors[queue[i]])if(!visited.has(j)){visited.add(j);queue.push(j);}assert.equal(visited.size,count);
 if(kind==='tetra')for(const c of m.cells){const p=c.ids.map(i=>m.vertices[i]),v=p.slice(1).map(q=>q.map((x,k)=>x-p[0][k]));const [a,b,d]=v;const det=a[0]*(b[1]*d[2]-b[2]*d[1])-a[1]*(b[0]*d[2]-b[2]*d[0])+a[2]*(b[0]*d[1]-b[1]*d[0]);assert.equal(Math.abs(det),1);}
}
for(const rule of ['wave','cyclic','threshold']){
 const a=mesh('square',5),b=mesh('rectangle',5);let sa=initial(a,'random',42,rule),sb=initial(b,'random',42,rule);
 assert.deepEqual(initial(a,'random',42,rule),sa);
 for(let i=0;i<20;i++){sa=evolve(a,sa,rule,.3).state;sb=evolve(b,sb,rule,.3).state;assert.deepEqual(sa,sb);}
 for(const [kind,parent] of [['triangle','square'],['tetra','cube']]){const m=mesh(kind,3),p=mesh(parent,3),sp=initial(p,'random',42,rule),sm=initial(m,'random',42,rule),factor=kind==='triangle'?2:6;sm.forEach((v,i)=>assert.equal(v,sp[Math.floor(i/factor)]));}
}
const line={neighbors:[[1],[0,2],[1]]};
assert.deepEqual([...evolve(line,Uint8Array.from([1,0,0]),'wave',.5).state],[2,1,0]);
assert.deepEqual([...evolve(line,Uint8Array.from([0,1,2]),'cyclic',.5).state],[1,2,2]);
assert.deepEqual([...evolve(line,Uint8Array.from([1,0,1]),'threshold',.5).state],[0,1,0]);
console.log('Passed: mesh counts, shared-facet boundaries, symmetry, connectivity, tetra volumes, matched seeds, square/rectangle invariance, synchronous rule fixtures.');
