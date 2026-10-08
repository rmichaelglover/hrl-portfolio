const assert=require('node:assert/strict');
const fs=require('node:fs'),vm=require('node:vm');
const {traceStep,nearestSeed}=require('./relaxation.js');
const state={S:[[1,0],[.5,.5],[0,1]],prior:[[1,0],[.5,.5],[0,1]],edges:[[0,1],[1,2]],C:[[1,0],[0,1]],ps:.6};
const original=JSON.stringify(state),t=traceStep(state);
assert.equal(JSON.stringify(state),original);
assert.deepEqual(t.raw,[[.5,.5],[1,1],[.5,.5]]);
assert.deepEqual(t.support,[[0,0],[0,0],[0,0]]);
assert.deepEqual(t.after,state.S);
const simple={...state,edges:[[0,1]]};
const one=traceStep(simple);assert.deepEqual(one.raw[1],[1,0]);assert.deepEqual(one.support[1],[1,0]);assert(Math.abs(one.after[1][0]-2/3)<1e-12);
assert.deepEqual(nearestSeed([[0],[10],[3]],new Set([0,1]),[[1,0],[0,1],[.5,.5]]).map(x=>x.label),[0,1,0]);
const html=fs.readFileSync(__dirname+'/index.html','utf8');
const data=html.slice(html.indexOf('const DIGIT_CLASSES='),html.indexOf('const mCv='));
const sandbox={};vm.createContext(sandbox);vm.runInContext(data+';globalThis.digits=DIGITS;globalThis.colors=DCOL',sandbox);
const digits=sandbox.digits,pixels=digits.map(d=>d.px);
assert.equal(digits.length,40);assert(digits.every(d=>d.px.length===64));
function edges(){const set=new Set();pixels.forEach((p,i)=>{pixels.map((q,j)=>[p.reduce((s,v,k)=>s+(v-q[k])**2,0),j]).filter(x=>x[1]!==i).sort((a,b)=>a[0]-b[0]).slice(0,5).forEach(([,j])=>set.add([Math.min(i,j),Math.max(i,j)].join(',')));});return [...set].map(s=>s.split(',').map(Number));}
function reference(st){const sup=st.S.map(()=>Array(5).fill(0));for(const [a,b] of st.edges)for(let j=0;j<5;j++){sup[a][j]+=st.S[b][j];sup[b][j]+=st.S[a][j];}return st.S.map((row,i)=>{const lo=Math.min(...sup[i]),span=Math.max(...sup[i])-lo;const v=row.map((s,j)=>st.prior[i][j]**st.ps*s**(1-st.ps)*(1+(span?(sup[i][j]-lo)/span:0)));const sum=v.reduce((a,b)=>a+b,0);return v.map(x=>x/sum);});}
for(let offset=0;offset<8;offset++){
 const prior=digits.map(()=>Array(5).fill(.2)),seeds=[0,8,16,24,32].map(i=>i+offset);for(const i of seeds){prior[i]=Array(5).fill(0);prior[i][digits[i].y]=1;}
 const st={prior,S:prior.map(r=>r.slice()),edges:edges(),C:Array.from({length:5},(_,i)=>Array.from({length:5},(_,j)=>+(i===j))),ps:.6};
 let stable=0;
 for(let k=0;k<500;k++){
  const ref=reference(st),trace=traceStep(st);trace.after.forEach((r,i)=>{assert(Math.abs(r.reduce((a,b)=>a+b,0)-1)<1e-12);r.forEach((v,j)=>assert(Math.abs(v-ref[i][j])<1e-12));});
  for(const i of seeds)assert.deepEqual(trace.after[i],prior[i]);
  assert(trace.delta.every((r,i)=>r.every((v,j)=>v===trace.after[i][j]-trace.before[i][j])));
  st.S=trace.after;stable=trace.maxDelta<1e-6?stable+1:0;if(stable>=5)break;
 }
 assert.equal(stable,5,'Convergence criterion met for seed offset '+offset);
}
console.log('PASS: exact support, ties, normalized updates, baseline, immutability, fixed seeds, reference equivalence and convergence for eight seed configurations.');
