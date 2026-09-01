const $=s=>document.querySelector(s), data=window.BIBLE_DATA;
const OT_BOOKS=39;
let state=JSON.parse(localStorage.getItem('ebr-state')||'null')||{t:'web',book:'Genesis',chapter:1};
const speech={supported:'speechSynthesis'in window&&'SpeechSynthesisUtterance'in window,active:false,paused:false,index:0,token:0,voices:[]};
const save=()=>localStorage.setItem('ebr-state',JSON.stringify(state));
const availableBooks=()=>Object.keys(data[state.t]||data.web);
const chapters=b=>Object.keys((data[state.t]||data.web)[b]||{}).map(Number).sort((a,b)=>a-b);
function render(){
  if(speech.active)stopReading();
  let source=data[state.t]||data.web;
  if(!source[state.book]) state.book=Object.keys(source)[0];
  let cs=chapters(state.book); if(!cs.includes(+state.chapter)) state.chapter=cs[0];
  const vs=source[state.book][state.chapter];
  $('#referenceBtn').textContent=`${state.book} ${state.chapter}`;
  const books=availableBooks(), testament=books.indexOf(state.book)<OT_BOOKS?'Old Testament':'New Testament';
  $('#passage').innerHTML=`<h1>${state.book}</h1><h2>${testament} · Chapter ${state.chapter} of ${cs.length}</h2>`+vs.map((v,i)=>`<span class="verse" id="v${i+1}"><span class="vnum">${i+1}</span>${escapeHtml(v)}</span>`).join('');
  document.querySelectorAll('.verse').forEach((verse,index)=>{verse.title=`Read from verse ${index+1}`;verse.onclick=()=>startReading(index)});
  fillNav(); save(); window.scrollTo({top:0});
}
function escapeHtml(s){return s.replace(/[&<>]/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;'}[c]))}
function fillNav(){
  const books=availableBooks(), options=items=>items.map(b=>`<option ${b===state.book?'selected':''}>${b}</option>`).join('');
  $('#book').innerHTML=`<optgroup label="Old Testament · 39 books">${options(books.slice(0,OT_BOOKS))}</optgroup><optgroup label="New Testament · 27 books">${options(books.slice(OT_BOOKS))}</optgroup>`;
  $('#chapter').innerHTML=chapters(state.book).map(c=>`<option ${c==state.chapter?'selected':''}>${c}</option>`).join('');
}
function parseRef(q){q=q.trim().replace(/^:/,'');let m=q.match(/^(.+?)\s+(\d+)(?::(\d+))?$/);if(!m)return null;let book=availableBooks().find(b=>b.toLowerCase()===m[1].toLowerCase())||availableBooks().find(b=>b.toLowerCase().startsWith(m[1].toLowerCase()));return book?{book,chapter:+m[2],verse:+m[3]||null}:null}
function go(ref){if(!ref)return;let src=(data[state.t]||data.web)[ref.book];if(!src||!src[ref.chapter])return;state.book=ref.book;state.chapter=ref.chapter;render();if(ref.verse)setTimeout(()=>$('#v'+ref.verse)?.scrollIntoView({block:'center'}),20)}
function step(dir){let books=availableBooks(), bi=books.indexOf(state.book), cs=chapters(state.book), ci=cs.indexOf(+state.chapter);ci+=dir;if(ci<0&&bi>0){state.book=books[--bi];cs=chapters(state.book);state.chapter=cs.at(-1)}else if(ci>=cs.length&&bi<books.length-1){state.book=books[++bi];state.chapter=chapters(state.book)[0]}else if(ci>=0&&ci<cs.length)state.chapter=cs[ci];render()}
function setup(){
  $('#translation').innerHTML=TRANSLATIONS.map(t=>`<option value="${t.id}" ${t.id===state.t?'selected':''} ${!data[t.id]?'disabled':''}>${t.abbr}${!data[t.id]?' ·':''}</option>`).join('');
  $('#menuBtn').onclick=$('#referenceBtn').onclick=()=>$('#drawer').classList.remove('hidden'); $('#settingsBtn').onclick=()=>$('#settings').classList.remove('hidden');
  document.querySelectorAll('[data-close]').forEach(b=>b.onclick=()=>$('#'+b.dataset.close).classList.add('hidden'));
  $('#jumpForm').onsubmit=e=>{e.preventDefault();go(parseRef($('#jump').value));};
  $('#book').onchange=e=>{state.book=e.target.value;state.chapter=chapters(state.book)[0];render()}; $('#chapter').onchange=e=>{state.chapter=+e.target.value;render()};
  $('#prev').onclick=()=>step(-1);$('#next').onclick=()=>step(1);
  $('#search').oninput=e=>search(e.target.value.replace(/^\//,''));
  $('#bookmarkBtn').onclick=bookmark; showBookmarks();
  setupSpeech();
  bindSetting('fontSize',v=>document.documentElement.style.setProperty('--size',v+'px'));
  bindSetting('lineWidth',v=>document.documentElement.style.setProperty('--measure',v+'ch'));
  bindSetting('lineHeight',v=>document.documentElement.style.setProperty('--lh',(v/10)));
  $('#verseNumbers').onchange=e=>$('#passage').classList.toggle('no-vnums',!e.target.checked);
  $('#serif').onchange=e=>document.body.classList.toggle('sans',!e.target.checked);$('#dark').onchange=e=>document.body.classList.toggle('dark',e.target.checked);
  document.addEventListener('keydown',keys);render();
}
function setupSpeech(){
  if(!speech.supported){$('#readBtn').disabled=true;$('#readBtn').title='Read aloud is unavailable in this browser';return}
  $('#readBtn').onclick=()=>{if(!speech.active)startReading(0);else toggleSpeech()};
  $('#speechToggle').onclick=toggleSpeech;$('#speechStop').onclick=stopReading;
  const loadVoices=()=>{speech.voices=speechSynthesis.getVoices();const select=$('#speechVoice'),chosen=select.value;select.replaceChildren(new Option('System default',''));speech.voices.forEach((voice,index)=>select.add(new Option(`${voice.name} · ${voice.lang}`,String(index))));select.value=chosen};
  loadVoices();speechSynthesis.addEventListener?.('voiceschanged',loadVoices);
}
function chapterVerses(){return (data[state.t]||data.web)[state.book][state.chapter]}
function startReading(index=0){
  if(!speech.supported)return;
  speechSynthesis.cancel();speech.token++;speech.active=true;speech.paused=false;speech.index=index;
  $('#speechBar').classList.remove('hidden');$('#readBtn').textContent='❚❚ Pause';$('#speechToggle').textContent='Pause';
  setTimeout(()=>speakCurrent(speech.token),20);
}
function speakCurrent(token){
  if(!speech.active||token!==speech.token)return;
  const verses=chapterVerses();
  while(speech.index<verses.length&&!verses[speech.index].trim())speech.index++;
  if(speech.index>=verses.length){finishReading();return}
  document.querySelectorAll('.verse.speaking').forEach(v=>v.classList.remove('speaking'));
  const element=$('#v'+(speech.index+1));element?.classList.add('speaking');element?.scrollIntoView({block:'center',behavior:'smooth'});
  const prefix=speech.index===0?`${state.book}, chapter ${state.chapter}. `:`Verse ${speech.index+1}. `;
  const utterance=new SpeechSynthesisUtterance(prefix+verses[speech.index]);
  utterance.rate=Number($('#speechRate').value);const voiceIndex=$('#speechVoice').value;if(voiceIndex!=='')utterance.voice=speech.voices[Number(voiceIndex)]||null;
  $('#speechStatus').textContent=`Verse ${speech.index+1} of ${verses.length}`;
  utterance.onend=()=>{if(speech.active&&token===speech.token){speech.index++;speakCurrent(token)}};
  utterance.onerror=event=>{if(event.error!=='canceled'&&event.error!=='interrupted'){stopReading();$('#speechStatus').textContent='Speech could not continue'}};
  speechSynthesis.speak(utterance);
}
function toggleSpeech(){
  if(!speech.active){startReading(0);return}
  if(speech.paused){speechSynthesis.resume();speech.paused=false;$('#readBtn').textContent='❚❚ Pause';$('#speechToggle').textContent='Pause'}
  else{speechSynthesis.pause();speech.paused=true;$('#readBtn').textContent='▶ Resume';$('#speechToggle').textContent='Resume'}
}
function stopReading(){
  if(!speech.supported)return;speech.token++;speech.active=false;speech.paused=false;speechSynthesis.cancel();
  document.querySelectorAll('.verse.speaking').forEach(v=>v.classList.remove('speaking'));$('#speechBar').classList.add('hidden');$('#readBtn').textContent='▶ Read';$('#speechStatus').textContent='Ready';
}
function finishReading(){
  speech.active=false;speech.paused=false;document.querySelectorAll('.verse.speaking').forEach(v=>v.classList.remove('speaking'));$('#readBtn').textContent='▶ Read';$('#speechToggle').textContent='Read again';$('#speechStatus').textContent='Chapter complete';
}
function bindSetting(id,fn){$('#'+id).oninput=e=>fn(e.target.value);fn($('#'+id).value)}
function search(q){let out=$('#searchResults');if(q.length<2){out.innerHTML='';return}let res=[];let src=data[state.t]||data.web;for(let [b,chs] of Object.entries(src))for(let [c,vs] of Object.entries(chs))vs.forEach((v,i)=>{if(v.toLowerCase().includes(q.toLowerCase())&&res.length<40)res.push({b,c:+c,v:i+1,text:v})});out.innerHTML=res.map(r=>`<button data-ref="${r.b}|${r.c}|${r.v}"><strong>${r.b} ${r.c}:${r.v}</strong><br>${escapeHtml(r.text)}</button>`).join('');out.querySelectorAll('button').forEach(b=>b.onclick=()=>{let [book,chapter,verse]=b.dataset.ref.split('|');go({book,chapter:+chapter,verse:+verse})})}
function bookmark(){let bs=JSON.parse(localStorage.getItem('ebr-bookmarks')||'[]'), key=`${state.t}|${state.book}|${state.chapter}`;bs=bs.includes(key)?bs.filter(x=>x!==key):[key,...bs];localStorage.setItem('ebr-bookmarks',JSON.stringify(bs));showBookmarks()}
function showBookmarks(){let bs=JSON.parse(localStorage.getItem('ebr-bookmarks')||'[]');$('#bookmarks').innerHTML=bs.length?bs.map(x=>{let [t,b,c]=x.split('|');return `<button data-b="${escapeHtml(x)}">${b} ${c} · ${t.toUpperCase()}</button>`}).join(''):'<small>No bookmarks yet.</small>';$('#bookmarks').querySelectorAll('button').forEach(b=>b.onclick=()=>{let [t,book,chapter]=b.dataset.b.split('|');if(data[t])state.t=t;go({book,chapter:+chapter})})}
let g=false;function keys(e){if(/INPUT|SELECT/.test(e.target.tagName)){if(e.key==='Escape')e.target.blur();return}if(e.key==='Escape')document.querySelectorAll('.panel').forEach(p=>p.classList.add('hidden'));else if(e.key==='/'){e.preventDefault();$('#drawer').classList.remove('hidden');$('#search').focus()}else if(e.key===':'){e.preventDefault();$('#drawer').classList.remove('hidden');$('#jump').focus();$('#jump').value=':'}else if(e.key===']')step(1);else if(e.key==='[')step(-1);else if(e.key==='j')scrollBy({top:60,behavior:'smooth'});else if(e.key==='k')scrollBy({top:-60,behavior:'smooth'});else if(e.key==='G')scrollTo({top:document.body.scrollHeight,behavior:'smooth'});else if(e.key==='g'){if(g){scrollTo({top:0,behavior:'smooth'});g=false}else{g=true;setTimeout(()=>g=false,500)}}else if(e.ctrlKey&&e.key==='f'){e.preventDefault();scrollBy({top:innerHeight*.85,behavior:'smooth'})}else if(e.ctrlKey&&e.key==='b'){e.preventDefault();scrollBy({top:-innerHeight*.85,behavior:'smooth'})}}
if('serviceWorker'in navigator)navigator.serviceWorker.register('sw.js');setup();
