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
const api={media,start,boundary,end,boundaryCoefficients,mediumAt,paths,sample,probeList};root.WaveWorld=api;if(typeof module!=='undefined')module.exports=api;
})(globalThis);
