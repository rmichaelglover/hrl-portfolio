const assert=require('node:assert/strict'),fs=require('node:fs'),vm=require('node:vm');
const R=require('./relax.js'),T=require('./tutor.js');
const isolated=R.run({nodes:[{prior:[.2,.3,.5]}]});assert.deepEqual(isolated.strengths[0],[.2,.3,.5]);assert(isolated.converged);
const field=R.run({nodes:[{prior:[.5,.5]},{prior:[1,0],fixed:true}],factors:[{a:0,b:1,matrix:[[1,0],[0,1]]}]});assert(field.strengths[0][0]>.5);assert.deepEqual(field.strengths[1],[1,0]);
assert.throws(()=>R.run({nodes:[{prior:[-1,2]}]}));
const pristine=T.infer([]),bad=T.infer([{id:'one',skill:'defense',decision:false,prediction:false,hinted:false}]);
assert(bad.skills[1].values[0]>pristine.skills[1].values[0]);
for(const result of [pristine,bad])for(const row of result.strengths){assert(Math.abs(row.reduce((a,b)=>a+b)-1)<1e-10);assert(row.every(v=>v>=0&&Number.isFinite(v)));}
class Element{constructor(){this.children=[];this.classList={add(){}};this.disabled=false;}append(e){this.children.push(e);}replaceChildren(){this.children=[];}setAttribute(k,v){this[k]=v;}focus(){}}
function app(storage){const nodes={},env={document:{getElementById:id=>nodes[id]??=new Element(),createElement:()=>new Element()},localStorage:storage,TutorRelax:R,CaptureTutor:T};vm.createContext(env);for(const f of ['lessons.js','app.js'])vm.runInContext(fs.readFileSync(__dirname+'/'+f,'utf8'),env);return {nodes,read:s=>vm.runInContext(s,env)};}
let saved={};const storage={getItem:k=>saved[k]??null,setItem:(k,v)=>saved[k]=v};const a=app(storage);
assert.equal(a.nodes.board.children.length,64);assert(a.nodes.forward.disabled);
a.nodes.answers.children[0].onclick();assert.equal(a.read('phase'),'prediction');assert(a.nodes.forward.disabled);
a.nodes.answers.children[1].onclick();assert.equal(a.read('records.length'),1);assert.equal(a.read('records[0].decision'),false);assert.equal(a.read('frame'),2);
a.nodes.back.onclick();assert.equal(a.read('frame'),1);a.nodes.forward.onclick();assert.equal(a.read('frame'),2);
a.read('start(lessons[0])');a.nodes.hint.onclick();a.nodes.answers.children[1].onclick();a.nodes.answers.children[0].onclick();assert.equal(a.read('records.length'),1);assert.equal(a.read('records[0].decision'),false);
const b=app(storage);assert.equal(b.read('records.length'),1);
b.read('start(lessons[4])');b.nodes.hint.onclick();b.nodes.answers.children[0].onclick();b.nodes.answers.children[2].onclick();assert.equal(b.read('records[1].hinted'),true);
b.nodes.reset.onclick();assert.equal(b.read('records.length'),2);b.nodes.reset.onclick();assert.equal(b.read('records.length'),0);
const denied=app({getItem(){throw Error('denied');},setItem(){throw Error('denied');}});assert.equal(denied.read('persistent'),false);
const lessons=a.read('lessons');assert.equal(T.validateRecords([null,{}, {id:'wrong',skill:'defense'}],lessons).length,0);
const all=lessons.map(l=>({id:l.id,skill:l.skill,decision:true,prediction:true,hinted:false}));assert(T.recommend(lessons,all).complete);
assert.notEqual(T.recommend(lessons,[all[0]]).lesson.id,all[0].id);
console.log('PASS: generic propagation, fixed evidence, normalization, adaptive recommendation, complete teaching loop, replay, hints, first-attempt preservation, reload, reset, denied storage.');
