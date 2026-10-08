/* The existing lab update, with observable intermediate values. No truth labels here. */
(function(root){
  'use strict';
  function traceStep(st){
    const before=st.S.map(row=>row.slice()),L=before[0].length;
    const raw=before.map(()=>Array(L).fill(0));
    for(const [i,k] of st.edges){
      for(let j=0;j<L;j++)for(let l=0;l<L;l++){
        raw[i][j]+=st.C[j][l]*before[k][l];
        raw[k][l]+=st.C[j][l]*before[i][j];
      }
    }
    const support=raw.map(row=>{const lo=Math.min(...row),span=Math.max(...row)-lo;return row.map(v=>span>0?(v-lo)/span:0);});
    const base=before.map((row,i)=>row.map((s,j)=>Math.pow(st.prior[i][j],st.ps)*Math.pow(s,1-st.ps)));
    const updated=base.map((row,i)=>row.map((v,j)=>v*(1+support[i][j])));
    const sums=updated.map(row=>row.reduce((a,b)=>a+b,0));
    const after=updated.map((row,i)=>row.map(v=>v/(sums[i]||1)));
    const delta=after.map((row,i)=>row.map((v,j)=>v-before[i][j]));
    return {before,raw,support,base,sums,after,delta,maxDelta:Math.max(...delta.flat().map(Math.abs))};
  }
  function nearestSeed(pixels,seeds,prior){
    return pixels.map(p=>{let best=Infinity,pick=-1;for(const i of seeds){const distance=p.reduce((sum,v,k)=>sum+(v-pixels[i][k])**2,0);if(distance<best){best=distance;pick=i;}}return {seed:pick,distance:Math.sqrt(best),label:prior[pick].indexOf(Math.max(...prior[pick]))};});
  }
  const api={traceStep,nearestSeed};
  if(typeof module!=='undefined'&&module.exports)module.exports=api;else root.LabRelaxation=api;
})(typeof globalThis!=='undefined'?globalThis:this);
