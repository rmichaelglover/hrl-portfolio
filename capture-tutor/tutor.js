/* Chess lesson policy; deterministic rules, no ML training or engine evaluation. */
(function(root){
'use strict';
const R=root.TutorRelax||(typeof require!=='undefined'&&require('./relax.js'));
const skills=[{id:'reply',name:'Check their reply'},{id:'defense',name:'Keep your defenses'},{id:'count',name:'Count the exchange'}];
function infer(records){
 const nodes=skills.map(s=>({id:s.id,prior:[.2,.2,.6]})),factors=[];
 for(const record of records){const skill=skills.findIndex(s=>s.id===record.skill);if(skill<0)continue;
  const prior=record.decision&&record.prediction?(record.hinted?[.4,.4,.2]:[.05,.9,.05]):[.9,.05,.05];
  const idx=nodes.length;nodes.push({id:record.id,prior,fixed:true});factors.push({a:skill,b:idx,matrix:[[1,0,0],[0,1,0],[0,0,1]]});
 }
 // A weak shared prerequisite: noticing replies supports checking defenses.
 // Direct exercise evidence is encoded separately above.
 factors.push({a:0,b:1,matrix:[[.12,0,0],[0,.12,0],[0,0,.12]]});
 const field=R.run({nodes,factors});
 return {...field,nodes,factors,skills:skills.map((s,i)=>({...s,values:field.strengths[i],observed:records.filter(r=>r.skill===s.id).length}))};
}
function recommend(lessons,records){
 const field=infer(records),done=new Set(records.map(r=>r.id)),remaining=lessons.filter(l=>!done.has(l.id));
 const pool=remaining.length?remaining:lessons;
 const score=l=>{const s=field.skills.find(s=>s.id===l.skill);return s.values[0]+.5*s.values[2];};
 return {lesson:pool.slice().sort((a,b)=>score(b)-score(a)||lessons.indexOf(a)-lessons.indexOf(b))[0],field,complete:!remaining.length};
}
function validateRecords(value,lessons){
 if(!Array.isArray(value))return [];const seen=new Set();return value.filter(r=>{
  const l=lessons.find(l=>l.id===r?.id);if(!l||l.skill!==r.skill||seen.has(r.id)||!['decision','prediction','hinted'].every(k=>typeof r[k]==='boolean'))return false;
  seen.add(r.id);return true;
 }).map(({id,skill,decision,prediction,hinted})=>({id,skill,decision,prediction,hinted}));
}
const api={skills,infer,recommend,validateRecords};root.CaptureTutor=api;if(typeof module!=='undefined')module.exports=api;
})(globalThis);
