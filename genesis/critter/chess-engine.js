/* Chess Critter: explicit multi-king chess variant, shared rectangular habitat.
   Dependency-free engine shared by the browser and Node verification. */
(function(root){
'use strict';
const VALUES={p:100,n:320,b:330,r:500,q:900,k:0};
const DIRS={b:[[1,1],[1,-1],[-1,1],[-1,-1]],r:[[1,0],[-1,0],[0,1],[0,-1]]};
DIRS.q=DIRS.b.concat(DIRS.r);
const KNIGHTS=[[1,2],[2,1],[-1,2],[-2,1],[1,-2],[2,-1],[-1,-2],[-2,-1]];
const KING=DIRS.q;
const other=c=>c==='w'?'b':'w';
const BACK_EMOJI=['🏰','🐴','🧙','👸','👑','🔮','🦄','🗼'];
const PAWN_EMOJI=['🌱','🌿','🍀','🌾','🍃','🌵','🌴','🌳'];
function hashSeed(text){let h=2166136261;for(const c of String(text)){h^=c.charCodeAt(0);h=Math.imul(h,16777619);}return h>>>0;}
function random(seed){let a=hashSeed(seed);return ()=>{a+=0x6D2B79F5;let t=a;t=Math.imul(t^t>>>15,t|1);t^=t+Math.imul(t^t>>>7,t|61);return ((t^t>>>14)>>>0)/4294967296;};}
class Habitat{
  constructor(width=18,height=13,seed='wings-out',pairs=1){
    if(width<8||height<8)throw new Error('The habitat must fit an 8×8 starting army.');
    this.width=width;this.height=height;this.seed=String(seed);this.rng=random(seed);
    this.board=Array(width*height).fill(null);this.turn='w';this.ply=0;this.halfmove=0;
    this.ep=null;this.armies=[];this.nextId=1;this.mated={w:0,b:0};this.captured={w:0,b:0};
    this.retired={w:0,b:0};this.result=null;this.history=[];this.repetition=new Map();this.lastMove=null;
    this.origins=[];
    const slots=[];
    const nx=Math.floor((width+2)/10),ny=Math.floor((height+2)/10);
    const left=Math.floor((width-(nx*10-2))/2),top=Math.floor((height-(ny*10-2))/2);
    for(let y=0;y<ny;y++)for(let x=0;x<nx;x++)slots.push({x:left+x*10,y:top+y*10});
    for(let i=slots.length-1;i>0;i--){const j=Math.floor(this.rng()*(i+1));[slots[i],slots[j]]=[slots[j],slots[i]];}
    this.pairs=Math.min(Math.max(1,pairs|0),slots.length);
    for(let i=0;i<this.pairs;i++)this.seedPair(slots[i].x,slots[i].y,i);
    if(this.kings('w').some(k=>this.attacked(k.x,k.y,'b'))||this.kings('b').some(k=>this.attacked(k.x,k.y,'w')))
      throw new Error('Seeded armies must start with all kings safe.');
    this.recordPosition();
  }
  inside(x,y){return x>=0&&y>=0&&x<this.width&&y<this.height;}
  at(x,y){return this.inside(x,y)?this.board[y*this.width+x]:null;}
  put(p){if(!this.inside(p.x,p.y)||this.at(p.x,p.y))throw new Error('Invalid placement');this.board[p.y*this.width+p.x]=p;}
  pieces(color){return this.board.filter(p=>p&&(!color||p.color===color));}
  kings(color){return this.pieces(color).filter(p=>p.type==='k');}
  seedPair(x,y,pair){
    this.origins.push({x,y,pair});
    for(const color of ['b','w']){
      const row=y+(color==='b'?0:7),pawnRow=y+(color==='b'?1:6),army=`${pair}-${color}`;
      const record={id:army,color,pair,homeX:x+4,homeY:row,kingId:null,rooks:[],active:true};
      this.armies.push(record);
      for(let col=0;col<8;col++){
        const p={id:this.nextId++,type:'rnbqkbnr'[col],birthType:'rnbqkbnr'[col],glyph:color==='w'?BACK_EMOJI[col]:null,color,army,x:x+col,y:row,moved:false};
        this.put(p);if(p.type==='k')record.kingId=p.id;if(p.type==='r')record.rooks.push(p.id);
        this.put({id:this.nextId++,type:'p',birthType:'p',glyph:color==='w'?PAWN_EMOJI[col]:null,color,army,x:x+col,y:pawnRow,moved:false});
      }
    }
  }
  attacked(x,y,by){
    // Attacks include pinned pieces, as in chess's king-safety definition.
    for(const p of this.pieces(by)){
      const dx=x-p.x,dy=y-p.y;
      if(p.type==='p'){if(Math.abs(dx)===1&&dy===(by==='w'?-1:1))return true;continue;}
      if(p.type==='n'){if(Math.abs(dx)*Math.abs(dy)===2)return true;continue;}
      if(p.type==='k'){if(Math.max(Math.abs(dx),Math.abs(dy))===1)return true;continue;}
      const diagonal=Math.abs(dx)===Math.abs(dy)&&dx!==0,straight=(dx===0)!==(dy===0);
      if(!((p.type==='b'&&diagonal)||(p.type==='r'&&straight)||(p.type==='q'&&(diagonal||straight))))continue;
      const sx=Math.sign(dx),sy=Math.sign(dy);let cx=p.x+sx,cy=p.y+sy,blocked=false;
      while(cx!==x||cy!==y){if(this.at(cx,cy)){blocked=true;break;}cx+=sx;cy+=sy;}
      if(!blocked)return true;
    }
    return false;
  }
  pseudoMoves(color=this.turn){
    const moves=[];
    const add=(p,x,y,extra={})=>{
      if(!this.inside(x,y))return;
      const target=this.at(x,y);
      if(target&&(target.color===p.color||target.type==='k'))return;
      if(p.type==='p'&&y===(p.color==='w'?0:this.height-1)){
        for(const promotion of ['q','r','b','n'])moves.push({id:p.id,fromX:p.x,fromY:p.y,x,y,promotion,...extra});
      }else moves.push({id:p.id,fromX:p.x,fromY:p.y,x,y,...extra});
    };
    for(const p of this.pieces(color)){
      if(p.type==='p'){
        const d=color==='w'?-1:1;
        if(this.inside(p.x,p.y+d)&&!this.at(p.x,p.y+d)){
          add(p,p.x,p.y+d);
          if(!p.moved&&this.inside(p.x,p.y+2*d)&&!this.at(p.x,p.y+2*d))add(p,p.x,p.y+2*d,{double:true});
        }
        for(const dx of [-1,1]){
          const target=this.at(p.x+dx,p.y+d);
          if(target&&target.color!==color)add(p,p.x+dx,p.y+d);
          else if(this.ep&&this.ep.x===p.x+dx&&this.ep.y===p.y+d){
            const victim=this.at(this.ep.victimX,this.ep.victimY);
            if(victim&&victim.id===this.ep.id&&victim.type==='p'&&victim.color!==color)add(p,p.x+dx,p.y+d,{enPassant:true});
          }
        }
      }else if(p.type==='n'||p.type==='k'){
        for(const [dx,dy] of p.type==='n'?KNIGHTS:KING)add(p,p.x+dx,p.y+dy);
        if(p.type==='k'&&!p.moved){
          const army=this.armies.find(a=>a.id===p.army);
          if(army&&p.x===army.homeX&&p.y===army.homeY&&!this.attacked(p.x,p.y,other(color))){
            for(const id of army.rooks){
              const rook=this.pieces(color).find(r=>r.id===id&&r.type==='r'&&!r.moved&&r.y===p.y);
              if(!rook)continue;
              const d=Math.sign(rook.x-p.x);let clear=true;
              for(let x=p.x+d;x!==rook.x;x+=d)if(this.at(x,p.y)){clear=false;break;}
              if(clear&&!this.attacked(p.x+d,p.y,other(color))&&!this.attacked(p.x+2*d,p.y,other(color)))
                add(p,p.x+2*d,p.y,{castle:rook.id,rookX:p.x+d});
            }
          }
        }
      }else{
        for(const [dx,dy] of DIRS[p.type])for(let x=p.x+dx,y=p.y+dy;this.inside(x,y);x+=dx,y+=dy){
          const target=this.at(x,y);add(p,x,y);if(target)break;
        }
      }
    }
    return moves;
  }
  trial(move){
    const p=this.at(move.fromX,move.fromY);
    if(!p||p.id!==move.id)throw new Error('Move has no source piece');
    const victim=move.enPassant?this.at(this.ep.victimX,this.ep.victimY):this.at(move.x,move.y);
    const previous={piece:p,x:p.x,y:p.y,type:p.type,moved:p.moved,victim};
    this.board[p.y*this.width+p.x]=null;if(victim)this.board[victim.y*this.width+victim.x]=null;
    p.x=move.x;p.y=move.y;p.moved=true;if(move.promotion)p.type=move.promotion;
    this.board[p.y*this.width+p.x]=p;
    if(move.castle){
      const rook=this.pieces(p.color).find(r=>r.id===move.castle);
      previous.rook={piece:rook,x:rook.x,y:rook.y,moved:rook.moved};
      this.board[rook.y*this.width+rook.x]=null;rook.x=move.rookX;rook.moved=true;this.board[rook.y*this.width+rook.x]=rook;
    }
    return previous;
  }
  undoTrial(t){
    const p=t.piece;this.board[p.y*this.width+p.x]=null;
    if(t.rook){const r=t.rook;this.board[r.piece.y*this.width+r.piece.x]=null;r.piece.x=r.x;r.piece.y=r.y;r.piece.moved=r.moved;this.board[r.y*this.width+r.x]=r.piece;}
    p.x=t.x;p.y=t.y;p.type=t.type;p.moved=t.moved;this.board[p.y*this.width+p.x]=p;
    if(t.victim)this.board[t.victim.y*this.width+t.victim.x]=t.victim;
  }
  legalMoves(color=this.turn,onlyKing=null){
    const moves=[];
    for(const move of this.pseudoMoves(color)){
      const t=this.trial(move),kings=this.kings(color).filter(k=>onlyKing===null||k.id===onlyKing);
      const safe=kings.length>0&&kings.every(k=>!this.attacked(k.x,k.y,other(color)));
      this.undoTrial(t);if(safe)moves.push(move);
    }
    return moves;
  }
  checkedKings(color=this.turn){return this.kings(color).filter(k=>this.attacked(k.x,k.y,other(color)));}
  finish(winner,reason){this.result={winner,reason,ply:this.ply};return this.result;}
  adjudicate(){
    if(this.result)return this.result;
    // Checkmate is local to each checked king: any allied piece may rescue it.
    // An inability to rescue all kings at once is instead a royal-deadlock draw.
    for(let pass=0;pass<=this.armies.length;pass++){
      const checked=this.checkedKings();
      const mated=checked.filter(k=>this.legalMoves(this.turn,k.id).length===0);
      if(!mated.length)break;
      const ids=new Set(mated.map(k=>k.army));
      for(const army of this.armies)if(ids.has(army.id)&&army.active){
        army.active=false;this.mated[army.color]++;
        const remaining=this.pieces(army.color).filter(p=>p.army===army.id);
        this.retired[army.color]+=remaining.length;
        for(const p of remaining)this.board[p.y*this.width+p.x]=null;
        const king=mated.find(k=>k.army===army.id);
        this.history.push({kind:'mate',color:army.color,army:army.id,x:king.x,y:king.y,ply:this.ply});
      }
      this.ep=null;this.halfmove=0;this.repetition.clear();
      if(!this.kings(this.turn).length)return this.finish(other(this.turn),'All opposing kings checkmated');
      this.recordPosition();
    }
    if(!this.kings('w').length||!this.kings('b').length)throw new Error('A king may disappear only through recorded checkmate');
    if(!this.legalMoves().length)return this.finish(null,this.checkedKings().length?'Royal deadlock: no move can protect every friendly king':'Stalemate');
    if(this.pieces().every(p=>p.type==='k'))return this.finish(null,'Bare kings: neither team can give a legal check');
    if(this.width===8&&this.height===8&&this.kings('w').length===1&&this.kings('b').length===1){
      const material=this.pieces().filter(p=>p.type!=='k');
      if(material.every(p=>p.type==='b'||p.type==='n')&&
         (material.length<=1||(material.every(p=>p.type==='b')&&new Set(material.map(p=>(p.x+p.y)%2)).size===1)))
        return this.finish(null,'Insufficient mating material in the classical single-king setting');
    }
    if(this.halfmove>=100)return this.finish(null,'50 moves per side without a pawn move or capture (automatic habitat rule)');
    if((this.repetition.get(this.positionKey())||0)>=3)return this.finish(null,'Threefold repetition (automatic habitat rule)');
    if(this.ply>=1200)return this.finish(null,'Habitat turn limit: 1,200 plies');
    return null;
  }
  positionKey(){
    const rights=this.armies.filter(a=>a.active).map(a=>{
      const king=this.pieces(a.color).find(p=>p.id===a.kingId);
      return !king||king.moved?'':a.rooks.filter(id=>this.pieces(a.color).some(p=>p.id===id&&!p.moved)).map(id=>`${a.id}:${id}`).join(',');
    }).filter(Boolean).join(';');
    const pawns=this.pieces().filter(p=>p.type==='p'&&!p.moved).map(p=>`${p.x},${p.y}`).sort().join(';');
    const ep=this.ep&&this.pseudoMoves(this.turn).some(m=>m.enPassant)&&this.legalMoves(this.turn).some(m=>m.enPassant)?`${this.ep.x},${this.ep.y}`:'-';
    return `${this.width}x${this.height}|${this.turn}|${this.board.map(p=>p?`${p.color}${p.type}:${p.army}`:'.').join(',')}|${rights}|${pawns}|${ep}`;
  }
  recordPosition(){const key=this.positionKey();this.repetition.set(key,(this.repetition.get(key)||0)+1);}
  move(candidate){
    if(this.adjudicate())return false;
    const move=this.legalMoves().find(m=>m.id===candidate.id&&m.x===candidate.x&&m.y===candidate.y&&(m.promotion||null)===(candidate.promotion||null));
    if(!move)return false;
    const piece=this.at(move.fromX,move.fromY),originalType=piece.type,color=piece.color;
    const t=this.trial(move);
    if(t.victim)this.captured[t.victim.color]++;
    this.halfmove=originalType==='p'||t.victim?0:this.halfmove+1;
    this.ep=move.double?{x:piece.x,y:(move.fromY+move.y)/2,victimX:piece.x,victimY:piece.y,id:piece.id}:null;
    this.ply++;this.turn=other(this.turn);this.lastMove={...move,color,capture:t.victim?.type||null,type:originalType};
    this.history.push({kind:'move',...this.lastMove,ply:this.ply});this.recordPosition();this.adjudicate();return true;
  }
  chooseMove(policy='forage'){
    if(this.adjudicate())return null;
    const moves=this.legalMoves();if(policy==='random')return moves[Math.floor(this.rng()*moves.length)];
    let best=-Infinity,choice=null;
    for(const move of moves){
      const p=this.at(move.fromX,move.fromY),target=move.enPassant?this.at(this.ep.victimX,this.ep.victimY):this.at(move.x,move.y);
      const enemyKings=this.kings(other(p.color));
      const distance=Math.min(...enemyKings.map(k=>Math.abs(k.x-move.x)+Math.abs(k.y-move.y)));
      let score=(target?VALUES[target.type]:0)+(move.promotion?VALUES[move.promotion]-VALUES.p:0)+(move.castle?35:0);
      score+=this.rng()*65-distance*2;
      const t=this.trial(move);
      if(this.checkedKings(other(p.color)).length)score+=50;
      if(this.attacked(p.x,p.y,other(p.color)))score-=VALUES[p.type]*.65;
      this.undoTrial(t);
      if(score>best){best=score;choice=move;}
    }
    return choice;
  }
  step(policy='forage'){const move=this.chooseMove(policy);return move?this.move(move):false;}
  snapshot(){return {format:'chess-critter-v1',seed:this.seed,width:this.width,height:this.height,pairs:this.pairs,turn:this.turn,ply:this.ply,halfmove:this.halfmove,ep:this.ep,armies:this.armies,board:this.board,mated:this.mated,captured:this.captured,retired:this.retired,result:this.result,history:this.history};}
}
const api={Habitat,hashSeed,random,VALUES};
if(typeof module!=='undefined'&&module.exports)module.exports=api;else root.ChessCritter=api;
})(typeof globalThis!=='undefined'?globalThis:this);
