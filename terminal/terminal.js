(() => {
'use strict';
const $ = id => document.getElementById(id);
const root = new URL('../', location.href);
const state = {entries:[], filtered:[], selected:0, category:'All', page:null, trail:[], version:0, tab:'text'};
let paused = matchMedia('(prefers-reduced-motion: reduce)').matches, angle = 0, lastFrame = 0;
const history = []; let historyIndex = 0;
const clean = value => String(value || '').replace(/[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]/g, '').trim();
function localURL(href, base=root) {
  const target = new URL(href, base);
  if (!['http:', 'https:'].includes(target.protocol) || target.origin !== root.origin || !target.pathname.startsWith(root.pathname)) return null;
  return target;
}
function log(text) {
  const p = document.createElement('p'); p.textContent = text; $('output').append(p);
  while ($('output').children.length > 100) $('output').firstChild.remove();
  $('output').scrollTop = $('output').scrollHeight;
}
function matches(query) {
  const words = query.toLocaleLowerCase().trim().split(/\s+/).filter(Boolean);
  return state.entries.filter(e => words.every(w => `${e.title} ${e.href} ${e.description} ${e.category}`.toLocaleLowerCase().includes(w)));
}
function choose(index, scroll=false) {
  state.selected = Math.max(0, Math.min(index, state.filtered.length - 1));
  [...$('worlds').children].forEach((el, i) => {
    el.setAttribute('aria-selected', String(i === state.selected));
    if (i === state.selected) { $('worlds').setAttribute('aria-activedescendant', el.id); if (scroll) el.scrollIntoView({block:'nearest'}); }
  });
  const e = state.filtered[state.selected];
  $('enter-preview').disabled = !e; $('read').disabled = !e;
  $('detail').textContent = e ? `${e.title}\n${e.category}\n\n${e.description}` : 'No matching worlds. Clear the filter or choose All.';
  if (!e) $('worlds').removeAttribute('aria-activedescendant');
}
function showDirectory() {
  stopLive();
  state.version++; state.page = null; state.trail = [];
  $('reader').hidden = true; document.querySelector('.workspace').hidden = false;
  $('back').disabled = true; $('breadcrumb').textContent = 'ROOT / WORLDS / ' + state.category.toUpperCase();
}
function filter(query) {
  showDirectory(); state.filtered = matches(query).filter(e => state.category === 'All' || e.category === state.category);
  $('worlds').replaceChildren();
  state.filtered.forEach((e, i) => {
    const row = document.createElement('div'); row.id = `world-${i}`; row.setAttribute('role','option');
    const number = document.createElement('span'); number.className = 'number'; number.textContent = String(i + 1).padStart(3,'0');
    const label = document.createElement('span'); label.textContent = e.title;
    const category = document.createElement('small'); category.textContent = e.category; label.append(category);
    const arrow = document.createElement('span'); arrow.textContent = '›'; row.append(number,label,arrow);
    row.addEventListener('click', () => { choose(i); openPage(localURL(e.href), e.title); });
    row.addEventListener('pointerenter', () => choose(i)); $('worlds').append(row);
  });
  choose(0); $('count').textContent = `${state.filtered.length} FOUND`;
  $('connection').textContent = `${state.entries.length} WORLDS / ONLINE`;
}
function categories() {
  ['All', ...new Set(state.entries.map(e => e.category))].forEach(name => {
    const button = document.createElement('button'); button.textContent = name; button.setAttribute('aria-pressed',String(name === state.category));
    button.addEventListener('click', () => { state.category = name; [...$('categories').children].forEach(el => el.setAttribute('aria-pressed',String(el === button))); filter($('search').value); });
    $('categories').append(button);
  });
}
function resolve(query) {
  if (!query.trim()) { const e=state.filtered[state.selected]; return e && {url:localURL(e.href), title:e.title}; }
  if (/^\d+$/.test(query)) { const e=state.filtered[Number(query)-1]; if(e) return {url:localURL(e.href), title:e.title}; log('That world number is not in the current list.'); return null; }
  const found = matches(query);
  if (found.length === 1) return {url:localURL(found[0].href),title:found[0].title};
  log(found.length ? `${found.length} matches. Search to narrow the list, then enter a world number.` : 'No matching worlds.'); return null;
}
function tab(name) {
  state.tab = name;
  ['text','links','visuals','live'].forEach(t => { $('page-'+t).hidden = t !== name; });
  document.querySelectorAll('[data-tab]').forEach(el => el.setAttribute('aria-pressed',String(el.dataset.tab === name)));
  if (name === 'visuals' && state.page) renderGraphics(state.page);
  if (name === 'live' && state.page) startLive(state.page);
}
function back() {
  if (state.trail.length) { const previous=state.trail.pop(); openPage(previous.url,previous.title,false); }
  else { showDirectory(); $('worlds').focus(); }
}
function pageText(doc) {
  const source=doc.querySelector('main,article,[role=main]') || doc.body;
  const clone=source.cloneNode(true);
  clone.querySelectorAll('script,style,template,noscript,svg,canvas,iframe').forEach(el=>el.remove());
  clone.querySelectorAll('p,div,h1,h2,h3,h4,li,section,article,br,tr,pre').forEach(el=>el.append(doc.createTextNode('\n')));
  return (clone.textContent || '').split('\n').map(line=>clean(line).replace(/[ \t]+/g,' ')).filter(Boolean).join('\n\n');
}
async function openPage(target, title, push=true) {
  if (!target) { log('This location is outside the portfolio.'); return; }
  if (push && state.page) state.trail.push({url:state.page.url,title:state.page.title});
  stopLive();
  const version=++state.version;
  state.page={url:target,title,version,images:[],graphicsStarted:false};
  $('reader').hidden=false; document.querySelector('.workspace').hidden=true;
  $('back').disabled=false; $('reader-title').textContent=title; $('breadcrumb').textContent=`ROOT / ${decodeURIComponent(target.pathname.slice(root.pathname.length)) || 'HOME'}`;
  $('page-status').textContent='LOADING WORLD…'; $('page-text').textContent=''; $('page-links').replaceChildren(); $('page-visuals').replaceChildren(); $('link-count').textContent=''; $('image-count').textContent=''; tab('text');
  try {
    if (/\.(pdf|pgn|csv|json|md|txt|py|js|cpp|h|css|xml)$/i.test(target.pathname)) { await openDocument(target,version); return; }
    if (/\.(png|jpe?g|gif|webp|svg)$/i.test(target.pathname)) { state.page.images=[{src:target.href,alt:title}]; $('page-status').textContent='IMAGE / CHARACTER RENDERER'; $('image-count').textContent='(1)'; tab('visuals'); return; }
    const response=await fetch(target); if(!response.ok) throw Error(`HTTP ${response.status}`);
    const type=response.headers.get('content-type')||'';
    if (!type.includes('html')) { await openDocument(target,version,response); return; }
    const source=await response.text(); const doc=new DOMParser().parseFromString(source,'text/html'); if(version!==state.version)return;
    state.page.source=source;
    const base=localURL(response.url)||target;
    const active=state.page; active.title=clean(doc.querySelector('h1')?.textContent)||title; $('reader-title').textContent=active.title;
    $('page-text').textContent=pageText(doc)||'This world generates its text dynamically.';
    const seen=new Set(); let external=0;
    doc.querySelectorAll('a[href]').forEach(a=>{
      const raw=a.getAttribute('href'); const dest=localURL(raw,base);
      if(!dest){external++;return;} const key=dest.href; if(seen.has(key))return;seen.add(key);
      const button=document.createElement('button');button.className='link-row'; const label=clean(a.textContent)||clean(a.querySelector('img')?.alt)||decodeURIComponent(dest.pathname.split('/').filter(Boolean).pop()||'Home');
      button.textContent=`[${seen.size}] ${label}`;const small=document.createElement('small');small.textContent=dest.pathname.slice(root.pathname.length)||'Home';button.append(small);
      button.addEventListener('click',()=>{if(dest.pathname===base.pathname && dest.hash){const anchor=doc.getElementById(decodeURIComponent(dest.hash.slice(1)));if(anchor){tab('text');const excerpt=clean(anchor.textContent).slice(0,120);const pos=$('page-text').textContent.indexOf(excerpt);$('page-text').scrollTop=Math.max(0, (pos/Math.max(1,$('page-text').textContent.length))*$('page-text').scrollHeight);return;}}openPage(dest,label);}); $('page-links').append(button);
    });
    if(!seen.size)$('page-links').textContent='No other portfolio pages linked here.';
    active.images=[...doc.querySelectorAll('img')].map(img=>({src:localURL(img.getAttribute('src'),base)?.href,alt:clean(img.alt)||'World graphic'})).filter(img=>img.src);
    const unique=new Set();active.images=active.images.filter(img=>{if(unique.has(img.src))return false;unique.add(img.src);return true;});
    active.dynamic=doc.querySelectorAll('canvas,iframe,video,audio').length; active.controls=doc.querySelectorAll('input,select,button').length;
    $('link-count').textContent=`(${seen.size})`; $('image-count').textContent=`(${active.images.length})`;
    $('page-status').textContent=`TUI VIEW / ${seen.size} local links / ${active.images.length} graphics`+(active.dynamic||active.controls?' / Try Live scene for canvas graphics and controls.':'')+(external?` / ${external} external references listed in source text.`:'');
    $('page-text').scrollTop=0;
  } catch(error) {if(version===state.version){$('page-status').textContent='WORLD UNAVAILABLE';$('page-text').textContent=`Could not load this world (${error.message}). Use Back or Worlds to continue.`;}}
}
async function openDocument(target,version,response) {
  const r=response||await fetch(target);if(!r.ok)throw Error(`HTTP ${r.status}`);
  if(version!==state.version)return;
  if(/\.pdf$/i.test(target.pathname)){ $('page-status').textContent='PDF DOCUMENT';$('page-text').textContent='This PDF needs a text or page-image adapter. Its browser viewer is not rendered as a TUI yet. Use Back to continue exploring.';return; }
  const text=await r.text();if(version!==state.version)return;$('page-status').textContent='SOURCE / TEXT DOCUMENT';$('page-text').textContent=clean(text).slice(0,500000);
}
async function asciiImage(src) {
  const image=new Image();image.decoding='async';
  await new Promise((resolve,reject)=>{image.onload=resolve;image.onerror=()=>reject(Error('Image could not be loaded'));image.src=src;});
  const width=96,height=Math.max(1,Math.min(64,Math.round(width*image.naturalHeight/image.naturalWidth*.46)));
  const canvas=document.createElement('canvas');canvas.width=width;canvas.height=height;const context=canvas.getContext('2d',{willReadFrequently:true});context.fillStyle='#000';context.fillRect(0,0,width,height);context.drawImage(image,0,0,width,height);
  const data=context.getImageData(0,0,width,height).data, shades=' .:;+=xX$&@';let result='';
  for(let y=0;y<height;y++){for(let x=0;x<width;x++){const i=(y*width+x)*4,l=.2126*data[i]+.7152*data[i+1]+.0722*data[i+2];result+=shades[Math.min(shades.length-1,Math.floor(l/256*shades.length))];}result+='\n';}return result;
}
async function renderGraphics(page) {
  if(page.graphicsStarted)return;page.graphicsStarted=true;
  const host=$('page-visuals');
  if(!page.images.length){host.textContent='No static images in this world. Live canvas / WebGL scenes need a scene-state adapter to render their graphics and controls in character cells.';return;}
  const cards=page.images.map((image,i)=>{const card=document.createElement('section');card.className='graphic';const heading=document.createElement('h3');heading.textContent=`[${i+1}] ${image.alt}`;const pre=document.createElement('pre');pre.className='ascii';pre.setAttribute('role','img');pre.setAttribute('aria-label',image.alt+' rendered as ASCII');pre.textContent='[ RENDERING… ]';card.append(heading,pre);host.append(card);return pre;});
  // Three workers keep image decoding bounded on pages with many graphics.
  let next=0;async function worker(){while(next<page.images.length){if(page.version!==state.version)return;const i=next++;try{const rendered=await asciiImage(page.images[i].src);if(page.version===state.version)cards[i].textContent=rendered;}catch(error){if(page.version===state.version)cards[i].textContent=`[ ${error.message} ]`;}}}
  await Promise.all([worker(),worker(),worker()]);
}
let engine = null, livePage = null, liveCanvases = [], controlSignature = '';
function stopLive() {
  if(engine)engine.remove(); engine=null;livePage=null;liveCanvases=[];controlSignature='';
}
function characters(context,width,height) {
  const data=context.getImageData(0,0,width,height).data,shades=' .:;+=xX$&@';let result='';
  for(let y=0;y<height;y++){for(let x=0;x<width;x++){const i=(y*width+x)*4,l=.2126*data[i]+.7152*data[i+1]+.0722*data[i+2];result+=shades[Math.min(shades.length-1,Math.floor(l/256*shades.length))];}result+='\n';}return result;
}
function startLive(page) {
  if(livePage===page)return;
  stopLive(); $('live-controls').replaceChildren();$('live-frames').replaceChildren();
  if(!page.source){$('live-status').textContent='Enter an HTML world to use the live scene adapter.';return;}
  livePage=page;$('live-status').textContent='Starting world engine / rendering canvases as character cells…';
  const doc=new DOMParser().parseFromString(page.source,'text/html');
  doc.querySelectorAll('base').forEach(el=>el.remove());
  const base=doc.createElement('base');base.href=page.url.href;doc.head.prepend(base);
  // Keep the drawing buffer so WebGL frames can be sampled after rendering.
  const hook=doc.createElement('script');hook.textContent="(()=>{const original=HTMLCanvasElement.prototype.getContext;HTMLCanvasElement.prototype.getContext=function(type,options){return original.call(this,type,/webgl/.test(type)?{...options,preserveDrawingBuffer:true}:options)};document.addEventListener('click',e=>{const a=e.target.closest('a');if(a)e.preventDefault()},true)})();";
  base.after(hook);
  engine=document.createElement('iframe');engine.className='engine-frame';engine.title='World engine for character rendering';engine.setAttribute('aria-hidden','true');engine.tabIndex=-1;
  engine.setAttribute('sandbox','allow-scripts allow-same-origin');engine.setAttribute('allow',"autoplay 'none'; camera 'none'; microphone 'none'; geolocation 'none'");
  engine.srcdoc='<!doctype html>'+doc.documentElement.outerHTML;
  const frame=engine;
  engine.addEventListener('load',()=>{if(engine!==frame)return;updateLiveControls();captureLive();for(const delay of [200,1000])setTimeout(()=>{if(engine===frame)captureLive();},delay);});document.body.append(engine);
}
function updateLiveControls() {
  if(!engine || !engine.contentDocument)return;
  const doc=engine.contentDocument;
  const controls=[...doc.querySelectorAll('button,select,input')].filter(el=>{
    const rect=el.getBoundingClientRect();return rect.width>0 && rect.height>0 && !el.disabled && !(el.tagName==='INPUT' && ['password','file','hidden','submit'].includes(el.type));
  });
  const signature=controls.map(el=>`${el.tagName}:${el.id}:${el.textContent}:${el.disabled}`).join('|');
  if(signature===controlSignature)return;controlSignature=signature;$('live-controls').replaceChildren();
  controls.slice(0,80).forEach(el=>{
    const label=clean(doc.querySelector(`label[for="${CSS.escape(el.id)}"]`)?.textContent || [...(el.closest('label')?.childNodes||[])].filter(n=>n.nodeType===3).map(n=>n.textContent).join(' ') || el.getAttribute('aria-label') || el.title || el.textContent || el.id || el.type).slice(0,100);
    if(el.tagName==='BUTTON'){const button=document.createElement('button');button.textContent=`[ ${label} ]`;button.addEventListener('click',()=>{el.click();controlSignature='';updateLiveControls();captureLive();});$('live-controls').append(button);return;}
    const wrapper=document.createElement('label');wrapper.textContent=label;
    const input=document.createElement(el.tagName==='SELECT'?'select':'input');
    if(el.tagName==='SELECT'){[...el.options].forEach(option=>{const item=document.createElement('option');item.value=option.value;item.textContent=option.textContent;input.append(item);});input.value=el.value;}
    else{input.type=['range','number','checkbox','radio','color'].includes(el.type)?el.type:'text';input.value=el.value;input.checked=el.checked;if(el.min)input.min=el.min;if(el.max)input.max=el.max;if(el.step)input.step=el.step;}
    input.addEventListener('input',()=>{el.value=input.value;el.checked=input.checked;el.dispatchEvent(new engine.contentWindow.Event('input',{bubbles:true}));});
    input.addEventListener('change',()=>{el.value=input.value;el.checked=input.checked;el.dispatchEvent(new engine.contentWindow.Event('change',{bubbles:true}));captureLive();});wrapper.append(input);$('live-controls').append(wrapper);
  });
}
function captureLive() {
  if(!engine || !engine.contentDocument || state.page!==livePage || state.tab!=='live')return;
  const sources=[...engine.contentDocument.querySelectorAll('canvas')].filter(c=>c.width>0&&c.height>0).slice(0,8);
  if(sources.length!==liveCanvases.length||sources.some((c,i)=>liveCanvases[i]?.source!==c)){
    $('live-frames').replaceChildren();liveCanvases=sources.map((source,i)=>{
      const card=document.createElement('section');card.className='graphic';const title=document.createElement('h3');title.textContent=`[LIVE ${i+1}] ${source.id||'World canvas'} / click character cells to interact`;
      const pre=document.createElement('pre');pre.className='ascii';pre.setAttribute('role','img');pre.setAttribute('aria-label','Live world canvas rendered as terminal characters');
      pre.addEventListener('click',event=>{const rect=pre.getBoundingClientRect(),bounds=source.getBoundingClientRect();const x=(event.clientX-rect.left)/rect.width*bounds.width,y=(event.clientY-rect.top)/rect.height*bounds.height;for(const type of ['pointerdown','mousedown','pointerup','mouseup','click']){const EventType=type.startsWith('pointer')?engine.contentWindow.PointerEvent:engine.contentWindow.MouseEvent;source.dispatchEvent(new EventType(type,{bubbles:true,clientX:bounds.left+x,clientY:bounds.top+y,button:0,pointerId:1,pointerType:'mouse',isPrimary:true}));}});
      card.append(title,pre);$('live-frames').append(card);return {source,pre};
    });
  }
  liveCanvases.forEach(({source,pre})=>{try{const width=96,height=Math.max(1,Math.min(60,Math.round(width*source.height/source.width*.46)));const canvas=document.createElement('canvas');canvas.width=width;canvas.height=height;const context=canvas.getContext('2d',{willReadFrequently:true});context.fillStyle='#000';context.fillRect(0,0,width,height);context.drawImage(source,0,0,width,height);pre.textContent=characters(context,width,height);}catch{pre.textContent='[ This canvas cannot be sampled: it uses protected external media. ]';}});
  $('live-status').textContent=sources.length?`LIVE TUI / ${sources.length} canvas surfaces / original world engine / character-cell controls`:'This world has no live canvas surface. Use Read, Explore links, or ASCII graphics. DOM-only games and audio need dedicated TUI adapters.';
  updateLiveControls();
}

function pause(){paused=!paused;$('pause').textContent=paused?'[ RESUME MOTION ]':'[ PAUSE MOTION ]';$('pause').setAttribute('aria-pressed',String(paused));}
function command(raw) {
  const [verb,...args]=raw.trim().split(/\s+/),query=args.join(' ');if(!verb)return;log(`hrl@matrix:~$ ${raw}`);
  switch(verb.toLowerCase()) {
    case 'help':$('console').open=true;log('Click any world to enter. Everything opens inside this terminal.\n\nsearch <words>   filter all worlds\nopen/read <n>    enter numbered world (or unique name)\nls [query]       list worlds\nback             previous page\nworlds           root directory\nlinks            linked portfolio pages\ngraphics         image-to-ASCII view\nlive             live canvas-to-ASCII view\npause            pause rain and 3D rotation\nclear            clear log\n\n↑ ↓ choose, Enter opens, / searches, Escape goes back.\nRead / Explore links / ASCII graphics / Live scene switch world views.');break;
    case 'ls':case 'list':log((query?matches(query):state.filtered).map((e,i)=>`[${i+1}] ${e.title} — ${e.href}`).join('\n')||'No matches.');$('console').open=true;break;
    case 'search':state.category='All';[...$('categories').children].forEach(el=>el.setAttribute('aria-pressed',String(el.textContent==='All')));$('search').value=query;filter(query);break;
    case 'read':case 'open':case 'go':{const e=resolve(query);if(e)openPage(e.url,e.title);break;}
    case 'worlds':showDirectory();break;case 'back':back();break;
    case 'links':if(state.page)tab('links');else log('Enter a world first.');break;
    case 'graphics':if(state.page)tab('visuals');else log('Enter a world first.');break;
    case 'live':if(state.page)tab('live');else log('Enter a world first.');break;
    case 'pause':pause();break;case 'clear':$('output').replaceChildren();break;
    default:if(/^\d+$/.test(verb)){const e=resolve(verb);if(e)openPage(e.url,e.title);}else{$('console').open=true;log('Unknown command. Type help, or use the world index.');}
  }
}
function knot(){const width=72,height=28, pixels=Array.from({length:height},()=>Array(width).fill(' ')),depth=Array.from({length:height},()=>Array(width).fill(-Infinity));const ca=Math.cos(angle),sa=Math.sin(angle),shades='.:-=+*#%@';for(let i=0;i<220;i++){const t=i*Math.PI*2/220;for(let j=0;j<12;j++){const v=j*Math.PI*2/12,r=2+Math.cos(3*t)+.22*Math.cos(v);let x=r*Math.cos(2*t),y=r*Math.sin(2*t),z=Math.sin(3*t)+.22*Math.sin(v);[x,z]=[x*ca+z*sa,z*ca-x*sa];[y,z]=[y*.85-z*.53,y*.53+z*.85];const perspective=5/(7-z),px=Math.floor(width/2+x*7*perspective*2),py=Math.floor(height/2-y*7*perspective);if(px>=0&&px<width&&py>=0&&py<height&&z>depth[py][px]){depth[py][px]=z;pixels[py][px]=shades[Math.min(8,Math.max(0,Math.floor((z+3.5)*1.4)))];}}}$('knot').textContent=pixels.map(row=>row.join('')).join('\n');}
const rainChars='01アイウエオカキクケコサシスセソラリルレロ';let rainStep=0;
function rain(){const cols=Math.min(140,Math.ceil(innerWidth/8.4)),rows=Math.min(70,Math.ceil(innerHeight/18));const lines=[];for(let y=0;y<rows;y++){let line='';for(let x=0;x<cols;x++){const head=(rainStep*(1+x%3)+x*x*7)%(rows+18),distance=(head-y+rows+18)%(rows+18);line+=distance<12?rainChars[(x*13+y*7+Math.floor(rainStep/3))%rainChars.length]:' ';}lines.push(line);}$('rain').textContent=lines.join('\n');rainStep++;}
function animate(now){if(!document.hidden&&!paused&&now-lastFrame>85){if(state.tab==='live')captureLive();angle+=.035;if(!state.page)knot();rain();lastFrame=now;}requestAnimationFrame(animate);}
function enter(){const e=state.filtered[state.selected];if(e)openPage(localURL(e.href),e.title);}
$('search').addEventListener('input',()=>filter($('search').value));$('browse').addEventListener('click',showDirectory);$('back').addEventListener('click',back);$('read').addEventListener('click',enter);$('enter-preview').addEventListener('click',enter);$('pause').addEventListener('click',pause);$('help').addEventListener('click',()=>command('help'));
document.querySelectorAll('[data-tab]').forEach(el=>el.addEventListener('click',()=>tab(el.dataset.tab)));
$('command-form').addEventListener('submit',event=>{event.preventDefault();const raw=$('command').value;history.push(raw);historyIndex=history.length;command(raw);$('command').value='';});
$('command').addEventListener('keydown',event=>{if(event.key==='ArrowUp'||event.key==='ArrowDown'){event.preventDefault();historyIndex=Math.max(0,Math.min(history.length,historyIndex+(event.key==='ArrowUp'?-1:1)));$('command').value=history[historyIndex]||'';}});
document.addEventListener('keydown',event=>{if(event.ctrlKey||event.metaKey||event.altKey)return;if(event.key==='Escape'){back();return;}if(event.target.matches('input,textarea'))return;if(event.key==='/'){event.preventDefault();$('search').focus();return;}if(state.page){if(['1','2','3','4'].includes(event.key)){event.preventDefault();tab(['text','links','visuals','live'][Number(event.key)-1]);}return;}if(event.key==='ArrowDown'||event.key==='ArrowUp'){event.preventDefault();choose(state.selected+(event.key==='ArrowDown'?1:-1),true);}if(event.key==='Enter'&&event.target===$('worlds')){event.preventDefault();enter();}});
if(paused){$('pause').textContent='[ RESUME MOTION ]';$('pause').setAttribute('aria-pressed','true');}knot();rain();requestAnimationFrame(animate);
log('MATRIX TERMINAL ONLINE. Choose a category, search, or click a world. Type help for commands.');
fetch(new URL('world-directory.json',root)).then(r=>{if(!r.ok)throw Error(`HTTP ${r.status}`);return r.json();}).then(data=>{state.entries=data.filter(e=>typeof e.title==='string'&&typeof e.description==='string'&&typeof e.category==='string'&&typeof e.href==='string'&&localURL(e.href));categories();filter('');}).catch(error=>{$('connection').textContent='OFFLINE';$('detail').textContent='Could not load the directory. Reload to retry.';log(error.message);});
})();
