const assert=require('node:assert/strict'),fs=require('fs'),crypto=require('crypto'),E=require('./engine.js'),A=require('./atlas-core.js'),data=require('./data/atlas.json');
E.configure(data);const s=E.fresh();for(let i=0;i<3;i++)E.deploy(s,i);s.phase='play';assert.equal(s.pieces.length,48);assert.equal(new Set(s.pieces.map(p=>p.at)).size,48);
for(let owner=0;owner<3;owner++){assert.equal(E.inCheck(s,owner),false);assert.ok(E.allLegal(s,owner).length);assert.ok(s.pieces.filter(p=>p.owner===owner).every(p=>E.cells[p.at].country===owner));}
const before=JSON.stringify(s),move=E.allLegal(s,0)[0];E.move(s,move.piece,move.to);assert.equal(s.turn,1);assert.equal(E.inCheck(s,0),false);assert.ok(s.km[0]>0);assert.notEqual(JSON.stringify(s),before);assert.throws(()=>E.move(s,move.piece,move.to));
const alliance=E.clone(s);E.accept(alliance,E.request(alliance,0,1));E.accept(alliance,E.request(alliance,1,2));assert.equal(alliance.phase,'finished');assert.deepEqual(alliance.winner,[0,1,2]);assert.ok(alliance.players.every(p=>p.score===1));
for(const region of data.regions){if(region.country!==null)assert.ok(['#bed4aa','#f1dfa0','#cbd0d2','#477553'].includes(region.mapColor));const [lon,lat]=region.center,key=Math.min(17,Math.max(0,Math.floor((lat+90)/10)))*36+Math.min(35,Math.max(0,Math.floor((lon+180)/10)));assert.ok(data.hitBins[key].includes(region.id),region.name);}
const original=require('../worlds-of-kings-earth/data/prototype-reference.json');for(const[name,hash]of Object.entries(original.files_sha256).filter(([name])=>["engine.js","test-engine.cjs"].includes(name)))assert.equal(crypto.createHash('sha256').update(fs.readFileSync(require('path').join(__dirname,'../worlds-of-kings/',name))).digest('hex'),hash);
console.log('PASS: 48-piece deployment, safe opening mobility, legal move and turn ownership, alliances/shared victory, native colors/index coverage, original engine unchanged.');
assert.equal(data.regions.filter(r=>r.country==='ATA').length,1);
assert.equal(data.countries.find(c=>c.id==='ATA').spaces.length,1);
assert.ok(data.regions.some(r=>r.promotion==='north-pole'));
for(const target of ['antarctica','north-pole'])for(const promotion of ['Q','R','B','N']){
 const fixture={countries:['USA','FRA','KOR'].map(id=>({id,name:id})),polar_links:[],regions:Array.from({length:6},(_,id)=>({id,name:'Space '+id,country:id===0?'USA':null,center:[id*20,0],neighbors:[],routes:Array.from({length:8},()=>[])}))};
 fixture.regions[1].promotion=target;fixture.regions[0].routes[0]=[1];
 E.configure(fixture);const state=E.fresh();for(let i=0;i<3;i++)E.addPiece(state,i,'K',i+3);const pawn=E.addPiece(state,0,'P',0);state.phase='play';
 assert.equal(pawn.type,'P');assert.ok(E.legal(state,pawn).some(m=>m.to===1));E.move(state,pawn.id,1,promotion);assert.equal(pawn.type,promotion);assert.equal(pawn.at,1);
 // An occupied polar destination cannot be entered straight ahead.
 const blocked=E.fresh();for(let i=0;i<3;i++)E.addPiece(blocked,i,'K',i+3);const p=E.addPiece(blocked,0,'P',0);E.addPiece(blocked,1,'Q',1);blocked.phase='play';assert.ok(!E.legal(blocked,p).some(m=>m.to===1));
 // Diagonal capture of the Ice Queen promotes, leaving exactly one occupant.
 fixture.regions[0].routes[0]=[];fixture.regions[0].routes[1]=[1];E.configure(fixture);assert.ok(E.legal(blocked,p).some(m=>m.to===1));E.move(blocked,p.id,1,promotion);assert.equal(p.type,promotion);assert.equal(blocked.pieces.filter(q=>q.at===1).length,1);
}
E.configure(data);
console.log('PASS: single Antarctic space; four promotion choices at both poles; occupied forward entry blocked; Ice Queen capture promotes.');
