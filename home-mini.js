/* Small homepage window into the existing legally verified capture lessons. */
(() => {
 'use strict';
 const board=document.getElementById('mini-board'), lessons=globalThis.CaptureLessons;
 if(!board||!lessons?.length)return;
 const $=id=>document.getElementById(id);
 const pieces={K:'♔',Q:'♕',R:'♖',B:'♗',N:'♘',P:'♙',k:'♚',q:'♛',r:'♜',b:'♝',n:'♞',p:'♟'};
 const names={k:'king',q:'queen',r:'rook',b:'bishop',n:'knight',p:'pawn'};
 let index=0,frame=0,answered=false;
 function draw(){
  const lesson=lessons[index],rows=lesson.frames[frame].split(' ')[0].split('/');
  const cells=[];rows.forEach((row,r)=>{let file=0;for(const symbol of row){if(/\d/.test(symbol)){for(let n=0;n<+symbol;n++)cells.push({r,file:file++,symbol:''});}else cells.push({r,file:file++,symbol});}});
  if(lesson.side==='Black')cells.reverse();
  const positionText=cells.filter(c=>c.symbol).map(c=>`${c.symbol===c.symbol.toUpperCase()?'White':'Black'} ${names[c.symbol.toLowerCase()]} on ${String.fromCharCode(97+c.file)}${8-c.r}`).join(', ');
  board.replaceChildren(...cells.map(({r,file,symbol},cellIndex)=>{const square=document.createElement('span');square.className='mini-square '+((r+file)%2?'dark':'light');square.textContent=pieces[symbol]||'';if(symbol){square.classList.add(symbol===symbol.toUpperCase()?'white-piece':'black-piece');square.title=`${String.fromCharCode(97+file)}${8-r}: ${symbol===symbol.toUpperCase()?'White':'Black'} ${names[symbol.toLowerCase()]}`;}if(cellIndex%8===0){const rank=document.createElement('small');rank.className='mini-co-rank';rank.textContent=8-r;rank.setAttribute('aria-hidden','true');square.append(rank);}if(cellIndex>=56){const label=document.createElement('small');label.className='mini-co-file';label.textContent=String.fromCharCode(97+file);label.setAttribute('aria-hidden','true');square.append(label);}return square;}));
  board.setAttribute('aria-label',`${lesson.side} puzzle: ${lesson.title}. Position ${frame+1} of ${lesson.frames.length}. ${positionText}`);
  $('mini-turn').textContent=frame?lesson.moves.slice(0,frame).map(m=>m.san).join(' · '):`${lesson.side} to move`;
  $('mini-replay').disabled=frame===lesson.frames.length-1;
 }
 function load(){frame=0;answered=false;const lesson=lessons[index];$('mini-title').textContent=lesson.title;$('mini-prompt').textContent=lesson.prompt;$('mini-count').textContent=`${index+1} / ${lessons.length}`;$('mini-feedback').textContent='No rush. Look for the reply.';$('mini-feedback').className='';$('mini-replay').hidden=true;document.querySelectorAll('[data-mini-answer]').forEach(b=>{b.disabled=false;b.removeAttribute('aria-pressed')});draw();}
 document.querySelectorAll('[data-mini-answer]').forEach(button=>button.addEventListener('click',()=>{if(answered)return;answered=true;const correct=(button.dataset.miniAnswer==='true')===lessons[index].take;$('mini-feedback').textContent=(correct?'You spotted it! ':'Let’s look together. ')+lessons[index].explanation;$('mini-feedback').className=correct?'mini-success':'mini-explain';document.querySelectorAll('[data-mini-answer]').forEach(b=>b.disabled=true);button.setAttribute('aria-pressed','true');$('mini-replay').hidden=false;}));
 $('mini-next').onclick=()=>{index=(index+1)%lessons.length;load()};
 $('mini-replay').onclick=()=>{if(frame<lessons[index].frames.length-1){frame++;draw()}};
 load();
})();
