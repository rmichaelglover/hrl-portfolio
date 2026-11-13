/* Michael Emanuel Glover's shared C++ motion kernel, live in the existing Glims. */
'use strict';
window.GlimsMotion=(()=>{
let kernel=null,turn=0,error=null,profile=null,last={engine:'Loading C++',moves:0,yields:0,rosePauses:0,examined:0};
const ready=Promise.all([fetch('glims-motion.wasm').then(r=>{if(!r.ok)throw Error('C++ kernel unavailable');return r.arrayBuffer();}).then(b=>WebAssembly.instantiate(b,{})),fetch('peaceful-garden/chess-profile.json').then(r=>{if(!r.ok)throw Error('Chess profile unavailable');return r.json();})]).then(([m,p])=>{kernel=m.instance.exports;profile=p;last.engine='Live C++ · WebAssembly';return true;}).catch(e=>{error=e.message;last.engine='Movement paused · '+error;return false;});
function swept(a,b,c,d){const x=a.x-c.x,z=a.z-c.z,vx=b.x-a.x-d.x+c.x,vz=b.z-a.z-d.z+c.z,vv=vx*vx+vz*vz,t=vv?Math.max(0,Math.min(1,-(x*vx+z*vz)/vv)):0;return Math.hypot(x+t*vx,z+t*vz);}
function segmentFree(a,b,terrain){const length=Math.hypot(b.x-a.x,b.z-a.z),n=Math.max(1,Math.ceil(length/.025));for(let i=1;i<=n;i++)if(!terrain(a.x+(b.x-a.x)*i/n,a.z+(b.z-a.z)*i/n))return false;return true;}
function step(agents,neighbors,dt,terrain){
 if(!kernel)return {feasible:false,pending:!error,positions:agents.map(a=>({x:a.x,z:a.z})),selected:[]};
 const weights=profile.weights,choices=[];
 kernel.reset_motion(agents.length,neighbors.length);
 agents.forEach((a,i)=>{
  const p={x:a.x,z:a.z},n=a.next||p,dx=n.x-p.x,dz=n.z-p.z,d=Math.hypot(dx,dz),length=Math.min(d,dt*(a.speed||1)),moving=d>1e-7&&length>0;
  const desired=moving?{x:p.x+dx/d*length,z:p.z+dz/d*length}:p;
  const rose=!!a.rosePause;
  const progress=(a.progress??weights.progress),anticipation=(a.anticipation??weights.anticipation),clearance=a.clearance||.43;
  const options=[{...desired,utility:moving?progress*(1+Math.min(a.waited||0,8)*.15):rose?weights.roses*(a.roseInterest??1):0,allowed:!moving||segmentFree(p,desired,terrain)},
   {...p,utility:moving?-.04-Math.min(a.waited||0,8)*.1:rose?weights.roses*(a.roseInterest??1):0,allowed:true}];
  if(moving&&!a.manual)for(const sign of [-1,1]){const q={x:p.x-dz/d*length*sign,z:p.z+dx/d*length*sign};options.push({...q,utility:-.08,allowed:segmentFree(p,q,terrain)});}
  choices.push(options);kernel.set_person(i,p.x,p.z,clearance,progress,anticipation,weights.roses);
  options.forEach((q,j)=>kernel.set_choice(i,j,q.x,q.z,q.utility,+q.allowed));
 });
 neighbors.forEach((n,i)=>kernel.set_neighbor(i,n.x,n.z,n.nx??n.x,n.nz??n.z,n.clearance||.4));
 const feasible=!!kernel.decide_motion(turn++);last.examined=kernel.examined_motion();
 const selected=agents.map((_,i)=>feasible?kernel.selected_motion(i):-1);
 const positions=agents.map((a,i)=>{const q=selected[i]>=0?choices[i][selected[i]]:a;const moving=Math.hypot(q.x-a.x,q.z-a.z)>1e-8;if(moving)last.moves++;else if(a.next&&Math.hypot(a.next.x-a.x,a.next.z-a.z)>1e-6)last.yields++;return {x:q.x,z:q.z};});
 return {feasible,positions,selected};
}
function noteRose(){last.rosePauses++;}
return {ready,step,swept,segmentFree,noteRose,status:()=>({...last,profile:profile?{games:profile.games.length,plies:profile.plies}:null}),loaded:()=>!!kernel};
})();

fetch('native-household.json').then(r=>{if(!r.ok)throw Error();return r.json();}).then(s=>{const a=s.people.find(p=>p.name==='Alex');document.getElementById('native-person-summary').textContent=`Native Alex snapshot: ${a.organs} modeled organs, ${a.eyes} eyes, ${a.molecules} symbolic molecular record in the owned cell hierarchy; ${a.movement_experiences} recorded joint-movement experience. The same kernel coordinates this rendered household.`;}).catch(()=>{document.getElementById('native-person-summary').textContent='The native body snapshot is unavailable. The full model remains linked below.';});
