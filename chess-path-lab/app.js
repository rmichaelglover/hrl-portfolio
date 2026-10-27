'use strict';
(async()=>{
 const r=await fetch('results.json');if(!r.ok)throw Error('Results unavailable');const data=await r.json(),$=s=>document.querySelector(s),ctx=$('#board').getContext('2d');let timer=null;
 const names={legal:'Legal baseline',material:'Material constraints',bound:'Movement assignment bound','bound+observed-midpoint':'Bound + observed midpoint'};
 const windows=data.searches.filter(s=>s.method==='bound');for(let i=0;i<windows.length;i++)$('#window').add(new Option(`Ply ${windows[i].start_ply} → ${windows[i].end_ply} (${windows[i].plies} plies)`,i));
 $('#piece').add(new Option('No trail',''));for(const id of Object.values(data.positions[0].legal_ids).sort())$('#piece').add(new Option(id,id));
 function xy(square){const c=square.charCodeAt(0)-97,r=+square[1]-1;return [(c+.5)*80,(7-r+.5)*80];}
 function tracks(p,mode){if(mode==='geometry')return Object.entries(p.geometry_tracks).map(([id,v])=>({id,x:v[0]*2,y:v[1]*2}));if(mode==='legal')return Object.entries(p.legal_ids||{}).map(([s,id])=>({id,...{x:xy(s)[0],y:xy(s)[1]}}));return Object.entries(p.observed).flatMap(([color,squares])=>squares.map(s=>({id:color==='white'?'w':'b',x:xy(s)[0],y:xy(s)[1]})));}
 function draw(){const ply=+$('#ply').value,p=data.positions[ply],mode=$('#mode').value;ctx.clearRect(0,0,640,640);for(let row=0;row<8;row++)for(let c=0;c<8;c++){ctx.fillStyle=(row+c)%2?'#cbd9bf':'#edf2e4';ctx.fillRect(c*80,row*80,80,80);}
  const selected=$('#piece').value;if(selected&&mode!=='raw'){ctx.beginPath();let open=false;for(const old of data.positions.slice(0,ply+1)){const t=tracks(old,mode).find(t=>t.id===selected);if(!t)continue;if(!open){ctx.moveTo(t.x,t.y);open=true;}else ctx.lineTo(t.x,t.y);}ctx.strokeStyle='#a22d5d';ctx.lineWidth=4;ctx.stroke();}
  for(const t of tracks(p,mode)){ctx.beginPath();ctx.arc(t.x,t.y,22,0,Math.PI*2);ctx.fillStyle=t.id.startsWith('w')?'#2387dc':'#e7932a';ctx.fill();ctx.strokeStyle=t.id===selected?'#942052':'#172b27';ctx.lineWidth=t.id===selected?5:2;ctx.stroke();if($('#labels').checked&&mode!=='raw'){ctx.font='bold 11px system-ui';ctx.fillStyle='#0b1721';ctx.textAlign='center';ctx.fillText(t.id,t.x,t.y+4);}}
  ctx.font='12px system-ui';ctx.textAlign='left';ctx.fillStyle='#324c35';for(let i=0;i<8;i++){ctx.fillText('abcdefgh'[i],i*80+4,636);ctx.fillText(String(8-i),3,i*80+15);}
  $('#position').textContent=`Ply ${ply} / 51 · ${p.legal_hypotheses} legal observation hypothesis · ${p.fen.split(' ')[1]==='w'?'White':'Black'} to move`;
  $('#piece').disabled=mode==='raw';
 }
 function showWindow(){const w=windows[+$('#window').value];$('#searches').replaceChildren();for(const s of data.searches.filter(s=>s.start_ply===w.start_ply)){const tr=document.createElement('tr');for(const t of [names[s.method],s.nodes.toLocaleString(),s.paths===null?'Unknown (capped)':String(s.paths),s.complete?'Yes':'No']){const td=document.createElement('td');td.textContent=t;tr.append(td);}$('#searches').append(tr);}
  $('#paths').replaceChildren();for(const moves of w.examples){const li=document.createElement('li');li.textContent=moves.join('  ');if(moves.join(' ')===w.witness_uci.join(' '))li.textContent+='  ← recorded game';$('#paths').append(li);}
 }
 function stop(){clearInterval(timer);timer=null;$('#play').textContent='▶ Play';}
 function step(n){$('#ply').value=Math.min(51,Math.max(0,n));draw();}
 $('#start').onclick=()=>{stop();step(0);};$('#end').onclick=()=>{stop();step(51);};$('#prev').onclick=()=>{stop();step(+$('#ply').value-1);};$('#next').onclick=()=>{stop();step(+$('#ply').value+1);};$('#play').onclick=()=>{if(timer){stop();return;}if(+$('#ply').value===51)step(0);$('#play').textContent='❚❚ Pause';timer=setInterval(()=>{step(+$('#ply').value+1);if(+$('#ply').value===51)stop();},450);};
 for(const id of ['ply','mode','labels','piece'])$('#'+id).addEventListener('input',draw);$('#ply').addEventListener('input',stop);$('#window').onchange=showWindow;
 $('#window-start').onclick=()=>{stop();step(windows[+$('#window').value].start_ply);};$('#window-end').onclick=()=>{stop();step(windows[+$('#window').value].end_ply);};
 document.addEventListener('keydown',e=>{if(['INPUT','SELECT','BUTTON','TEXTAREA'].includes(document.activeElement.tagName))return;const keys={ArrowLeft:()=>step(+$('#ply').value-1),ArrowRight:()=>step(+$('#ply').value+1),Home:()=>step(0),End:()=>step(51)};if(keys[e.key]){e.preventDefault();stop();keys[e.key]();}});draw();showWindow();
})().catch(e=>{const p=document.createElement('p');p.textContent='The recorded data could not load. Open the report or results JSON below.';document.querySelector('header').append(p);console.error(e);});
