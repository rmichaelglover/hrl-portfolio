'use strict';
const $=id=>document.getElementById(id),M=SoundField;
const selected=new Set([0,4,7]),account=M.ledger(),initialTotal=M.total(account);
let audio,bus,analyser,samples,voices=[],audible=false,moving=true,openWindow=false,visualTime=0,lastFrame=0,events=[];
function color(i){return M.notes[i].pitch==='C'&&$('cColor').value==='black'?'#050505':M.notes[i].color;}
function amplitude(){return Math.sqrt(account.energy/(account.energy+9));}
function camera(){return {x:+$('side').value,z:0,yaw:+$('yaw').value};}
function updateAudio(){if(!audio)return;const bearing=M.project([0,-.5,2],0,1,camera()),pan=bearing?Math.max(-1,Math.min(1,bearing.x)):0;
 for(let i=0;i<voices.length;i++){voices[i].gain.gain.setTargetAtTime(selected.has(i)?amplitude()/Math.max(1,selected.size):0,audio.currentTime,.03);voices[i].pan.pan.setTargetAtTime(pan,audio.currentTime,.03);}
 bus.gain.setTargetAtTime(audible?+$('volume').value:0,audio.currentTime,.03);
}
function refresh(){[...$('notes').children].forEach((b,i)=>{b.setAttribute('aria-pressed',selected.has(i));b.style.setProperty('--note',color(i));});updateAudio();
 $('ledger').textContent='LOCAL      energy '+account.energy.toFixed(2)+' | matter '+account.matter.toFixed(2)+'\nRESERVOIR  energy '+account.reservoirEnergy.toFixed(2)+' | matter '+account.reservoirMatter.toFixed(2)+'\nTOTAL EQUIVALENT  '+M.total(account).toFixed(2)+' / initial '+initialTotal.toFixed(2);
 $('status').textContent=audible?(selected.size?'Sound enabled. '+selected.size+' notes selected.':'Sound enabled; empty selection is silent.'):'Sound off. Visual preview active.';
}
M.notes.forEach((note,i)=>{const b=document.createElement('button');b.className='key';b.innerHTML=note.name+'<small>'+note.frequency.toFixed(1)+' Hz</small>';b.title=note.name+' / '+note.frequency.toFixed(2)+' Hz';b.onclick=()=>{selected.has(i)?selected.delete(i):selected.add(i);refresh();};$('notes').append(b);});
function choose(list){selected.clear();list.forEach(i=>selected.add(i));refresh();}
$('major').onclick=()=>choose([0,4,7]);$('scale').onclick=()=>choose([0,2,4,5,7,9,11,12]);$('silence').onclick=()=>choose([]);
$('play').onclick=async()=>{try{
 if(!audio){audio=new AudioContext();bus=audio.createGain();bus.gain.value=0;analyser=audio.createAnalyser();analyser.fftSize=2048;samples=new Float32Array(analyser.fftSize);bus.connect(analyser);analyser.connect(audio.destination);
 voices=M.notes.map(note=>{const oscillator=audio.createOscillator(),gain=audio.createGain(),pan=audio.createStereoPanner();oscillator.type='sine';oscillator.frequency.value=note.frequency;gain.gain.value=0;oscillator.connect(gain);gain.connect(pan);pan.connect(bus);oscillator.start();return {oscillator,gain,pan};});}
 await audio.resume();audible=!audible;$('play').textContent=audible?'Mute sound':'Enable sound';$('play').setAttribute('aria-pressed',String(audible));refresh();
 }catch(e){$('status').textContent='Audio unavailable: '+e.message;}};
