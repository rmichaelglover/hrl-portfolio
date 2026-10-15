/* SPDX-License-Identifier: MIT -- Copyright (c) 2026 R. Michael Glover */
(() => {
'use strict';
const $=id=>document.getElementById(id),canvas=$('earth'),ctx=canvas.getContext('2d'),M=VirtualEarthModel;
let W=innerWidth,H=innerHeight,land=null,level=0,lon=15,lat=5,paused=matchMedia('(prefers-reduced-motion: reduce)').matches,mesh=false,model=null,ground=null,follow=null,last=0,accumulator=0,stepCount=0,drag=null,localX=M.SIZE/2,localY=M.SIZE/2;
const pointers=new Map();let pinch=null;
const projection=d3.geoOrthographic();
function resize(){W=innerWidth;H=innerHeight;const dpr=Math.min(2,devicePixelRatio||1);canvas.width=W*dpr;canvas.height=H*dpr;ctx.setTransform(dpr,0,0,dpr,0,0);}
function isLocal(){return level>=4;}
function notice(){ $('notice').textContent=isLocal()?'Synthetic ecosystem · select an animal to follow · Escape returns to Earth':'Unlabeled Earth geometry · scroll closer or press ⌖ to enter synthetic life'; }
function setLevel(value){const was=isLocal();level=M.clamp(value,0,12);$('zoom').value=level;if(isLocal()&&!was){createModel();}if(!isLocal())follow=null;notice();}
function createModel(){if(!land)return;const seed=Number($('seed').value)>>>0,patchSeed=(seed^Math.imul(Math.round((lon+180)*4),73856093)^Math.imul(Math.round((lat+90)*4),19349663))>>>0;model=new M.Ecosystem({seed:patchSeed,population:Number($('population').value),aquatic:!d3.geoContains(land,[lon,lat]),latitude:lat});stepCount=0;accumulator=0;follow=null;const center=model.agents[Math.floor(model.agents.length/2)];localX=center?.x||M.SIZE/2;localY=center?.y||M.SIZE/2;buildGround();}
function buildGround(){ground=document.createElement('canvas');ground.width=ground.height=512;const g=ground.getContext('2d'),image=g.createImageData(512,512);for(let y=0;y<512;y++)for(let x=0;x<512;x++){const i=model.index(x/512*M.SIZE,y/512*M.SIZE),h=model.height[i],wet=model.water[i],shade=M.noise(x/12,y/12,model.seed)*14;const color=wet?[14+h*12,55+h*36,67+h*42]:[36+h*64+shade,66+h*61+shade,35+h*31+shade*.5];const p=(y*512+x)*4;image.data[p]=color[0];image.data[p+1]=color[1];image.data[p+2]=color[2];image.data[p+3]=255;}g.putImageData(image,0,0);}
function localScale(){return Math.min(W,H)/M.SIZE*2**(level-4);}
function localPoint(x,y){const s=localScale();return [W/2+model.delta(x,localX)*s,H/2+model.delta(y,localY)*s*.72];}
function drawGlobe(t){
 const radius=Math.min(W*.43,H*.39)*2**Math.min(level,3.99),cx=W/2,cy=H*.51;
 projection.translate([cx,cy]).scale(radius).rotate([-lon,-lat]);
 const glow=ctx.createRadialGradient(cx,cy,radius*.95,cx,cy,radius*1.065);glow.addColorStop(0,'#7ed9e444');glow.addColorStop(1,'#7ed9e400');ctx.fillStyle=glow;ctx.beginPath();ctx.arc(cx,cy,radius*1.065,0,Math.PI*2);ctx.fill();
 ctx.save();ctx.beginPath();ctx.arc(cx,cy,radius,0,Math.PI*2);ctx.clip();
 const ocean=ctx.createLinearGradient(cx-radius,cy-radius,cx+radius,cy+radius);ocean.addColorStop(0,'#318188');ocean.addColorStop(.45,'#154b5d');ocean.addColorStop(1,'#071c2b');ctx.fillStyle=ocean;ctx.fillRect(0,0,W,H);
 if(land){const path=d3.geoPath(projection,ctx);ctx.beginPath();path(land);const fill=ctx.createLinearGradient(0,cy-radius,0,cy+radius);fill.addColorStop(0,'#b4c9b8');fill.addColorStop(.22,'#a1aa70');fill.addColorStop(.48,'#507e58');fill.addColorStop(.73,'#8e9c68');fill.addColorStop(1,'#c2d5ce');ctx.fillStyle=fill;ctx.fill();}
 // Analytic flow traces are an illustrative vector field, not meteorological data.
 ctx.strokeStyle='#c2e8d719';ctx.lineWidth=1;
 for(let j=-70;j<80;j+=14)for(let i=-180;i<180;i+=24){ctx.beginPath();let drawing=false;for(let k=0;k<18;k++){const a=i+k*1.2+t*.35,b=j+Math.sin((a+j)*Math.PI/90)*4,p=projection([a,b]),visible=d3.geoDistance([lon,lat],[a,b])<Math.PI/2;if(visible&&p){if(!drawing)ctx.moveTo(...p);else ctx.lineTo(...p);drawing=true;}else drawing=false;}ctx.stroke();}
 if(mesh){ctx.beginPath();d3.geoPath(projection,ctx)(d3.geoGraticule10());ctx.strokeStyle='#c6eacb55';ctx.stroke();}
 const shadow=ctx.createRadialGradient(cx-radius*.35,cy-radius*.4,radius*.15,cx+radius*.4,cy+radius*.2,radius*1.35);shadow.addColorStop(0,'#0000');shadow.addColorStop(.65,'#0002');shadow.addColorStop(1,'#000e');ctx.fillStyle=shadow;ctx.fillRect(0,0,W,H);ctx.restore();
}
function drawAnimal(a,p,s){
 const size=(a.type===0?3.8:a.type===1?1.8:a.type===2?2.7:a.type===3?2:2.6)*s;
 if(size<1){ctx.fillStyle=a.type===2?'#d79b62':'#e2d4b2';ctx.fillRect(p[0],p[1],1.7,1.7);return;}
 ctx.save();ctx.translate(p[0],p[1]);ctx.scale(Math.max(.4,size/12),Math.max(.4,size/12));
 ctx.fillStyle='#0004';ctx.beginPath();ctx.ellipse(1,3,13,5,0,0,Math.PI*2);ctx.fill();ctx.rotate(a.angle);
 if(a.type===4){ctx.fillStyle='#a7c9b0';ctx.beginPath();ctx.ellipse(0,0,10,3.6,0,0,Math.PI*2);ctx.fill();ctx.beginPath();ctx.moveTo(-8,0);ctx.lineTo(-15,-5*Math.cos(a.phase));ctx.lineTo(-15,5*Math.cos(a.phase));ctx.fill();ctx.fillStyle='#0b2929';ctx.fillRect(6,-1,1.5,1.5);}
 else if(a.type===3){ctx.strokeStyle='#d0d8bf';ctx.lineWidth=3;ctx.beginPath();ctx.moveTo(-8,Math.sin(a.phase)*10);ctx.lineTo(0,0);ctx.lineTo(-8,-Math.sin(a.phase)*10);ctx.stroke();ctx.fillStyle='#3b3028';ctx.beginPath();ctx.ellipse(0,0,6,2.7,0,0,Math.PI*2);ctx.fill();ctx.fillStyle='#d1b47e';ctx.fillRect(5,-1,4,2);}
 else{
  const color=a.type===0?'#aa8660':a.type===1?'#b7a48b':'#c47c43';ctx.strokeStyle=a.type===2?'#382d22':'#65503c';ctx.lineWidth=2;
  for(const side of [-1,1])for(const end of [-1,1]){const gait=Math.sin(a.phase+side*end*Math.PI/2)*(a.activity===1?.5:3);ctx.beginPath();ctx.moveTo(end*6,side*3);ctx.lineTo(end*6+gait,side*7);ctx.stroke();}
  ctx.fillStyle=color;ctx.beginPath();ctx.ellipse(0,0,a.type===1?8:11,a.type===1?5:4.8,0,0,Math.PI*2);ctx.fill();
  if(a.type===2){ctx.strokeStyle=color;ctx.lineWidth=5;ctx.beginPath();ctx.moveTo(-9,0);ctx.quadraticCurveTo(-19,Math.sin(a.phase)*5,-22,-2);ctx.stroke();ctx.strokeStyle='#e3d6af';ctx.lineWidth=3;ctx.beginPath();ctx.moveTo(-20,-1);ctx.lineTo(-23,-2);ctx.stroke();}
  ctx.save();ctx.translate(a.type===1?7:11,0);if(a.activity===1)ctx.rotate(Math.sin(a.phase)*.2);ctx.fillStyle=color;ctx.beginPath();ctx.ellipse(1,0,5,3.4,0,0,Math.PI*2);ctx.fill();
  ctx.fillStyle=a.type===2?'#6c422d':color;for(const sign of [-1,1]){ctx.beginPath();ctx.moveTo(-1,sign*2);ctx.lineTo(a.type===1?-7:-1,sign*(a.type===1?10:7));ctx.lineTo(3,sign*3);ctx.fill();}
  if(a.type===0){ctx.strokeStyle='#d6c7a0';ctx.lineWidth=1;for(const sign of [-1,1]){ctx.beginPath();ctx.moveTo(0,sign*2);ctx.lineTo(-6,sign*10);ctx.lineTo(-10,sign*11);ctx.moveTo(-4,sign*7);ctx.lineTo(-1,sign*10);ctx.stroke();}}
  ctx.fillStyle='#201c16';ctx.fillRect(4,-1,2,2);ctx.restore();
 }
 ctx.restore();
}
function drawLocal(t){
 if(!model||!ground)return;const s=localScale();if(follow!==null){const a=model.agents.find(a=>a.id===follow);if(a){localX=a.x;localY=a.y;}else follow=null;}
 const halfX=W/(2*s),halfY=H/(2*s*.72),world=M.SIZE;
 // Tile the periodic ecosystem so crossing an edge is visually continuous.
 for(let j=-2;j<=2;j++)for(let i=-2;i<=2;i++){const x=W/2+(i*world-localX)*s,y=H/2+(j*world-localY)*s*.72;ctx.drawImage(ground,x,y,world*s,world*s*.72);}
 const startX=Math.floor((localX-halfX)/20)*20,endX=localX+halfX,startY=Math.floor((localY-halfY)/20)*20,endY=localY+halfY;
 const detail=Math.min(1,s/2);
 for(let y=startY;y<endY;y+=20)for(let x=startX;x<endX;x+=20){const wx=M.wrap(x,world),wy=M.wrap(y,world),i=model.index(wx,wy),p=[W/2+(x-localX)*s,H/2+(y-localY)*s*.72],h=model.height[i];
  if(model.water[i]){if(s>.7){ctx.strokeStyle='#c2e3c526';ctx.lineWidth=1;ctx.beginPath();ctx.moveTo(p[0],p[1]);ctx.lineTo(p[0]+s*8,p[1]+Math.sin(t*.7+x)*s);ctx.stroke();}continue;}
  const food=model.food[i];ctx.strokeStyle=`rgba(188,202,115,${Math.min(.7,food*.9)})`;ctx.lineWidth=Math.max(.7,s*.25);
  if(s>.5)for(let k=0;k<3;k++){const gx=p[0]+(M.noise(wx+k*100,wy,model.seed)-.5)*s*18,gy=p[1]+(M.noise(wx,wy+k*100,model.seed)-.5)*s*12;ctx.beginPath();ctx.moveTo(gx,gy);ctx.lineTo(gx+Math.sin(t*.8+k)*s,gy-s*(1+food*3));ctx.stroke();}
  if(h>.59&&h<.74&&M.noise(wx/12,wy/12,model.seed+5)>.52&&s>.3){const height=(7+M.noise(wx/40,wy/40,model.seed)*8)*s;ctx.fillStyle='#04190e44';ctx.beginPath();ctx.ellipse(p[0]+height*.25,p[1]+height*.2,height*.5,height*.2,0,0,Math.PI*2);ctx.fill();ctx.strokeStyle='#514431';ctx.lineWidth=Math.max(1,s);ctx.beginPath();ctx.moveTo(...p);ctx.lineTo(p[0],p[1]-height*.65);ctx.stroke();ctx.fillStyle=`hsl(${125+h*20} 26% ${23+h*13}%)`;ctx.beginPath();ctx.ellipse(p[0],p[1]-height*.7,height*.45,height*.6,0,0,Math.PI*2);ctx.fill();}
  if(mesh){ctx.strokeStyle='#d4e1b622';ctx.lineWidth=.5;ctx.strokeRect(p[0],p[1],20*s,20*s*.72);}
 }
 const visible=model.agents.map(a=>({a,p:localPoint(a.x,a.y)})).filter(({p})=>p[0]>-100&&p[0]<W+100&&p[1]>-100&&p[1]<H+100).sort((a,b)=>a.p[1]-b.p[1]);for(const {a,p} of visible)drawAnimal(a,p,s);
 const vignette=ctx.createRadialGradient(W/2,H/2,Math.min(W,H)*.15,W/2,H/2,Math.max(W,H)*.7);vignette.addColorStop(0,'#0000');vignette.addColorStop(1,'#020b0c88');ctx.fillStyle=vignette;ctx.fillRect(0,0,W,H);
}
function updatePanel(){if(!model)return;$('alive').textContent=model.agents.length;$('time').textContent=model.time.toFixed(1);$('biomass').textContent=(model.food.reduce((a,b)=>a+b,0)/model.food.length).toFixed(3);$('turnover').textContent=`${model.births} / ${model.deaths}`;}
function frame(now){const elapsed=Math.min(.1,(now-(last||now))/1000);last=now;if(!document.hidden){if(model&&!paused){accumulator+=elapsed*Number($('speed').value);while(accumulator>=1/30){model.step(1/30);accumulator-=1/30;stepCount++;}}ctx.fillStyle='#020b0c';ctx.fillRect(0,0,W,H);if(isLocal())drawLocal(model?.time||0);else drawGlobe(paused?0:now/1000);if(stepCount%15===0)updatePanel();}requestAnimationFrame(frame);}
function togglePause(){paused=!paused;$('pause').textContent=paused?'▶':'Ⅱ';$('pause').setAttribute('aria-pressed',String(paused));$('pause').setAttribute('aria-label',paused?'Resume simulation':'Pause simulation');}
function dive(){if(!land)return;if(!isLocal())setLevel(6);else setLevel(level+1);}
function whole(){setLevel(0);}
$('zoom').addEventListener('input',()=>setLevel(Number($('zoom').value)));$('plus').onclick=()=>setLevel(level+.7);$('minus').onclick=()=>setLevel(level-.7);$('whole').onclick=whole;$('dive').onclick=dive;$('pause').onclick=togglePause;$('lines').onclick=()=>{mesh=!mesh;$('lines').setAttribute('aria-pressed',String(mesh));};$('info').onclick=()=>{$('panel').hidden=!$('panel').hidden;$('info').setAttribute('aria-expanded',String(!$('panel').hidden));};$('close').onclick=()=>{$('panel').hidden=true;$('info').setAttribute('aria-expanded','false');};$('reset').onclick=()=>{createModel();updatePanel();};
$('export').onclick=()=>{if(!model)createModel();if(!model)return;const data={format:'virtual-earth-v1',anchor:[lon,lat],camera:{level,localX,localY},stepCount,dt:1/30,ecosystem:model.snapshot()};const blob=new Blob([JSON.stringify(data)],{type:'application/json'}),link=document.createElement('a');link.href=URL.createObjectURL(blob);link.download='virtual-earth-state.json';link.click();setTimeout(()=>URL.revokeObjectURL(link.href),1000);};
canvas.addEventListener('wheel',e=>{e.preventDefault();setLevel(level-e.deltaY*.003);},{passive:false});
canvas.onpointerdown=e=>{canvas.focus();canvas.setPointerCapture(e.pointerId);pointers.set(e.pointerId,{x:e.clientX,y:e.clientY});drag={x:e.clientX,y:e.clientY,lon,lat,localX,localY,moved:false};if(pointers.size===2){const p=[...pointers.values()];pinch={distance:Math.hypot(p[0].x-p[1].x,p[0].y-p[1].y),level};}};
canvas.onpointermove=e=>{if(!pointers.has(e.pointerId))return;pointers.set(e.pointerId,{x:e.clientX,y:e.clientY});if(pointers.size===2&&pinch){const p=[...pointers.values()],distance=Math.hypot(p[0].x-p[1].x,p[0].y-p[1].y);setLevel(pinch.level+Math.log2(distance/Math.max(1,pinch.distance)));return;}if(!drag)return;const dx=e.clientX-drag.x,dy=e.clientY-drag.y;if(Math.hypot(dx,dy)>4)drag.moved=true;if(isLocal()){follow=null;const s=localScale();localX=M.wrap(drag.localX-dx/s,M.SIZE);localY=M.wrap(drag.localY-dy/(s*.72),M.SIZE);}else{lon=drag.lon-dx*.22/2**level;lat=M.clamp(drag.lat+dy*.22/2**level,-85,85);}};
canvas.onpointerup=e=>{if(drag&&!drag.moved&&pointers.size===1){if(isLocal()){let closest=null,d=30;for(const a of model.agents){const p=localPoint(a.x,a.y),distance=Math.hypot(p[0]-e.clientX,p[1]-e.clientY);if(distance<d){d=distance;closest=a;}}follow=closest?.id??null;}else{const point=projection.invert([e.clientX,e.clientY]);if(point&&Math.hypot(e.clientX-W/2,e.clientY-H*.51)<=projection.scale()){lon=point[0];lat=point[1];}}}pointers.delete(e.pointerId);drag=null;pinch=null;};canvas.onpointercancel=e=>{pointers.delete(e.pointerId);drag=null;pinch=null;};canvas.ondblclick=dive;
canvas.onkeydown=e=>{if(['ArrowLeft','ArrowRight','ArrowUp','ArrowDown','+','=','-','Enter','Escape',' '].includes(e.key))e.preventDefault();if(e.key==='Escape')whole();else if(e.key==='Enter')dive();else if(e.key===' ')togglePause();else if(e.key==='+'||e.key==='=')setLevel(level+.5);else if(e.key==='-')setLevel(level-.5);else if(e.key.startsWith('Arrow')){if(isLocal()){follow=null;const d=50/localScale();localX=M.wrap(localX+(e.key==='ArrowRight'?d:e.key==='ArrowLeft'?-d:0),M.SIZE);localY=M.wrap(localY+(e.key==='ArrowDown'?d:e.key==='ArrowUp'?-d:0),M.SIZE);}else{lon+=(e.key==='ArrowRight'?10:e.key==='ArrowLeft'?-10:0)/2**level;lat=M.clamp(lat+(e.key==='ArrowUp'?10:e.key==='ArrowDown'?-10:0)/2**level,-85,85);}}};
new ResizeObserver(resize).observe(canvas);resize();notice();if(paused){$('pause').textContent='▶';$('pause').setAttribute('aria-pressed','true');$('pause').setAttribute('aria-label','Resume simulation');}
fetch('data/land.json').then(r=>{if(!r.ok)throw Error(`HTTP ${r.status}`);return r.json();}).then(data=>{land=data;$('loading').hidden=true;}).catch(error=>{$('loading').textContent=`Earth geometry could not load (${error.message}). Reload to retry.`;});
window.VirtualEarth={snapshot:()=>({level,lon,lat,localX,localY,paused,mesh,follow,stepCount,ecosystem:model?.snapshot()}),enter:dive,reset:createModel,setLevel};requestAnimationFrame(frame);
})();
