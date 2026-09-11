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

const box={enabled:true,form:'closed',face:'near',x:0,y:-.35,z:10,size:3};
assert.equal(W.faces(box).length,6);
assert.equal(W.faces({...box,form:'open'}).length,5);
assert.equal(W.faces({...box,form:'single'}).length,1);
assert.equal(W.obstaclePaths('air',19,'air',box).length,0,'closed box shadows downstream');
const echo=W.obstaclePaths('air',7,'air',box).find(p=>p.kind==='box');
assert.equal(echo.gain,1);assert(Math.abs(echo.delay-8/343)<1e-12);
assert.deepEqual(W.obstaclePaths('air',19,'air',{...box,x:5}),W.paths('air',19,'air'));
assert.deepEqual(W.obstaclePaths('air',19,'air',{...box,y:5}),W.paths('air',19,'air'));
assert.equal(W.obstaclePaths('air',10,'air',box).length,0,'closed interior has no external input');
assert(W.obstaclePaths('air',10,'air',{...box,form:'open'}).some(p=>p.kind==='box'),'near opening admits wave to far wall');
assert.equal(W.obstaclePaths('air',19,'air',{...box,form:'single',face:'top'}).length,1,'parallel face does not intercept');
for(const world of ['air','water','mixed'])for(const source of ['air','water'])for(const form of ['closed','open','single'])for(const face of ['near','far','top'])for(const bz of [5.1,10,12,15,22.9])for(const z of [2,7,11.9,12.1,19,26]){
 const ps=W.obstaclePaths(world,z,source,{...box,form,face,z:bz});assert(ps.length<=8);assert(ps.every(p=>p.delay>=0&&p.delay<.2&&Number.isFinite(p.gain)));
}
console.log('Passed: rigid face counts, shadowing, reflection delay and sign, XYZ placement, open interior, parallel square, bounded mixed-world paths.');
