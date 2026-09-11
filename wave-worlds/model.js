/* Lossless, linear, normal-incidence plane-wave model; distance in meters. */
(function(root){
'use strict';
const media={air:{density:1.204,speed:343},water:{density:998.2,speed:1482}};
for(const m of Object.values(media))m.impedance=m.density*m.speed;
const start=2,boundary=12,end=26;
function boundaryCoefficients(from,to){const a=media[from].impedance,b=media[to].impedance,r=(b-a)/(b+a),tp=2*b/(a+b),T=4*a*b/(a+b)**2;return {r,tp,R:r*r,T,t:Math.sqrt(T)};}
function mediumAt(world,z){return world==='mixed'?(z<boundary?'air':'water'):world;}
function paths(world,z,source){
 if(z<start||z>end)throw Error('Point outside field');
 if(world!=='mixed')return world===source?[{kind:'incident',source,medium:world,gain:1,delay:(source==='air'?z-start:end-z)/media[world].speed}]:[];
 const target=source==='air'?'water':'air',c=media[source].speed,d=media[target].speed,k=boundaryCoefficients(source,target);
 if(source==='air')return z<boundary?[
  {kind:'incident',source,medium:source,gain:1,delay:(z-start)/c},
  {kind:'reflected',source,medium:source,gain:k.r,delay:(2*boundary-start-z)/c}
 ]:[{kind:'transmitted',source,medium:target,gain:k.t,delay:(boundary-start)/c+(z-boundary)/d}];
 return z>=boundary?[
  {kind:'incident',source,medium:source,gain:1,delay:(end-z)/c},
  {kind:'reflected',source,medium:source,gain:k.r,delay:(end+z-2*boundary)/c}
 ]:[{kind:'transmitted',source,medium:target,gain:k.t,delay:(end-boundary)/c+(boundary-z)/d}];
}
function sample(world,z,frequency,time,sources,boost=1){let value=0;
 for(const source of ['air','water'])for(const p of paths(world,z,source))value+=(sources[source]||0)*p.gain*(p.kind==='transmitted'?boost:1)*Math.sin(2*Math.PI*frequency*(time-p.delay));
 return value;
}
function probeList(worlds,hear){const out=[];for(const world of worlds){if(world!=='water'&&hear.air)out.push({world,medium:'air',z:7});if(world!=='air'&&hear.water)out.push({world,medium:'water',z:19});}return out;}
// Finite, axis-aligned rigid faces. Axial rays only; at most four encounters.
function faces(box){
 if(!box?.enabled)return [];
 const h=box.size/2,x=box.x,y=box.y,z=box.z;
 const all=[
 {name:'near',axis:2,value:z-h,points:[[x-h,y-h,z-h],[x+h,y-h,z-h],[x+h,y+h,z-h],[x-h,y+h,z-h]]},
 {name:'far',axis:2,value:z+h,points:[[x-h,y-h,z+h],[x+h,y-h,z+h],[x+h,y+h,z+h],[x-h,y+h,z+h]]},
 {name:'top',axis:1,points:[[x-h,y+h,z-h],[x+h,y+h,z-h],[x+h,y+h,z+h],[x-h,y+h,z+h]]},
 {name:'bottom',axis:1,points:[[x-h,y-h,z-h],[x+h,y-h,z-h],[x+h,y-h,z+h],[x-h,y-h,z+h]]},
 {name:'left',axis:0,points:[[x-h,y-h,z-h],[x-h,y+h,z-h],[x-h,y+h,z+h],[x-h,y-h,z+h]]},
 {name:'right',axis:0,points:[[x+h,y-h,z-h],[x+h,y+h,z-h],[x+h,y+h,z+h],[x+h,y-h,z+h]]}];
 return all.filter(f=>box.form==='closed'||(box.form==='open'?f.name!==box.face:f.name===box.face));
}
function obstaclePaths(world,z,source,box,x=0,y=-.35){
 if(!box?.enabled)return paths(world,z,source);
 if(world!=='mixed'&&world!==source)return [];
 const walls=Math.abs(x-box.x)<=box.size/2&&Math.abs(y-box.y)<=box.size/2?faces(box).filter(f=>f.axis===2).map(f=>f.value):[];
 if(!walls.length)return paths(world,z,source);
 const out=[];
 function travel(pos,dir,medium,gain,delay,depth,kind){
  let stop=dir>0?end:start,event='end';
  for(const w of walls)if((w-pos)*dir>1e-7&&(stop-w)*dir>=0){stop=w;event='wall';}
  if(world==='mixed'&&(boundary-pos)*dir>1e-7&&(stop-boundary)*dir>1e-7){stop=boundary;event='interface';}
  if((z-pos)*dir>=-1e-8&&(stop-z)*dir>=0)out.push({kind,source,medium,gain,delay:delay+Math.abs(z-pos)/media[medium].speed});
  if(event==='end'||depth===4)return;
  const t=delay+Math.abs(stop-pos)/media[medium].speed;
  if(event==='wall')travel(stop,-dir,medium,gain,t,depth+1,'box');
  else {const other=medium==='air'?'water':'air',k=boundaryCoefficients(medium,other);
   travel(stop,-dir,medium,gain*k.r,t,depth+1,kind==='box'?'box':'reflected');
   travel(stop,dir,other,gain*k.t,t,depth+1,kind==='box'?'box':'transmitted');}
 }
 travel(source==='air'?start:end,source==='air'?1:-1,source,1,0,0,'incident');
 return out;
}
const api={faces,obstaclePaths,media,start,boundary,end,boundaryCoefficients,mediumAt,paths,sample,probeList};root.WaveWorld=api;if(typeof module!=='undefined')module.exports=api;
})(globalThis);
