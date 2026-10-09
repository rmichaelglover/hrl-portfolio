'use strict';
const $=id=>document.getElementById(id);
let chapters=[],chapterIndex=0,nodeId=0,practicing=false,selected=null,pending=null,ready=false;
const chapter=()=>chapters[chapterIndex],node=()=>chapter().nodes[nodeId];
const prose=s=>s.replace(/\[%[^\]]*\]/g,'').trim();
function send(data){if(ready)$('maestro').contentWindow.postMessage(data,location.origin);}
function setNode(id){nodeId=id;selected=null;pending=null;render();}
function openChapter(i,id=0){chapterIndex=Math.max(0,Math.min(chapters.length-1,i));nodeId=chapter().nodes[id]?id:0;practicing=chapter().mode==='practice'&&nodeId===0;selected=null;pending=null;$('hint').hidden=true;$('feedback').textContent='';render();}
function readHash(){const m=location.hash.match(/^#chapter=(\d+)&node=(\d+)$/);return m?[+m[1]-1,+m[2]]:[0,0];}
function renderTree(){
  $('tree').replaceChildren();
  function walk(id,target){const n=chapter().nodes[id],b=document.createElement('button');b.textContent=n.parent===null?'Start':`${chapter().nodes[n.parent].fullmove}${chapter().nodes[n.parent].turn==='w'?'.':'...'} ${n.san}`;b.className=id===nodeId?'active':'';b.onclick=()=>setNode(id);target.append(b);if(n.children.length){walk(n.children[0],target);n.children.slice(1).forEach(child=>{const v=document.createElement('span');v.className='branch';target.append(v);walk(child,v);});}}
  walk(0,$('tree'));
}
function render(){
  const c=chapter(),n=node();$('chapters').replaceChildren();
  chapters.forEach((ch,i)=>{const b=document.createElement('button');b.textContent=ch.title;b.className=i===chapterIndex?'active':'';b.setAttribute('aria-current',i===chapterIndex?'true':'false');const label=document.createElement('span');label.textContent=ch.mode==='practice'?'Interactive lesson':'Annotated exploration';b.append(label);b.onclick=()=>openChapter(i);$('chapters').append(b);});
  $('chapterNumber').textContent=`CHAPTER ${chapterIndex+1} / ${chapters.length}`;$('title').textContent=c.title.split(' · ')[1];$('chapterIntro').textContent=prose(c.nodes[0].comment);
  $('turn').textContent=`${n.turn==='w'?'White':'Black'} to move · ${practicing?'your turn':'explore'}`;$('outcome').textContent=n.outcome;
  $('practice').hidden=!practicing;$('explore').hidden=practicing;$('mode').hidden=c.mode!=='practice';$('mode').textContent=practicing?'Explore':'Try lesson again';$('promotion').hidden=!pending;$('hint').textContent=c.hint;
  $('positionLabel').textContent=n.parent===null?'Starting position':`${c.nodes[n.parent].fullmove}${c.nodes[n.parent].turn==='w'?'.':'...'} ${n.san}`;$('comment').hidden=n.parent===null;$('comment').textContent=prose(n.comment)||(n.outcome||'Follow the next move, or jump to the next story beat.');
  $('variations').replaceChildren();n.children.forEach((id,i)=>{const b=document.createElement('button');b.textContent=c.nodes[id].san+(i?' · variation':'');b.onclick=()=>setNode(id);$('variations').append(b);});
  if(practicing)$('tree').replaceChildren();else renderTree();
  $('first').disabled=practicing||nodeId===0;$('prev').disabled=practicing||n.parent===null;for(const id of ['next','last'])$(id).disabled=practicing||!n.children.length;$('beat').disabled=practicing||!c.beats.some(id=>id>nodeId);$('previousChapter').disabled=chapterIndex===0;$('nextChapter').disabled=chapterIndex===chapters.length-1;
  history.replaceState(null,'',`#chapter=${chapterIndex+1}&node=${nodeId}`);document.title=`${$('title').textContent} · The Stalemate Gambit Explained`;
  send({type:'maestro-study-position',frame:n.frame,classic:$('pieces').value==='classic',squares:(n.comment.match(/\[%csl ([^\]]+)\]/)||[])[1]||''});
}
function chooseMove(uci){
  pending=null;$('promotion').hidden=true;
  if(practicing&&!chapter().answers.includes(uci)){$('feedback').textContent=chapterIndex===3?'That crown does not preserve a winning game here. Try another piece, or reveal the variations to see why.':'That is not the move for this lesson. Try the hint.';selected=null;send({type:'maestro-study-highlight',selected:null,targets:[]});return;}
  const next=node().children.find(id=>chapter().nodes[id].uci===uci);
  if(next===undefined){$('outcome').textContent='That legal move is outside this chapter’s authored variations. Choose a move from the move tree.';selected=null;send({type:'maestro-study-highlight',selected:null,targets:[]});return;}
  const solved=practicing;practicing=false;setNode(next);if(solved)$('outcome').textContent=(node().outcome?node().outcome+' · ':'')+'Lesson solved! Explore the replies below.';
}
function clickSquare(square){
  const legal=node().legal;
  if(selected){const choices=legal.filter(m=>m.slice(0,2)===selected&&m.slice(2,4)===square);if(choices.length>1){pending=choices;$('promotion').hidden=false;return;}if(choices.length===1){chooseMove(choices[0]);return;}}
  selected=legal.some(m=>m.slice(0,2)===square)?square:null;send({type:'maestro-study-highlight',selected,targets:selected?[...new Set(legal.filter(m=>m.slice(0,2)===selected).map(m=>m.slice(2,4)))]:[]});
}
window.addEventListener('message',e=>{if(e.origin!==location.origin||e.source!==$('maestro').contentWindow)return;if(e.data.type==='maestro-study-ready'){ready=true;if(chapters.length)render();}if(e.data.type==='maestro-study-square'&&chapters.length)clickSquare(e.data.square);});
$('maestro').addEventListener('load',()=>{ready=true;if(chapters.length)render();});$('pieces').onchange=render;
$('first').onclick=()=>setNode(0);$('prev').onclick=()=>{if(node().parent!==null)setNode(node().parent);};$('next').onclick=()=>{if(node().children.length)setNode(node().children[0]);};$('last').onclick=()=>{let n=node();while(n.children.length)n=chapter().nodes[n.children[0]];setNode(n.id);};$('beat').onclick=()=>{const next=chapter().beats.find(id=>id>nodeId);if(next!==undefined)setNode(next);};
$('previousChapter').onclick=()=>openChapter(chapterIndex-1);$('nextChapter').onclick=()=>openChapter(chapterIndex+1);$('hintButton').onclick=()=>{$('hint').hidden=!$('hint').hidden;};$('reveal').onclick=()=>{practicing=false;render();};$('mode').onclick=()=>{if(practicing){practicing=false;render();}else openChapter(chapterIndex);};
document.querySelectorAll('[data-promo]').forEach(b=>b.onclick=()=>{if(pending){const move=pending.find(m=>m[4]===b.dataset.promo);if(move)chooseMove(move);}});
document.addEventListener('keydown',e=>{if(['INPUT','SELECT','TEXTAREA','BUTTON'].includes(e.target.tagName)||practicing)return;if(e.key==='ArrowRight'){$('next').click();e.preventDefault();}if(e.key==='ArrowLeft'){$('prev').click();e.preventDefault();}});
window.addEventListener('hashchange',()=>{if(chapters.length)openChapter(...readHash());});
fetch('study.json').then(r=>{if(!r.ok)throw Error('Could not load chapters');return r.json();}).then(data=>{chapters=data;openChapter(...readHash());}).catch(e=>{$('title').textContent='The study could not open';$('chapterIntro').textContent=e.message+'. Reload, or download the PGN above.';});
// Load Maestro after the portfolio's existing entry agreement is accepted.
function startBoard(){if(document.querySelector('.gaia-entry'))return false;$('maestro').src=$('maestro').dataset.src;return true;}
if(!startBoard()){const observer=new MutationObserver(()=>{if(startBoard())observer.disconnect();});observer.observe(document.body,{childList:true});}
