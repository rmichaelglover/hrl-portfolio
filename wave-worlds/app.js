'use strict';
const $=id=>document.getElementById(id),W=WaveWorld,N=SoundField.notes;
const selected=new Set([0,4,7]),worldNames={air:'Air',water:'Water',mixed:'Mixed'};
let visualTime=0,paused=false,last=0,audio,bus,analyser,samples,oscillators=[],routes=[],playing=false;
function shown(){return Object.keys(worldNames).filter(k=>$('show'+worldNames[k]).checked);}
function sources(){return {air:$('sourceAir').checked?+$('levelAir').value:0,water:$('sourceWater').checked?+$('levelWater').value:0};}
function noteColor(i){return N[i].pitch==='C'&&$('palette').value==='black'?'#050505':N[i].color;}
function activeProbes(){return W.probeList(shown(),{air:$('hearAir').checked,water:$('hearWater').checked});}
function boxState(){return {enabled:$('boxEnabled').checked,form:$('boxForm').value,face:$('boxFace').value,x:+$('boxX').value,y:+$('boxY').value,z:+$('boxZ').value,size:+$('boxSize').value};}
function lane(i){return (i-6)*.35;}
let pathCache=new Map();
function fieldPaths(world,z,source,i){const key=[world,z,source,i].join(':');if(!pathCache.has(key))pathCache.set(key,W.obstaclePaths(world,z,source,boxState(),lane(i)));return pathCache.get(key);}
function updateBox(){pathCache.clear();const b=boxState();$('boxFace').disabled=b.form==='closed';$('faceLabel').textContent=b.form==='single'?'Square face':'Opening';$('boxReadout').textContent=(b.enabled?'Placed':'Off')+' / x '+b.x.toFixed(1)+' / y '+b.y.toFixed(2)+' / z '+b.z.toFixed(1)+' m / size '+b.size.toFixed(1)+' m';refresh();}
for(const id of ['boxEnabled','boxForm','boxFace'])$(id).onchange=updateBox;
for(const id of ['boxX','boxY','boxZ','boxSize'])$(id).oninput=updateBox;
$('boxReset').onclick=()=>{$('boxX').value=0;$('boxY').value=-.35;$('boxZ').value=10;$('boxSize').value=3;updateBox();};
function syncAudio(){if(!audio)return;const active=new Set(activeProbes().map(p=>p.world+':'+p.medium)),s=sources();
 for(const r of routes){const p=fieldPaths(r.world,r.z,r.source,r.note)[r.slot];r.pathGain=p?.gain||0;r.delay.delayTime.setTargetAtTime(p?.delay||0,audio.currentTime,.02);const gain=active.has(r.world+':'+r.medium)&&selected.has(r.note)?s[r.source]*r.pathGain/Math.max(1,selected.size):0;r.gain.gain.setTargetAtTime(gain,audio.currentTime,.02);}
 bus.gain.setTargetAtTime(playing?+$('volume').value/8:0,audio.currentTime,.02);
}
function refresh(){const visible=shown();$('worlds').style.setProperty('--count',Math.max(1,visible.length));$('empty').hidden=visible.length>0;
 for(const key of Object.keys(worldNames))$('world'+worldNames[key]).hidden=!visible.includes(key);
 [...$('notes').children].forEach((b,i)=>{b.setAttribute('aria-pressed',selected.has(i));b.style.setProperty('--color',noteColor(i));});
 syncAudio();const probeCount=activeProbes().length,s=sources();$('status').textContent=playing?'Sound enabled / '+probeCount+' monitors / '+selected.size+' selected notes'+(!s.air&&!s.water?' / emitters off':''):'Sound off / visual preview';
 render();}
