/* State lives on maximal cells; adjacency is shared codimension-one facets. */
(function(root){
'use strict';
const permutations=[[0,1,2],[0,2,1],[1,0,2],[1,2,0],[2,0,1],[2,1,0]];
function mesh(kind,n){
 const dim=['cube','tetra'].includes(kind)?3:2,cells=[],vertices=[],lookup=new Map();
 function vertex(p){const key=p.join(',');if(!lookup.has(key)){lookup.set(key,vertices.length);vertices.push(p);}return lookup.get(key);}
 function add(points,faces,base){const ids=points.map(vertex);cells.push({ids,faces:faces.map(f=>f.map(i=>ids[i])),base,center:[0,1,2].map(k=>points.reduce((s,p)=>s+p[k],0)/points.length)});}
 for(let z=0;z<(dim===3?n:1);z++)for(let y=0;y<n;y++)for(let x=0;x<n;x++){
  const base=[x,y,z];
  if(dim===2){const p=[[x,y,0],[x+1,y,0],[x+1,y+1,0],[x,y+1,0]];
   if(kind==='triangle'){add([p[0],p[1],p[2]],[[0,1],[1,2],[2,0]],base);add([p[0],p[2],p[3]],[[0,1],[1,2],[2,0]],base);}
   else add(p,[[0,1],[1,2],[2,3],[3,0]],base);
  }else if(kind==='tetra'){
   for(const order of permutations){const p=[[x,y,z]],q=[x,y,z];for(const axis of order){q[axis]++;p.push([...q]);}add(p,[[0,1,2],[0,1,3],[0,2,3],[1,2,3]],base);}
  }else add([[x,y,z],[x+1,y,z],[x+1,y+1,z],[x,y+1,z],[x,y,z+1],[x+1,y,z+1],[x+1,y+1,z+1],[x,y+1,z+1]],[[0,1,2,3],[4,5,6,7],[0,1,5,4],[1,2,6,5],[2,3,7,6],[3,0,4,7]],base);
 }
 const facets=new Map(),neighbors=cells.map(()=>[]);
 cells.forEach((c,i)=>c.faces.forEach(face=>{const key=[...face].sort((a,b)=>a-b).join(',');if(!facets.has(key))facets.set(key,[]);facets.get(key).push(i);}));
 for(const owners of facets.values()){if(owners.length>2)throw Error('Non-manifold facet');if(owners.length===2){const [a,b]=owners;neighbors[a].push(b);neighbors[b].push(a);}}
 return {kind,n,dim,cells,vertices,neighbors,facets};
}
function hash(x,y,z,seed){let h=Math.imul(x+17,374761393)^Math.imul(y+29,668265263)^Math.imul(z+43,1274126177)^Math.imul(seed,1597334677);h=Math.imul(h^(h>>>13),1274126177);return ((h^(h>>>16))>>>0)/4294967296;}
function initial(m,pattern,seed,rule){return Uint8Array.from(m.cells,c=>{
 const [x,y,z]=c.base,n=m.n,r=hash(x,y,z,seed);
 if(pattern==='random')return rule==='cyclic'?Math.floor(r*3):+(r<.34);
 const dist=Math.hypot(x+.5-n/2,y+.5-n/2,m.dim===3?z+.5-n/2:0);
 return +(pattern==='center'?dist<n*.22:x===Math.floor(n/2));
});}
function evolve(m,state,rule,threshold){const next=new Uint8Array(state.length);let changed=0;
 for(let i=0;i<state.length;i++){const list=m.neighbors[i],degree=list.length;let target=rule==='cyclic'?(state[i]+1)%3:1;const count=list.reduce((s,j)=>s+(state[j]===target),0);const fraction=degree?count/degree:0;
  if(rule==='cyclic')next[i]=degree&&count>0&&fraction>=threshold?target:state[i];
  else if(rule==='wave')next[i]=state[i]===1?2:state[i]===2?0:degree&&count>0&&fraction>=threshold?1:0;
  else next[i]=degree&&fraction>=threshold?1:0;
  changed+=next[i]!==state[i];
 }return {state:next,changed};}
const api={mesh,initial,evolve};if(typeof module!=='undefined')module.exports=api;root.CellComplex=api;
})(typeof globalThis!=='undefined'?globalThis:this);
