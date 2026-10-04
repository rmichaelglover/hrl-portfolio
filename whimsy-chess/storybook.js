(function(root){
  'use strict';
  function tell(s={}){
    const san=String(s.san||''),ply=Number(s.ply)||0;
    const side=s.side|| (ply%2?'White':'Black');
    if(!ply)return '🎬 The cast assembles. Knights check their roller skates; the queen checks the exits. Every adventure starts with one honest move.';
    const move=`${Math.ceil(ply/2)}${ply%2?'.':'…'} ${san}`;
    let line;
    if(/#$/.test(san))line='🏆 CHECKMATE. The king’s emergency exits have all failed inspection. Curtain, confetti, handshake!';
    else if(s.stalemate===true)line='🪨 STALEMATE. No check, no legal move: the king has found the world’s smallest escape room and earned half a point.';
    else if(/=/.test(san))line='👑 A pawn reaches the far shore and changes costume. Promotion earned; the adventure still needs its ending.';
    else if(/^O-O/.test(san))line='🏰 The king changes apartments and brings a rook into the renovation. New address, same responsibility: inspect the doors.';
    else if(/x/.test(san))line='🍽️ '+side+' collects something from the board buffet. Enjoy the bite—but check what the empty square lets through.';
    else if(/\+$/.test(san))line='📣 Check! The king must answer this knock before attending to the rest of the party.';
    else {
      const type=san[0];
      const jokes={N:'🛼 A knight takes the scenic route. Roller skates optional; the L-shaped itinerary is compulsory.',B:'🧣 A bishop glides down a diagonal like a scarf caught in a helpful breeze.',R:'🚚 A rook changes lanes. The furniture truck prefers straight roads.',Q:'👑 The queen arrives with excellent range and suspiciously little luggage.',K:'🧭 The king takes a small walk. One square can be an entire adventure.'};
      line=jokes[type]||'🌱 A pawn takes its little step. Tiny shoes, potentially very large consequences.';
    }
    if(/x/.test(san)&&/\+$/.test(san))line+=' And the bill arrives WITH CHECK.';
    if(s.final&&!/#$/.test(san)&&s.stalemate!==true)line+=' The recorded result is '+String(s.result||'unfinished')+'. The move record alone does not tell us why play stopped.';
    return move+' — '+line;
  }
  let panel,body,last;
  function update(s){
    last=s;
    if(typeof document==='undefined')return tell(s);
    if(!panel){
      const old=document.querySelector('#narr')||document.querySelector('#story');
      if(!old)return;
      panel=document.createElement('details');panel.className='storybook-commentary';panel.open=true;
      const title=document.createElement('summary');title.textContent='🎬 Storybook commentary';
      body=document.createElement('p');
      const link=document.createElement('a');link.href='/hrl-portfolio/whimsy-chess/storybook/';link.textContent='Two new adventures →';
      panel.append(title,body,link);old.insertAdjacentElement('afterend',panel);
      const css=document.createElement('style');css.textContent='.storybook-commentary{margin:12px 0;padding:12px 15px;border:1px solid #b8995866;border-radius:14px;background:#c7952510;font:inherit;line-height:1.6}.storybook-commentary summary{cursor:pointer;font-weight:700}.storybook-commentary p{margin:8px 0}.storybook-commentary a{color:inherit;text-decoration:underline}';document.head.append(css);
    }
    body.textContent=tell(s);
  }
  const api={tell,update};root.ChessStorybook=api;
  if(typeof module!=='undefined')module.exports=api;
})(typeof window!=='undefined'?window:globalThis);
