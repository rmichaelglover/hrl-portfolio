const assert=require('node:assert/strict');
const E=require('./engine.js');
const at=E.fromSquare;
let total=0;function test(name,fn){fn();total++;console.log('PASS',name);}
function board(items,turn='w'){const s=E.blank();s.turn=turn;for(const [sq,c,t,promoted=false]of items)s.board[at(sq)]=E.piece(c,t,promoted);return s;}
function move(s,from,to,extra={}){return E.apply(s,{kind:'move',from:at(from),to:at(to),...extra});}
const initial=()=>board([['a1','w','K'],['h8','b','K']]);
const count=s=>s.board.filter(Boolean).length+['w','b'].reduce((n,c)=>n+Object.values(s.pockets[c]).reduce((a,b)=>a+b,0),0);
test('fresh setup, turns and ordinary capture to reserve',()=>{
 let s=E.setup();assert.equal(E.actions(s).length,20);s=move(s,'e2','e4');assert.equal(s.turn,'b');s=move(s,'d7','d5');s=move(s,'e4','d5');assert.equal(s.pockets.w.P,1);assert.equal(s.ruins.length,0);assert.equal(count(s),32);assert.throws(()=>move(s,'d5','d6'));
});
test('normal queen capture is a distinct fire-free action',()=>{
 let s=E.setup('crossing');assert.ok(E.actions(s).some(a=>a.kind==='strike'&&a.to===at('d6')));s=move(s,'d4','d6');assert.equal(s.board[at('d6')].t,'Q');assert.equal(s.pockets.w.R,1);assert.equal(s.waves.length,0);assert.equal(s.ruins.length,0);
});
test('only a queen can strike an unobstructed enemy target',()=>{
 let s=board([['a1','w','K'],['h8','b','K'],['d4','w','Q'],['d5','w','P'],['d6','b','R'],['h4','b','B'],['e2','w','N'],['g3','b','P']]);
 assert.throws(()=>E.apply(s,{kind:'strike',from:at('e2'),to:at('g3')}));assert.throws(()=>E.apply(s,{kind:'strike',from:at('d4'),to:at('d6')}));assert.throws(()=>E.apply(s,{kind:'strike',from:at('d4'),to:at('f4')}));assert.ok(E.actions(s).some(a=>a.kind==='strike'&&a.to===at('h4')));
});
test('strike stays put; exact three edge-adjacent waves; friendly capture flips reserve',()=>{
 let s=E.setup('crossing'),n=count(s);s=E.apply(s,{kind:'strike',from:at('d4'),to:at('d6')});assert.equal(s.board[at('d4')].t,'Q');assert.deepEqual(s.ruins,[at('d6')]);assert.equal(s.waves[0].age,0);
 assert.equal(s.pockets.w.R,1);assert.equal(s.board[at('e6')].t,'B');assert.ok(E.nextWave(s).includes(at('e6')));assert.ok(!E.nextWave(s).includes(at('e5')));
 s=move(s,'h7','h6');assert.equal(s.pockets.w.B,1);assert.equal(s.waves[0].age,1);assert.equal(s.board[at('d4')].t,'Q');
 s=move(s,'a1','a2');assert.equal(s.board[at('d4')],null);assert.equal(s.pockets.b.Q,1);assert.equal(s.waves[0].age,2);
 s=move(s,'h6','h5');assert.equal(s.waves.length,0);assert.equal(s.ruins.length,E.forecast(E.blank(),at('d6')).reduce((n,w)=>n+w.squares.length,0));assert.equal(count(s),n);
});
test('several fire fronts resolve together and a new strike does not skip old spread',()=>{
 let s=board([['a1','w','K'],['h8','b','K'],['d4','w','Q'],['f6','b','Q'],['d6','b','R'],['f4','w','N'],['e6','b','B']]);s=E.apply(s,{kind:'strike',from:at('d4'),to:at('d6')});s=E.apply(s,{kind:'strike',from:at('f6'),to:at('f4')});assert.equal(s.waves.length,2);assert.equal(s.waves[0].age,1);assert.equal(s.waves[1].age,0);assert.equal(s.board[at('e6')],null);
});
test('scorched squares block drops and slider rays; knights jump over terrain',()=>{
 let s=board([['a1','w','K'],['h8','b','K'],['d1','w','R'],['b1','w','N']]);s.ruins=[at('d2'),at('b2')];s.pockets.w.N=1;assert.ok(!E.moves(s,at('d1')).some(a=>a.to===at('d3')));assert.ok(E.moves(s,at('b1')).some(a=>a.to===at('c3')));assert.ok(!E.actions(s).some(a=>a.kind==='drop'&&a.to===at('d2')));
});
test('drops use a turn, reduce reserve and forbid end-rank pawns',()=>{
 let s=initial();s.pockets.w.P=1;assert.throws(()=>E.apply(s,{kind:'drop',type:'P',to:at('e8')}));s=E.apply(s,{kind:'drop',type:'P',to:at('e2')});assert.equal(s.pockets.w.P,0);assert.equal(s.turn,'b');s=move(s,'h8','h7');assert.ok(!E.moves(s,at('e2')).some(a=>a.to===at('e4')));assert.throws(()=>E.apply(s,{kind:'drop',type:'P',to:at('a4')}));
});
test('promotion and recapture return a promoted piece as a pawn',()=>{
 let s=board([['a1','w','K'],['h8','b','K'],['e7','w','P'],['d8','b','R']]);s=move(s,'e7','e8',{promotion:'N'});assert.equal(s.board[at('e8')].t,'N');assert.equal(s.board[at('e8')].promoted,true);s=move(s,'d8','e8');assert.equal(s.pockets.b.P,1);assert.equal(s.pockets.b.N,0);
});
test('ordinary king kidnapping ends the game without fire or a king reserve',()=>{
 let s=board([['a1','w','K'],['h8','b','K'],['h1','w','R']]);s=move(s,'h1','h8');assert.equal(s.result.winner,'w');assert.equal(s.ruins.length,0);assert.equal(s.pockets.w.K,undefined);assert.deepEqual(E.actions(s),[]);assert.throws(()=>move(s,'a1','b1'));
});
test('both crowns captured by the same fire wave is a draw',()=>{
 let s=board([['c4','w','K'],['e4','b','K'],['d1','w','Q'],['d4','b','P'],['h8','b','N']]);s=E.apply(s,{kind:'strike',from:at('d1'),to:at('d4')});s=move(s,'h8','f7');assert.equal(s.result.winner,null);assert.match(s.result.reason,/Both crowns/);
});
test('a direct king capture and an existing fire capture also resolve together',()=>{
 let s=board([['c4','w','K'],['h8','b','K'],['h1','w','R']]);s.waves=[{origin:at('d4'),age:0}];s=move(s,'h1','h8');assert.equal(s.result.winner,null);
});
test('détente preserves turn and reserves, cancels spread, keeps ruins and ordinary captures',()=>{
 let s=E.setup('crossing');s=E.apply(s,{kind:'strike',from:at('d4'),to:at('d6')});const n=s.ruins.length,ply=s.ply,p=JSON.stringify(s.pockets);s=E.offer(s);assert.equal(s.offer,'b');s=E.accept(s);assert.equal(s.disarmed,true);assert.equal(s.turn,'b');assert.equal(s.ply,ply);assert.equal(JSON.stringify(s.pockets),p);assert.equal(s.waves.length,0);assert.equal(s.ruins.length,n);assert.ok(!E.actions(s).some(a=>a.kind==='strike'));s=move(s,'f6','d4');assert.equal(s.pockets.b.Q,1);assert.equal(s.ruins.length,n);
});
test('offer expires on a move; declining uses no turn',()=>{
 let s=E.offer(E.setup());s=E.decline(s);assert.equal(s.turn,'w');assert.equal(s.offer,null);s=move(E.offer(s),'e2','e4');assert.equal(s.offer,null);
});
test('no moves and no drops draws; an available reserve prevents a false draw',()=>{
 let s=board([['a1','w','K'],['h8','b','K'],['g6','w','N']]);s.ruins=[at('g8'),at('g7'),at('h7')];let t=move(s,'g6','e5');assert.equal(t.result.winner,null);s.pockets.b.N=1;t=move(s,'g6','e5');assert.equal(t.result,null);
});
test('save validation and deterministic bot return playable actions',()=>{
 assert.equal(E.valid(E.setup()),true);assert.equal(E.valid({version:1,board:[]}),false);assert.equal(E.valid(null),false);let s=E.setup('pockets');for(let n=0;n<12&&!s.result;n++){const a=E.chooseBot(s,()=>.1);assert.ok(a);s=E.apply(s,a);assert.ok(E.valid(s));}
});
console.log(total+' engine tests passed.');
