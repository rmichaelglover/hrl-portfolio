const assert=require('node:assert/strict'),fs=require('node:fs'),vm=require('node:vm');
const WaveWorld=require('./model.js'),SoundField=require('../hyperobject/field-model.js');
const defaults={side:0,yaw:0,fov:65,slow:.004,levelAir:.6,levelWater:.6,volume:.12,palette:'white',boxForm:'closed',boxFace:'near',boxX:0,boxY:-.35,boxZ:10,boxSize:3};
const checks=['showAir','showWater','showMixed','sourceAir','sourceWater','hearAir','hearWater','reflected'];
const context=new Proxy({},{get:(_,key)=>key==='createLinearGradient'?()=>({addColorStop(){}}):()=>{}});
function element(id){return {value:defaults[id]??'',checked:checks.includes(id),children:[],style:{setProperty(){}},clientWidth:500,clientHeight:470,setAttribute(){},getContext(){return context;},append(e){this.children.push(e);}};}
const nodes={};const document={getElementById:id=>nodes[id]??=element(id),createElement:()=>element('')};
const env={document,WaveWorld,SoundField,window:{devicePixelRatio:1,addEventListener(){}},requestAnimationFrame(){}};vm.createContext(env);vm.runInContext(fs.readFileSync(__dirname+'/app.js','utf8'),env);
const read=s=>vm.runInContext(s,env);
assert.equal(read('shown().length'),3);nodes.step.onclick();nodes.step.onclick();assert.equal(read('visualTime'),.0005);
nodes.showAir.checked=false;nodes.showAir.onchange();assert.equal(read('visualTime'),.0005);assert.equal(nodes.worldAir.hidden,true);
nodes.showWater.checked=false;nodes.showWater.onchange();assert.equal(read('shown().join()'),'mixed');
nodes.hearWater.checked=false;nodes.hearWater.onchange();assert(read('sources().water')>0);assert.equal(read('activeProbes().length'),1);
nodes.sourceAir.checked=false;nodes.sourceAir.onchange();assert.equal(read('sources().air'),0);assert(read('sources().water')>0);
nodes.showMixed.checked=false;nodes.showMixed.onchange();assert.equal(read('activeProbes().length'),0);assert.equal(nodes.empty.hidden,false);
nodes.reset.onclick();assert.equal(read('visualTime'),0);
console.log('Passed: repeated stepping, preserved time on world changes, independent emitter/monitor switches, hidden-world routing, reset.');

nodes.boxEnabled.checked=true;nodes.boxEnabled.onchange();nodes.step.onclick();const t=read('visualTime');
assert.equal(read("fieldPaths('air',19,'air',6).length"),0);
nodes.boxX.value=5;nodes.boxX.oninput();assert.equal(read('visualTime'),t);assert.equal(read("fieldPaths('air',19,'air',6).length"),1);
nodes.boxReset.onclick();assert.equal(read('visualTime'),t);assert.equal(read("fieldPaths('air',19,'air',6).length"),0);
nodes.boxForm.value='single';nodes.boxForm.onchange();assert.equal(nodes.boxFace.disabled,false);
console.log('Passed: box movement invalidates field cache and preserves time; reset and face controls.');
