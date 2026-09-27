/* Prior-respecting sparse relaxation, extending the local contractive.py idea.
 * Independent binary theme channels: not a partition of people or cultures.
 * Hierarchy pools cards to theme hubs; explicit triples supply joint support.
 * Strengths are editorial affinity scores, not calibrated truth probabilities.
 */
(function(root){
function run(cards,{triangles=true,iterations=60}={}){
 const prior=cards.map(c=>c.themes.map(v=>v?.85:.15));let p=prior.map(r=>r.slice());
 const edges=[];for(let i=0;i<cards.length;i++)for(let j=i+1;j<cards.length;j++){
 const shared=cards[i].themes.map((v,t)=>v&&cards[j].themes[t]?t:-1).filter(t=>t>=0);
 if(shared.length)edges.push({a:i,b:j,themes:shared});
 }
 // An editorial three-way comparison: food, welcome, and gathering in three practices.
 const ids=['couscous','kimjang','bunya'];const triple=ids.map(id=>cards.findIndex(c=>c.id===id));
 const simplices=triple.every(i=>i>=0)?[{nodes:triple,theme:1,reason:'Three documented food-sharing or gathering practices; thematic comparison only.'}]:[];
 let delta=0,step=0;const history=[];
 for(;step<iterations;step++){
 const hubs=[0,1,2].map(t=>p.reduce((s,row)=>s+row[t],0)/p.length);
 const next=p.map((row,i)=>row.map((v,t)=>{
 const neighbors=edges.filter(e=>e.themes.includes(t)&&(e.a===i||e.b===i)).map(e=>p[e.a===i?e.b:e.a][t]);
 const msgs=neighbors.map(x=>2*x-1);if(cards[i].themes[t])msgs.push(2*hubs[t]-1);
 if(triangles)for(const f of simplices)if(f.theme===t&&f.nodes.includes(i))msgs.push(2*f.nodes.filter(j=>j!==i).reduce((a,j)=>a*p[j][t],1)-1);
 const support=msgs.length?msgs.reduce((a,b)=>a+b,0)/msgs.length:0;
 return 1/(1+Math.exp(-(Math.log(prior[i][t]/(1-prior[i][t]))+.6*support)));
 }));
 delta=Math.max(...next.flatMap((r,i)=>r.map((v,t)=>Math.abs(v-p[i][t]))));p=next;history.push(delta);if(delta<1e-8){step++;break;}
 }
 return {strengths:p,edges,simplices,iterations:step,delta,converged:delta<1e-8,history};
}
root.AtlasEngine={run};if(typeof module!=='undefined')module.exports=root.AtlasEngine;
})(globalThis);
