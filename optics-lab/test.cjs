const assert=require('node:assert/strict'),{fresnel,absorbing}=require('./optics.js');
const near=(a,b,t=1e-12)=>assert(Math.abs(a-b)<t,`${a} differs from ${b}`);
near(fresnel(1,1.5,0).r,.04);near(fresnel(1.5,1,0).r,.04);
near(fresnel(1,1.5,Math.atan(1.5)*180/Math.PI).rp,0);
assert(fresnel(1.5,1,50).tir);near(fresnel(1.5,1,50).r,1);
for(const a of [0,15,45,89]){near(fresnel(1.5,1.5,a).r,0);near(fresnel(1.5,1.5,a).angle,a);}
for(const n1 of [1,1.33,1.5,2.5])for(const n2 of [1,1.33,1.5,2.5])for(let a=0;a<90;a+=.5){const r=fresnel(n1,n2,a);assert(r.r>=0&&r.r<=1);near(r.r+r.t,1);if(!r.tir)near(n1*Math.sin(a*Math.PI/180),n2*Math.sin(r.angle*Math.PI/180));}
near(absorbing(1.5,0),.04);near(absorbing(.2,3),9.64/10.44);
for(const n of [.1,.5,1,2,3])for(const k of [0,1,3,6])assert(absorbing(n,k)>=0&&absorbing(n,k)<=1);
assert.throws(()=>fresnel(0,1,0));assert.throws(()=>fresnel(1,1,90));assert.throws(()=>absorbing(1,-1));
console.log('PASS: normal incidence, Brewster zero, total reflection, matched media, Snell law, energy conservation, complex-index limit and input validation.');
