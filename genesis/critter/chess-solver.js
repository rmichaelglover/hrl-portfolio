/* Sound win/draw/loss bounds for the explicitly bounded Chess Critter rules. */
(function(root){
'use strict';
const engine=typeof module!=='undefined'&&module.exports?require('./chess-engine.js'):root.ChessCritter;
const copy=value=>JSON.parse(JSON.stringify(value));
function serialize(h){
  return {...copy(h.snapshot()),origins:copy(h.origins),nextId:h.nextId,repetition:[...h.repetition]};
}
function restore(data){
  if(!Array.isArray(data.repetition))throw new Error('Search requires full repetition history; old snapshots cannot certify outcomes.');
  const h=Object.create(engine.Habitat.prototype);
  Object.assign(h,copy(data));h.repetition=new Map(data.repetition);h.rng=engine.random(h.seed);
  return h;
}
function clone(h){return restore(serialize(h));}
function outcome(result){return result.winner==='w'?1:result.winner==='b'?-1:0;}
function ordered(h,moves){
  return moves.map((move,index)=>{
    const target=move.enPassant?h.at(h.ep.victimX,h.ep.victimY):h.at(move.x,move.y);
    return {move,index,score:(target?engine.VALUES[target.type]:0)+(move.promotion?engine.VALUES[move.promotion]:0)};
  }).sort((a,b)=>b.score-a.score||a.index-b.index).map(x=>x.move);
}
function analyze(input,options={},onProgress=()=>{}){
  const h=input instanceof engine.Habitat?clone(input):restore(input);
  const started=Date.now(),milliseconds=Math.max(1,Number(options.milliseconds)||5000);
  const maxNodes=Math.max(1,Number(options.maxNodes)||100000),maxDepth=Math.min(1200-h.ply,Math.max(1,Number(options.maxDepth)||1200));
  let nodes=0,halted=false,completedDepth=0,attemptedDepth=0;
  const exhausted=()=>{if(halted||nodes>=maxNodes||Date.now()-started>=milliseconds){halted=true;return true;}return false;};
  function visit(state,depth){
    if(exhausted())return [-1,1];nodes++;
    state.adjudicate();if(state.result){const v=outcome(state.result);return [v,v];}
    if(depth===0)return [-1,1];
    const maximizing=state.turn==='w';let lower=maximizing?-1:1,upper=lower;
    const moves=ordered(state,state.legalMoves());
    for(let i=0;i<moves.length;i++){
      let bounds=[-1,1];
      if(!exhausted()){
        const child=clone(state);
        if(!child.move(moves[i]))throw new Error('Search generated an illegal move');
        bounds=visit(child,depth-1);
      }
      lower=maximizing?Math.max(lower,bounds[0]):Math.min(lower,bounds[0]);
      upper=maximizing?Math.max(upper,bounds[1]):Math.min(upper,bounds[1]);
      if((maximizing&&lower===1)||(!maximizing&&upper===-1))return [lower,upper];
    }
    return [lower,upper];
  }
  h.adjudicate();
  const moves=h.result?[]:ordered(h,h.legalMoves());
  const entries=moves.map(move=>({move,lower:-1,upper:1}));
  let lower=-1,upper=1;
  if(h.result)lower=upper=outcome(h.result);
  function report(){
    const maximizing=h.turn==='w';
    const sorted=entries.slice().sort((a,b)=>maximizing?b.lower-a.lower||b.upper-a.upper:a.upper-b.upper||a.lower-b.lower);
    return {format:'chess-critter-analysis-v1',rules:'Chess Critter automatic draws and 1200-ply cap',perspective:'White',status:lower===upper?'proven':'unresolved',lower,upper,epsilon:upper-lower,value:lower===upper?lower:null,turn:h.turn,ply:h.ply,nodes,completedDepth,attemptedDepth,elapsedMs:Date.now()-started,stopReason:lower===upper?'exact outcome established':halted?'budget exhausted':'depth limit reached',terminalReason:h.result?.reason||null,candidate:sorted[0]?.move||null,moves:entries.map(e=>({...e,proven:e.lower===e.upper})),state:serialize(h)};
  }
  for(let depth=1;depth<=maxDepth&&lower!==upper&&!exhausted();depth++){
    attemptedDepth=depth;
    for(const entry of entries){
      if(entry.lower===entry.upper)continue;
      if(exhausted())break;
      const child=clone(h);if(!child.move(entry.move))throw new Error('Root move is illegal');
      const bounds=visit(child,depth-1);
      entry.lower=Math.max(entry.lower,bounds[0]);entry.upper=Math.min(entry.upper,bounds[1]);
      if(entry.lower>entry.upper)throw new Error('Inconsistent search bounds');
      lower=h.turn==='w'?Math.max(...entries.map(e=>e.lower)):Math.min(...entries.map(e=>e.lower));
      upper=h.turn==='w'?Math.max(...entries.map(e=>e.upper)):Math.min(...entries.map(e=>e.upper));
      if(lower===upper)break;
    }
    if(!halted)completedDepth=depth;
    onProgress(report());
  }
  return report();
}
const api={serialize,restore,clone,analyze};
if(typeof module!=='undefined'&&module.exports)module.exports=api;else root.ChessSolver=api;
})(typeof globalThis!=='undefined'?globalThis:this);
