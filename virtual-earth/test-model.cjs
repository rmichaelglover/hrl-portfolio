// SPDX-License-Identifier: MIT
const assert=require('node:assert/strict');
const {Ecosystem,N,SIZE,MAX_AGENTS}=require('./model.js');
const a=new Ecosystem({seed:123,population:180}),b=new Ecosystem({seed:123,population:180});
for(let i=0;i<600;i++){a.step(1/30);b.step(1/30);}
assert.deepEqual(a.snapshot(),b.snapshot(),'same seed and steps must reproduce state');
const resumed=Ecosystem.restore(JSON.parse(JSON.stringify(a.snapshot())));
for(let i=0;i<100;i++){a.step(1/30);resumed.step(1/30);}
assert.deepEqual(a.snapshot(),resumed.snapshot(),'exported state must resume exactly');
for(const aquatic of [false,true]){
 const m=new Ecosystem({seed:36,population:240,aquatic});
 const before=m.snapshot(),foodBefore=m.food.reduce((a,b)=>a+b,0);
 for(let i=0;i<3000;i++)m.step(.1);
 assert(m.agents.length<=MAX_AGENTS);
 for(const agent of m.agents){assert(agent.x>=0&&agent.x<SIZE&&agent.y>=0&&agent.y<SIZE);assert(Number.isFinite(agent.energy)&&agent.energy>0);assert(agent.type===3||Boolean(m.water[m.index(agent.x,agent.y)])===(agent.type===4),'habitat constraint');}
 for(let i=0;i<N*N;i++)assert(m.food[i]>=0&&m.food[i]<=m.capacity(i)+1e-6,'resource bounds');
 assert(m.agents.some((agent)=>Math.hypot(agent.x-before.agents.find(p=>p.id===agent.id)?.x,agent.y-before.agents.find(p=>p.id===agent.id)?.y)>1),'agents move');
 assert.notEqual(m.food.reduce((a,b)=>a+b,0),foodBefore,'resources change');
 assert.equal(m.agents.length,before.agents.length+m.births-m.deaths,'population accounting');
 console.log('PASS',aquatic?'aquatic':'terrestrial','movement, habitat, resources and population accounting',m.agents.length,'alive',m.births,'births',m.deaths,'deaths');
}
console.log('PASS deterministic replay and exact state restoration');
