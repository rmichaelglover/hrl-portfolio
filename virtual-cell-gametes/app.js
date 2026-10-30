/* The tour renders saved Python states. Illustrated organelles are not simulated. */
(() => {
 'use strict';
 const $=id=>document.getElementById(id),scenario=$('scenario');
 let data,step=0;
 const parts={
  membrane:{icon:'◌',title:'A boundary with a job',description:'The egg’s membrane separates its inside from the outside. It helps control what crosses the boundary. The sperm and egg membranes must fuse for sperm entry.',question:'Look for the thin pink outline inside the outer coat.',target:'membrane-outline'},
  dna:{icon:'〰',title:'Instructions, still duplicated',description:'DNA carries genetic information. At this egg’s metaphase-II starting point, its chromosomes are still duplicated. Later, one maternal copy is set aside in the second polar body.',question:'Amber marks maternal DNA. Mint marks the sperm’s contribution. The symbols are not a chromosome count.',target:'maternal-dna'},
  er:{icon:'≋',title:'A calcium store',description:'The endoplasmic reticulum, or ER, is a folded membrane network inside the cell. It stores calcium that can be released as part of the egg’s activation signals.',question:'Find the lilac folds. Our next research step is to model calcium moving between the ER and cytosol.',target:'cell-er'},
  mito:{icon:'◒',title:'The energy team',description:'Mitochondria help make ATP, a molecule that powers many cell processes. Moving molecules and maintaining a living cell take energy.',question:'Find the little green ovals with folded lines. Their number and placement here are illustrative.',target:'cell-mito'},
  sperm:{icon:'↝',title:'A very different cell',description:'A sperm has a compact head containing paternal DNA, a mitochondria-rich midpiece, and a long flagellum used for movement. Our model begins after its journey, when it is ready at the egg membrane.',question:'An egg is much larger than a sperm. This diagram enlarges the sperm so you can see it.',target:'sperm-one'}
 };
 const story={
  initial:['Before','A cell on pause.','The egg is waiting at a stage called metaphase II. Its chromosomes are still duplicated. A sperm brings another set of DNA.','The egg starts with 2C inside; a sperm contributes 1C when it enters.'],
  fusion:['Fusion','Two membranes meet.','In this supplied event, one sperm fuses with the egg and brings its paternal DNA inside. The cell now contains the maternal 2C plus the paternal 1C.','The mint sperm moves across the boundary. Total accounted DNA increases because DNA entered the model.'],
  activation:['Activation','A signal to begin.','The egg is activated. Calcium signaling is part of this biological change. Here we supply activation as an event, rather than calculating its chemistry.','The green glow is an illustration of signaling, not a measured calcium wave.'],
  block_established:['Entry block','The boundary changes.','We now supply an effective block to further sperm entry. In the model, later fusion attempts are rejected. The detailed biological blocking mechanisms are not simulated.','The dashed mint ring marks this idealized entry gate.'],
  meiosis_II_completion:['Meiosis II','One share is set aside.','The egg completes meiosis II. One maternal genome’s worth of DNA goes into the second polar body, while one remains inside with the sperm’s contribution.','Nothing vanished: 1C maternal + 1C paternal inside, plus 1C in the second polar body.'],
  pronuclear_formation:['Two pronuclei','One cell. Two pronuclei.','The maternal and paternal genomes occupy two pronuclei inside the same cell. Our normal tour stops here, before DNA replication and the first division.','Two circles mark two pronuclei. They are not a pair of daughter cells.' ]
 };
 function selectPart(key){const p=parts[key];$('part-icon').textContent=p.icon;$('part-title').textContent=p.title;$('part-description').textContent=p.description;$('part-question').textContent=p.question;document.querySelectorAll('[data-part]').forEach(b=>b.setAttribute('aria-pressed',String(b.dataset.part===key)));document.querySelectorAll('.part-highlight').forEach(e=>e.classList.remove('part-highlight'));$(p.target).classList.add('part-highlight');}
 document.querySelectorAll('[data-part]').forEach(b=>b.addEventListener('click',()=>selectPart(b.dataset.part)));
 for(const [key,p]of Object.entries(parts)){const target=$(p.target);target.setAttribute('role','button');target.setAttribute('tabindex','0');target.setAttribute('aria-label',p.title);target.addEventListener('click',()=>selectPart(key));target.addEventListener('keydown',e=>{if(e.key==='Enter'||e.key===' '){e.preventDefault();selectPart(key)}});}
 function show(id,visible){$(id).classList.toggle('svg-hidden',!visible)}
 function units(id,count){$(id).replaceChildren(...Array.from({length:count},()=>document.createElement('i')));}
 function render(){
  const history=data[scenario.value].history,item=step?history[step-1]:null,state=item?item.state:data.initial;
  const event=item?item.event:'initial',copy=story[event].slice();
  if(state.status==='polyspermy'){copy[1]='What if two enter?';copy[2]='A second sperm entered before an effective block. The model flags polyspermy: two paternal contributions are now inside. This branch stops here and does not predict what develops.';copy[3]='Count the DNA: maternal 2C + paternal 2C = 4C accounted for.';}
  $('stage-number').textContent=`${String(step).padStart(2,'0')} / ${step?'A CHANGE IN THE CELL':'BEFORE THE BEGINNING'}`;$('stage-title').textContent=copy[1];$('stage-story').textContent=copy[2];$('stage-look').textContent=copy[3];$('scene-stage').textContent=copy[1];$('scene-caption').textContent=copy[2];$('scene-badge').textContent=state.status==='polyspermy'?'Two sperm entered':copy[0]==='Before'?'Ready at the membrane':copy[0];
  $('scene-title').textContent=copy[1];$('scene-description').textContent=copy[2]+' This is a simplified diagram, not to scale.';
  show('sperm-one',state.fused_sperm.length===0||!state.pronuclei);$('sperm-one').style.transform=state.fused_sperm.length?'translate(130px, 20px) rotate(-5deg)':'none';show('sperm-label',state.fused_sperm.length===0);show('sperm-two',state.fused_sperm.length>1);show('calcium-signal',state.activated);show('effective-block',state.block_established);show('polar-body',state.meiosis_complete);show('maternal-dna',!state.meiosis_complete);show('maternal-pronucleus',state.meiosis_complete);show('paternal-pronucleus',state.pronuclei);
  show('maternal-single',state.meiosis_complete&&!state.pronuclei);show('maternal-pronucleus',state.pronuclei);
  // Completion stage retains symbolic paternal material before the two-pronucleus endpoint.
  if(state.meiosis_complete&&!state.pronuclei)$('sperm-one').style.transform='translate(235px, 5px)';
  for(const [prefix,key]of [['maternal','maternal_nuclear_dna_C'],['paternal','paternal_nuclear_dna_C'],['polar','second_polar_body_dna_C']]){units(prefix+'-units',state[key]);$(prefix+'-count').textContent=state[key]+'C';}
  $('dna-total').textContent=`Total accounted: ${state.total_accounted_nuclear_dna_C}C`;
  $('step-status').textContent=`Step ${step} of ${history.length}`;$('previous').disabled=step===0;$('next').disabled=step===history.length;
  document.querySelectorAll('[data-step]').forEach(b=>b.disabled=+b.dataset.step<0?step===0:step===history.length);
  $('stage-buttons').replaceChildren(...Array.from({length:history.length+1},(_,n)=>{const b=document.createElement('button');b.type='button';const number=document.createElement('span');number.textContent=String(n).padStart(2,'0');b.append(number,document.createTextNode(n?stateLabel(history[n-1],n):'Before'));if(n===step)b.setAttribute('aria-current','step');b.onclick=()=>{step=n;render();$('stage-buttons').children[n].focus({preventScroll:true})};return b;}));
 }
 function stateLabel(item,n){return scenario.value==='polyspermy'&&n===2?'Second sperm':story[item.event][0];}
 function advance(delta){if(!data)return;step=Math.max(0,Math.min(data[scenario.value].history.length,step+delta));render();}
 $('previous').onclick=()=>advance(-1);$('next').onclick=()=>advance(1);$('reset').onclick=()=>{if(data){step=0;render()}};scenario.onchange=()=>{if(data){step=0;render()}};
 document.querySelectorAll('[data-step]').forEach(b=>b.onclick=()=>advance(+b.dataset.step));
 document.querySelectorAll('[data-quiz]').forEach(b=>b.onclick=()=>{document.querySelectorAll('[data-quiz]').forEach(other=>other.setAttribute('aria-pressed',String(other===b)));$('quiz-feedback').textContent=b.dataset.quiz==='body'?'Exactly! It is set aside in the second polar body. The DNA is still accounted for.':'Look again at the amber-striped block: the extra 1C is set aside in the second polar body. Try that answer.';});
 selectPart('membrane');
 fetch('demonstration.json').then(r=>{if(!r.ok)throw Error('Saved states unavailable');return r.json()}).then(result=>{data=result;render()}).catch(()=>{$('stage-story').textContent='The saved event sequence could not load. Refresh to try again, or download the saved sequences in the research notes.';$('scene-caption').textContent='The saved tour could not load. The cell parts and check-in still work.';scenario.disabled=true;});
})();
