/* Original household art set for Michael Emanuel Glover's Glims. */
'use strict';
window.GlimsArt=(()=>{
const $=id=>document.getElementById(id),subjects=['flowers','river','stars'],palettes={garden:['#f5e8c9','#507a69','#b76558','#d6a553'],sunset:['#efd4ba','#a66c75','#d78862','#f3c778'],blue:['#dce4dc','#648ea5','#466e79','#d6c491']};
const books=[['A Little Room','The kettle settled. Someone turned a page. Outside, the leaves kept their own time. There was enough room for a question, and enough quiet to let it wait.'],['The River’s Lesson','The river did not keep the shape of yesterday’s light. It carried a new sky past the same stones. Alex watched, then went looking for his blue paint.'],['Flowers for the Window','Mama moved the little vase toward the light. Papa found a pencil. Nobody had to paint the same flower, although they were all looking at it together.']];
let get,api,book=0,ink='#b76558',drawing=false,signature='';
function paint(c,w,h,subject='flowers',palette='garden',time=0){const p=palettes[palette]||palettes.garden;c.save();c.fillStyle=p[0];c.fillRect(0,0,w,h);c.lineWidth=Math.max(1,w*.018);
 if(subject==='river'){c.fillStyle=p[1];c.fillRect(0,h*.45,w,h*.55);c.fillStyle=p[2];c.beginPath();c.moveTo(0,h*.55);c.quadraticCurveTo(w*.3,h*.15,w*.6,h*.5);c.lineTo(w,h*.3);c.lineTo(w,h*.6);c.lineTo(0,h*.7);c.fill();c.strokeStyle=p[3];for(let i=0;i<5;i++){c.beginPath();c.moveTo(w*(.1+(i%2)*.15),h*(.65+i*.06));c.lineTo(w*(.7+Math.sin(time*.3+i)*.08),h*(.65+i*.06));c.stroke();}}
 else if(subject==='stars'){c.fillStyle=p[2];c.fillRect(0,0,w,h);for(let i=0;i<17;i++){const x=((i*47+13)%101)/101*w,y=((i*31+9)%83)/83*h;c.fillStyle=p[3];c.beginPath();c.arc(x,y,Math.max(1,w*.014),0,Math.PI*2);c.fill();}}
 else for(let i=0;i<5;i++){const x=w*(.18+i*.16),y=h*(.25+(i%3)*.12);c.strokeStyle=p[1];c.beginPath();c.moveTo(w*.5,h*.93);c.lineTo(x,y);c.stroke();for(let k=0;k<5;k++){c.fillStyle=p[2];c.beginPath();c.arc(x+Math.cos(k*1.257)*w*.055,y+Math.sin(k*1.257)*w*.055,w*.045,0,Math.PI*2);c.fill();}c.fillStyle=p[3];c.beginPath();c.arc(x,y,w*.026,0,Math.PI*2);c.fill();}
 c.restore();}
function paper(){const canvas=$('art-paper'),c=canvas.getContext('2d'),s=get();canvas.width=700;canvas.height=420;paint(c,700,420,s.artSubject,s.artPalette);for(const stroke of s.sketch){c.strokeStyle=stroke.color;c.lineWidth=7;c.lineCap='round';c.beginPath();stroke.points.forEach((p,i)=>i?c.lineTo(p[0]*700,p[1]*420):c.moveTo(p[0]*700,p[1]*420));c.stroke();}}
function connect(read,actions){get=read;api=actions;
 for(const mode of ['paint','read'])$(mode+'-together').onclick=()=>{get().artMode=mode;api.log(mode==='paint'?'The family brought out their colors.':'A quiet reading hour, together.');api.act(mode);api.updateUI();};
 $('tv-toggle').onclick=()=>{get().tvOn=!get().tvOn;api.updateUI();};
 for(const key of ['subject','palette'])$('art-'+key).onchange=e=>{get()[key==='subject'?'artSubject':'artPalette']=e.target.value;get().sketch=[];api.updateUI();};
 document.querySelectorAll('[data-ink]').forEach(b=>b.onclick=()=>{ink=b.dataset.ink;document.querySelectorAll('[data-ink]').forEach(a=>a.setAttribute('aria-pressed',String(a===b)));});
 const canvas=$('art-paper');canvas.style.touchAction='none';
 function point(e){const r=canvas.getBoundingClientRect();return [Math.max(0,Math.min(1,(e.clientX-r.left)/r.width)),Math.max(0,Math.min(1,(e.clientY-r.top)/r.height))];}
 canvas.onpointerdown=e=>{if(get().sketch.length>=200)return;drawing=true;canvas.setPointerCapture(e.pointerId);get().sketch.push({color:ink,points:[point(e),point(e)]});paper();};
 canvas.onpointermove=e=>{if(!drawing)return;const stroke=get().sketch.at(-1);if(stroke.points.length<500)stroke.points.push(point(e));paper();};
 const finish=()=>{if(!drawing)return;drawing=false;api.addArtwork('Alex');get().wishes.creative=true;api.updateUI();};canvas.onpointerup=finish;canvas.onpointercancel=finish;
 $('clear-art').onclick=()=>{get().sketch=[];paper();};$('download-art').onclick=()=>{const a=document.createElement('a');a.download='the-glims-alex-art.png';a.href=canvas.toDataURL('image/png');a.click();};
 $('read-page').onclick=()=>api.act('read');$('next-book').onclick=()=>{book=(book+1)%books.length;api.updateUI();};
}
function update(s,pastime){for(const id of ['papa','mama'])$(id+'-pastime').textContent=pastime(id)==='paint'?'Painting a little world':'Enjoying a good book';for(const id of ['cypher','rosy'])if(pastime(id))$(id+'-mood').textContent=pastime(id)==='paint'?'Sketching alongside the family':'Lost in a good book';
 $('art-subject').value=s.artSubject;$('art-palette').value=s.artPalette;$('book-title').textContent=books[book][0];$('book-excerpt').textContent=books[book][1];$('tv-toggle').textContent=s.tvOn?'Turn TV off':'Turn TV on';$('tv-toggle').setAttribute('aria-pressed',String(s.tvOn));$('tv-status').textContent=s.tvOn?'Now showing: The Quiet River · original animated nature scene · muted':'The television is off. A little quiet is welcome, too.';$('art-caption').textContent='Alex’s page · draw with a finger or mouse · '+s.booksRead+' pages enjoyed';
 for(const mode of ['paint','read'])$(mode+'-together').setAttribute('aria-pressed',String(s.artMode===mode));
 paper();const next=JSON.stringify([s.artworks,s.sketch]);if(next!==signature){signature=next;$('family-gallery').replaceChildren(...s.artworks.map(a=>{const f=document.createElement('figure'),c=document.createElement('canvas'),label=document.createElement('figcaption');f.className='gallery-picture';c.width=240;c.height=160;paint(c.getContext('2d'),240,160,a.subject,a.palette);if(a.author==='Alex'){const ctx=c.getContext('2d');for(const stroke of s.sketch){ctx.strokeStyle=stroke.color;ctx.lineWidth=3;ctx.beginPath();stroke.points.forEach((p,i)=>i?ctx.lineTo(p[0]*240,p[1]*160):ctx.moveTo(p[0]*240,p[1]*160));ctx.stroke();}}label.textContent=a.author+' · '+a.subject;f.append(c,label);return f;}));}$('gallery-caption').textContent=s.artworks.length?'A little wall of shared attention. Everyone keeps their own page.':'Paint together to fill the family gallery.';
}
function restore(next,saved){if(['mixed','paint','read'].includes(saved.artMode))next.artMode=saved.artMode;if(subjects.includes(saved.artSubject))next.artSubject=saved.artSubject;if(Object.hasOwn(palettes,saved.artPalette))next.artPalette=saved.artPalette;next.tvOn=saved.tvOn===true;if(Number.isFinite(saved.artistry))next.artistry=Math.max(0,Math.min(1,saved.artistry));if(Number.isSafeInteger(saved.booksRead))next.booksRead=Math.max(0,Math.min(100000,saved.booksRead));
 if(Array.isArray(saved.artworks))next.artworks=saved.artworks.slice(0,5).filter(a=>a&&['Alex','Papa','Mama','Cypher','Rosy'].includes(a.author)&&subjects.includes(a.subject)&&Object.hasOwn(palettes,a.palette)).map(a=>({author:a.author,subject:a.subject,palette:a.palette}));
 if(Array.isArray(saved.sketch))next.sketch=saved.sketch.slice(0,200).filter(a=>a&&/^#[0-9a-f]{6}$/i.test(a.color)&&Array.isArray(a.points)).map(a=>({color:a.color,points:a.points.slice(0,500).filter(p=>Array.isArray(p)&&p.length===2&&p.every(n=>Number.isFinite(n)&&n>=0&&n<=1))}));
}
return {paint,connect,update,restore};
})();
