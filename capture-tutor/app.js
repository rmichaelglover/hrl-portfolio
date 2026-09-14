'use strict';
const $=id=>document.getElementById(id),lessons=CaptureLessons,T=CaptureTutor,KEY='capture-tutor-v0.1';
let records=[],persistent=true,current,phase='decision',frame=0,flipped=false,decision=false,hinted=false,resetArmed=false;
try{records=T.validateRecords(JSON.parse(localStorage.getItem(KEY)||'[]'),lessons);}catch{persistent=false;}
function save(){try{localStorage.setItem(KEY,JSON.stringify(records));}catch{persistent=false;}renderProgress();}
function text(tag,value,parent){const e=document.createElement(tag);e.textContent=value;parent.append(e);return e;}
function drawBoard(){
 const fen=current.frames[frame],rows=fen.split(' ')[0].split('/'),board={};
 rows.forEach((row,r)=>{let f=0;for(const ch of row){if(/[1-8]/.test(ch))f+=Number(ch);else board['abcdefgh'[f++]+(8-r)]=ch;}});
 const names={p:'pawn',r:'rook',n:'knight',b:'bishop',q:'queen',k:'king'},symbols={p:'♟',r:'♜',n:'♞',b:'♝',q:'♛',k:'♚'};
 const ranks=flipped?[1,2,3,4,5,6,7,8]:[8,7,6,5,4,3,2,1],files=(flipped?'hgfedcba':'abcdefgh').split('');
 const move=frame?current.moves[frame-1].uci:null,capture=current.moves[0].uci;
 $('board').replaceChildren();
 for(const rank of ranks)for(const file of files){const sq=file+rank,p=board[sq],e=document.createElement('div');e.className='square'+(('abcdefgh'.indexOf(file)+rank)%2?' dark':' ');
  if(move&&(sq===move.slice(0,2)||sq===move.slice(2,4)))e.classList.add('moved');
  if(frame===0&&sq===capture.slice(2,4))e.classList.add('target');
  if(p){const piece=text('span',symbols[p.toLowerCase()],e);piece.className='piece '+(p===p.toUpperCase()?'white':'black');}
  text('small',sq,e);e.title=sq+(p?' '+(p===p.toUpperCase()?'White ':'Black ')+names[p.toLowerCase()]:' empty');$('board').append(e);
 }
 const description=Object.entries(board).map(([sq,p])=>(p===p.toUpperCase()?'White ':'Black ')+names[p.toLowerCase()]+' '+sq).join(', ');
 $('board').setAttribute('aria-label',(fen.split(' ')[1]==='w'?'White':'Black')+' to move. '+description);
 $('turn').textContent=(fen.split(' ')[1]==='w'?'White':'Black')+' to move';
 $('positionLabel').textContent=frame===0?'Starting position. The outlined piece is the offered capture.':frame===1?'After the proposed capture.':'After the demonstrated reply.';
 $('line').textContent=frame?current.moves.slice(0,frame).map(m=>m.san).join('  '):'Candidate: '+current.moves[0].san;
 $('back').disabled=phase!=='feedback'||frame===0;$('forward').disabled=phase!=='feedback'||frame===2;
}
function renderProgress(){
 const r=T.recommend(lessons,records),f=r.field;
 $('progress').textContent=records.length+' / '+lessons.length+' first attempts recorded. '+records.filter(r=>r.decision&&r.prediction&&!r.hinted).length+' answered both parts without a hint.';
 $('skills').replaceChildren();
 f.skills.forEach(s=>{const e=document.createElement('div');e.className='skill';text('strong',s.name,e);const rs=records.filter(r=>r.skill===s.id);text('span',!rs.length?'Not tried yet':rs.some(r=>!r.decision||!r.prediction)?'Worth another look':rs.some(r=>r.hinted)?'Practiced with help':'Both answers connected',e);$('skills').append(e);});
 $('trace').textContent='Fixed rule weights; not probabilities or an Elo estimate.\n'+f.skills.map(s=>s.name+': practice '+s.values[0].toFixed(3)+' / steady '+s.values[1].toFixed(3)+' / unknown '+s.values[2].toFixed(3)).join('\n')+'\nRelaxation: '+f.iterations+' iterations; '+(f.converged?'converged':'iteration limit reached')+'.\nObjects: '+f.nodes.length+'; pairwise factors: '+f.factors.length+'.\nEach first attempt is a fixed evidence object attached to its lesson skill. Reply and defense also share a weak compatibility factor.';
 $('storage').textContent=persistent?'Saved only in this browser.':'Browser storage unavailable; this session still works, but may not survive reload.';
 $('recommendation').textContent=r.complete?'All six attempted. Review a lesson below; fresh positions are needed before drawing conclusions about transfer.':'Suggested next: '+r.lesson.title+'. Unseen exercises come first; practice need and uncertainty determine their order.';
 $('lessonList').replaceChildren();lessons.forEach(l=>{const b=text('button',(records.some(r=>r.id===l.id)?'✓ ':'')+l.title,$('lessonList'));b.onclick=()=>start(l);});
}
function start(l){const navigating=!!current;current=l;phase='decision';frame=0;flipped=l.side==='Black';hinted=false;decision=false;
 $('title').textContent=l.title;$('phase').textContent='1 / DECIDE';$('prompt').textContent=l.prompt;$('feedback').replaceChildren();$('hintText').textContent='';$('hint').hidden=false;$('hint').disabled=false;$('next').hidden=true;$('answers').replaceChildren();
 for(const [label,value] of [['Take the piece',true],['Leave this capture',false]]){const b=text('button',label,$('answers'));b.onclick=()=>decide(value);}
 drawBoard();renderProgress();if(navigating)$('turn').scrollIntoView?.({block:'start'});
}
function decide(value){if(phase!=='decision')return;decision=value===current.take;phase='prediction';frame=1;$('phase').textContent='2 / PREDICT';$('prompt').textContent=current.question;$('answers').replaceChildren();
 current.options.forEach((label,i)=>{const b=text('button',label,$('answers'));b.onclick=()=>answer(i);});drawBoard();}
