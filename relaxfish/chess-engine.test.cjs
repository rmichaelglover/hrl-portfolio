const assert=require('node:assert/strict');
const {Habitat}=require('./chess-engine.js');
function empty(width=8,height=8,turn='w'){
  const h=new Habitat(width,height);h.board.fill(null);h.armies=[];h.nextId=1;h.turn=turn;h.repetition.clear();return h;
}
function add(h,type,color,x,y,army=color+'0',moved=true){
  let a=h.armies.find(a=>a.id===army);
  if(!a){a={id:army,color,active:true,homeX:4,homeY:color==='w'?h.height-1:0,kingId:null,rooks:[]};h.armies.push(a);}
  const p={id:h.nextId++,type,color,x,y,army,moved};h.put(p);
  if(type==='k')a.kingId=p.id;if(type==='r')a.rooks.push(p.id);return p;
}
function perft(h,depth){
  if(depth===0)return 1;let count=0;
  for(const m of h.legalMoves()){
    const t=h.trial(m),turn=h.turn,ep=h.ep;
    h.turn=turn==='w'?'b':'w';h.ep=m.double?{x:m.x,y:(m.fromY+m.y)/2,victimX:m.x,victimY:m.y,id:m.id}:null;
    count+=perft(h,depth-1);h.turn=turn;h.ep=ep;h.undoTrial(t);
  }
  return count;
}
let h=new Habitat(8,8,'perft',1);
assert.equal(h.pieces().length,32);assert.equal(h.board.length,64);
assert.equal(new Set(h.pieces('w').map(p=>p.glyph)).size,16,'home army has sixteen distinct emoji identities');
assert.deepEqual([perft(h,1),perft(h,2),perft(h,3)],[20,400,8902]);
assert.equal(h.pieces().filter(p=>p.moved).length,0,'trial generation preserves piece rights');

h=empty();add(h,'k','w',4,7);add(h,'b','w',4,6);add(h,'r','b',4,0);add(h,'k','b',0,0);
assert(!h.legalMoves().some(m=>m.fromX===4&&m.fromY===6),'pinned bishop cannot expose its king');

h=empty();const wk=add(h,'k','w',4,7,'w0',false);add(h,'r','w',0,7,'w0',false);add(h,'r','w',7,7,'w0',false);add(h,'k','b',4,0);
assert.equal(h.legalMoves().filter(m=>m.castle).length,2);
const castle=h.legalMoves().find(m=>m.castle&&m.x===6);assert(h.move(castle));assert.equal(h.at(6,7).type,'k');assert.equal(h.at(5,7).type,'r');
h=empty();add(h,'k','w',4,7,'w0',false);add(h,'r','w',7,7,'w0',false);add(h,'k','b',0,0);add(h,'r','b',5,0);
assert(!h.legalMoves().some(m=>m.castle),'castling cannot cross an attacked square');

h=empty();add(h,'k','w',7,3);add(h,'p','w',6,3);add(h,'k','b',4,0);add(h,'r','b',0,3);const bp=add(h,'p','b',5,3);
h.ep={x:5,y:2,victimX:5,victimY:3,id:bp.id};assert(h.pseudoMoves().some(m=>m.enPassant));assert(!h.legalMoves().some(m=>m.enPassant),'en passant cannot expose rook check');
h=empty();add(h,'k','w',7,7);add(h,'p','w',0,1);add(h,'k','b',7,0);
assert.deepEqual(h.legalMoves().filter(m=>m.fromX===0).map(m=>m.promotion).sort(),['b','n','q','r']);

h=empty(8,8,'b');add(h,'k','b',7,0);add(h,'q','w',6,1);add(h,'k','w',5,2);
assert(!h.pseudoMoves('w').some(m=>m.x===7&&m.y===0),'kings cannot be captured');
assert.equal(h.adjudicate().winner,'w');assert.equal(h.mated.b,1);
h=empty(8,8,'b');add(h,'k','b',7,0,'b0');add(h,'r','b',3,4,'b0');add(h,'k','b',0,0,'b1');add(h,'q','w',6,1);add(h,'k','w',5,2);
assert.equal(h.adjudicate(),null);assert.equal(h.mated.b,1);assert.equal(h.kings('b').length,1);assert.equal(h.retired.b,2,'only the mated army retires');
h=empty(8,8,'b');add(h,'k','b',7,0);add(h,'q','w',5,1);add(h,'k','w',6,2);
assert.equal(h.adjudicate().reason,'Stalemate');assert.equal(h.mated.b,0);

h=empty(12,12);add(h,'k','w',2,10,'w0');add(h,'k','w',8,10,'w1');add(h,'r','b',2,0);add(h,'r','b',8,0);add(h,'k','b',5,0);
assert.equal(h.checkedKings().length,2);assert.equal(h.legalMoves().length,0);
assert(h.checkedKings().every(k=>h.legalMoves('w',k.id).length>0));
assert(h.adjudicate().reason.startsWith('Royal deadlock'));assert.equal(h.mated.w,0,'conflicting rescue requirements are not false checkmates');

h=empty(24,16);add(h,'k','w',0,15);add(h,'r','w',7,8);add(h,'k','b',23,0);
assert(h.legalMoves().some(m=>m.fromX===7&&m.x===15&&m.y===8),'pieces freely cross former region boundaries');
h=new Habitat(8,8,'repeat');
for(let i=0;i<2;i++)for(const [fx,fy,x,y] of [[6,7,5,5],[1,0,2,2],[5,5,6,7],[2,2,1,0]]){
  const m=h.legalMoves().find(m=>m.fromX===fx&&m.fromY===fy&&m.x===x&&m.y===y);assert(m);assert(h.move(m));
}
assert(h.result.reason.startsWith('Threefold'));
h=empty();add(h,'k','w',0,7);add(h,'r','w',2,6);add(h,'k','b',7,0);h.halfmove=100;
assert(h.adjudicate().reason.startsWith('50 moves'));
h=empty();add(h,'k','w',0,7);add(h,'k','b',7,0);assert(h.adjudicate().reason.startsWith('Bare kings'));
h=empty();add(h,'k','w',0,7);add(h,'b','w',2,6);add(h,'k','b',7,0);assert(h.adjudicate().reason.startsWith('Insufficient'));

for(const [w,hh,pairs] of [[18,13,1],[18,13,2],[32,24,6],[48,32,6]]){
  const a=new Habitat(w,hh,'repeatable',pairs),b=new Habitat(w,hh,'repeatable',pairs);
  assert.deepEqual(a.snapshot(),b.snapshot());
  for(let i=0;i<35&&!a.result;i++){
    assert(a.step('forage'));assert(b.step('forage'));assert.deepEqual(a.snapshot(),b.snapshot());
    const previous=a.turn==='w'?'b':'w';assert(a.kings(previous).every(k=>!a.attacked(k.x,k.y,a.turn)),'every completed move protects every moving-team king');
    assert.equal(a.pieces().length+a.captured.w+a.captured.b+a.retired.w+a.retired.b,a.pairs*32,'population accounting');
  }
}
console.log('PASS: standard perft 20/400/8902; pins; castling; en passant discovered check; four promotions; no king captures; local/all-king checkmates; stalemate; royal deadlock; cross-region movement; repetition; 50-move and bare-king draws; deterministic RNG; multi-king safety and population accounting.');
