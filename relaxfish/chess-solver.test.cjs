'use strict';
const assert=require('node:assert/strict');
const {Habitat,WOODLAND}=require('./chess-engine.js');
const {analyze,serialize,restore}=require('./chess-solver.js');
function fixture(turn='w'){
 const h=new Habitat(8,8);h.board.fill(null);h.armies=[];h.repetition.clear();h.turn=turn;
 function add(type,color,x,y){let a=h.armies.find(a=>a.id===color);if(!a){a={id:color,color,active:true,homeX:x,homeY:y,rooks:[],pair:0};h.armies.push(a);}const p={id:h.nextId++,type,color,x,y,moved:true,army:color};h.put(p);if(type==='k')a.kingId=p.id;return p;}
 return {h,add};
}
const options={milliseconds:10000,maxNodes:10000,maxDepth:2};
let {h,add}=fixture();add('k','w',5,2);add('q','w',6,2);add('k','b',7,0);h.recordPosition();
const before=serialize(h);let result=analyze(h,options);assert.equal(result.value,1);assert.equal(result.status,'proven');assert.deepEqual(serialize(h),before,'search leaves live board untouched');
let child=restore(before);assert(child.move(result.candidate));assert.equal(child.result.winner,'w','candidate realizes mate');
({h,add}=fixture('b'));add('k','b',5,5);add('q','b',6,5);add('k','w',7,7);h.recordPosition();result=analyze(h,options);assert.equal(result.value,-1);
({h,add}=fixture('b'));add('k','b',7,0);add('q','w',5,1);add('k','w',6,2);h.recordPosition();assert.equal(analyze(h,options).value,0,'terminal stalemate exact');
({h,add}=fixture());add('k','w',0,7);add('r','w',2,6);add('k','b',7,0);h.ply=1199;h.recordPosition();assert.equal(analyze(h,options).value,0,'all remaining branches reach habitat limit');
const start=new Habitat(8,8);result=analyze(start,{maxNodes:1,milliseconds:1000,maxDepth:3});assert.equal(result.status,'unresolved');assert.deepEqual([result.lower,result.upper],[-1,1],'budget never invents certainty');
const reports=[];analyze(start,{maxNodes:80,milliseconds:1000,maxDepth:3},r=>reports.push(r));for(let i=1;i<reports.length;i++){assert(reports[i].lower>=reports[i-1].lower);assert(reports[i].upper<=reports[i-1].upper);}
start.repetition.set(start.positionKey(),3);const roundtrip=restore(serialize(start));assert.equal(roundtrip.repetition.get(start.positionKey()),3);assert.equal(analyze(roundtrip,options).value,0,'repetition history survives branching');
assert.throws(()=>restore(start.snapshot()),/repetition/);
assert.equal(WOODLAND.Ke[0],'🦁');assert.equal(start.at(4,7).character,'King Ethelheim');
// Independent exhaustive recursion checks endpoint propagation across both turns.
function exhaustive(state){
 const stateCopy=restore(serialize(state));stateCopy.adjudicate();
 if(stateCopy.result)return stateCopy.result.winner==='w'?1:stateCopy.result.winner==='b'?-1:0;
 const values=stateCopy.legalMoves().map(move=>{const child=restore(serialize(stateCopy));assert(child.move(move));return exhaustive(child);});
 return stateCopy.turn==='w'?Math.max(...values):Math.min(...values);
}
for(const turn of ['w','b']){
 const f=fixture(turn);f.add('k','w',5,2);f.add('q','w',6,2);f.add('k','b',7,0);f.h.ply=1198;f.h.recordPosition();
 const exact=exhaustive(f.h);const searched=analyze(f.h,{milliseconds:10000,maxNodes:10000,maxDepth:2});assert.equal(searched.value,exact,'matches independent exhaustive two-ply horizon');
}
console.log('PASS: White and Black mate-in-one, terminal stalemate, full horizon draw, sound interrupted bounds, monotonic reports, repetition preservation, live-state isolation, Woodland cast.');
