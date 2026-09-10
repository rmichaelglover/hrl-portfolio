const assert=require('node:assert/strict');
const M=require('./field-model.js');
assert.equal(M.notes.length,13);assert.equal(M.notes[9].frequency,440);assert.equal(M.notes[12].frequency/M.notes[0].frequency,2);
assert.equal(M.notes[0].color,M.notes[12].color);
assert.equal(M.notes[4].color,'#ff0000');assert.equal(M.notes[7].color,'#00ff00');assert.equal(M.notes[11].color,'#0000ff');
for(const yaw of [-35,0,35])for(const x of [-2,0,2])for(const b of [0,.65,1.5]){
 const p=[1,.8,12],camera={yaw,x,z:0},l=M.project(p,-b/2,400,camera),r=M.project(p,b/2,400,camera);
 assert.equal(l.y,r.y);assert(Math.abs(l.x-r.x-400*b/l.depth)<1e-10);
}
assert.equal(M.project([0,0,-1],0,400,{yaw:0,x:0,z:0}),null);
const s=M.ledger(),total=M.total(s);
for(let i=0;i<100;i++){
 for(const kind of ['energyIn','energyOut','matterIn','matterOut'])M.transfer(s,kind,i*.37);
 M.convert(s,'toEnergy');M.convert(s,'toMatter');assert(Math.abs(M.total(s)-total)<1e-9);
 for(const key of ['energy','matter','reservoirEnergy','reservoirMatter'])assert(s[key]>=0);
}
M.transfer(s,'energyOut',1e6);assert.equal(s.energy,0);assert.equal(M.transfer(s,'energyOut',1),0);assert.equal(M.convert(s,'toMatter'),0);
console.log('Passed: octave frequencies, stereo epipolar rows/disparity, near clipping, exchange/conversion conservation, reservoir exhaustion.');
