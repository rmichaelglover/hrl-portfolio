const assert=require('node:assert/strict'),E=require('./engine.js');
function game(){const s=E.fresh();s.phase='play';return s;}
function kings(s){E.addPiece(s,0,'K',E.id(2,12));E.addPiece(s,1,'K',E.id(10,12));E.addPiece(s,2,'K',E.id(18,2));}
{
 const s=game();for(let i=0;i<3;i++)E.deploy(s,i);assert.equal(s.pieces.length,48);assert.equal(new Set(s.pieces.map(p=>p.at)).size,48);for(let i=0;i<3;i++){assert.equal(s.pieces.filter(p=>p.owner===i&&p.type==='K').length,1);assert.ok(E.allLegal(s,i).length);assert.ok(!E.inCheck(s,i));}
 console.log('PASS: 48 pieces, unique deployment, legal opening moves for every country.');
}
{
 for(let n=0;n<E.cells.length;n++)for(const[dx,dy]of[[0,1],[0,-1],[1,0],[-1,0],[1,1],[1,-1],[-1,1],[-1,-1]]){const a=E.step(n,dx,dy),b=E.step(a.at,-a.dx,-a.dy);assert.equal(b.at,n);}
 const a=E.step(E.id(0,0),0,-1);assert.equal(a.at,E.id(12,0));assert.equal(a.dy,1);assert.equal(E.step(E.id(23,7),1,0).at,E.id(0,7));
 console.log('PASS: every edge/diagonal step reverses, longitude wraps, polar crossing changes hemisphere direction.');
}
{
 const s=game();kings(s);const r=E.addPiece(s,0,'R',E.id(5,7));const own=E.addPiece(s,0,'P',E.id(7,7));const enemy=E.addPiece(s,1,'B',E.id(5,4));let m=E.legal(s,r);assert.ok(m.some(m=>m.to===enemy.at));assert.ok(!m.some(m=>m.to===own.at||m.to===E.id(8,7)));assert.throws(()=>E.move(s,enemy.id,E.id(6,5)),/turn/);
 E.move(s,r.id,enemy.at);assert.ok(!s.pieces.some(p=>p.id===enemy.id));assert.equal(s.turn,1);assert.ok(s.km[0]>0);
 console.log('PASS: blocked sliding routes, capture, turn ownership, geographic travel counter.');
}
{
 const s=game();kings(s);s.pieces.find(p=>p.owner===0).at=E.id(3,7);E.addPiece(s,1,'R',E.id(3,4));E.addPiece(s,1,'P',E.id(3,3));const r=E.addPiece(s,0,'R',E.id(3,6));assert.ok(!E.inCheck(s,0));assert.ok(!E.legal(s,r).some(m=>m.to===E.id(4,6)));s.pieces=s.pieces.filter(p=>p.id!==r.id);assert.ok(E.inCheck(s,0));
 console.log('PASS: attacks and own-king safety reject an exposed king.');
}
{
 const s=game();kings(s);const p=E.addPiece(s,0,'P',E.id(6,1));assert.equal(E.pseudo(s,p).length,3);assert.equal(E.pseudo(s,p,true).length,2);E.addPiece(s,1,'N',E.id(7,0));const capture=E.legal(s,p).find(m=>m.to===E.id(7,0));assert.ok(capture?.capture);assert.ok(!E.legal(s,p).some(m=>m.to===E.id(6,2)));
 console.log('PASS: three visible forward choices at exceptional junctions, two capture routes, no backward pawn move.');
}
{
 const s=game();kings(s);const p=E.addPiece(s,0,'P',E.id(10,6));p.departed=true;p.dy=1;E.move(s,p.id,E.id(10,7),'N');assert.equal(p.type,'N');
 const home=game();kings(home);const q=E.addPiece(home,0,'P',E.id(2,6));q.departed=true;q.dy=1;E.move(home,q.id,E.id(2,7));assert.equal(q.type,'P');assert.throws(()=>E.move(home,q.id,E.id(2,8),'K'),/promotion/);
 console.log('PASS: foreign coast promotion, home coast exclusion, valid promotion types.');
}
{
 const s=game();kings(s);const a=E.request(s,0,1);E.accept(s,a);assert.ok(E.allied(s,0,1));assert.equal(s.phase,'play');const b=E.request(s,2,1);assert.deepEqual(b.members,[0,1,2]);E.accept(s,b);assert.equal(s.phase,'finished');assert.deepEqual(s.winner,[0,1,2]);assert.deepEqual(s.players.map(p=>p.score),[1,1,1]);assert.throws(()=>E.request(s,0,1));
 const t=game();kings(t);for(let i=0;i<3;i++)E.request(t,0,1);assert.throws(()=>E.request(t,0,1),/Three/);assert.equal(E.request(t,0,2).count,1);assert.equal(E.request(t,1,0).count,1);
 console.log('PASS: full-alliance mergers, shared victory, request cap per rival and direction.');
}
{
 const s=game();s.players[2].alive=false;s.players[2].score=0;E.addPiece(s,0,'K',E.id(4,7));E.addPiece(s,1,'K',E.id(6,7));const blocker=E.addPiece(s,1,'N',E.id(2,5));E.addPiece(s,1,'N',E.id(1,7));E.addPiece(s,1,'N',E.id(2,7));assert.equal(E.allLegal(s,0).length,0);assert.ok(!E.inCheck(s,0));const result=E.resolveRound(s);assert.equal(result[0].check,false);assert.equal(s.players[0].score,.5);assert.ok(!s.pieces.some(p=>p.owner===0));assert.ok(s.pieces.some(p=>p.id===blocker.id));assert.equal(s.players[1].score,1);
 console.log('PASS: stalemate earns half a point, eliminated army disappears, surviving king wins.');
}
{
 const s=game();E.addPiece(s,0,'K',E.id(4,7));E.addPiece(s,2,'K',E.id(16,7));E.addPiece(s,1,'K',E.id(6,7));for(const[x,y]of[[3,9],[5,5],[5,6],[15,9],[17,5],[17,6]])E.addPiece(s,1,'Q',E.id(x,y));const batch=E.resolveRound(s);assert.deepEqual(batch.map(x=>x.owner),[0,2]);assert.ok(batch.every(x=>x.check));assert.ok(s.pieces.every(p=>p.owner===1));assert.deepEqual(s.players.map(p=>p.score),[0,1,0]);
 console.log('PASS: two checkmated armies disappear in the same batch; no king capture or transfer.');
}
{
 const s=game();kings(s);const p=E.addPiece(s,0,'Q',E.id(5,5));const queen=new Set(E.pseudo(s,p).map(m=>m.to));p.type='R';const rook=E.pseudo(s,p);p.type='B';const bishop=E.pseudo(s,p);assert.deepEqual([...queen].sort((a,b)=>a-b),[...new Set([...rook,...bishop].map(m=>m.to))].sort((a,b)=>a-b));
 console.log('PASS: crossing ray paths do not prematurely truncate queen movement.');
}
console.log('All Worlds of Kings engine checks passed.');
