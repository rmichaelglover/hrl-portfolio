/* Generic sparse relaxation labeling. No chess knowledge or fitted weights.
 * Adapted from the respected-prior update in python/hrl_generic/engine.py.
 * This small browser implementation supports pairwise factors and fixed evidence.
 */
(function(root){
'use strict';
function normalize(row){const s=row.reduce((a,b)=>a+b,0);if(!s||row.some(x=>!Number.isFinite(x)||x<0))throw Error('Invalid label strengths');return row.map(x=>x/s);}
function run({nodes,factors=[],priorStrength=.85,maxIterations=40,tolerance=1e-7}){
 if(!nodes.length)throw Error('Nodes required');
 if(!(priorStrength>=0&&priorStrength<=1))throw Error('Invalid prior strength');
 const n=nodes[0].prior.length,priors=nodes.map(o=>{if(o.prior.length!==n)throw Error('Label size mismatch');return normalize(o.prior);});
 for(const f of factors)if(!nodes[f.a]||!nodes[f.b]||f.matrix.length!==n||f.matrix.some(row=>row.length!==n||row.some(x=>!Number.isFinite(x))))throw Error('Invalid factor');
 let strengths=priors.map(x=>x.slice()),history=[strengths],converged=false,iterations=0;
 for(;iterations<maxIterations;){
  const support=nodes.map(()=>Array(n).fill(0));
  for(const f of factors)for(let a=0;a<n;a++)for(let b=0;b<n;b++){
   support[f.a][a]+=f.matrix[a][b]*strengths[f.b][b];support[f.b][b]+=f.matrix[a][b]*strengths[f.a][a];
  }
  const next=nodes.map((o,i)=>{
   if(o.fixed)return priors[i].slice();
   const lo=Math.min(...support[i]),span=Math.max(...support[i])-lo;
   return normalize(priors[i].map((p,j)=>Math.pow(p,priorStrength)*Math.pow(strengths[i][j],1-priorStrength)*(1+(span?(support[i][j]-lo)/span:0))));
  });
  const delta=Math.max(...next.flatMap((row,i)=>row.map((v,j)=>Math.abs(v-strengths[i][j]))));
  strengths=next;history.push(strengths);iterations++;if(delta<tolerance){converged=true;break;}
 }
 return {strengths,history,iterations,converged};
}
const api={run,normalize};root.TutorRelax=api;if(typeof module!=='undefined')module.exports=api;
})(globalThis);
