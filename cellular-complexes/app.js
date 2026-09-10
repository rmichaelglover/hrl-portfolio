'use strict';
const $=id=>document.getElementById(id),C=CellComplex;
const names={square:'Squares',rectangle:'Rectangles',triangle:'Triangles',cube:'Cubes',tetra:'Tetrahedra'};
for(const id of ['left','right'])for(const [value,text] of Object.entries(names))$(id).add(new Option(text,value));
let fields=[],allFields={},generation=0,running=false,history=[],last=0;
function stop(){running=false;$('run').textContent='Run';$('run').setAttribute('aria-pressed','false');}
function selectFields(){fields=['left','right'].map(id=>allFields[$(id).value]);history=fields[0].history.map((v,i)=>[v,fields[1].history[i]]);}
function changeGeometry(){stop();selectFields();render();}
function reset(){stop();generation=0;const seed=Number($('seed').value);$('seed').value=Number.isFinite(seed)?Math.max(0,Math.min(999999,Math.trunc(seed))):42;
 allFields=Object.fromEntries(Object.keys(names).map(kind=>{const m=C.mesh(kind,['cube','tetra'].includes(kind)?5:18);return [kind,{m,state:C.initial(m,$('pattern').value,+$('seed').value,$('rule').value),changed:0,history:[]}];}));record();render();}
