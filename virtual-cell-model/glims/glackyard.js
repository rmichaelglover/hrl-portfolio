/* Michael Emanuel Glover's Glims × Tiny Creeks. Original canvas landscape. */
'use strict';
(()=>{
const $=id=>document.getElementById(id),canvas=$('yard-canvas'),ctx=canvas.getContext('2d'),world=window.glimsWorld;
const names=['Alex','Mama','Papa','Cypher','Rosy'],colors=['#8cb8a6','#ba93a5','#c4aa7f','#81a9b1','#c68f80'];
const spots={roses:{x:5.35,y:5.35},tea:{x:2.8,y:3.6},paint:{x:5.7,y:4.8},read:{x:3.6,y:1.9},bridge:{x:9,y:3.1},rest:{x:1.8,y:2}};
const key='glover-glims-glackyard-v1';let active=false,W=900,H=570,scale=1,ox=0,oy=0,last=0;
let selectedWildlife=null;
let state=fresh();
function fresh(){return {night:false,time:0,activity:null,elapsed:0,completed:false,path:[],people:names.map((name,i)=>({name,x:2+i*.5,y:5+i*.12,path:[]})),visits:0};}
function creek(y){return 7.45+Math.sin(y*1.25)*.38;}
function walkable(x,y){return x>=.5&&x<=11.5&&y>=.5&&y<=7.5&&(Math.abs(x-creek(y))>.64||(y>=3.35&&y<=4.15));}
function route(from,to){const available=(x,y)=>walkable(x,y)&&!state.people.some(p=>p!==from&&Math.hypot(p.x-x,p.y-y)<.46)&&!GlimsWildlife.positions(state.time,state.night,creek).some(a=>['frog','rodent','lizard'].includes(a.kind)&&Math.hypot(a.x-x,a.y-y)<.44);if(!available(to.x,to.y))return [];const cell=.2,cols=60,rows=40,idx=(x,y)=>Math.floor(y/cell)*cols+Math.floor(x/cell),start=idx(from.x,from.y),end=idx(to.x,to.y),q=[start],prev=new Map([[start,-1]]);for(let head=0;head<q.length;head++){const k=q[head];if(k===end)break;const x=k%cols,y=Math.floor(k/cols);for(const [dx,dy] of [[1,0],[-1,0],[0,1],[0,-1]]){const a=x+dx,b=y+dy,n=b*cols+a;if(a<0||b<0||a>=cols||b>=rows||prev.has(n)||!available((a+.5)*cell,(b+.5)*cell))continue;prev.set(n,k);q.push(n);}}if(!prev.has(end))return [];const path=[];for(let k=end;k!==start;k=prev.get(k))path.push({x:(k%cols+.5)*cell,y:(Math.floor(k/cols)+.5)*cell});path.reverse();path.push(to);return path;}
function move(p,dt){if(!p.path.length)return;const n=p.path[0],dx=n.x-p.x,dy=n.y-p.y,d=Math.hypot(dx,dy),step=dt*1.15;if(d<=step){p.x=n.x;p.y=n.y;p.path.shift();}else{p.x+=dx/d*step;p.y+=dy/d*step;}}
function go(kind){if(!spots[kind])return false;const path=route(state.people[0],spots[kind]);if(!path.length)return false;state.activity=kind;state.elapsed=0;state.completed=false;state.people.forEach(p=>{p.roseVisited=false;p.roseRemaining=0;});state.people[0].path=path;
 state.people.slice(1).forEach((p,i)=>{const s=spots[kind],target={x:s.x+(i%2?.6:-.6),y:s.y+.75+Math.floor(i/2)*.85};p.path=route(p,target);});
 $('yard-thought').textContent={tea:'Mama: I brought enough cups for everybody.',paint:'Alex: The creek never holds the same reflection for long.',read:'Papa: I saved a place under the canvas for you.',bridge:'Cypher: A little bridge makes a whole other side possible.',rest:'Rosy: The best expedition has excellent pillows.'}[kind]||'Alex: There is time for the roses, and room for everyone.';update();return true;}
function advanceYard(dt){
 const now=GlimsWildlife.positions(state.time,state.night,creek),future=GlimsWildlife.positions(state.time+dt,state.night,creek);
 const neighbors=now.filter(a=>['frog','rodent','lizard'].includes(a.kind)).map(a=>{const next=future.find(b=>b.id===a.id);return {x:a.x,z:a.y,nx:next.x,nz:next.y,clearance:.4};});
 const agents=state.people.map(p=>{
  if(p.roseRemaining>0)p.roseRemaining=Math.max(0,p.roseRemaining-dt);
  if(state.activity==='roses'&&!p.roseVisited&&Math.hypot(p.x-spots.roses.x,p.y-spots.roses.y)<1.9){p.roseVisited=true;p.roseRemaining=2;GlimsMotion.noteRose();}
  return {id:p.name,x:p.x,z:p.y,next:p.roseRemaining>0?null:p.path[0]?{x:p.path[0].x,z:p.path[0].y}:null,speed:1.15,waited:p.motionWait||0,rosePause:p.roseRemaining>0,roseInterest:p.name==='Alex'?.9:.7};
 });
 const result=GlimsMotion.step(agents,neighbors,dt,(x,z)=>walkable(x,z));
 if(!result.feasible){state.jointMotion={...GlimsMotion.status(),feasible:false};return;}
 state.time+=dt;world.outdoorTick(dt);
 state.people.forEach((p,i)=>{const q=result.positions[i],moved=Math.hypot(q.x-p.x,q.z-p.y)>1e-8;p.x=q.x;p.y=q.z;
  p.motionWait=agents[i].next&&!moved?(p.motionWait||0)+dt:0;
  if(p.path.length&&Math.hypot(p.x-p.path[0].x,p.y-p.path[0].y)<1e-6)p.path.shift();
  p.replan=(p.replan||0)-dt;if(p.path.length&&p.replan<=0){const replacement=route(p,p.path[p.path.length-1]);if(replacement.length)p.path=replacement;p.replan=.6;}});
 state.jointMotion={...GlimsMotion.status(),feasible:true};
 if(state.activity&&!state.people[0].path.length&&!state.completed){state.elapsed+=dt;if(state.elapsed>=7){state.completed=true;world.outdoorReward(state.activity==='roses'?'rest':state.activity);$('yard-status').textContent=state.activity==='roses'?'A rose moment, shared. Nobody had to hurry.':'A '+state.activity+' moment, shared. Choose another little adventure.';update();}}
}
function tick(dt){if(!active||world.getState().paused)return;const duration=Math.min(.1,dt)*world.getState().speed;for(let t=0;t<duration;t+=.05)advanceYard(Math.min(.05,duration-t));}
function enter(){active=true;world.outdoors(true);$('glackyard').hidden=false;document.querySelector('.world-shell').hidden=true;$('go-glamping').textContent='You’re in the glackyard ↓';state.visits++;resize();$('glackyard').scrollIntoView({behavior:matchMedia('(prefers-reduced-motion: reduce)').matches?'instant':'smooth',block:'start'});update();}
function leave(){active=false;world.outdoors(false);$('glackyard').hidden=true;document.querySelector('.world-shell').hidden=false;$('go-glamping').textContent='Go glamping in the glackyard ↗';document.querySelector('.world-shell').scrollIntoView({block:'start'});}
function update(){const shared=world.getState();$('yard-pause').textContent=shared.paused?'Resume':'Pause';$('yard-speed').textContent=shared.speed+'×';$('yard-night').textContent=state.night?'Morning light':'Evening lights';$('yard-night').setAttribute('aria-pressed',String(state.night));document.querySelectorAll('[data-yard]').forEach(b=>b.setAttribute('aria-pressed',String(b.dataset.yard===state.activity)));const r={id:'glims-georgia-glackyard',country:'USA',center:[-84.5,34],continent:'North America'};const neighbors=TinyWorld.residents(r,state.night);$('yard-neighbors').textContent='From Tiny Creek World’s shared neighbor catalog: '+neighbors.map(n=>n.name+' the '+n.label.toLowerCase()).join(' · ')+'. Fictional visitors to our Georgia-inspired garden.';}
function save(){try{localStorage.setItem(key,JSON.stringify({version:1,night:state.night,people:state.people.map(p=>({x:p.x,y:p.y})),visits:state.visits}));$('yard-status').textContent='Home and glackyard saved in this browser.';}catch(e){$('yard-status').textContent='This browser could not save the glackyard.';}}
function load(){try{const s=JSON.parse(localStorage.getItem(key));if(s?.version!==1)return;state=fresh();state.night=s.night===true;if(Number.isSafeInteger(s.visits))state.visits=Math.max(0,Math.min(100000,s.visits));if(Array.isArray(s.people))s.people.slice(0,5).forEach((p,i)=>{if(p&&Number.isFinite(p.x)&&Number.isFinite(p.y)&&walkable(p.x,p.y)){state.people[i].x=p.x;state.people[i].y=p.y;}});if(active)world.outdoors(true);update();}catch(e){/* An invalid local save leaves the current outing intact. */}}
function resize(){if(!active)return;const r=canvas.getBoundingClientRect(),d=Math.min(devicePixelRatio||1,2);W=r.width;H=r.height;canvas.width=W*d;canvas.height=H*d;ctx.setTransform(d,0,0,d,0,0);scale=Math.min(W/12.8,H/9);ox=(W-12*scale)/2;oy=(H-8*scale)/2;draw();}
const point=(x,y)=>({x:ox+x*scale,y:oy+y*scale});
function path(points,fill,stroke,width=1){ctx.beginPath();points.forEach(([x,y],i)=>{const p=point(x,y);i?ctx.lineTo(p.x,p.y):ctx.moveTo(p.x,p.y);});if(fill){ctx.closePath();ctx.fillStyle=fill;ctx.fill();}if(stroke){ctx.strokeStyle=stroke;ctx.lineWidth=width;ctx.stroke();}}
function circle(x,y,r,color){const p=point(x,y);ctx.beginPath();ctx.arc(p.x,p.y,r*scale,0,Math.PI*2);ctx.fillStyle=color;ctx.fill();}
function text(x,y,label,size=10,color='#375b4a'){const p=point(x,y);ctx.fillStyle=color;ctx.font=size+'px system-ui';ctx.textAlign='center';ctx.fillText(label,p.x,p.y);}
function tent(x,y,w=2){path([[x-w/2,y+.7],[x,y-1],[x+w/2,y+.7]],'#e4cca0','#927c59',2);path([[x,y-1],[x+w*.8,y-.55],[x+w,y+.7],[x+w/2,y+.7]],'#c3ad83');path([[x-.35,y+.7],[x,y-.2],[x+.35,y+.7]],'#5d7360');path([[x-.52,y+.5],[x+.43,y+.5],[x+.5,y+.7],[x-.6,y+.7]],'#b88a78');}
function draw(){if(!active)return;ctx.clearRect(0,0,W,H);ctx.fillStyle=state.night?'#294c46':'#c9d4ae';ctx.fillRect(0,0,W,H);
 // Curving banks and a real traversable bridge in a continuous lawn.
 const left=[],right=[];for(let y=-1;y<=9;y+=.12){left.push([creek(y)-.62,y]);right.push([creek(y)+.62,y]);}path([...left,...right.reverse()],state.night?'#477b7d':'#79a9a4');
 for(let i=0;i<24;i++){const y=((i*.43+state.time*.15)%9)-.5,x=creek(y)+Math.sin(i*3)*.3;path([[x-.13,y],[x+.14,y]],null,state.night?'#9dc9bd66':'#e3f1d299',1);}
 for(let i=0;i<70;i++){const x=(i*1.739)%12,y=(i*2.371)%8;if(Math.abs(x-creek(y))<.9)continue;circle(x,y,.025,i%3?'#a6b88a':'#e8c88e');}
 // Back porch, family tents, picnic rug, easel and lantern circle.
 path([[.4,6.7],[4.2,6.7],[4.2,7.8],[.4,7.8]],'#9d8767');for(let x=.5;x<4.2;x+=.25)path([[x,6.7],[x,7.8]],null,'#bdab86',1);text(2.3,7.45,'HOME, SWEET HOME',9,state.night?'#f0ddba':'#4d5846');
 tent(2,1.7,2.1);tent(4.7,1.9,1.6);
 path([[1.9,3.5],[3.7,3.5],[3.7,4.7],[1.9,4.7]],'#b2806d');for(let x=2;x<3.7;x+=.2)path([[x,3.5],[x,4.7]],null,'#ead9ae55');circle(2.8,4,.35,'#dac6a0');for(let i=0;i<5;i++)circle(2.8+Math.cos(i*1.26)*.24,4+Math.sin(i*1.26)*.12,.045,'#f4e7ce');
 path([[5.25,5.4],[5.7,4.1],[6.15,5.4]],null,'#9d7854',3);const e=point(5.35,4.25);ctx.save();ctx.translate(e.x,e.y);GlimsArt.paint(ctx,scale*.7,scale*.55,'river','garden');ctx.restore();
 path([[6.55,3.35],[8.4,3.35],[8.4,4.15],[6.55,4.15]],'#b4956d');for(let x=6.6;x<8.4;x+=.15)path([[x,3.35],[x,4.15]],null,'#735f46',1);path([[6.5,3.3],[8.45,3.3]],null,'#e4d1a5',3);path([[6.5,4.2],[8.45,4.2]],null,'#e4d1a5',3);
 for(const [x,y] of [[.65,.8],[10.5,1.5],[11,6.5],[9.8,7.3],[.6,5]]){path([[x,y],[x,y-.75]],null,'#836e4e',6);circle(x,y-.85,.55,state.night?'#355e48':'#789565');circle(x-.25,y-1.1,.4,state.night?'#426b50':'#8da673');}
 path([[1,1],[5.8,.7],[10.5,1.5]],null,state.night?'#b8b38d':'#727d5f',1);for(let i=0;i<13;i++){const x=1+i*.78,y=x<5.8?1-(x-1)*.0625:.7+(x-5.8)*.17;if(state.night){const p=point(x,y);const g=ctx.createRadialGradient(p.x,p.y,0,p.x,p.y,scale*.28);g.addColorStop(0,'#ffe3a288');g.addColorStop(1,'#ffe3a200');ctx.fillStyle=g;ctx.fillRect(p.x-scale*.3,p.y-scale*.3,scale*.6,scale*.6);}circle(x,y,.045,state.night?'#ffe2a0':'#f0dcab');}
 for(const [x,y] of [[5.05,5.05],[5.45,5.35],[5.75,5.15]]){path([[x,y+.2],[x,y-.15]],null,'#5c8056',2);for(let j=0;j<5;j++)circle(x+Math.cos(j*1.256)*.065,y-.15+Math.sin(j*1.256)*.065,.055,'#cf8994');circle(x,y-.15,.035,'#eed192');}
 GlimsWildlife.draw(ctx,point,scale,state.time,state.night,creek,selectedWildlife);
 state.people.slice().sort((a,b)=>a.y-b.y).forEach(p=>{const i=names.indexOf(p.name),q=point(p.x,p.y);ctx.fillStyle='#183b3328';ctx.beginPath();ctx.ellipse(q.x,q.y+scale*.09,scale*.17,scale*.07,0,0,Math.PI*2);ctx.fill();ctx.lineCap='round';ctx.strokeStyle=colors[i];ctx.lineWidth=scale*.22;ctx.beginPath();ctx.moveTo(q.x,q.y-scale*.1);ctx.lineTo(q.x,q.y-scale*.45);ctx.stroke();circle(p.x,p.y-.61,.13,i>2?'#bfd1c5':'#dcb38f');if(i>2){path([[p.x-.09,p.y-.65],[p.x+.09,p.y-.65]],null,'#274b4b',3);}if(state.activity==='read'&&!p.path.length)path([[p.x-.18,p.y-.32],[p.x+.18,p.y-.32],[p.x+.18,p.y-.15],[p.x-.18,p.y-.15]],'#f0e2bf');text(p.x,p.y+.36,p.name.toUpperCase(),Math.max(8,Math.min(11,scale*.2)),state.night?'#f1dfb9':'#315344');});
 text(9.4,5.7,'TINY CREEKS',Math.max(9,scale*.22),state.night?'#d1d7b3':'#537c6e');text(9.4,6.05,'big little evenings',Math.max(8,scale*.17),state.night?'#c0cfb0':'#6b856d');
}
$('yard-roses-home').onclick=()=>{enter();go('roses');};$('go-glamping').onclick=enter;$('go-home').onclick=leave;$('yard-night').onclick=()=>{state.night=!state.night;update();draw();};$('yard-pause').onclick=()=>{$('pause').click();update();};$('yard-speed').onclick=()=>{$('speed').click();update();};$('yard-save').onclick=()=>{$('save').click();};$('save').addEventListener('click',save);$('load').addEventListener('click',()=>{load();if(active)world.outdoors(true);});$('reset').addEventListener('click',()=>{state=fresh();if(active)world.outdoors(true);update();});
document.querySelectorAll('[data-yard]').forEach(b=>b.onclick=()=>go(b.dataset.yard));canvas.onpointerdown=e=>{const r=canvas.getBoundingClientRect(),x=(e.clientX-r.left-ox)/scale,y=(e.clientY-r.top-oy)/scale,path=route(state.people[0],{x,y});const animal=GlimsWildlife.positions(state.time,state.night,creek).map(a=>({a,d:Math.hypot((a.x-x)*scale,(a.y-y)*scale)})).sort((a,b)=>a.d-b.d)[0];if(animal&&animal.d<20){spotAnimal(animal.a.id);return;}if(!path.length){$('yard-status').textContent='Follow the bank, or use the wooden footbridge to cross.';return;}state.activity=null;state.people[0].path=path;$('yard-thought').textContent='Alex: A little wandering is part of being home.';update();};
function spotAnimal(id){const a=GlimsWildlife.catalog.find(a=>a.id===id);if(!a)return;selectedWildlife=id;$('wildlife-note').textContent=a.note;document.querySelectorAll('[data-wildlife]').forEach(b=>b.setAttribute('aria-pressed',String(b.dataset.wildlife===id)));draw();}
$('wildlife-roster').replaceChildren(...GlimsWildlife.catalog.map(a=>{const b=document.createElement('button');b.textContent=a.name;b.dataset.wildlife=a.id;b.setAttribute('aria-pressed','false');b.onclick=()=>spotAnimal(a.id);return b;}));
window.glimsYard={wildlife:()=>GlimsWildlife.positions(state.time,state.night,creek),spotAnimal,enter,leave,go,walkable,route,getState:()=>JSON.parse(JSON.stringify({...state,active})),step:seconds=>{for(let t=0;t<seconds;t+=.05)tick(.05/world.getState().speed);draw();},save,load};
load();new ResizeObserver(resize).observe(canvas);requestAnimationFrame(function frame(ms){const dt=last?Math.min(.1,(ms-last)/1000):0;last=ms;tick(dt);draw();requestAnimationFrame(frame);});
})();