N.forEach((n,i)=>{const b=document.createElement('button');b.className='note';b.innerHTML=n.name+'<small>'+n.frequency.toFixed(1)+' Hz</small>';b.onclick=()=>{selected.has(i)?selected.delete(i):selected.add(i);refresh();};$('notes').append(b);});
function choose(list){selected.clear();list.forEach(i=>selected.add(i));refresh();}
$('major').onclick=()=>choose([0,4,7]);$('octave').onclick=()=>choose([0,2,4,5,7,9,11,12]);$('clear').onclick=()=>choose([]);
for(const id of ['showAir','showWater','showMixed','sourceAir','sourceWater','hearAir','hearWater','palette'])$(id).onchange=refresh;
for(const id of ['levelAir','levelWater','volume'])$(id).oninput=refresh;
for(const id of ['side','yaw','fov','reflected','boost'])$(id).oninput=render;
$('slow').oninput=()=>{$('slowValue').textContent=$('slow').value+'x';};
function setPaused(p){paused=p;$('pause').setAttribute('aria-pressed',String(p));$('pause').textContent=p?'Resume visual time':'Pause visual time';}
$('pause').onclick=()=>setPaused(!paused);$('step').onclick=()=>{setPaused(true);visualTime+=.00025;render();};$('reset').onclick=()=>{visualTime=0;render();};
$('play').onclick=async()=>{try{if(!audio){audio=new AudioContext();bus=audio.createGain();bus.gain.value=0;analyser=audio.createAnalyser();analyser.fftSize=2048;samples=new Float32Array(analyser.fftSize);bus.connect(analyser);analyser.connect(audio.destination);
 const startTime=audio.currentTime+.03;oscillators=N.map(n=>{const o=audio.createOscillator();o.type='sine';o.frequency.value=n.frequency;o.start(startTime);return o;});
 for(const probe of W.probeList(['air','water','mixed'],{air:true,water:true})){
  const pan=audio.createStereoPanner();pan.pan.value=probe.world==='mixed'?(probe.medium==='air'?-.7:.7):probe.world==='air'?-.25:.25;pan.connect(bus);
  for(const source of ['air','water'])for(let slot=0;slot<8;slot++)for(let i=0;i<N.length;i++){
   const delay=audio.createDelay(.2),gain=audio.createGain();delay.delayTime.value=0;gain.gain.value=0;oscillators[i].connect(delay);delay.connect(gain);gain.connect(pan);routes.push({world:probe.world,medium:probe.medium,source,note:i,z:probe.z,slot,pathGain:0,gain,delay});
  }
 }
 }await audio.resume();playing=!playing;$('play').textContent=playing?'Mute all sound':'Enable sound';$('play').setAttribute('aria-pressed',String(playing));refresh();}catch(e){$('status').textContent='Audio unavailable: '+e.message;}};