function record(){for(const f of Object.values(allFields)){f.history.push(f.state.reduce((s,x)=>s+(x===1),0)/f.state.length);if(f.history.length>200)f.history.shift();}selectFields();}
function advance(){for(const f of Object.values(allFields)){const result=C.evolve(f.m,f.state,$('rule').value,+$('threshold').value);f.state=result.state;f.changed=result.changed;}generation++;record();render();}
function context(id){const canvas=$(id),dpr=window.devicePixelRatio||1,w=canvas.clientWidth,h=canvas.clientHeight;canvas.width=w*dpr;canvas.height=h*dpr;const ctx=canvas.getContext('2d');ctx.setTransform(dpr,0,0,dpr,0,0);return {ctx,w,h};}
const palette=['#17283f','#77e4c6','#b695f2'];
function drawField(f,id,stats){const {ctx,w,h}=context(id),m=f.m,stretch=m.kind==='rectangle'?1.6:1;
 function point(p){let x=(p[0]/m.n-.5)*stretch,y=p[1]/m.n-.5,z=p[2]/m.n-.5;
  if(m.dim===2){const scale=Math.min((w-30)/stretch,h-30);return [w/2+x*scale,h/2-y*scale,0];}
  const a=+$('yaw').value*Math.PI/180,rx=x*Math.cos(a)+z*Math.sin(a),rz=-x*Math.sin(a)+z*Math.cos(a),ry=y*Math.cos(.55)-rz*Math.sin(.55),depth=y*Math.sin(.55)+rz*Math.cos(.55)+3;
  const scale=Math.min(w,h)*1.45/depth;return [w/2+rx*scale,h/2-ry*scale,depth];
 }
 const points=m.vertices.map(point),polygons=[];
 m.cells.forEach((c,i)=>{
  if(m.dim===2)polygons.push({ids:c.ids,state:f.state[i],depth:0});
  else {if($('layers').value==='slice'){if(c.base[2]!==Math.floor(m.n/2))return;}else if(!f.state[i])return;
   for(const face of c.faces)polygons.push({ids:face,state:f.state[i],depth:face.reduce((s,v)=>s+points[v][2],0)/face.length});}
 });
 polygons.sort((a,b)=>b.depth-a.depth);for(const poly of polygons){ctx.beginPath();poly.ids.forEach((v,i)=>i?ctx.lineTo(points[v][0],points[v][1]):ctx.moveTo(points[v][0],points[v][1]));ctx.closePath();ctx.fillStyle=palette[poly.state];ctx.fill();ctx.lineWidth=m.dim===3?.6:.65;ctx.strokeStyle=m.dim===3?'#233851':'#080f1b';ctx.stroke();}
 if(m.dim===3){ctx.strokeStyle='#69839b';ctx.lineWidth=1;const corners=[[0,0,0],[m.n,0,0],[m.n,m.n,0],[0,m.n,0],[0,0,m.n],[m.n,0,m.n],[m.n,m.n,m.n],[0,m.n,m.n]].map(point);for(const [a,b] of [[0,1],[1,2],[2,3],[3,0],[4,5],[5,6],[6,7],[7,4],[0,4],[1,5],[2,6],[3,7]]){ctx.beginPath();ctx.moveTo(...corners[a].slice(0,2));ctx.lineTo(...corners[b].slice(0,2));ctx.stroke();}}
 const degrees=m.neighbors.map(x=>x.length),count=f.state.reduce((s,x)=>s+(x===1),0);
 $(stats).innerHTML='<b>'+m.cells.length+' cells</b> | '+Math.min(...degrees)+'-'+Math.max(...degrees)+' neighbors (boundary to interior)<br>State 1: <b>'+count+' / '+m.cells.length+' ('+(100*count/m.cells.length).toFixed(1)+'%)</b> | Changed this step: '+f.changed;
}
function drawHistory(){const {ctx,w,h}=context('history');ctx.font='11px system-ui';ctx.fillStyle='#aec3d9';ctx.fillText('100%',3,13);ctx.fillText('0%',3,h-5);ctx.strokeStyle='#24374e';ctx.beginPath();ctx.moveTo(40,h-15);ctx.lineTo(w-8,h-15);ctx.stroke();history[0]?.forEach((_,j)=>{ctx.beginPath();ctx.strokeStyle=j?'#ffcd7c':'#77e4c6';ctx.lineWidth=j?1.5:3;history.forEach((row,i)=>{const x=40+i*(w-50)/Math.max(1,history.length-1),y=12+(1-row[j])*(h-27);i?ctx.lineTo(x,y):ctx.moveTo(x,y);});ctx.stroke();});}
function render(){drawField(fields[0],'a','statsA');drawField(fields[1],'b','statsB');drawHistory();$('generation').textContent='Generation '+generation;
 const [a,b]=fields,rectPair=[a.m.kind,b.m.kind].every(k=>['square','rectangle'].includes(k));
 $('comparison').textContent=rectPair?'Square / rectangle invariant: '+(a.state.every((x,i)=>x===b.state[i])?'all corresponding cell states match.':'states differ.'):
 a.m.dim!==b.m.dim?'Cross-dimensional view: the spatial domains and initial fields are not directly matched. Use a comparison preset for matched dimensions.':'Matched parent-block seed; different cell counts and adjacency. A shared fraction threshold does not make the discrete neighborhoods equivalent.';
}
$('preset').onchange=()=>{const pair={ '2d':['square','triangle'],stretch:['square','rectangle'],'3d':['cube','tetra']}[$('preset').value];$('left').value=pair[0];$('right').value=pair[1];changeGeometry();};
for(const id of ['rule','pattern','seed'])$(id).onchange=reset;
for(const id of ['left','right'])$(id).onchange=()=>{$('preset').value='custom';changeGeometry();};
$('threshold').oninput=()=>{$('thresholdValue').textContent=(+$('threshold').value).toFixed(2);reset();};
$('speed').oninput=()=>{$('speedValue').textContent=$('speed').value;};
$('yaw').oninput=()=>{$('yawValue').textContent=$('yaw').value;render();};$('layers').onchange=render;
$('reset').onclick=reset;$('step').onclick=()=>{stop();advance();};$('run').onclick=()=>{running=!running;$('run').textContent=running?'Pause':'Run';$('run').setAttribute('aria-pressed',String(running));last=performance.now();};
window.addEventListener('resize',render);function tick(time){if(running&&time-last>=1000/+$('speed').value){advance();last=time;}requestAnimationFrame(tick);}
$('right').value='triangle';reset();requestAnimationFrame(tick);
