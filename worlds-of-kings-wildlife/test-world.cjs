const assert=require('node:assert/strict'),fs=require('node:fs'),crypto=require('node:crypto'),path=require('node:path'),E=require('./engine.js'),Emoji=require('./emoji-core.js'),themes=require('./data/themes.json'),data=require('../worlds-of-kings-fusion/data/atlas.json');
const previous=require('./data/previous-version.json');for(const [name,hash]of Object.entries(previous.files_sha256))assert.equal(crypto.createHash('sha256').update(fs.readFileSync(path.join(__dirname,'../worlds-of-kings-fusion',name))).digest('hex'),hash,'Previous version changed: '+name);
assert.equal(crypto.createHash('sha256').update(fs.readFileSync(path.join(__dirname,'engine.js'))).digest('hex'),previous.files_sha256['engine.js']);assert.equal(Emoji.theme(themes,'FRA').flag,'🇫🇷');
E.configure(data);const s=E.fresh();for(let i=0;i<3;i++)E.deploy(s,i);s.phase='play';assert.equal(s.pieces.length,48);assert.equal(new Set(s.pieces.map(p=>p.at)).size,48);
for(const p of s.players){assert.equal(E.inCheck(s,p.id),false);assert.ok(E.allLegal(s,p.id).length);}
for(const c of data.countries){const t=Emoji.theme(themes,c.id);assert.ok(t.colors.length&&t.symbols.length);assert.ok(t.colors.every(c=>/^#[0-9a-f]{6}$/i.test(c)));}
for(const r of data.regions.filter(r=>r.country)){assert.ok(Emoji.resident(themes,r).emoji);}
for(const p of s.pieces){const code=E.COUNTRIES[p.owner].code,a=Emoji.character(themes,code,p);assert.ok(a.emoji&&a.name);if(a.kind==='native wildlife inspiration')assert.ok(a.source);}
assert.equal(Emoji.resident(themes,{country:'ATA',id:1723}).emoji,'🦭');assert.equal(Emoji.resident(themes,{country:'DEU',id:1}).kind,'flag decoration');
const move=E.allLegal(s,0)[0],p=s.pieces.find(p=>p.id===move.piece),symbol=Emoji.character(themes,'USA',p);E.move(s,p.id,move.to);assert.equal(s.turn,1);assert.deepEqual(Emoji.character(themes,'USA',p),symbol);
assert.equal(data.regions.filter(r=>r.country==='ATA').length,1);assert.ok(data.regions.some(r=>r.promotion==='north-pole'));
console.log('PASS: preserved previous globe hashes, legal 48-piece opening, country palettes, deterministic province residents, native source links, fallback decorations, unchanged character after moving, turn ownership, polar board.');

for(const c of data.countries){for(const type of ['K','Q'])assert.equal(Emoji.character(themes,c.id,{id:9,type}).emoji,Emoji.theme(themes,c.id).flag);}
assert.equal(Emoji.character(themes,'USA',{id:8,type:'Q'}).emoji,'🇺🇸');
console.log('PASS: kings and queens share country flags, including promoted queens.');