function answer(i){if(phase!=='prediction')return;phase='feedback';const prediction=i===current.answer,recorded=records.some(r=>r.id===current.id);
 if(!recorded)records.push({id:current.id,skill:current.skill,decision,prediction,hinted});
 $('phase').textContent='3 / REPLAY & REFLECT';$('prompt').textContent='Step backward and forward to connect the explanation to the board.';$('answers').replaceChildren();$('hint').hidden=true;
 text('h3',decision&&prediction?'You connected the decision and its consequence.':'Here is the connection to practice.',$('feedback'));
 text('p','Capture decision: '+(decision?'correct':'revisit')+'. Prediction: '+(prediction?'correct':'revisit')+'.'+(hinted?' You used a hint.':''),$('feedback'));
 text('p',current.explanation,$('feedback'));text('strong',current.takeaway,$('feedback'));
 if(recorded)text('p','Review only: your original first-attempt record is unchanged.',$('feedback'));
 frame=2;$('next').hidden=false;$('next').textContent=records.length===lessons.length?'Review suggested lesson':'Next exercise';save();drawBoard();$('feedback').focus();}
$('hint').onclick=()=>{if(phase==='feedback')return;hinted=true;$('hintText').textContent=current.hint;$('hint').disabled=true;};
$('flip').onclick=()=>{flipped=!flipped;drawBoard();};$('back').onclick=()=>{if(phase==='feedback'&&frame>0){frame--;drawBoard();}};$('forward').onclick=()=>{if(phase==='feedback'&&frame<2){frame++;drawBoard();}};
$('next').onclick=()=>start(T.recommend(lessons,records).lesson);
$('reset').onclick=()=>{if(!resetArmed){resetArmed=true;$('reset').textContent='Click again to clear all six first attempts';return;}records=[];resetArmed=false;$('reset').textContent='Clear saved practice';save();start(lessons[0]);};
start(T.recommend(lessons,records).lesson);
