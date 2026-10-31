fetch('games.json').then(r=>{if(!r.ok)throw Error('Replay data unavailable');return r.json()}).then(data=>{
const symbols={K:'♚',Q:'♛',R:'♜',B:'♝',N:'♞',P:'♟',k:'♚',q:'♛',r:'♜',b:'♝',n:'♞',p:'♟'};
for(const root of document.querySelectorAll('.replay')){
 const game=data.games.find(g=>g.id===root.dataset.game),slider=root.querySelector('input');let ply=0;
 function render(){const frame=game.frames[ply],board=root.querySelector('.board');board.replaceChildren();const ranks=frame.fen.split(' ')[0].split('/');
 ranks.forEach((rank,r)=>{let file=0;for(const token of rank){const count=/[1-8]/.test(token)?Number(token):1;for(let n=0;n<count;n++){
 const piece=/[1-8]/.test(token)?'':token,square=String.fromCharCode(97+file)+(8-r),cell=document.createElement('span');cell.className='square '+((r+file)%2?'dark':'light')+(piece?' '+(piece===piece.toUpperCase()?'white-piece':'black-piece'):'');cell.textContent=symbols[piece]||'';const coord=document.createElement('small');coord.className='coord';coord.textContent=square;cell.append(coord);board.append(cell);file++;
 }}});board.setAttribute('aria-label',frame.label+'. FEN: '+frame.fen);slider.value=ply;root.querySelector('.status').textContent=frame.label+' · '+ply+' / '+game.legal_plies+(frame.clock===null?'':' · mover clock '+frame.clock+'s');root.querySelector('.note').textContent=frame.note||'Exact recorded position.';for(const b of root.querySelectorAll('[data-step]'))b.disabled=(['start','prev'].includes(b.dataset.step)?ply===0:ply===game.legal_plies);
 }
 slider.addEventListener('input',()=>{ply=Number(slider.value);render()});root.addEventListener('click',e=>{const b=e.target.closest('button');if(!b)return;if(b.dataset.ply!==undefined)ply=Number(b.dataset.ply);else if(b.dataset.step)ply=({start:0,prev:Math.max(0,ply-1),next:Math.min(game.legal_plies,ply+1),end:game.legal_plies})[b.dataset.step];render()});render();
}
}).catch(e=>{for(const el of document.querySelectorAll('.status'))el.textContent=e.message+'. The original PGN downloads remain available.'});