$('motion').onclick=()=>{moving=!moving;$('motion').textContent=moving?'Pause wave motion':'Resume wave motion';$('motion').setAttribute('aria-pressed',String(moving));};
$('window').onclick=()=>{openWindow=!openWindow;$('window').textContent=openWindow?'Close release window':'Open release window';$('window').setAttribute('aria-pressed',String(openWindow));};
function exchange(type,amount){const moved=M.transfer(account,type,amount);if(moved>0)events.push({type,life:1});return moved;}
document.querySelectorAll('[data-exchange]').forEach(b=>b.onclick=()=>{const type=b.dataset.exchange,moved=exchange(type,1);$('exchange').textContent=type+': transferred '+moved.toFixed(2)+' '+(type.startsWith('matter')?'matter tokens':'energy units')+'.';refresh();});
$('toEnergy').onclick=()=>{$('exchange').textContent='Converted '+M.convert(account,'toEnergy').toFixed(2)+' matter tokens to energy.';refresh();};
$('toMatter').onclick=()=>{$('exchange').textContent='Converted energy into '+M.convert(account,'toMatter').toFixed(2)+' matter tokens.';refresh();};
for(const id of ['side','yaw','baseline','fov','slow'])$(id).oninput=()=>{$(id+'Value').textContent=$(id).value+(id==='yaw'||id==='fov'?' deg':id==='slow'?'x':'');updateAudio();};
$('volume').oninput=updateAudio;$('cColor').onchange=refresh;$('home').onclick=()=>{for(const id of ['side','yaw']){$(id).value=0;$(id).oninput();}};
function surface(id){const c=$(id),r=window.devicePixelRatio||1,w=c.clientWidth,h=c.clientHeight;if(c.width!==Math.round(w*r)||c.height!==Math.round(h*r)){c.width=Math.round(w*r);c.height=Math.round(h*r);}const g=c.getContext('2d');g.setTransform(r,0,0,r,0,0);g.clearRect(0,0,w,h);return {g,w,h};}
function wavePoint(i,z){const phase=2*Math.PI*M.notes[i].frequency*((z-2)/343-visualTime);return [(i-6)*.07*(z-2),-.5+amplitude()*.18*Math.sin(phase),z];}
function drawField(){const {g,w,h}=surface('field'),stereo=$('view').value==='stereo',panels=stereo?2:1,vw=w/panels,f=vw/2/Math.tan(+$('fov').value*Math.PI/360),cam=camera(),base=+$('baseline').value;
 const tracerIndex=[...selected][0],tracerZ=3+(visualTime*343)%23,tracer=tracerIndex===undefined?null:wavePoint(tracerIndex,tracerZ);let traced=[];
 for(let eyeIndex=0;eyeIndex<panels;eyeIndex++){const eye=stereo?(eyeIndex-.5)*base:0,offset=eyeIndex*vw;
  const point=p=>{const v=M.project(p,eye,f,cam);return v?{x:offset+vw/2+v.x,y:h/2+v.y,depth:v.depth}:null;};
  g.save();g.beginPath();g.rect(offset,0,vw,h);g.clip();
  const gradient=g.createLinearGradient(0,0,0,h);gradient.addColorStop(0,'#050a17');gradient.addColorStop(1,'#12243a');g.fillStyle=gradient;g.fillRect(offset,0,vw,h);
  function path(points,stroke,width=1){g.strokeStyle=stroke;g.lineWidth=width;g.beginPath();let pen=false;for(const p of points){const q=point(p);if(q){pen?g.lineTo(q.x,q.y):g.moveTo(q.x,q.y);pen=true;}else pen=false;}g.stroke();}
  for(let z=2;z<=40;z+=2)path([[-12,-1.6,z],[12,-1.6,z]],'#233b55');for(let x=-12;x<=12;x+=2)path([[x,-1.6,2],[x,-1.6,40]],'#233b55');
  for(const x of [-3,3])path([[x,-1.4,10],[x,1.4,10],[x,1.4,13],[x,-1.4,13],[x,-1.4,10]],openWindow?'#e6c782':'#526c88',2);
  for(const i of selected){const points=[];for(let k=0;k<=600;k++){const z=2+k*26/600;points.push(wavePoint(i,z));}if(color(i)==='#050505')path(points,'#a9bbcf',4);path(points,color(i),2);
   const tag=point(wavePoint(i,6));if(tag){g.fillStyle=color(i)==='#050505'?'#c0ccdd':color(i);g.font='11px system-ui';g.fillText(M.notes[i].name,tag.x+4,tag.y-12);}}
  const source=point([0,-.5,2]);if(source){g.strokeStyle='#fff';g.lineWidth=2;g.beginPath();g.arc(source.x,source.y,10,0,Math.PI*2);g.stroke();g.fillStyle='#08101c';g.fill();g.fillStyle='#d3e5f8';g.font='11px system-ui';g.fillText('0 / conductor',source.x+15,source.y+4);}
  for(let i=0;i<Math.min(30,Math.floor(account.matter));i++){const a=i*2.399,rad=.15+.035*Math.sqrt(i),p=point([Math.cos(a)*rad,-.5+Math.sin(a)*rad,2.2+i*.012]);if(p){g.fillStyle='#ffce83';g.fillRect(p.x-2,p.y-2,4,4);}}
  for(const e of events){const t=e.type.endsWith('In')?e.life:1-e.life,p=point([3*t,-.5,2+9*t]);if(p){g.fillStyle=e.type.startsWith('matter')?'#ffce83':'#8decd6';g.beginPath();g.arc(p.x,p.y,3,0,Math.PI*2);g.fill();}}
  if(tracer){const p=point(tracer);if(p){traced.push(p);g.setLineDash([6,6]);g.strokeStyle='#c3d8f388';g.beginPath();g.moveTo(offset,p.y);g.lineTo(offset+vw,p.y);g.stroke();g.setLineDash([]);g.strokeStyle='#fff';g.lineWidth=2;g.beginPath();g.arc(p.x,p.y,6,0,Math.PI*2);g.stroke();}}
  g.fillStyle='#90aecd';g.font='12px ui-monospace';g.fillText(stereo?(eyeIndex?'RIGHT EYE':'LEFT EYE'):'FIRST PERSON',offset+16,h-18);g.restore();
 }
 if(stereo){g.strokeStyle='#47617e';g.beginPath();g.moveTo(vw,0);g.lineTo(vw,h);g.stroke();}
 $('hud').textContent='OUTGOING PRESSURE TRACES / '+(moving?'VISUAL TIME '+visualTime.toFixed(3)+' s':'VISUAL PAUSED');
 $('stereoReadout').textContent=traced.length===2?'Tracer depth: '+traced[0].depth.toFixed(2)+'\nDisparity: '+(traced[0].x-(traced[1].x-vw)).toFixed(2)+' px\nEpipolar row error: '+Math.abs(traced[0].y-traced[1].y).toFixed(6)+' px':stereo?'Select a note to track stereo correspondence.':'Single camera: switch to two eyes for epipolar correspondence.';
}
function drawScope(){const {g,w,h}=surface('scope');g.strokeStyle='#28405c';g.beginPath();g.moveTo(0,h/2);g.lineTo(w,h/2);g.stroke();const live=audible&&audio?.state==='running';if(live)analyser.getFloatTimeDomainData(samples);
 g.strokeStyle='#8be9d7';g.lineWidth=1.5;g.beginPath();for(let x=0;x<w;x++){let signal=0;if(live){signal=samples[Math.min(samples.length-1,Math.floor(x/w*audio.sampleRate*.012))];}else{for(const i of selected)signal+=Math.sin(2*Math.PI*M.notes[i].frequency*(x/w*.012-visualTime));signal*=amplitude()*+$('volume').value/Math.max(1,selected.size);}const y=h/2-signal*h*1.7;x?g.lineTo(x,y):g.moveTo(x,y);}g.stroke();$('scopeLabel').textContent=(live?'Live post-volume audio waveform':'Silent mathematical preview')+' / 12 ms window / display gain 3.4x. Visual slow motion does not lower audio pitch.';
}
function frame(now){const dt=lastFrame?Math.min(.1,(now-lastFrame)/1000):0;lastFrame=now;if(moving){visualTime+=dt*+$('slow').value;if(openWindow&&account.energy>0){M.transfer(account,'energyOut',dt);refresh();}events=events.map(e=>({...e,life:e.life-dt*.6})).filter(e=>e.life>0);}drawField();drawScope();requestAnimationFrame(frame);}
window.addEventListener('pagehide',()=>{if(audio)audio.suspend();});refresh();requestAnimationFrame(frame);
