/* Exact PGN replay from verified server-generated frames. No browser chess engine. */
(() => {
 'use strict';
 const $=id=>document.getElementById(id);
 const glyph={K:'♔',Q:'♕',R:'♖',B:'♗',N:'♘',P:'♙',k:'♚',q:'♛',r:'♜',b:'♝',n:'♞',p:'♟'};
 const role={k:'king',q:'queen',r:'rook',b:'bishop',n:'knight',p:'pawn'};
 let data,index=28,ply=32,blackView=true,classic=false;
 function game(){return data.games[index]}
 function position(){const result={},ranks=game().frames[ply].fen.split(' ')[0].split('/');ranks.forEach((rank,r)=>{let f=0;for(const p of rank){if(/\d/.test(p))f+=+p;else{result[String.fromCharCode(97+f)+(8-r)]=p;f++}}});return result;}
 function label(n){return `${Math.ceil(n/2)}${n%2?'.':'...'}${game().moves[n-1]}`;}
 function draw(){
  const g=game(),fr=g.frames[ply],pieces=position(),side=fr.fen.split(' ')[1],ranks=blackView?[1,2,3,4,5,6,7,8]:[8,7,6,5,4,3,2,1],files=blackView?'hgfedcba':'abcdefgh';
  const description=[];const cells=[];
  for(const [ri,rank]of ranks.entries())for(const [fi,file]of [...files].entries()){
   const sq=file+rank,p=pieces[sq],dark=(file.charCodeAt(0)-97+rank)%2===1,square=document.createElement('span');square.className='square '+(dark?'dark':'light');square.dataset.square=sq;
   if(fr.last&&(fr.last.slice(0,2)===sq||fr.last.slice(2,4)===sq))square.classList.add('last');if(fr.check===sq)square.classList.add('check');
   if(p){const cast=fr.wood[sq]&&data.cast[fr.wood[sq]],color=p===p.toUpperCase()?'White':'Black',name=cast?cast[1]:`${color} ${role[p.toLowerCase()]}`;
    square.title=`${sq}: ${name}, ${color.toLowerCase()} ${role[p.toLowerCase()]}`;description.push(square.title);
    const piece=document.createElement('span');piece.className=cast&&!classic?'woodland-piece':'piece '+(color==='White'?'white-piece':'black-piece');piece.textContent=cast&&!classic?cast[0]:glyph[p];piece.setAttribute('aria-hidden','true');square.append(piece);
    if(cast&&!classic){const badge=document.createElement('small');badge.className='role-mark';badge.textContent=glyph[p];badge.setAttribute('aria-hidden','true');square.append(badge);}
   }
   if(fi===0){const c=document.createElement('small');c.className='coord rank';c.textContent=rank;square.append(c)}
   if(ri===7){const c=document.createElement('small');c.className='coord file';c.textContent=file;square.append(c)}
   cells.push(square);
  }
  $('board').replaceChildren(...cells);$('board').setAttribute('aria-label',`Game ${g.number}. ${ply?label(ply):'Starting position'}. ${side==='w'?'White':'Black'} to move. ${description.join('; ')}`);
  const h=g.headers,top=blackView?'White':'Black',bottom=blackView?'Black':'White';
  $('top-player').textContent=`${h[top]} (${h[top+'Elo']}) · ${top}${top.toLowerCase()===g.side?' · Woodland':''}`;
  $('bottom-player').textContent=`${h[bottom]} (${h[bottom+'Elo']}) · ${bottom}${bottom.toLowerCase()===g.side?' · Woodland':''}`;
  $('turn-label').textContent=ply===g.moves.length?`Record ends · ${h.Result}`:`${side==='w'?'White':'Black'} to move`;
  $('ply-label').textContent=ply?`${label(ply)} · ${ply}/${g.moves.length}`:`Start · 0/${g.moves.length}`;
  $('first').disabled=$('previous').disabled=ply===0;$('last').disabled=$('next').disabled=ply===g.moves.length;
  $('cast-toggle').textContent=classic?'Woodland pieces':'Classic pieces';$('cast-toggle').setAttribute('aria-pressed',String(classic));
  const beat=[...g.beats].reverse().find(b=>b.ply<=ply);
  $('current-speaker').textContent=beat?`${beat.speaker} · ${label(beat.ply)}`:'At the whiteboard';
  $('current-comment').textContent=beat?beat.text:g.capsule;
  $('game-label').textContent=`GAME ${String(g.number).padStart(2,'0')} · ${g.outcome.toUpperCase()}${g.queen_departures.length?' · QUEEN-FOR-MATERIAL EPISODE':''}`;
  $('game-title').textContent=g.title;$('game-capsule').textContent=g.capsule;
  $('game-result').textContent=`Manny: ${g.side}. Recorded result ${h.Result} · ${h.Termination}.`;
  $('source-link').href=`https://lichess.org/${g.id}`;$('source-link').rel='noopener';
  $('beat-buttons').replaceChildren(...g.beats.map(b=>{const button=document.createElement('button');button.type='button';button.textContent=label(b.ply);button.setAttribute('aria-current',String(b.ply===ply));button.onclick=()=>{ply=b.ply;draw()};return button;}));
  $('move-list').replaceChildren(...g.moves.map((san,n)=>{const button=document.createElement('button');button.type='button';button.textContent=`${Math.floor(n/2)+1}${n%2?'...':'.'}${san}`;if(n+1===ply)button.className='current';button.onclick=()=>{ply=n+1;draw()};return button;}));
  const e=g.evaluations[ply];let ev;
  if(e.mate_winner)ev=`Recorded checkmate for ${e.mate_winner}.`;
  else if(e.mate_white!==null)ev=`Engine reports mate in ${Math.abs(e.mate_white)} for ${e.mate_white>0?'White':'Black'}.`;
  else if(e.cp_white!==null)ev=`Board estimate, White perspective: ${e.cp_white>=0?'+':''}${(e.cp_white/100).toFixed(2)} pawns${e.depth?' · depth '+e.depth:''}. The recorded clock result stands separately.`;
  else ev='No numerical estimate at this terminal position.';
  $('evaluation').textContent=ev;
  $('story-next').disabled=!g.beats.some(b=>b.ply>ply);$('game-select').value=String(g.number);
  const url=new URL(location.href);url.searchParams.set('game',g.number);url.searchParams.set('ply',ply);history.replaceState(null,'',url);
 }
 function loadGame(number,p=0,scroll=false){if(!data)return;index=Math.max(0,Math.min(data.games.length-1,Math.trunc(number)-1));ply=Math.max(0,Math.min(game().moves.length,Math.trunc(p)));blackView=game().side==='black';draw();if(scroll)$('replay').scrollIntoView({behavior:matchMedia('(prefers-reduced-motion:reduce)').matches?'instant':'smooth'});}
 function step(delta){if(!data)return;ply=Math.max(0,Math.min(game().moves.length,ply+delta));draw();}
 $('first').onclick=()=>{if(data){ply=0;draw()}};$('previous').onclick=()=>step(-1);$('next').onclick=()=>step(1);$('last').onclick=()=>{if(data){ply=game().moves.length;draw()}};
 $('flip').onclick=()=>{if(data){blackView=!blackView;draw()}};$('cast-toggle').onclick=()=>{if(data){classic=!classic;draw()}};
 $('story-next').onclick=()=>{if(data){const b=game().beats.find(b=>b.ply>ply);if(b){ply=b.ply;draw()}}};
 $('game-select').onchange=()=>loadGame(+$('game-select').value);
 document.addEventListener('keydown',e=>{if(/^(INPUT|SELECT|TEXTAREA)$/.test(e.target.tagName)||e.target.isContentEditable)return;if(e.key==='ArrowRight'||e.key==='ArrowLeft'){e.preventDefault();step(e.key==='ArrowRight'?1:-1)}});
 document.querySelectorAll('[data-game]').forEach(button=>button.addEventListener('click',e=>{e.preventDefault();loadGame(+button.dataset.game,+button.dataset.ply,true)}));
 document.querySelectorAll('[data-puzzle]').forEach(button=>button.addEventListener('click',()=>{if(!data)return;const n=+button.dataset.puzzle,c=data.checkpoints[n],correct=button.dataset.answer===c.answer;document.querySelectorAll(`[data-puzzle="${n}"]`).forEach(b=>b.setAttribute('aria-pressed',String(b===button)));$(`puzzle-feedback-${n}`).textContent=correct?'You found it. '+c.explanation:'Try another route. Read the checking line or follow the open file.';}));
 fetch('review.json').then(r=>{if(!r.ok)throw Error('Review data unavailable');return r.json()}).then(result=>{data=result;$('game-select').replaceChildren(...data.games.map(g=>new Option(`${String(g.number).padStart(2,'0')} · ${g.opponent} · ${g.outcome}`,g.number)));const params=new URLSearchParams(location.search);const n=Number(params.get('game')||data.default_game),p=Number(params.get('ply')||data.default_ply);loadGame(Number.isFinite(n)?n:data.default_game,Number.isFinite(p)?p:0)}).catch(()=>{$('current-comment').textContent='The replay data could not load. The featured review and downloads remain available below.';$('turn-label').textContent='Replay unavailable';});
})();
