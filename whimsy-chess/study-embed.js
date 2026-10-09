/* Same-origin study adapter. Maestro keeps its original standalone behavior. */
if(new URLSearchParams(location.search).get('studyEmbed')==='1'&&parent!==window){
  document.documentElement.classList.add('maestro-embedded');
  const style=document.createElement('style');
  style.textContent='body{margin:0!important;padding:0!important;overflow:hidden;background:transparent!important}.top,.links,#otbHint,#studyPanel,#loadPanel,#exportPanel,#flagPanel,.side,.pbar,.narr,.rage-strip,.storybook,.storybook-commentary{display:none!important}.app{display:block!important;margin:0!important;padding:0!important;max-width:none!important}.boardcol{width:100%!important;max-width:none!important;margin:0!important;padding:0!important}.board{width:100%!important;max-width:none!important;aspect-ratio:1!important;margin:0!important;border:0!important;border-radius:0!important}.sq.study-selected{box-shadow:inset 0 0 0 4px #e8b859!important}.sq.study-target:after{content:"";position:absolute;width:22%;height:22%;border-radius:50%;background:#22483188;top:39%;left:39%;z-index:5}.sq.study-red{background-image:linear-gradient(#c7515144,#c7515144)!important}.sq.study-green{box-shadow:inset 0 0 0 3px #398b64!important}';document.head.append(style);
  const tell=data=>parent.postMessage(data,location.origin);
  boardEl.addEventListener('click',e=>{const square=e.target.closest('[data-sq]');if(square){e.stopImmediatePropagation();tell({type:'maestro-study-square',square:square.dataset.sq});}},true);
  window.addEventListener('message',e=>{
    if(e.origin!==location.origin||e.source!==parent)return;const d=e.data;
    if(d.type==='maestro-study-position'){
      stop();gameKey='_studyEmbed';game={label:'The Stalemate Gambit Explained',hero:'w',white:'Woodland Kingdom',black:'The visiting army',result:'*',tc:''};GAMES[gameKey]=game;pieceW=d.classic?'classic':'woodland';pieceB='classic';rolesOn=false;riverOn=false;qcdOn=false;frames=[d.frame];moves=[];cur=0;branched=false;otbOn=false;document.getElementById('moves').dataset.built='';render();
      for(const mark of d.squares.split(',')){const square=boardEl.querySelector(`[data-sq="${mark.slice(1)}"]`);if(square)square.classList.add(mark[0]==='G'?'study-green':'study-red');}
    }
    if(d.type==='maestro-study-highlight')for(const square of boardEl.querySelectorAll('[data-sq]')){square.classList.toggle('study-selected',square.dataset.sq===d.selected);square.classList.toggle('study-target',d.targets.includes(square.dataset.sq));}
  });
  tell({type:'maestro-study-ready'});
}
