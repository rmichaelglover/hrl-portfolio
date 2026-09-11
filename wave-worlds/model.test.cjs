const assert=require('node:assert/strict'),W=require('./model.js');
for(const a of ['air','water'])for(const b of ['air','water']){
 const q=W.boundaryCoefficients(a,b);assert(Math.abs(q.R+q.T-1)<1e-12);assert(Math.abs(q.tp-(1+q.r))<1e-12);assert(Math.abs(q.tp*q.tp*W.media[a].impedance/W.media[b].impedance-q.T)<1e-12);
 if(a===b){assert.equal(q.r,0);assert.equal(q.T,1);}
}
const aw=W.boundaryCoefficients('air','water'),wa=W.boundaryCoefficients('water','air');assert.equal(aw.r,-wa.r);assert.equal(aw.T,wa.T);assert(aw.T>.001&&aw.T<.002);
for(const source of ['air','water'])for(const time of [0,.0007,.003]){
 const sources={[source]:.6},a=W.sample('mixed',12-1e-8,440,time,sources)*Math.sqrt(W.media.air.impedance),b=W.sample('mixed',12+1e-8,440,time,sources)*Math.sqrt(W.media.water.impedance);assert(Math.abs(a-b)<1e-3,'pressure continuity');
}
assert.equal(W.paths('air',7,'water').length,0);assert.equal(W.paths('water',19,'air').length,0);
assert.equal(W.paths('mixed',7,'air').length,2);assert.equal(W.paths('mixed',19,'air')[0].kind,'transmitted');
assert.equal(W.paths('mixed',19,'water').length,2);assert.equal(W.paths('mixed',7,'water')[0].kind,'transmitted');
for(const world of ['air','water','mixed'])for(const z of [2,7,12,19,26])for(const source of ['air','water'])for(const p of W.paths(world,z,source)){assert(p.delay>=0&&p.delay<.2);assert(Number.isFinite(p.gain));}
assert.equal(W.probeList(['air','water','mixed'],{air:true,water:true}).length,4);assert.equal(W.probeList([],{air:true,water:true}).length,0);assert.equal(W.probeList(['mixed'],{air:false,water:true})[0].medium,'water');
assert.equal(W.sample('mixed',19,440,.003,{air:0,water:0}),0);
assert(Math.abs(W.sample('mixed',19,440,.003,{air:.6,water:.4})-W.sample('mixed',19,440,.003,{air:.6})-W.sample('mixed',19,440,.003,{water:.4}))<1e-12);
console.log('Passed: reflection/transmission energy balance, pressure continuity, phase reversal, source availability, propagation delays, probe routing, linear superposition.');
