'use strict';
const $=id=>document.getElementById(id),canvas=$('board'),ctx=canvas.getContext('2d');
const HOME={k:'👑',q:'👸',r:'🏰',b:'🧙',n:'🐴',p:'🌱'},AWAY={k:'♚',q:'♛',r:'♜',b:'♝',n:'♞',p:'♟'};
const NAME={k:'King',q:'Queen',r:'Rook',b:'Bishop',n:'Knight',p:'Pawn'};
let world,playing=false,cellSize=36,last=performance.now(),selected=null,hovered=null,legal=[],fit=false;
const team=c=>c==='w'?'White / home':'Black / away';
const square=(x,y)=>`${String.fromCharCode(65+x%26)}${x>=26?Math.floor(x/26)+1:''}:${world.height-y}`;
function pause(){playing=false;$('play').textContent='▶ Observe';last=performance.now();}
function seedWorld(){
  pause();const [w,h]=$('size').value.split(',').map(Number);
  world=new ChessCritter.Habitat(w,h,$('seed').value||'wings-out',Number($('pairs').value));
  $('pairs').value=String(world.pairs);selected=hovered=null;legal=[];
  setCanvasSize();update();
}
function setCanvasSize(){
  cellSize=fit?Math.max(1,Math.floor(($('board-wrap').clientWidth-2)/world.width)):Number($('zoom').value);
  canvas.width=world.width*cellSize;canvas.height=world.height*cellSize;draw();
}
function draw(){
  if(!world)return;
  const checks=new Set([...world.checkedKings('w'),...world.checkedKings('b')].map(k=>k.id));
  const moves=new Set(legal.filter(m=>m.id===selected).map(m=>m.y*world.width+m.x));
  for(let y=0;y<world.height;y++)for(let x=0;x<world.width;x++){
    const px=x*cellSize,py=y*cellSize,p=world.at(x,y),lastMove=world.lastMove;
    ctx.fillStyle=(x+y)%2?'#254549':'#466665';ctx.fillRect(px,py,cellSize,cellSize);
    if(lastMove&&((lastMove.x===x&&lastMove.y===y)||(lastMove.fromX===x&&lastMove.fromY===y))){ctx.fillStyle='#e3bc4455';ctx.fillRect(px,py,cellSize,cellSize);}
    if(p){
      if(p.color==='b'){
        ctx.fillStyle='#e2e9d4';ctx.beginPath();ctx.arc(px+cellSize/2,py+cellSize/2,cellSize*.41,0,Math.PI*2);ctx.fill();
      }
      ctx.font=`${Math.max(3,cellSize*.78)}px ${p.color==='w'?'"Apple Color Emoji","Segoe UI Emoji","Noto Color Emoji",sans-serif':'"DejaVu Sans","Segoe UI Symbol",serif'}`;
      ctx.textAlign='center';ctx.textBaseline='middle';ctx.fillStyle=p.color==='w'?'#ffffff':'#132327';
      ctx.fillText(p.color==='w'?(p.glyph||HOME[p.type]):AWAY[p.type],px+cellSize/2,py+cellSize*.52);
      if(p.color==='w'&&p.birthType==='p'&&p.type!=='p'){
        ctx.fillStyle='#0c272d';ctx.fillRect(px+cellSize*.48,py+cellSize*.48,cellSize*.52,cellSize*.52);
        ctx.font=`${Math.max(6,cellSize*.40)}px "Noto Color Emoji",sans-serif`;
        ctx.fillText(HOME[p.type],px+cellSize*.76,py+cellSize*.76);
      }
      const army=world.armies.find(a=>a.id===p.army);ctx.fillStyle=`hsl(${(army.pair||0)*67},75%,70%)`;
      ctx.fillRect(px+2,py+2,Math.max(2,cellSize*.10),Math.max(2,cellSize*.10));
      if(checks.has(p.id)){ctx.strokeStyle='#ff7c82';ctx.lineWidth=2;ctx.strokeRect(px+1.5,py+1.5,cellSize-3,cellSize-3);}
      if(p.id===selected){ctx.strokeStyle='#b7f580';ctx.lineWidth=2;ctx.strokeRect(px+2,py+2,cellSize-4,cellSize-4);}
    }
    if(moves.has(y*world.width+x)){ctx.fillStyle='#78f5e9bb';ctx.beginPath();ctx.arc(px+cellSize/2,py+cellSize/2,cellSize*.13,0,Math.PI*2);ctx.fill();}
  }
  for(const event of world.history.filter(e=>e.kind==='mate')){
    if(world.at(event.x,event.y))continue;
    const x=(event.x+.5)*cellSize,y=(event.y+.5)*cellSize;
    ctx.strokeStyle='#ff8c8666';ctx.lineWidth=2;ctx.beginPath();ctx.moveTo(x-cellSize*.2,y-cellSize*.2);ctx.lineTo(x+cellSize*.2,y+cellSize*.2);ctx.moveTo(x+cellSize*.2,y-cellSize*.2);ctx.lineTo(x-cellSize*.2,y+cellSize*.2);ctx.stroke();
  }
  if($('origins').checked){
    ctx.strokeStyle='#c8f69b99';ctx.lineWidth=1.5;ctx.setLineDash([5,5]);
    for(const origin of world.origins)ctx.strokeRect(origin.x*cellSize+1,origin.y*cellSize+1,8*cellSize-2,8*cellSize-2);
    ctx.setLineDash([]);
  }
}
function update(){
  world.adjudicate();if(world.result)pause();
  const result=world.result;
  $('status').textContent=result?(result.winner?`${team(result.winner)} victorious`:'Habitat drawn'):`${team(world.turn)} to move${playing?' · observing':' · paused'}`;
  const wk=world.kings('w').length,bk=world.kings('b').length;
  $('summary').textContent=`${world.width} × ${world.height} squares · ply ${world.ply} · ${world.pieces().length} pieces alive · White kings ${wk}/${world.pairs} · Black kings ${bk}/${world.pairs} · mated W ${world.mated.w}, B ${world.mated.b} · captured ${world.captured.w+world.captured.b} · retired ${world.retired.w+world.retired.b}${result?' · '+result.reason:''}`;
  const events=world.history.slice(-14).reverse();$('journal').replaceChildren();
  if(!events.length){const li=document.createElement('li');li.textContent=`Seed “${world.seed}”: ${world.pairs} army pair${world.pairs>1?'s':''}, ${world.pairs*32} pieces. All kings start safe.`;$('journal').append(li);}
  for(const e of events){const li=document.createElement('li');li.textContent=e.kind==='mate'?`Ply ${e.ply}: ${team(e.color)} king ${e.army} checkmated; its army retires.`:`${e.ply}. ${team(e.color)} ${NAME[e.type]} ${square(e.fromX,e.fromY)} → ${square(e.x,e.y)}${e.capture?' captures '+NAME[e.capture]:''}${e.promotion?' promotes to '+NAME[e.promotion]:''}${e.castle?' castles':''}${e.enPassant?' en passant':''}`;$('journal').append(li);}
  $('play').disabled=$('step').disabled=Boolean(result);describe();draw();
}
function describe(){
  const p=world.pieces().find(p=>p.id===(selected??hovered));
  if(!p){$('inspector').textContent=world.result?world.result.reason:'Hover to inspect; while paused, select a moving-team node to show legal destinations.';return;}
  const choices=p.color===world.turn?(selected===p.id?legal:world.legalMoves()).filter(m=>m.id===p.id):[];
  const checked=p.type==='k'&&world.attacked(p.x,p.y,p.color==='w'?'b':'w');
  $('inspector').textContent=`${p.color==='w'?(p.glyph||HOME[p.type]):AWAY[p.type]} ${team(p.color)} ${NAME[p.type]}${p.birthType==='p'&&p.type!=='p'?' (promoted)':''} · army ${p.army} · ${square(p.x,p.y)}${checked?' · IN CHECK':''} · ${p.color===world.turn?new Set(choices.map(m=>`${m.x},${m.y}`)).size+' legal destinations':'waiting for its team turn'}`;
}
function step(){pause();world.step($('policy').value);selected=null;legal=[];update();}
function cellAt(event){const r=canvas.getBoundingClientRect();return {x:Math.floor((event.clientX-r.left)/r.width*world.width),y:Math.floor((event.clientY-r.top)/r.height*world.height)};}
canvas.addEventListener('pointermove',event=>{const {x,y}=cellAt(event);hovered=world.at(x,y)?.id??null;describe();});
canvas.addEventListener('pointerleave',()=>{hovered=null;describe();});
canvas.addEventListener('click',event=>{
  if(playing||world.result)return;
  const {x,y}=cellAt(event),p=world.at(x,y);
  if(p&&p.color===world.turn){selected=p.id;legal=world.legalMoves();describe();draw();return;}
  const move=legal.find(m=>m.id===selected&&m.x===x&&m.y===y&&(!m.promotion||m.promotion===$('promotion').value));
  if(move&&world.move(move)){selected=null;legal=[];update();}
});
$('play').onclick=()=>{if(world.result)return;playing=!playing;last=performance.now();selected=null;legal=[];$('play').textContent=playing?'⏸ Pause':'▶ Observe';update();};
$('step').onclick=step;$('seed-world').onclick=seedWorld;
$('new-seed').onclick=()=>{$('seed').value='critter-'+crypto.getRandomValues(new Uint32Array(1))[0].toString(36);seedWorld();};
$('size').onchange=()=>{
  const [w,h]=$('size').value.split(',').map(Number),capacity=Math.floor((w+2)/10)*Math.floor((h+2)/10);
  for(const option of $('pairs').options)option.disabled=Number(option.value)>capacity;
  if(Number($('pairs').value)>capacity)$('pairs').value='1';seedWorld();
};
$('pairs').onchange=seedWorld;
$('zoom').onchange=()=>{fit=false;setCanvasSize();};$('fit').onclick=()=>{fit=true;setCanvasSize();};
$('origins').onchange=draw;$('speed').onchange=()=>{last=performance.now();};
$('export').onclick=()=>{
  const blob=new Blob([JSON.stringify({...world.snapshot(),policy:$('policy').value},null,2)],{type:'application/json'}),url=URL.createObjectURL(blob),a=document.createElement('a');
  a.href=url;a.download=`chess-critter-${world.ply}.json`;a.click();setTimeout(()=>URL.revokeObjectURL(url),1000);
};
addEventListener('resize',()=>{if(fit)setCanvasSize();});
function loop(time){
  const interval=1000/Number($('speed').value),elapsed=time-last;
  if(playing&&elapsed>=interval){world.step($('policy').value);last=time-elapsed%interval;update();}
  requestAnimationFrame(loop);
}
// Disable army counts that do not fit the initial Conway-sized habitat.
for(const option of $('pairs').options)option.disabled=Number(option.value)>2;
seedWorld();requestAnimationFrame(loop);
