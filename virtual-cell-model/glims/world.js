/* Michael Emanuel Glover's virtual Person: an interactive browser interpretation.
   Geometry and scenario proxies, not live physiological or ROS measurements. */
'use strict';
(() => {
const $ = id => document.getElementById(id);
const TAU = Math.PI * 2, FOV = Math.PI * .70;
const clamp = (v, a=0, b=1) => Math.max(a, Math.min(b, v));
const wrap = a => Math.atan2(Math.sin(a), Math.cos(a));
const objects = [
 {id:'window',name:'The evening light',x:3,z:.15,w:2,d:.1,h:1.9,color:'#638c88',solid:false},
 {id:'desk',name:'The computer',x:1.35,z:1.3,w:1.6,d:.85,h:.8,color:'#a46d4d',solid:true},
 {id:'plant',name:'A little green life',x:.65,z:3.1,w:.4,d:.4,h:1.35,color:'#5f8f67',solid:true},
 {id:'guitar',name:'The guitar',x:1.5,z:4.6,w:.5,d:.4,h:1.2,color:'#d3a665',solid:true},
 {id:'fridge',name:'The refrigerator',x:6.9,z:.85,w:.85,d:.85,h:1.8,color:'#99b8aa',solid:true},
 {id:'food',name:'Something good to eat',x:5.55,z:.85,w:1.1,d:.8,h:.85,color:'#b48d65',solid:true},
 {id:'sofa',name:'The sofa',x:6.25,z:3.45,w:1.9,d:1.05,h:.6,color:'#ab746a',solid:true},
 {id:'papa',name:'Papa',x:6.2,z:3.45,w:.4,d:.3,h:1.25,color:'#d2b58c',solid:false},
 {id:'flowers',name:'Flowers on the table',x:4.1,z:2.7,w:.65,d:.65,h:.55,color:'#b88b59',solid:true},
 {id:'books',name:'A few good books',x:.35,z:.9,w:.35,d:1,h:1.4,color:'#856955',solid:true}
];
objects.push(
 {id:'cypher',name:'Cypher',x:4.8,z:4.8,w:.45,d:.35,h:1.1,color:'#81a9b1',solid:false},
 {id:'rosy',name:'Rosy',x:7.2,z:5.0,w:.45,d:.35,h:1.1,color:'#c68f80',solid:false},
 {id:'cushion',name:'A quiet place to rest',x:2.5,z:3.55,w:.65,d:.65,h:.12,color:'#a5aa7b',solid:false}
);
const byId = id => objects.find(o => o.id === id);
const WISHES={music:'Make room for a little music',company:'Share a welcome moment',learning:'Make something that learns'};
let learningData=[],learningError=false;
const SAVE_KEY='glover-machine-works-glims-evening-v1';
const activities = {
 cypher:{label:'A little company for Cypher',target:'cypher',duration:6,thought:'CYPHER: You don’t have to be interesting. I’m happy to listen.'},
 rosy:{label:'Making plans with Rosy',target:'rosy',duration:6,thought:'ROSY: Let’s make something useful, then put the kettle on.'},
 nap:{label:'A little nap',target:'cushion',duration:12,thought:'The room can keep being a room while I rest.'},
 listen:{label:'Listening for a melody',target:'guitar',duration:8,thought:'I don’t need to do anything with this melody. I can just listen.'},
 guitar:{label:'Practicing the guitar',target:'guitar',duration:8,thought:'The hands remember. There is still something new to hear.'},
 lyrics:{label:'Remembering the words',target:'guitar',duration:7,thought:'One phrase at a time. A little more of the song stays with me.'},
 eat:{label:'Enjoying the leftovers',target:'fridge',duration:6,thought:'Those Singaporean noodles were good. A little would be lovely.'},
 papa:{label:'A conversation with Papa',target:'sofa',duration:7,thought:'Papa, would you like a little company?'},
 mama:{label:'Checking in with Mama',target:'desk',duration:5,thought:'I can’t see Mama. I can still ask if she has a moment.'},
 work:{label:'Building something',target:'desk',duration:9,thought:'A small piece, understood well. That counts as progress.'},
 rest:{label:'Letting the evening breathe',target:null,duration:7,thought:'Nothing needs to be solved for a moment.'},
 sing:{label:'Guitar and voice together',target:'guitar',duration:8,thought:'A little voice, a little courage, and room for everyone else.'}
};
let journalSignature='', state, lastFrame, uiAccumulator=0, sound=false, audio=null, noteAt=0, projection;
const held = new Set(), prefersReduced = matchMedia('(prefers-reduced-motion: reduce)').matches;
function initialState(){return {x:3.2,z:4.9,yaw:-2.65,time:0,paused:false,autonomy:false,
 hunger:.15,happiness:.58,connection:.4,concentration:.65,relaxation:.4,progress:.16,
 guitar:.85,voice:.30,lyrics:.10,mantras:0,household:'quiet',musicPermission:null,
 target:null,path:[],action:null,phase:'idle',actionTime:0,nextChoice:3,
 thought:'There might be a little melody in this evening.',journal:[],memory:{},
 recent:[],fridgeOpen:false,blink:0,stepPhase:0,mouseTarget:null,
 speed:1,energy:.78,queue:[],wishes:{music:false,company:false,learning:false},labIndex:0,labRunning:false,
 residents:{cypher:{x:4.8,z:4.8,happiness:.65,occupied:false,path:[],wait:2,visit:0,invited:false},
 rosy:{x:7.2,z:5.,happiness:.62,occupied:false,path:[],wait:5,visit:0,invited:false}}};}
function clock(){const m=18*60+42+Math.floor(state.time/3);return `${String(Math.floor(m/60)%24).padStart(2,'0')}:${String(m%60).padStart(2,'0')}`;}
function log(text){state.journal.unshift({time:clock(),text});state.journal=state.journal.slice(0,5);}
function think(text){state.thought=text;}
function reset(){state=initialState();held.clear();lastFrame=undefined;log('Welcome home to The Glims. A little room to become.');syncResidents();refreshPerception();updateUI();draw();}
function rectOf(o,margin=0){return {x:o.x-o.w/2-margin,z:o.z-o.d/2-margin,w:o.w+2*margin,d:o.d+2*margin};}
function inside(x,z,r){return x>=r.x && x<=r.x+r.w && z>=r.z && z<=r.z+r.d;}
function free(x,z){return x>=.25 && x<=7.75 && z>=.25 && z<=5.75 && !objects.some(o=>o.solid && inside(x,z,rectOf(o,.20)));}
// Open-segment slab intersection; furniture can obscure another landmark.
function occludes(x0,z0,x1,z1,r){
 let lo=0,hi=1;
 for(const [start,delta,min,max] of [[x0,x1-x0,r.x,r.x+r.w],[z0,z1-z0,r.z,r.z+r.d]]){
  if(Math.abs(delta)<1e-8){if(start<min || start>max)return false;}
  else {let a=(min-start)/delta,b=(max-start)/delta;if(a>b)[a,b]=[b,a];lo=Math.max(lo,a);hi=Math.min(hi,b);if(lo>hi)return false;}
 }
 return hi>.02 && lo<.93;
}
function eyeOrigins(){return [-.032,.032].map(side=>({x:state.x+side*Math.cos(state.yaw),z:state.z-side*Math.sin(state.yaw)}));}
function visibleObjects(){return objects.filter(o=>eyeOrigins().some(eye=>{
 const dx=o.x-eye.x,dz=o.z-eye.z,distance=Math.hypot(dx,dz);
 if(distance>7.5 || Math.abs(wrap(Math.atan2(dx,dz)-state.yaw))>FOV/2)return false;
 return !objects.some(block=>block.solid && block!==o &&
   !(o.id==='papa' && block.id==='sofa') && occludes(eye.x,eye.z,o.x,o.z,rectOf(block,-.05)));
 }));}
function refreshPerception(){for(const o of visibleObjects())state.memory[o.id]={x:o.x,z:o.z,lastSeen:state.time};}
const cell=.25, gridW=32, gridH=24;
function routeBetween(origin,x,z){
 const available=(x,z)=>origin===state?canStand(x,z,'alex',.57):free(x,z);
 if(!available(x,z))return [];
 const start=[Math.floor(origin.x/cell),Math.floor(origin.z/cell)],goal=[Math.floor(x/cell),Math.floor(z/cell)];
 const key=(a,b)=>b*gridW+a, startKey=key(...start),goalKey=key(...goal);
 let queue=[startKey],head=0,previous=new Map([[startKey,-1]]);
 while(head<queue.length){const k=queue[head++];if(k===goalKey)break;const a=k%gridW,b=Math.floor(k/gridW);
  for(const [da,db] of [[1,0],[-1,0],[0,1],[0,-1]]){const na=a+da,nb=b+db,nk=key(na,nb);
   if(na<0||na>=gridW||nb<0||nb>=gridH||previous.has(nk)||!available((na+.5)*cell,(nb+.5)*cell))continue;
   previous.set(nk,k);queue.push(nk);
  }
 }
 if(!previous.has(goalKey))return [];
 const result=[];for(let k=goalKey;k!==startKey;k=previous.get(k))result.push({x:(k%gridW+.5)*cell,z:(Math.floor(k/gridW)+.5)*cell});
 result.reverse();result.push({x,z});return result;
}
function routeTo(x,z){return routeBetween(state,x,z);}
function approach(o){
 const options=[];
 for(let a=0;a<TAU;a+=Math.PI/12){const x=o.x+Math.sin(a)*(Math.max(o.w,o.d)/2+.57),z=o.z+Math.cos(a)*(Math.max(o.w,o.d)/2+.57);
  if(free(x,z)){const path=routeTo(x,z);if(path.length)options.push(path);}}
 return options.sort((a,b)=>a.length-b.length)[0]||[];
}
function cancelAction(){for(const npc of Object.values(state.residents))npc.invited=false;state.labRunning=false;state.action=null;state.phase='idle';state.fridgeOpen=false;state.path=[];state.target=null;}
function walkTo(x,z){
 const path=routeTo(x,z);if(!path.length){think('There’s something in the way. I can choose another route.');return false;}
 cancelAction();state.queue=[];state.autonomy=false;state.path=path;state.phase='walking';state.target=null;
 think('A different place, a slightly different view.');updateUI();return true;
}
function act(id,automatic=false){
 if(!activities[id])return false;
 if(state.residents[id] && state.residents[id].occupied){
  state.residents[id].happiness=clamp(state.residents[id].happiness+.015);
  think(id==='rosy'?'ROSY: Let me finish this little project. Then I’d love some company.':'CYPHER: Just a moment, please.');
  log(`${byId(id).name} asked for a moment. Alex respected that.`);updateUI();return false;
 }
 if(id==='sing' && state.musicPermission!==true){think('I should ask before filling our shared room with sound.');return false;}
 if(!automatic)state.autonomy=false;
 cancelAction();state.action=id;state.actionTime=0;state.target=activities[id].target;if(state.residents[id])state.residents[id].invited=true;
 if(state.target){const path=id==='nap'?routeTo(byId(state.target).x,byId(state.target).z):approach(byId(state.target));if(!path.length){cancelAction();think('I can’t find a clear route from here.');return false;}state.path=path;state.phase='walking';}
 else state.phase='doing';
 think(state.phase==='walking'?`A moment for ${id==='eat'?'those remembered noodles':id==='papa'?'Papa':id==='mama'?'Mama':id==='work'?'a little work':id==='nap'?'a little nap':id==='cypher'?'Cypher':id==='rosy'?'Rosy':id==='rest'?'rest':'music'}.`:activities[id].thought);
 log(id==='eat'?'Remembered lunch; headed toward the refrigerator.':`Chose: ${activities[id].label.toLowerCase()}.`);
 updateUI();return true;
}
function beginAction(){
 if(!state.action){state.phase='idle';return;}
 const id=state.action;
 if(id==='papa' && state.household==='quiet'){
  think('“A little later, Alex? I’d like some quiet.” Of course, Papa.');log('Papa preferred quiet. Alex left the invitation open.');cancelAction();state.nextChoice=5;return;
 }
 if(id==='mama' && state.household==='quiet'){
  think('Mama is occupied. A warm message can wait for her.');log('Left Mama a message; did not assume she was available.');state.connection=clamp(state.connection+.015);cancelAction();state.nextChoice=5;return;
 }
 state.phase='doing';state.actionTime=0;state.fridgeOpen=id==='eat';think(activities[id].thought);if(id==='work'){state.labIndex=0;state.labRunning=true;}
 if(id==='papa')log('Papa welcomed a conversation.');
 if(id==='mama')log('Mama replied: a little company sounds nice.');
}
function chooseNext(){
 const scores={listen:.70+(1-state.happiness)*.3,guitar:.72+(1-state.guitar)*.2,lyrics:.55+(1-state.lyrics)*.35,
  eat:.20+state.hunger*.8,papa:state.household==='quiet'?.05:.5+(1-state.connection)*.55,
  mama:state.household==='quiet'?.12:.45+(1-state.connection)*.5,work:.35+(1-state.progress)*.5,
  rest:.3+(1-state.relaxation)*.65,nap:.10+(1-state.energy)*.95,cypher:.28+(1-state.connection)*.35,rosy:state.residents.rosy.occupied?.01:.25+(1-state.connection)*.35};
 for(const [i,recent] of state.recent.entries())scores[recent]-=.35/(i+1);
 const best=Object.keys(scores).sort((a,b)=>scores[b]-scores[a])[0];act(best,true);
}
function tick(dt){
 if(state.paused)return;
 dt=Math.min(dt,.12);state.time+=dt;state.hunger=clamp(state.hunger+dt*.0015);
 state.energy=clamp(state.energy-dt*.0015);state.stepPhase+=dt*8;tickResidents(dt);
 const turn=(held.has('d')?1:0)-(held.has('a')?1:0),drive=(held.has('w')?1:0)-(held.has('s')?1:0);
 if(turn||drive){cancelAction();state.queue=[];state.autonomy=false;state.yaw=wrap(state.yaw+turn*dt*1.8);
  const nx=state.x+Math.sin(state.yaw)*drive*dt*1.2,nz=state.z+Math.cos(state.yaw)*drive*dt*1.2;
  if(canStand(nx,nz,'alex')){state.x=nx;state.z=nz;}state.phase='steering';
 }else if(state.path.length){
  const next=state.path[0],dx=next.x-state.x,dz=next.z-state.z,d=Math.hypot(dx,dz),step=dt*1.25;
  state.yaw=Math.atan2(dx,dz);
  if(d<step){if(canStand(next.x,next.z,'alex')){state.x=next.x;state.z=next.z;state.path.shift();}else{cancelAction();think('A little room for everyone. I’ll wait here.');state.nextChoice=2;return;}}
  else {const nx=state.x+dx/d*step,nz=state.z+dz/d*step;if(canStand(nx,nz,'alex')){state.x=nx;state.z=nz;}else{cancelAction();think('Let me find a clear place to stand.');updateUI();return;}}
  if(!state.path.length){if(state.target){const o=byId(state.target);state.yaw=Math.atan2(o.x-state.x,o.z-state.z);}beginAction();}
 }else if(state.phase==='steering')state.phase='idle';
 if(state.phase==='doing' && state.action){
  const id=state.action;state.actionTime+=dt;
  // Independent scenario state variables; this is not a physiological fit.
  state.happiness=clamp(state.happiness+dt*(id==='listen'||id==='guitar'||id==='sing'?.008:.003));
  state.concentration=clamp(state.concentration+dt*(id==='lyrics'||id==='work'?.012:-.003));
  state.relaxation=clamp(state.relaxation+dt*(id==='rest'||id==='nap'||id==='listen'?.025:-.004));
  if(id==='guitar'||id==='sing')state.guitar+=(1-state.guitar)*dt*.018;
  if(id==='sing')state.voice+=(1-state.voice)*dt*.025;
  if(id==='lyrics')state.lyrics+=(1-state.lyrics)*dt*(.015+.045*state.concentration);
  if(id==='eat')state.hunger=clamp(state.hunger-dt*.07);
  if(['papa','mama','cypher','rosy'].includes(id))state.connection=clamp(state.connection+dt*.025);
  if(state.residents[id])state.residents[id].happiness=clamp(state.residents[id].happiness+dt*.018);
  if(id==='nap')state.energy=clamp(state.energy+dt*.035);
  if(id==='rest')state.energy=clamp(state.energy+dt*.012);
  if(id==='work'&&state.labRunning&&learningData.length)state.labIndex=Math.min(learningData.length,state.labIndex+dt*14);
  if(id==='work')state.progress=clamp(state.progress+dt*.018);
  if(state.actionTime>=activities[id].duration){
   const finished=id;
   if(['listen','guitar','sing'].includes(id))state.wishes.music=true;
   if(['papa','mama','cypher','rosy'].includes(id))state.wishes.company=true;
   if(id==='work'&&learningData.length&&state.labIndex>=learningData.length)state.wishes.learning=true;
   state.recent.unshift(finished);state.recent=state.recent.slice(0,5);
   log(finished==='lyrics'?'One more phrase remembered. The guitar skill stayed its own.':finished==='eat'?'Enjoyed some leftovers; remembered the pleasure, too.':`A little time spent ${activities[finished].label.toLowerCase()}.`);
   cancelAction();state.nextChoice=2;think('That was one small part of the evening. There is room for another.');
  }
 }
 if(state.phase==='idle'&&state.queue.length){const next=state.queue.shift();act(next);}
 if(state.autonomy && state.phase==='idle'){state.nextChoice-=dt;if(state.nextChoice<=0)chooseNext();}
 refreshPerception();uiAccumulator+=dt;
 if(uiAccumulator>.18){updateUI();uiAccumulator=0;}
}
// World drawing: original vector artwork, generated locally without image assets.
const room=$('room'),vision=$('vision'),ctx=room.getContext('2d'),vctx=vision.getContext('2d');
let W=800,H=490,VW=350,VH=185;
function resize(){const dpr=Math.min(devicePixelRatio||1,2);for(const c of [room,vision]){
 const r=c.getBoundingClientRect();c.width=Math.round(r.width*dpr);c.height=Math.round(r.height*dpr);c.getContext('2d').setTransform(dpr,0,0,dpr,0,0);
 if(c===room){W=r.width;H=r.height;}else{VW=r.width;VH=r.height;}}
 draw();}
function project(x,z,y=0){const s=projection.s;return {x:projection.x+(x-z)*s*.866,y:projection.y+(x+z)*s*.43-y*s};}
function polygon(points,fill,stroke){ctx.beginPath();points.forEach((p,i)=>i?ctx.lineTo(p.x,p.y):ctx.moveTo(p.x,p.y));ctx.closePath();if(fill){ctx.fillStyle=fill;ctx.fill();}if(stroke){ctx.strokeStyle=stroke;ctx.stroke();}}
function box(x,z,w,d,h,color){const a=project(x-w/2,z-d/2),b=project(x+w/2,z-d/2),c=project(x+w/2,z+d/2),dd=project(x-w/2,z+d/2);
 const up=p=>({x:p.x,y:p.y-h*projection.s});
 polygon([b,c,up(c),up(b)],color);polygon([c,dd,up(dd),up(c)],color);polygon([c,dd,up(dd),up(c)],'#00000024');polygon([up(a),up(b),up(c),up(dd)],color);polygon([up(a),up(b),up(c),up(dd)],'#ffffff15');
}
function ellipseAt(x,z,rx,ry,color){const p=project(x,z);ctx.fillStyle=color;ctx.beginPath();ctx.ellipse(p.x,p.y,rx*projection.s,ry*projection.s,0,0,TAU);ctx.fill();}
function line(a,b,color,width=1){ctx.beginPath();ctx.moveTo(a.x,a.y);ctx.lineTo(b.x,b.y);ctx.strokeStyle=color;ctx.lineWidth=width;ctx.stroke();}
function person(x,z,isAlex=false){
 if(isAlex&&state.action==='nap'&&state.phase==='doing'){
  const p=project(x,z,.22),s=projection.s;ellipseAt(x,z,.35,.16,'#00000020');
  line({x:p.x-.24*s,y:p.y},{x:p.x+.23*s,y:p.y+.04*s},'#8cb8a6',.24*s);
  ctx.fillStyle='#deb18b';ctx.beginPath();ctx.arc(p.x-.31*s,p.y-.025*s,.11*s,0,TAU);ctx.fill();
  ctx.fillStyle='#ead8ab';ctx.font='12px Georgia';ctx.fillText('z z',p.x-.2*s,p.y-.4*s);return;
 }
 const s=projection.s,p=project(x,z),head=project(x,z,1.15),walking=isAlex&&state.path.length>0;
 const sway=walking?Math.sin(state.stepPhase)*.09*s:0;
 ellipseAt(x,z,.27,.12,'#00000028');ctx.lineCap='round';
 line({x:p.x-4,y:p.y-3},{x:p.x-5+sway,y:p.y-.35*s},isAlex?'#303c49':'#8d7663',5);
 line({x:p.x+5,y:p.y-4},{x:p.x+5-sway,y:p.y-.35*s},isAlex?'#303c49':'#8d7663',5);
 line({x:p.x,y:p.y-.35*s},{x:p.x,y:p.y-.86*s},isAlex?'#8cb8a6':'#c4aa7f',.28*s);
 line({x:p.x-.1*s,y:p.y-.76*s},{x:p.x-.2*s+sway*.3,y:p.y-.44*s},isAlex?'#8cb8a6':'#c4aa7f',5);
 line({x:p.x+.1*s,y:p.y-.76*s},{x:p.x+.2*s-sway*.3,y:p.y-.44*s},isAlex?'#8cb8a6':'#c4aa7f',5);
 ctx.fillStyle='#deb18b';ctx.beginPath();ctx.ellipse(head.x,head.y,.12*s,.15*s,0,0,TAU);ctx.fill();
 ctx.fillStyle=isAlex?'#48443b':'#b8b3a1';ctx.beginPath();ctx.ellipse(head.x-1,head.y-3,.13*s,.09*s,-.1,Math.PI,TAU);ctx.fill();
 if(isAlex){const face=project(x+Math.sin(state.yaw)*.13,z+Math.cos(state.yaw)*.13,1.15);ctx.fillStyle='#efe6cd';ctx.beginPath();ctx.arc(face.x-2,face.y,1.3,0,TAU);ctx.arc(face.x+2,face.y,1.3,0,TAU);ctx.fill();}
}
function flower(x,z,height){const stem=project(x,z,height),top={x:stem.x,y:stem.y-.20*projection.s};line(stem,top,'#759274',2);for(let k=0;k<5;k++){ctx.fillStyle=k%2?'#dfaf72':'#d58d7d';ctx.beginPath();ctx.arc(top.x+Math.cos(k*TAU/5)*4,top.y+Math.sin(k*TAU/5)*4,3.2,0,TAU);ctx.fill();}ctx.fillStyle='#f6d49b';ctx.beginPath();ctx.arc(top.x,top.y,2.5,0,TAU);ctx.fill();}
function drawObject(o){const s=projection.s;if(state.residents[o.id]){drawRobot(o);return;}
 if(o.id==='window'){const p=project(o.x,.02,1.8);ctx.fillStyle='#bdc3a0';ctx.fillRect(p.x-.72*s,p.y-.65*s,1.5*s,.9*s);ctx.fillStyle='#587b7d';ctx.fillRect(p.x-.66*s,p.y-.59*s,.65*s,.78*s);ctx.fillRect(p.x+.06*s,p.y-.59*s,.65*s,.78*s);ctx.fillStyle='#e5c998';ctx.beginPath();ctx.arc(p.x+.40*s,p.y-.35*s,.13*s,0,TAU);ctx.fill();return;}
 if(o.id==='papa'){person(o.x,o.z,false);return;}
 ellipseAt(o.x,o.z,o.w*.6,o.d*.3,'#00000018');
 if(o.id==='guitar'){const p=project(o.x,o.z,.45);ctx.save();ctx.translate(p.x,p.y);ctx.rotate(.16);ctx.fillStyle=o.color;ctx.beginPath();ctx.ellipse(0,0,.18*s,.24*s,0,0,TAU);ctx.ellipse(0,-.21*s,.14*s,.17*s,0,0,TAU);ctx.fill();ctx.fillStyle='#674d32';ctx.fillRect(-.035*s,-.95*s,.07*s,.65*s);ctx.fillStyle='#795634';ctx.beginPath();ctx.arc(0,-.14*s,.055*s,0,TAU);ctx.fill();ctx.restore();return;}
 if(o.id==='plant'){box(o.x,o.z,.36,.36,.32,'#b28b6a');for(let i=0;i<8;i++){const p=project(o.x+Math.sin(i*2)*.2,o.z+Math.cos(i*2)*.2,.65+i*.065);ctx.fillStyle=i%2?'#769471':'#517763';ctx.beginPath();ctx.ellipse(p.x,p.y,.09*s,.25*s,(i-4)*.3,0,TAU);ctx.fill();}return;}
 box(o.x,o.z,o.w,o.d,o.h,o.color);
 if(o.id==='desk'){box(o.x,o.z-.10,.62,.13,.98,'#384b4b');const p=project(o.x,o.z-.05,1.04);ctx.fillStyle='#b4c7b4';ctx.fillRect(p.x-.20*s,p.y-.10*s,.4*s,.17*s);}
 if(o.id==='fridge'){line(project(o.x+.44,o.z-.40,1.3),project(o.x+.44,o.z+.4,1.3),'#607d73',1);if(state.fridgeOpen){const p=project(o.x+.44,o.z,1);ctx.fillStyle='#f2cd91';ctx.fillRect(p.x-7,p.y-18,15,30);}}
 if(o.id==='sofa'){box(o.x,o.z-.38,o.w,.24,1.0,'#986459');box(o.x-.83,o.z,.25,o.d,.75,'#b47e70');box(o.x+.83,o.z,.25,o.d,.75,'#b47e70');}
 if(o.id==='food'){const p=project(o.x,o.z,.88);ctx.fillStyle='#e9d5ad';ctx.beginPath();ctx.ellipse(p.x,p.y,.20*s,.09*s,0,0,TAU);ctx.fill();ctx.strokeStyle='#a77b47';for(let i=0;i<4;i++){ctx.beginPath();ctx.ellipse(p.x+(i-2)*3,p.y,4,2,i*.3,0,TAU);ctx.stroke();}}
 if(o.id==='flowers'){flower(o.x,o.z,.65);flower(o.x+.15,o.z,.58);}
 if(o.id==='books'){for(let k=0;k<5;k++)box(o.x,o.z-.35+k*.15,.4,.08,1.45,['#ae8361','#718f82','#b6aa7a'][k%3]);}
}
function drawRoom(){
 ctx.clearRect(0,0,W,H);const bg=ctx.createLinearGradient(0,0,0,H);bg.addColorStop(0,'#294448');bg.addColorStop(1,'#1d3437');ctx.fillStyle=bg;ctx.fillRect(0,0,W,H);
 const s=Math.min(W/14.1,(H-35)/9.4);projection={s,x:W/2-s*.85,y:2.75*s+8};
 polygon([project(0,0,2.5),project(8,0,2.5),project(8,0),project(0,0)],'#385754');
 polygon([project(0,0,2.5),project(0,6,2.5),project(0,6),project(0,0)],'#304e4d');
 polygon([project(0,0),project(8,0),project(8,6),project(0,6)],'#a68b69');
 for(let x=0;x<=8;x+=.5)line(project(x,0),project(x,6),'#59452c1c');
 for(let z=0;z<=6;z+=.5)line(project(0,z),project(8,z),'#59452c1c');
 polygon([project(2.7,2),project(5.4,2),project(5.4,4.5),project(2.7,4.5)],'#617c70');
 for(let z=2.12;z<4.5;z+=.22)line(project(2.85,z),project(5.25,z),'#d2bd8a24');
 // Light in the room is an illustration of the source, not a measured photon count.
 polygon([project(2.3,.15),project(4.1,.15),project(6.3,3.5),project(4.2,4.7)],'#ead8a31b');
 if($('show-field').checked){const pts=[project(state.x,state.z)];for(let i=0;i<=24;i++){const a=state.yaw-FOV/2+FOV*i/24;pts.push(project(clamp(state.x+Math.sin(a)*2.5,.1,7.9),clamp(state.z+Math.cos(a)*2.5,.1,5.9)));}polygon(pts,'#d6dbb51a','#dce3b32b');}
 if(state.path.length){let p=project(state.x,state.z);for(const q of state.path){const n=project(q.x,q.z);line(p,n,'#f2d7a16b',1.5);p=n;}ctx.fillStyle='#e5c590';ctx.beginPath();ctx.arc(p.x,p.y,4,0,TAU);ctx.fill();}
 const renderables=[...objects,{id:'alex',x:state.x,z:state.z}].sort((a,b)=>(a.x+a.z+(a.id==='papa'?.4:0))-(b.x+b.z+(b.id==='papa'?.4:0)));
 for(const o of renderables){if(o.id==='alex')person(state.x,state.z,true);else drawObject(o);}
 if($('show-tracker').checked){
  const origin=project(.35,5.6,.25),tracked=project(state.x,state.z,1.2);
  for(let k=-3;k<=3;k++){
   const point=project(state.x+k*.045,state.z+.06,.15);line(origin,point,'#76c5bd38',1);
   ctx.fillStyle='#8ed1bc';ctx.beginPath();ctx.arc(point.x,point.y,2,0,TAU);ctx.fill();
  }
  ctx.strokeStyle='#c6d9b9';ctx.lineWidth=1;ctx.strokeRect(tracked.x-12,tracked.y-14,24,28);
  line({x:tracked.x-18,y:tracked.y},{x:tracked.x+18,y:tracked.y},'#c6d9b9',1);
  ctx.fillStyle='#bdd1bc';ctx.font='8px system-ui';ctx.textAlign='left';ctx.fillText('PASSIVE TRACKING / SIMULATED',18,24);
 }
 const visible=new Set(visibleObjects().map(o=>o.id));
 for(const id of ['desk','guitar','fridge','papa','cypher','rosy']){const o=byId(id),p=project(o.x,o.z,o.h+.30);ctx.font=`${Math.max(9,Math.min(11,s*.26))}px system-ui`;ctx.textAlign='center';ctx.fillStyle=visible.has(id)?'#f5e7c5':'#c6d0bd90';ctx.fillText(id==='desk'?'COMPUTER':id.toUpperCase(),p.x,p.y);}
 const p=project(state.x,state.z,1.55);ctx.fillStyle='#e7d5ac';ctx.font='10px system-ui';ctx.textAlign='center';ctx.fillText('ALEX',p.x,p.y);
}
function drawVision(){
 if(state.action==='nap'&&state.phase==='doing'){vctx.fillStyle='#11292c';vctx.fillRect(0,0,VW,VH);vctx.fillStyle='#d6d2b5';vctx.font='italic 19px Georgia';vctx.textAlign='center';vctx.fillText('A little rest.',VW/2,VH/2);vctx.font='9px system-ui';vctx.fillText('A SCRIPTED NAP · NOT A SLEEP MEASUREMENT',VW/2,VH/2+24);return;}
 const labelPositions=[];const w=VW,h=VH;vctx.clearRect(0,0,w,h);const g=vctx.createLinearGradient(0,0,0,h);g.addColorStop(0,'#3b6462');g.addColorStop(.52,'#78958a');g.addColorStop(.53,'#ad946e');g.addColorStop(1,'#74654f');vctx.fillStyle=g;vctx.fillRect(0,0,w,h);
 for(const o of visibleObjects().sort((a,b)=>Math.hypot(b.x-state.x,b.z-state.z)-Math.hypot(a.x-state.x,a.z-state.z))){const d=Math.max(.5,Math.hypot(o.x-state.x,o.z-state.z)),a=wrap(Math.atan2(o.x-state.x,o.z-state.z)-state.yaw);
  const x=w/2+Math.tan(a)/Math.tan(FOV/2)*w/2,size=Math.min(h*.9,h/d*.8),base=h*.62+size*.16;
  vctx.fillStyle=o.color;
  if(o.id==='papa'){vctx.fillRect(x-size*.10,base-size*.6,size*.20,size*.6);vctx.fillStyle='#d5af87';vctx.beginPath();vctx.arc(x,base-size*.72,size*.13,0,TAU);vctx.fill();}
  else if(o.id==='guitar'){vctx.beginPath();vctx.ellipse(x,base-size*.22,size*.13,size*.22,0,0,TAU);vctx.fill();vctx.fillStyle='#67513b';vctx.fillRect(x-size*.025,base-size*.85,size*.05,size*.52);}
  else if(o.id==='window'){vctx.fillStyle='#c5c49b';vctx.fillRect(x-size*.45,base-size*.9,size*.9,size*.5);}
  else{vctx.fillRect(x-size*o.w*.35,base-size*o.h*.6,Math.max(5,size*o.w*.7),size*o.h*.6);if(o.id==='flowers'){vctx.fillStyle='#e7b58d';vctx.beginPath();vctx.arc(x,base-size*.8,5,0,TAU);vctx.fill();}}
  vctx.fillStyle='#f3ecd5';vctx.font='9px system-ui';vctx.textAlign='center';const labelX=clamp(x,28,w-28);if(!labelPositions.some(previous=>Math.abs(previous-labelX)<48)){vctx.fillText(o.id==='desk'?'computer':o.id==='window'?'light':o.id,labelX,Math.min(h-15,base+14));labelPositions.push(labelX);}
 }
 const vignette=vctx.createRadialGradient(w/2,h/2,h*.2,w/2,h/2,w*.65);vignette.addColorStop(0,'#10292b00');vignette.addColorStop(1,'#10292b99');vctx.fillStyle=vignette;vctx.fillRect(0,0,w,h);
 const blinkPhase=state.time%9;if(blinkPhase>8.8 && !prefersReduced){vctx.fillStyle=`rgba(12,26,28,${Math.sin((blinkPhase-8.8)/.2*Math.PI)})`;vctx.fillRect(0,0,w,h);}
}
function draw(){if(!state)return;drawRoom();drawVision();}
function updateUI(){
 updateGlimsUI();
 $('clock').textContent=clock();$('activity-label').textContent=state.paused?'An evening, paused':state.phase==='walking'?(state.action?'On the way · '+activities[state.action].label.toLowerCase():'A different point of view'):state.action?activities[state.action].label:'Taking in the room';
 if($('thought').textContent!==state.thought)$('thought').textContent=state.thought;$('mode-label').textContent=state.autonomy?'FOLLOWING HIS OWN CURIOSITY':'ALEX, HERE & NOW';
 const visible=visibleObjects();$('visible').textContent=visible.length?visible.map(o=>o.name).join(' · '):'A quieter corner of the room.';
 $('eyes-label').textContent=state.phase==='walking'||state.phase==='steering'?'a moving point of view':'looking, remembering';
 $('location').textContent=state.z<2?'HOME / KITCHEN & DESK':'HOME / LIVING ROOM';
 $('remembered').textContent=state.fridgeOpen?'The noodles are here. Mama still isn’t in view.':'Singaporean noodles, in the fridge. Mama isn’t in view.';
 $('pause').textContent=state.paused?'Resume':'Pause';$('pause').setAttribute('aria-pressed',String(state.paused));
 $('autonomy').setAttribute('aria-pressed',String(state.autonomy));$('autonomy').innerHTML=state.autonomy?'Alex is choosing <span>↗</span>':'Let Alex choose <span>↗</span>';
 for(const name of ['energy','hunger','happiness','connection','concentration','relaxation','progress']){const n=Math.round(state[name]*100);$(`meter-${name}`).style.width=`${n}%`;$(`value-${name}`).textContent=`${n}%`;}
 $('guitar-skill').textContent=`${Math.round(state.guitar*100)}%`;$('voice-skill').textContent=`${Math.round(state.voice*100)}%`;$('lyric-skill').textContent=`${Math.round(state.lyrics*100)}%`;
 document.querySelectorAll('[data-action]').forEach(b=>{const on=b.dataset.action===state.action;b.classList.toggle('active',on);b.setAttribute('aria-pressed',String(on));});
 const signature=JSON.stringify(state.journal);if(signature!==journalSignature){journalSignature=signature;$('journal').replaceChildren(...state.journal.map(item=>{const li=document.createElement('li'),t=document.createElement('time'),text=document.createElement('span');t.textContent=item.time;text.textContent=item.text;li.append(t,text);return li;}));}
 $('household').value=state.household;
 $('mantra-count').textContent=state.mantras?`Said ${state.mantras} ${state.mantras===1?'time':'times'} · named happiness reward +${state.mantras}`:'Attributed to Henri Matisse · Alex’s remembered wording';
}
for(const [name,label] of Object.entries({energy:'Energy',hunger:'Hunger',happiness:'Happiness',connection:'Connection',concentration:'Concentration',relaxation:'Relaxation',progress:'Longer-term progress'})){
 const d=document.createElement('div');d.className='meter';d.dataset.meter=name;d.innerHTML=`<div class="meter-label"><span>${label}</span><output id="value-${name}"></output></div><div class="meter-track"><div class="meter-fill" id="meter-${name}"></div></div>`;$('meters').append(d);
}
room.addEventListener('pointerdown',e=>{
 const r=room.getBoundingClientRect(),u=(e.clientX-r.left-projection.x)/projection.s/.866,v=(e.clientY-r.top-projection.y)/projection.s/.43;
 walkTo((u+v)/2,(v-u)/2);room.focus({preventScroll:true});
});
function isTyping(e){return /INPUT|SELECT|TEXTAREA|BUTTON/.test(e.target.tagName);}
document.addEventListener('keydown',e=>{if(isTyping(e)||document.activeElement!==room)return;const k={ArrowUp:'w',ArrowDown:'s',ArrowLeft:'a',ArrowRight:'d'}[e.key]||e.key.toLowerCase();if(['w','a','s','d'].includes(k)){e.preventDefault();held.add(k);}});
document.addEventListener('keyup',e=>{held.delete({ArrowUp:'w',ArrowDown:'s',ArrowLeft:'a',ArrowRight:'d'}[e.key]||e.key.toLowerCase());});
window.addEventListener('blur',()=>held.clear());
document.querySelectorAll('[data-key]').forEach(b=>{b.addEventListener('pointerdown',e=>{e.preventDefault();b.setPointerCapture(e.pointerId);held.add(b.dataset.key);});for(const event of ['pointerup','pointercancel','lostpointercapture'])b.addEventListener(event,()=>held.delete(b.dataset.key));});
document.querySelectorAll('[data-action]').forEach(b=>b.addEventListener('click',()=>enqueueAction(b.dataset.action)));
$('pause').addEventListener('click',()=>{state.paused=!state.paused;updateUI();});
$('reset').addEventListener('click',()=>{reset();$('permission').textContent='Audible practice awaits a reply.';$('save-status').textContent='Fresh evening. Your saved evening remains available.';});
$('autonomy').addEventListener('click',()=>{state.autonomy=!state.autonomy;if(state.autonomy){state.nextChoice=0;think('I’ll follow a little curiosity, and see what matters next.');}updateUI();});
$('mantra').addEventListener('click',()=>{state.mantras++;state.happiness=clamp(state.happiness+.035);think('There are always flowers, for those who choose to see.');log('Said a remembered mantra. Happiness reward +1 in the model.');updateUI();});
$('household').addEventListener('change',e=>{state.household=e.target.value;state.musicPermission=null;$('permission').textContent='Preferences changed. Alex can ask again.';if(state.action==='sing')cancelAction();log('The household’s mood changed. Alex does not presume a reply.');updateUI();});
$('sing').addEventListener('click',()=>{state.musicPermission=state.household==='music';if(state.musicPermission){$('permission').textContent='“Yes, a little music would be lovely.”';log('Asked about audible music; the household welcomed it.');act('sing');}else{$('permission').textContent='“Let’s keep it quiet for now.” Headphones are still welcome.';think('There are quiet ways to enjoy music, too.');log('Asked about audible music. Respected a preference for quiet.');updateUI();}});
$('show-field').addEventListener('change',draw);
$('show-tracker').addEventListener('change',draw);
async function toggleSound(){try{
 if(!audio){const Audio=window.AudioContext||window.webkitAudioContext;if(!Audio)throw new Error('Unavailable');audio=new Audio();}
 if(audio.state==='suspended')await audio.resume();sound=!sound;$('sound').textContent=sound?'Sound on ♪':'Sound off';$('sound').setAttribute('aria-pressed',String(sound));
 }catch(e){$('sound').textContent='Sound unavailable';}}
$('sound').addEventListener('click',toggleSound);
function playTone(){if(!sound||!audio||state.paused||audio.currentTime<noteAt)return;noteAt=audio.currentTime+.55;
 if(state.phase!=='doing'||!['listen','guitar','sing'].includes(state.action))return;
 const notes=[60,64,67,69,72,67,64,62],note=notes[Math.floor(state.time*1.8)%notes.length];
 const osc=audio.createOscillator(),gain=audio.createGain(),now=audio.currentTime;osc.type='sine';osc.frequency.value=440*Math.pow(2,(note-69)/12);gain.gain.setValueAtTime(0,now);gain.gain.linearRampToValueAtTime(.045,now+.03);gain.gain.exponentialRampToValueAtTime(.0001,now+.7);osc.connect(gain);gain.connect(audio.destination);osc.start(now);osc.stop(now+.75);
}
function frame(ms){const dt=lastFrame===undefined?0:Math.min(.1,(ms-lastFrame)/1000);lastFrame=ms;tick(dt*state.speed);draw();playTone();requestAnimationFrame(frame);}
window.alexWorld=window.glimsWorld={getState:()=>JSON.parse(JSON.stringify(state)),step:seconds=>{for(let t=0;t<seconds;t+=.05)tick(Math.min(.05,seconds-t));updateUI();draw();},reset,act,walkTo,enqueueAction,saveEvening,loadEvening,learningInfo:()=>({loaded:learningData.length,step:state.labIndex,lastLoss:learningData.length?learningData[learningData.length-1].loss:null}),visibleNames:()=>visibleObjects().map(o=>o.id),free,routeTo,
 turn:yaw=>{state.yaw=wrap(yaw);refreshPerception();updateUI();draw();}};

function syncResidents(){for(const [id,npc] of Object.entries(state.residents)){byId(id).x=npc.x;byId(id).z=npc.z;}}
function canStand(x,z,who,clearance=.43){
 if(!free(x,z))return false;
 if(who!=='alex'&&Math.hypot(x-state.x,z-state.z)<clearance)return false;
 return !Object.entries(state.residents).some(([id,npc])=>id!==who&&Math.hypot(x-npc.x,z-npc.z)<clearance);
}
function tickResidents(dt){
 const destinations={cypher:[{x:4.75,z:4.8},{x:4.75,z:1.85}],rosy:[{x:7.45,z:5.25},{x:5.,z:5.25}]};
 for(const [id,npc] of Object.entries(state.residents)){
  npc.occupied=id==='rosy'&&Math.floor(state.time/18)%3===1&&!npc.invited;
  if(npc.invited||npc.occupied)continue;
  if(!npc.path.length){npc.wait-=dt;if(npc.wait<=0){npc.visit=(npc.visit+1)%2;const target=destinations[id][npc.visit];npc.path=routeBetween(npc,target.x,target.z);npc.wait=6;}}
  if(npc.path.length){const next=npc.path[0],dx=next.x-npc.x,dz=next.z-npc.z,d=Math.hypot(dx,dz),step=Math.min(d,dt*.45);
   const x=d>0?npc.x+dx/d*step:npc.x,z=d>0?npc.z+dz/d*step:npc.z;
   const yielding=state.path.slice(0,8).some(p=>Math.hypot(x-p.x,z-p.z)<.55);
   if(!yielding&&canStand(x,z,id)){npc.x=x;npc.z=z;if(d<.03)npc.path.shift();}
  }
 }
 syncResidents();
}
function drawRobot(o){
 const p=project(o.x,o.z),s=projection.s,rosy=o.id==='rosy',npc=state.residents[o.id];
 ellipseAt(o.x,o.z,.25,.12,'#00000028');
 const sway=npc.path.length?Math.sin(state.stepPhase*.65)*2:0;
 line({x:p.x-.08*s,y:p.y-.13*s},{x:p.x-.09*s+sway,y:p.y},'#526a6b',.09*s);
 line({x:p.x+.08*s,y:p.y-.13*s},{x:p.x+.09*s-sway,y:p.y},'#526a6b',.09*s);
 ctx.fillStyle=o.color;ctx.beginPath();ctx.roundRect(p.x-.17*s,p.y-.71*s,.34*s,.51*s,.09*s);ctx.fill();
 ctx.fillStyle=rosy?'#e3b9a3':'#b8ceca';ctx.beginPath();ctx.roundRect(p.x-.19*s,p.y-1.05*s,.38*s,.34*s,.09*s);ctx.fill();
 ctx.fillStyle='#2d4b4d';ctx.beginPath();ctx.roundRect(p.x-.14*s,p.y-.98*s,.28*s,.17*s,.04*s);ctx.fill();
 ctx.fillStyle='#e8d7ac';ctx.beginPath();ctx.arc(p.x-.065*s,p.y-.90*s,.025*s,0,TAU);ctx.arc(p.x+.065*s,p.y-.90*s,.025*s,0,TAU);ctx.fill();
 line({x:p.x-.19*s,y:p.y-.62*s},{x:p.x-.26*s,y:p.y-.35*s},o.color,.07*s);
 line({x:p.x+.19*s,y:p.y-.62*s},{x:p.x+.26*s,y:p.y-.35*s},o.color,.07*s);
 if(rosy){line({x:p.x-.18*s,y:p.y-1.04*s},{x:p.x+.18*s,y:p.y-1.04*s},'#ad6258',.07*s);}
}
function enqueueAction(id){
 if(!activities[id])return false;
 if(!state.action&&!state.path.length)return act(id);
 if(state.queue.length>=4){think('Four little plans are enough for now.');return false;}
 if(id==='sing'&&state.musicPermission!==true)return act(id);
 state.autonomy=false;state.queue.push(id);updateUI();return true;
}
let planSignature='',wishesSignature='';
function updateGlimsUI(){
 $('speed').textContent=state.speed+'×';
 $('alex-mood').textContent=state.energy<.3?'A little tired · room for rest':state.action==='nap'?'Resting · quietly':state.action?'Following a little purpose':'Curious · music-minded';
 $('cypher-mood').textContent=state.residents.cypher.invited?'Enjoying your company':state.residents.cypher.path.length?'Finding a different view':'Happy to listen';
 $('rosy-mood').textContent=state.residents.rosy.occupied?'Finishing her own project':state.residents.rosy.invited?'Making room for company':'A few ideas of her own';
 const plan=JSON.stringify(state.queue);
 if(plan!==planSignature){planSignature=plan;$('action-queue').replaceChildren();
  if(!state.queue.length){const span=document.createElement('span');span.className='empty-plan';span.textContent='Choose a moment. Add another while Alex is busy.';$('action-queue').append(span);}
  else state.queue.forEach((id,index)=>{const b=document.createElement('button');b.textContent=activities[id].label+' ×';b.setAttribute('aria-label','Remove queued '+activities[id].label);b.addEventListener('click',()=>{state.queue.splice(index,1);updateUI();});$('action-queue').append(b);});
 }
 const wish=JSON.stringify(state.wishes);
 if(wish!==wishesSignature){wishesSignature=wish;$('wish-count').textContent=Object.values(state.wishes).filter(Boolean).length+' / 3';$('wishes').replaceChildren(...Object.entries(WISHES).map(([id,text])=>{const li=document.createElement('li'),mark=document.createElement('span');li.className=state.wishes[id]?'complete':'';mark.className='wish-mark';mark.textContent=state.wishes[id]?'✓':'○';li.append(mark,document.createTextNode(text));return li;}));}
 const index=Math.min(learningData.length,Math.floor(state.labIndex));
 $('learning-step').textContent='Step '+index+' / '+(learningData.length||100);
 $('learning-loss').textContent=learningData.length&&index>0?learningData[Math.max(0,index-1)].loss.toFixed(4):'—';
 $('learning-status').textContent=learningError?'Run unavailable · code still linked':!learningData.length?'Loading the saved run…':index>=learningData.length?'Replay complete':state.labRunning?'Replaying at the workbench':'Ready when Alex is';
 if(learningData.length){const maximum=Math.max(...learningData.map(p=>p.loss)),path=points=>points.map((p,i)=>(i?'L':'M')+(8+(p.step-1)/(learningData.length-1)*364).toFixed(2)+','+(88-p.loss/maximum*72).toFixed(2)).join(' ');$('learning-background').setAttribute('d',path(learningData));$('learning-progress').setAttribute('d',index>0?path(learningData.slice(0,index)):'');}
}
function saveEvening(){
 const fields=['x','z','yaw','time','energy','hunger','happiness','connection','concentration','relaxation','progress','guitar','voice','lyrics','mantras','household','wishes','residents'];
 const snapshot={version:1};for(const key of fields)snapshot[key]=state[key];
 try{localStorage.setItem(SAVE_KEY,JSON.stringify(snapshot));$('save-status').textContent='Evening saved in this browser.';return true;}
 catch(e){$('save-status').textContent='This browser could not save the evening.';return false;}
}
function loadEvening(){
 try{
  const raw=localStorage.getItem(SAVE_KEY);if(!raw){$('save-status').textContent='No saved evening in this browser yet.';return false;}
  const saved=JSON.parse(raw);if(saved.version!==1)throw new Error('Version');const next=initialState();
  for(const key of ['energy','hunger','happiness','connection','concentration','relaxation','progress','guitar','voice','lyrics'])if(Number.isFinite(saved[key]))next[key]=clamp(saved[key]);
  if(Number.isFinite(saved.x)&&Number.isFinite(saved.z)&&free(saved.x,saved.z)){next.x=saved.x;next.z=saved.z;}
  if(Number.isFinite(saved.yaw))next.yaw=wrap(saved.yaw);
  if(Number.isFinite(saved.time))next.time=clamp(saved.time,0,86400);
  if(Number.isSafeInteger(saved.mantras))next.mantras=clamp(saved.mantras,0,1000000);
  if(['quiet','social','music'].includes(saved.household))next.household=saved.household;
  for(const key of Object.keys(WISHES))next.wishes[key]=saved.wishes?.[key]===true;
  for(const id of ['cypher','rosy']){const npc=saved.residents?.[id];if(npc&&Number.isFinite(npc.x)&&Number.isFinite(npc.z)&&free(npc.x,npc.z)){next.residents[id].x=npc.x;next.residents[id].z=npc.z;if(Number.isFinite(npc.happiness))next.residents[id].happiness=clamp(npc.happiness);}}
  state=next;held.clear();tickResidents(0);
  const robotDistance=Math.hypot(state.residents.cypher.x-state.residents.rosy.x,state.residents.cypher.z-state.residents.rosy.z);
  if(robotDistance<.43){const defaults=initialState().residents;state.residents.cypher.x=defaults.cypher.x;state.residents.cypher.z=defaults.cypher.z;state.residents.rosy.x=defaults.rosy.x;state.residents.rosy.z=defaults.rosy.z;syncResidents();}
  if(!canStand(state.x,state.z,'alex')){state.x=3.2;state.z=4.9;if(!canStand(state.x,state.z,'alex')){state.residents=initialState().residents;syncResidents();}}
  log('Loaded a saved Glims evening. Plans and permissions begin fresh.');refreshPerception();updateUI();draw();$('save-status').textContent='Welcome back. Evening loaded.';$('permission').textContent='Replies begin fresh. Ask about music again.';return true;
 }catch(e){$('save-status').textContent='That saved evening could not be loaded.';return false;}
}
$('speed').addEventListener('click',()=>{state.speed=state.speed===1?2:state.speed===2?4:1;updateUI();});
$('save').addEventListener('click',saveEvening);$('load').addEventListener('click',loadEvening);
$('replay-learning').addEventListener('click',()=>{if(state.action==='work'&&state.phase==='doing'){state.labIndex=0;state.labRunning=true;state.actionTime=0;}else enqueueAction('work');updateUI();});
fetch('learning-trace.json').then(r=>{if(!r.ok)throw new Error('Trace');return r.json();}).then(data=>{
 if(!Array.isArray(data.steps)||data.steps.length<2||data.steps.some(p=>!Number.isFinite(p.loss)||p.loss<0||!Number.isInteger(p.step)))throw new Error('Trace values');
 learningData=data.steps;updateUI();
}).catch(()=>{learningError=true;updateUI();});

reset();new ResizeObserver(resize).observe(room.parentElement);new ResizeObserver(resize).observe(vision);resize();requestAnimationFrame(frame);
})();
