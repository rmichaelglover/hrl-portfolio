const assert=require('node:assert/strict');
const B=require('./board-display.js'),data=require('./data/atlas.json');
const pieces=B.initialize(data);
assert.equal(new Set(pieces.map(p=>p.at)).size,pieces.length);
assert(pieces.every(p=>data.regions[p.at].country===p.country));
for(const country of data.countries){const army=pieces.filter(p=>p.country===country.id);assert.equal(army.length,Math.min(16,country.spaces.filter(id=>!data.regions[id].promotion).length));}
for(const zoom of [1,3,10,80]){
 const groups=B.cluster(pieces,p=>data.regions[p.at].center.map(x=>x*zoom),{zoom});
 assert.equal(groups.reduce((n,g)=>n+g.pieces.length,0),pieces.length);
 for(let i=0;i<groups.length;i++)for(let j=i+1;j<groups.length;j++)assert(Math.hypot(groups[i].x-groups[j].x,groups[i].y-groups[j].y)>=48);
}
const focused=pieces[10];const groups=B.cluster(pieces,()=>[100,100],{selected:focused.at});assert.equal(groups[0].pieces[0].at,focused.at);
assert.equal(B.cluster(pieces,()=>null).length,0);
console.log(`PASS: ${pieces.length} unique pieces; deployment coverage, lossless clustering, spacing, selection priority and hidden hemisphere.`);