function surface(id){const c=$(id),w=c.clientWidth,h=c.clientHeight,d=window.devicePixelRatio||1;const pw=Math.round(w*d),ph=Math.round(h*d);if(c.width!==pw||c.height!==ph){c.width=pw;c.height=ph;}const g=c.getContext('2d');g.setTransform(d,0,0,d,0,0);g.clearRect(0,0,w,h);return {g,w,h};}
function drawWorld(world){const {g,w,h}=surface(world),f=w*.5/Math.tan(+$('fov').value*Math.PI/360),cam={x:+$('side').value,yaw:+$('yaw').value,z:0},s=sources(),boost=$('boost').checked?20:1;
 const bg=g.createLinearGradient(0,0,0,h);bg.addColorStop(0,world==='water'?'#052440':'#090f1c');bg.addColorStop(1,world==='water'?'#105174':'#243548');g.fillStyle=bg;g.fillRect(0,0,w,h);
 function project(p){const q=SoundField.project(p,0,f,cam);return q?{x:w/2+q.x,y:h*.46+q.y}:null;}
 function line(points,col,width=1,dashed=false){g.strokeStyle=col;g.lineWidth=width;g.setLineDash(dashed?[5,4]:[]);g.beginPath();let pen=false;for(const p of points){const q=p&&project(p);if(q){pen?g.lineTo(q.x,q.y):g.moveTo(q.x,q.y);pen=true;}else pen=false;}g.stroke();g.setLineDash([]);}
 if(world==='mixed'){const corners=[[-8,4,12],[8,4,12],[8,-3,12],[-8,-3,12]].map(project);if(corners.every(Boolean)){g.beginPath();corners.forEach((p,i)=>i?g.lineTo(p.x,p.y):g.moveTo(p.x,p.y));g.closePath();g.fillStyle='#0b5a7c88';g.fill();g.strokeStyle='#7cdef4';g.stroke();}const q=project([-6,3.5,12]);if(q){g.fillStyle='#a4e8ff';g.font='11px system-ui';g.fillText('WATER BEYOND / INTERFACE 12 m',q.x,q.y-6);}}
 for(let z=2;z<=28;z+=2)line([[-14,-1.5,z],[14,-1.5,z]],'#49769266');for(let x=-14;x<=14;x+=2)line([[x,-1.5,2],[x,-1.5,28]],'#49769266');
 for(const i of selected)for(const source of ['air','water']){if(!s[source])continue;for(const kind of ['incident','transmitted','reflected','box']){if((kind==='reflected'||kind==='box')&&!$('reflected').checked)continue;const points=[];let any=false;
  for(let k=0;k<=420;k++){const z=2+k*24/420,paths=fieldPaths(world,z,source,i).filter(p=>p.kind===kind);if(!paths.length){points.push(null);continue;}any=true;const q=paths.reduce((sum,p)=>sum+s[source]*p.gain*Math.sin(2*Math.PI*N[i].frequency*(visualTime-p.delay)),0)*(kind==='transmitted'?boost:1);points.push([lane(i),-.35+q*.48,z]);}

  if(!any)continue;const col=noteColor(i);g.globalAlpha=(kind==='reflected'||kind==='box')?.55:1;if(col==='#050505')line(points,'#a9c2d5',4,(kind==='reflected'||kind==='box'));line(points,col,kind==='transmitted'?2.4:1.7,(kind==='reflected'||kind==='box'));g.globalAlpha=1;
 }
 }
 for(const face of W.faces(boxState())){const corners=face.points.map(project);if(corners.every(Boolean)){g.beginPath();corners.forEach((p,i)=>i?g.lineTo(p.x,p.y):g.moveTo(p.x,p.y));g.closePath();g.fillStyle='#ffc28a12';g.fill();}line([...face.points,face.points[0]],'#ffc28a',2);}
 for(const medium of ['air','water']){if(world!=='mixed'&&world!==medium)continue;const z=medium==='air'?2:26,q=project([0,-.35,z]);if(q){g.fillStyle=s[medium]?'#fff':'#71849a';g.beginPath();g.arc(q.x,q.y,medium==='air'?5:3,0,Math.PI*2);g.fill();g.font='10px system-ui';g.fillText(medium.toUpperCase()+' SOURCE'+(s[medium]?'':' OFF'),q.x+8,q.y+16);}}
 for(const probe of W.probeList([world],{air:true,water:true})){const q=project([0,-.35,probe.z]);if(q){g.strokeStyle=probe.medium==='air'?'#ffd08c':'#78edff';g.strokeRect(q.x-4,q.y-4,8,8);g.fillStyle=g.strokeStyle;g.font='10px system-ui';g.fillText(probe.medium+' probe '+probe.z+' m',q.x+8,q.y-8);}}
 // Mark one forward-moving phase along each enabled source's path.
 const i=[...selected][0];if(i!==undefined)for(const source of ['air','water']){if(!s[source]||(world!=='mixed'&&world!==source))continue;let z;
  if(world!=='mixed'){const distance=(visualTime*W.media[source].speed)%24;z=source==='air'?2+distance:26-distance;}
  else {const first=source==='air'?10:14,second=24-first,c1=W.media[source].speed,c2=W.media[source==='air'?'water':'air'].speed,t=visualTime%(first/c1+second/c2),distance=t<first/c1?t*c1:first+(t-first/c1)*c2;z=source==='air'?2+distance:26-distance;}
  const q=W.obstaclePaths(world,z,source,boxState(),lane(i)).some(p=>p.kind==='incident'||p.kind==='transmitted')&&project([lane(i),-.35,z]);if(q){g.fillStyle=noteColor(i)==='#050505'?'#fff':noteColor(i);g.beginPath();g.arc(q.x,q.y,3,0,Math.PI*2);g.fill();}
 }
 g.fillStyle='#b9d8e9';g.font='11px ui-monospace';g.fillText('FIRST PERSON / '+(world==='mixed'?'AIR NEAR, WATER FAR':world.toUpperCase()),12,h-17);
 const freq=i===undefined?440:N[i].frequency,note=i===undefined?'A4 reference':N[i].name;
 $('stats'+worldNames[world]).textContent=world==='mixed'?'Same '+note+' frequency across the boundary. Dashed = reflection. '+($('boost').checked?'Transmission display 20x; audio unchanged.':'True relative amplitude.'):
 note+': wavelength '+(W.media[world].speed/freq).toFixed(2)+' m. '+(s[world]?'Emitter active.':'Emitter off: enable the '+world+' source.')+' Travel across 24 m: '+(24000/W.media[world].speed).toFixed(1)+' ms.';
}
function drawScope(){const {g,w,h}=surface('scope');g.strokeStyle='#38516b';g.beginPath();g.moveTo(0,h/2);g.lineTo(w,h/2);g.stroke();const live=audio&&audio.state==='running'&&playing;
 if(live){analyser.getFloatTimeDomainData(samples);g.strokeStyle='#89e9d2';g.beginPath();for(let x=0;x<w;x++){const v=samples[Math.min(samples.length-1,Math.floor(x/w*audio.sampleRate*.012))],y=h/2-v*h*3;x?g.lineTo(x,y):g.moveTo(x,y);}g.stroke();}
 $('scopeLabel').textContent=live?'Live post-volume audio / 12 ms / fixed display gain 6x.':'Audio off. Enable sound for the measured waveform.';
}
function render(){for(const world of shown())drawWorld(world);$('clock').textContent='Visual time '+(visualTime*1000).toFixed(2)+' ms';drawScope();}
const coeff=W.boundaryCoefficients('air','water');$('boundaryStats').textContent='Reflected energy: '+(coeff.R*100).toFixed(4)+'%\nTransmitted energy: '+(coeff.T*100).toFixed(4)+'%\nAir -> water pressure reflection: +'+coeff.r.toFixed(5)+'\nWater -> air pressure reflection: '+(-coeff.r).toFixed(5)+' (phase reversal)';
function frame(t){const dt=last?Math.min(.1,(t-last)/1000):0;last=t;if(!paused)visualTime+=dt*+$('slow').value;render();requestAnimationFrame(frame);}
window.addEventListener('pagehide',()=>audio?.suspend());updateBox();requestAnimationFrame(frame);
