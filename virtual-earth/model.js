/* SPDX-License-Identifier: MIT -- Copyright (c) 2026 R. Michael Glover */
(function(root){
'use strict';
const N=72, SIZE=1400, MAX_AGENTS=1200;
const wrap=(x,n)=>((x%n)+n)%n;
const clamp=(x,a,b)=>Math.max(a,Math.min(b,x));
function random(seed){let state=(seed>>>0)||1;const rng=()=>{state^=state<<13;state^=state>>>17;state^=state<<5;return (state>>>0)/4294967296;};rng.state=()=>state>>>0;return rng;}
function hash(x,y,seed){let h=Math.imul(x^seed,374761393)^Math.imul(y,668265263);h=Math.imul(h^(h>>>13),1274126177);return ((h^(h>>>16))>>>0)/4294967295;}
function noise(x,y,seed){const ix=Math.floor(x),iy=Math.floor(y),a=x-ix,b=y-iy,u=a*a*(3-2*a),v=b*b*(3-2*b);return (hash(ix,iy,seed)*(1-u)+hash(ix+1,iy,seed)*u)*(1-v)+(hash(ix,iy+1,seed)*(1-u)+hash(ix+1,iy+1,seed)*u)*v;}
function terrain(x,y,seed){return noise(x/240,y/240,seed)*.6+noise(x/90,y/90,seed+1)*.28+noise(x/34,y/34,seed+2)*.12;}
class Ecosystem{
 constructor({seed=2026,population=180,aquatic=false,latitude=0}={}){
  this.seed=seed>>>0;this.rng=random(this.seed);this.aquatic=!!aquatic;this.latitude=latitude;this.time=0;this.births=0;this.deaths=0;this.nextId=0;this.agents=[];
  this.height=new Float32Array(N*N);this.moisture=new Float32Array(N*N);this.food=new Float32Array(N*N);this.water=new Uint8Array(N*N);
  for(let y=0;y<N;y++)for(let x=0;x<N;x++){const i=y*N+x,h=terrain(x/N*SIZE,y/N*SIZE,this.seed);this.height[i]=h;this.water[i]=aquatic||h<.27?1:0;this.moisture[i]=clamp(1-h*.65-Math.abs(latitude)/180,.12,1);this.food[i]=this.capacity(i)*(.35+this.rng()*.6);}
  for(let i=0;i<clamp(Math.floor(population),0,MAX_AGENTS);i++)this.spawn();
 }
 index(x,y){return Math.floor(wrap(y,SIZE)/SIZE*N)*N+Math.floor(wrap(x,SIZE)/SIZE*N);}
 capacity(i){return this.water[i]?.65:clamp(this.moisture[i]*(1-Math.max(0,this.height[i]-.7)),.05,1);}
 spawn(parent){
  const type=parent?parent.type:this.aquatic?4:(this.rng()<.09?2:this.rng()<.2?3:this.rng()<.5?0:1);
  let x,y,found=false;
  for(let k=0;k<100;k++){x=parent?wrap(parent.x+(this.rng()-.5)*40,SIZE):this.rng()*SIZE;y=parent?wrap(parent.y+(this.rng()-.5)*40,SIZE):this.rng()*SIZE;const wet=this.water[this.index(x,y)];if(type===3||Boolean(wet)===(type===4)){found=true;break;}}
  if(!found)return false;
  this.agents.push({id:this.nextId++,type,x,y,angle:this.rng()*Math.PI*2,energy:parent?.5:.45+this.rng()*.4,age:0,phase:this.rng()*Math.PI*2,activity:0});return true;
 }
 delta(a,b){let d=a-b;if(d>SIZE/2)d-=SIZE;if(d<-SIZE/2)d+=SIZE;return d;}
 step(dt){
  dt=clamp(Number(dt)||0,0,.1);if(!dt)return;this.time+=dt;
  const season=.7+.3*Math.sin(this.time*.005);
  for(let i=0;i<this.food.length;i++){const cap=this.capacity(i);this.food[i]=clamp(this.food[i]+dt*.012*this.moisture[i]*season*(1-this.food[i]/Math.max(.01,cap)),0,cap);}
  // Spatial bins keep local interactions bounded instead of all-pairs scans.
  const bins=new Map(),B=20,cell=SIZE/B;
  for(const a of this.agents){const key=Math.floor(a.y/cell)*B+Math.floor(a.x/cell);if(!bins.has(key))bins.set(key,[]);bins.get(key).push(a);}
  const nearby=a=>{const list=[],bx=Math.floor(a.x/cell),by=Math.floor(a.y/cell);for(let j=-1;j<=1;j++)for(let i=-1;i<=1;i++)list.push(...(bins.get(wrap(by+j,B)*B+wrap(bx+i,B))||[]));return list;};
  const newborn=[];
  for(const a of this.agents){
   if(a.energy<=0)continue;
   a.age+=dt;a.phase+=dt*(a.type===3?12:5);let best=-Infinity,heading=a.angle;
   const neighbors=nearby(a);let threat=null,prey=null,nearThreat=90,nearPrey=130;
   for(const b of neighbors){if(a===b||b.energy<=0)continue;const d=Math.hypot(this.delta(b.x,a.x),this.delta(b.y,a.y));if(a.type!==2&&a.type!==3&&a.type!==4&&b.type===2&&d<nearThreat){threat=b;nearThreat=d;}if(a.type===2&&(b.type===0||b.type===1)&&d<nearPrey){prey=b;nearPrey=d;}}
   if(threat)heading=Math.atan2(this.delta(a.y,threat.y),this.delta(a.x,threat.x));
   else if(prey)heading=Math.atan2(this.delta(prey.y,a.y),this.delta(prey.x,a.x));
   else for(let k=0;k<10;k++){const angle=a.angle+(this.rng()-.5)*Math.PI*1.7,d=12+this.rng()*35,x=wrap(a.x+Math.cos(angle)*d,SIZE),y=wrap(a.y+Math.sin(angle)*d,SIZE),i=this.index(x,y);if(a.type!==3&&Boolean(this.water[i])!==(a.type===4))continue;let score=this.food[i]-.08*Math.abs(angle-a.angle)+this.rng()*.07;for(const b of neighbors)if(b!==a&&Math.hypot(this.delta(b.x,x),this.delta(b.y,y))<10)score-=.1;if(score>best){best=score;heading=angle;}}
   a.angle+=Math.atan2(Math.sin(heading-a.angle),Math.cos(heading-a.angle))*Math.min(1,dt*5);
   const i=this.index(a.x,a.y);a.activity=0;
   if(a.type!==2&&!threat&&this.food[i]>.02){const bite=Math.min(this.food[i],dt*(a.type===0?.022:.012));this.food[i]-=bite;a.energy=Math.min(1.5,a.energy+bite*2);a.activity=1;}
   if(prey&&nearPrey<7&&prey.energy>0){a.energy=Math.min(1.5,a.energy+prey.energy*.65);prey.energy=0;a.activity=2;}
   const speed=(a.type===0?7:a.type===1?9:a.type===2?12:a.type===3?18:8)*(threat?2.2:a.activity===1?.18:1);
   const x=wrap(a.x+Math.cos(a.angle)*speed*dt,SIZE),y=wrap(a.y+Math.sin(a.angle)*speed*dt,SIZE);
   if(a.type===3||Boolean(this.water[this.index(x,y)])===(a.type===4)){a.x=x;a.y=y;}else a.angle+=Math.PI*.7;
   a.energy-=dt*(a.type===2?.004:.0025); // sunlight-funded food replenishes energy
   if(a.energy>1.1&&a.age>25&&this.agents.length+newborn.length<MAX_AGENTS&&this.rng()<dt*.018){a.energy-=.52;newborn.push(a);}
  }
  this.agents=this.agents.filter(a=>{if(a.energy<=0||a.age>1800){this.deaths++;return false;}return true;});
  for(const parent of newborn)if(this.spawn(parent))this.births++;
 }
 static restore(record){
  if(record.version!==1||!Array.isArray(record.agents)||record.agents.length>MAX_AGENTS)throw Error('Unsupported ecosystem state');
  const model=Object.create(Ecosystem.prototype);
  for(const key of ['seed','aquatic','latitude','time','births','deaths','nextId'])model[key]=record[key];
  model.rng=random(record.randomState);model.agents=record.agents.map(a=>({...a}));
  for(const key of ['height','moisture','food','water']){if(record[key]?.length!==N*N)throw Error('Invalid field dimensions');model[key]=key==='water'?new Uint8Array(record[key]):new Float32Array(record[key]);}
  return model;
 }
 snapshot(){return {version:1,seed:this.seed,randomState:this.rng.state(),aquatic:this.aquatic,latitude:this.latitude,time:this.time,births:this.births,deaths:this.deaths,nextId:this.nextId,agents:this.agents.map(a=>({...a})),height:Array.from(this.height),moisture:Array.from(this.moisture),food:Array.from(this.food),water:Array.from(this.water)};}
}
const api={Ecosystem,N,SIZE,MAX_AGENTS,noise,terrain,wrap,clamp};if(typeof module!=='undefined'&&module.exports)module.exports=api;else root.VirtualEarthModel=api;
})(typeof globalThis!=='undefined'?globalThis:this);
