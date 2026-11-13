'use strict';
(async()=>{
const $=s=>document.getElementById(s),svg=$('garden'),colors=['#477b65','#ac705a','#8b7395','#a07e35','#427b95'];
let replay,index=0,playing=false,last=0;
const ns='http://www.w3.org/2000/svg';
function el(tag,attrs,text){const n=document.createElementNS(ns,tag);for(const [k,v] of Object.entries(attrs))n.setAttribute(k,v);if(text!==undefined)n.textContent=text;svg.append(n);return n;}
const pos=p=>[50+p[0]*100,50+p[1]*100];
function line(a,b,c,dash){const [x1,y1]=pos(a),[x2,y2]=pos(b);el('line',{x1,y1,x2,y2,stroke:c,'stroke-width':dash?3:7,'stroke-dasharray':dash?'7 7':'none','stroke-linecap':'round',opacity:.7});}
function render(){const s=replay.states[index];svg.replaceChildren();
for(let y=0;y<7;y++)for(let x=0;x<9;x++){el('rect',{x:x*100+3,y:y*100+3,width:94,height:94,rx:18,fill:(x+y)%2?'#d9dfc0':'#e9e9cf'});}
for(const p of s.walls){const [cx,cy]=pos(p);el('rect',{x:cx-42,y:cy-42,width:84,height:84,rx:25,fill:'#718d63'});el('text',{x:cx,y:cy+5,'text-anchor':'middle',fill:'#e8ecd6','font-size':14},'HEDGE');}
for(const p of s.roses){const [cx,cy]=pos(p);for(let j=0;j<5;j++)el('circle',{cx:cx+Math.cos(j*1.256)*13,cy:cy+Math.sin(j*1.256)*13,r:10,fill:'#c68488',opacity:.65});el('circle',{cx,cy,r:7,fill:'#e9cf88'});}
for(let i=0;i<s.people.length;i++){const p=s.people[i],[cx,cy]=pos(p.goal);el('circle',{cx,cy,r:33,fill:'none',stroke:colors[i],'stroke-width':2,'stroke-dasharray':'3 5'});}
if(index&&s.decision.from){s.people.forEach((p,i)=>{if($('intentions').checked)line(s.decision.from[i],s.decision.preferred[i],colors[i],true);line(s.decision.from[i],p.position,colors[i],false);});}
const [fx,fy]=pos(s.frog);el('ellipse',{cx:fx,cy:fy+4,rx:18,ry:13,fill:'#6d984a'});for(const dx of [-9,9]){el('circle',{cx:fx+dx,cy:fy-7,r:7,fill:'#6d984a'});el('circle',{cx:fx+dx,cy:fy-8,r:3,fill:'#fff5cb'});}el('text',{x:fx,y:fy+35,'text-anchor':'middle','font-size':13,fill:'#3f613e'},'FROG');
s.people.forEach((p,i)=>{const [cx,cy]=pos(p.position);el('circle',{cx,cy,r:23,fill:colors[i],stroke:'#fff8e7','stroke-width':3});el('text',{x:cx,y:cy+6,'text-anchor':'middle','font-size':20,fill:'#fff8e7'},p.name[0]);el('text',{x:cx,y:cy+43,'text-anchor':'middle','font-size':15,fill:'#243f36','font-family':'system-ui'},p.name);});
$('turn').textContent=`${index} / ${replay.states.length-1}`;$('scrub').value=index;
$('ledger').replaceChildren(...s.people.map((p,i)=>{const n=document.createElement('div');n.className='person';n.style.borderColor=colors[i];const name=document.createElement('strong');name.textContent=p.name;const note=document.createElement('small');note.textContent=`${p.position.every((v,j)=>v===p.goal[j])?'At destination':'On the way'} · Rose pauses: ${p.rose_pauses}`;n.append(name,note);return n;}));
const arrived=s.people.filter(p=>p.position.every((v,j)=>v===p.goal[j])).length;
$('status').textContent=arrived===5?'Everyone has arrived. The frog is safe, and there was time for roses.':s.decision.reason;
$('play').textContent=playing?'Pause':'Play walk';
}
try{const r=await fetch('replay.json');if(!r.ok)throw Error(r.status);replay=await r.json();$('scrub').max=replay.states.length-1;const p=replay.profile;$('profile').textContent=`${p.games.map(g=>g.white+' – '+g.black).join('; ')}: ${p.plies} legal plies, ${(p.quiet_fraction*100).toFixed(1)}% non-capturing moves. Progress weight ${p.weights.progress.toFixed(3)}; anticipation weight ${p.weights.anticipation.toFixed(3)}.`;
$('play').onclick=()=>{if(index===replay.states.length-1)index=0;playing=!playing;last=0;render();};$('step').onclick=()=>{playing=false;index=Math.min(index+1,replay.states.length-1);render();};$('restart').onclick=()=>{playing=false;index=0;render();};$('scrub').oninput=()=>{playing=false;index=+$('scrub').value;render();};$('intentions').onchange=render;render();
requestAnimationFrame(function frame(t){if(playing&&(!last||t-last>650)){last=t;index=Math.min(index+1,replay.states.length-1);if(index===replay.states.length-1)playing=false;render();}requestAnimationFrame(frame);});
}catch(e){$('status').textContent='The recorded garden could not load. Reload the page to try again.';for(const id of ['play','step','restart','scrub'])$(id).disabled=true;}
})();
