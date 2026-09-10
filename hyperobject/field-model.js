(function(root){
'use strict';
const labels=['C','C#','D','D#','E','F','F#','G','G#','A','A#','B','C'];
const colors=['#ffffff','#ffd1e3','#ff94bf','#ed426d','#ff0000','#ffff00','#a6ed36','#00ff00','#66dca9','#00ffff','#20bce0','#0000ff','#ffffff'];
const notes=labels.map((name,i)=>({name:name+(i===12?'5':'4'),pitch:name,color:colors[i],frequency:440*2**((i-9)/12)}));
function project(p,eye,f,camera){const a=camera.yaw*Math.PI/180,x=p[0]-camera.x,z=p[2]-camera.z;const X=x*Math.cos(a)-z*Math.sin(a),Z=x*Math.sin(a)+z*Math.cos(a);if(Z<=.15)return null;return {x:f*(X-eye)/Z,y:-f*p[1]/Z,depth:Z};}
function ledger(){return {energy:9,matter:6,reservoirEnergy:91,reservoirMatter:24,c:2};}
function transfer(s,type,amount){const source={energyIn:'reservoirEnergy',energyOut:'energy',matterIn:'reservoirMatter',matterOut:'matter'}[type],target={energyIn:'energy',energyOut:'reservoirEnergy',matterIn:'matter',matterOut:'reservoirMatter'}[type];if(!source)throw Error('Unknown exchange');const moved=Math.min(s[source],Math.max(0,amount));s[source]-=moved;s[target]+=moved;return moved;}
function convert(s,direction){if(direction==='toEnergy'){const m=Math.min(1,s.matter);s.matter-=m;s.energy+=m*s.c*s.c;return m;}const m=Math.min(1,s.energy/(s.c*s.c));s.energy-=m*s.c*s.c;s.matter+=m;return m;}
function total(s){return s.energy+s.reservoirEnergy+(s.matter+s.reservoirMatter)*s.c*s.c;}
const api={notes,project,ledger,transfer,convert,total};root.SoundField=api;if(typeof module!=='undefined')module.exports=api;
})(globalThis);
