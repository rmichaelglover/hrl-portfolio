/* Original glackyard wildlife illustrations for Michael Emanuel Glover's Glims. */
'use strict';
window.GlimsWildlife=(()=>{
const catalog=[
 {id:'owl',name:'Owls',x:10.5,y:.55,kind:'owl',color:'#aa8d68',note:'An owl watches from the tree. Evening lights bring open eyes and a gentle head bob.'},
 {id:'chipmunk',name:'Chipmunks',x:1.1,y:5.8,kind:'rodent',color:'#b9814e',note:'Striped chipmunks make tiny, darting trips near the porch.'},
 {id:'squirrel',name:'Squirrels',x:10.6,y:6,kind:'rodent',color:'#a99580',note:'A squirrel with a great curling tail investigates the trees.'},
 {id:'bird',name:'Birds',x:4.4,y:.45,kind:'bird',color:'#6b9eb4',note:'Little blue birds flit through the garden by day and settle down in the evening.'},
 {id:'fish',name:'Fishies',x:0,y:2.1,kind:'fish',color:'#e7b36d',note:'Fishies swim with the creek’s curves, staying in the water and below the footbridge.'},
 {id:'frog',name:'Froggies',x:6.35,y:6.1,kind:'frog',color:'#87a95e',note:'Froggies make little hops beside the creek. Their ripples drift away.'},
 {id:'lizard',name:'Lizards',x:9.1,y:2.2,kind:'lizard',color:'#8caa74',note:'A green lizard pauses by the warm garden stones, then gives a little tail flick.'},
 {id:'skink',name:'Skinks',x:5.1,y:6.3,kind:'lizard',color:'#b88b64',note:'A striped skink slips through the grass, showing a bright blue tail.'}
];
function positions(time,night,creek){return catalog.map((a,i)=>{const rest=night&&['chipmunk','squirrel','bird','lizard','skink'].includes(a.id),t=rest?0:time;let x=a.x+Math.sin(t*.65+i)*.2,y=a.y+Math.sin(t*.4+i)*.1;if(a.id==='owl'){x=a.x;y=a.y;}if(a.id==='fish'){y=a.y+Math.sin(time*.32)*.48;x=creek(y)+Math.sin(time*.6)*.18;}if(a.id==='frog'){x=a.x+Math.max(0,Math.sin(time*1.6))*.16;y=a.y-Math.max(0,Math.sin(time*1.6))*.12;}return {...a,x,y,rest};});}
function draw(ctx,point,scale,time,night,creek,selected){const animals=positions(time,night,creek);for(const a of animals){const p=point(a.x,a.y),size=Math.max(13,Math.min(24,scale*.34));ctx.save();ctx.translate(p.x,p.y);ctx.scale(size/20,size/20);ctx.lineCap='round';ctx.lineJoin='round';
 const ellipse=(x,y,rx,ry,color)=>{ctx.fillStyle=color;ctx.beginPath();ctx.ellipse(x,y,rx,ry,0,0,Math.PI*2);ctx.fill();};
 const line=(points,color,width=2)=>{ctx.strokeStyle=color;ctx.lineWidth=width;ctx.beginPath();points.forEach(([x,y],i)=>i?ctx.lineTo(x,y):ctx.moveTo(x,y));ctx.stroke();};
 const poly=(points,color)=>{ctx.fillStyle=color;ctx.beginPath();points.forEach(([x,y],i)=>i?ctx.lineTo(x,y):ctx.moveTo(x,y));ctx.closePath();ctx.fill();};
 if(a.id===selected){ctx.strokeStyle='#f6e4b5';ctx.lineWidth=1.5;ctx.beginPath();ctx.arc(0,0,18,0,Math.PI*2);ctx.stroke();}
 ellipse(0,8,12,3,'#173e3928');
 if(a.kind==='owl'){ellipse(0,0,10,13,a.color);poly([[-10,-8],[-9,-18],[-2,-11]],a.color);poly([[10,-8],[9,-18],[2,-11]],a.color);ellipse(-4,-4,4,5,'#e6d8b5');ellipse(4,-4,4,5,'#e6d8b5');if(night){ellipse(-4,-4,1.7,2,'#2f4240');ellipse(4,-4,1.7,2,'#2f4240');}else{line([[-6,-3],[-3,-2]],'#625746');line([[3,-2],[6,-3]],'#625746');}poly([[-2,0],[2,0],[0,4]],'#d5a65e');line([[-9,3],[-6,9]],'#83694c');line([[9,3],[6,9]],'#83694c');}
 if(a.kind==='rodent'){if(a.id==='squirrel'){ctx.strokeStyle=a.color;ctx.lineWidth=7;ctx.beginPath();ctx.moveTo(-7,3);ctx.bezierCurveTo(-25,-1,-18,-22,-10,-13);ctx.stroke();}else line([[-8,5],[-17,1],[-19,-4]],a.color,5);ellipse(0,3,10,6,a.color);ellipse(8,-2,6,6,a.color);ellipse(6,-8,3,4,a.color);ellipse(10,-3,1,1,'#293e35');if(a.id==='chipmunk'){line([[-7,0],[3,0]],'#f4dfb1',2);line([[-7,3],[2,3]],'#65533e',2);}line([[-4,7],[-6,10]],'#65533e');line([[7,5],[9,9]],'#65533e');}
 if(a.kind==='bird'){poly([[-7,3],[-17,0],[-14,7]],a.color);ellipse(0,1,10,7,a.color);ellipse(7,-5,6,6,a.color);poly([[12,-5],[18,-2],[12,0]],'#ddba76');ellipse(8,-6,1.2,1.2,'#263e40');line([[-5,0],[2,5],[5,0]],'#476f83');line([[0,7],[0,12],[4,12]],'#94754e');}
 if(a.kind==='fish'){poly([[-7,0],[-16,-7],[-16,7]],a.color);ellipse(0,0,10,5,a.color);ellipse(6,-1,1,1,'#385c59');line([[0,-3],[-3,-7]],a.color);ctx.strokeStyle='#d5ebe080';ctx.lineWidth=1;ctx.beginPath();ctx.ellipse(0,1,17,9,0,0,Math.PI*2);ctx.stroke();}
 if(a.kind==='frog'){ellipse(0,3,10,7,a.color);ellipse(-7,7,6,3,a.color);ellipse(7,7,6,3,a.color);ellipse(-5,-3,4,5,a.color);ellipse(5,-3,4,5,a.color);ellipse(-5,-4,2,2,'#e5e9bf');ellipse(5,-4,2,2,'#e5e9bf');ellipse(-5,-4,1,1,'#314b38');ellipse(5,-4,1,1,'#314b38');line([[-3,4],[0,5],[3,4]],'#4f7147',1);}
 if(a.kind==='lizard'){line([[-6,2],[-15,4],[-23,1],[-28,-3+Math.sin(time*2)]],a.id==='skink'?'#70afc7':a.color,3);ellipse(0,0,11,4,a.color);ellipse(10,-1,6,4,a.color);for(const sign of [-1,1]){line([[-5,sign*2],[-9,sign*7],[-5,sign*8]],a.color);line([[5,sign*2],[8,sign*7],[12,sign*7]],a.color);}if(a.id==='skink')line([[-8,-1],[10,-1]],'#f0db9f',1.5);ellipse(12,-2,1,1,'#263f34');}
 ctx.restore();}return animals;}
return {catalog,positions,draw};
})();
