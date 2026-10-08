'use strict';
let selectedSample=1;
const $=id=>document.getElementById(id);
let iteration=0,paused=matchMedia('(prefers-reduced-motion: reduce)').matches,lastTime=performance.now(),trace=null,history=[],baseline=[],stableSteps=0,settled=false;
const EPSILON=1e-6,MAX_STEPS=500;
function uniqueLabel(row){const best=Math.max(...row);return row.filter(v=>Math.abs(v-best)<1e-10).length===1?argmax(row):-1;}
function score(){let correct=0,tied=0;DIGITS.forEach((d,i)=>{if(mnistSeeds.has(i))return;const p=uniqueLabel(mnistState.S[i]);if(p<0)tied++;if(p===d.y)correct++;});return {correct,tied};}
function snapshot(delta){const {correct,tied}=score();const entropy=mnistState.S.filter((_,i)=>!mnistSeeds.has(i)).reduce((s,row)=>s-row.reduce((v,p)=>v+(p>0?p*Math.log2(p):0),0),0)/35;return {iteration,delta,correct,tied,entropy,S:mnistState.S.map(r=>r.slice())};}
function initializeRun(){iteration=0;trace=null;stableSteps=0;settled=false;history=[snapshot(null)];baseline=LabRelaxation.nearestSeed(DIGITS.map(d=>d.px),mnistSeeds,mnistState.prior);lastTime=performance.now();drawInspector();}
function advance(){
  if(settled||iteration>=MAX_STEPS)return;
  trace=step(mnistState);iteration++;stableSteps=trace.maxDelta<EPSILON?stableSteps+1:0;settled=stableSteps>=5;
  history.push(snapshot(trace.maxDelta));if(settled||iteration===MAX_STEPS)paused=true;drawInspector();
}
const select=$('digitSelect');
DIGITS.forEach((d,i)=>{const option=document.createElement('option');option.value=i;option.textContent='Sample '+(i+1);select.append(option);});
select.addEventListener('change',()=>{selectedSample=Number(select.value);drawInspector();});
mCv.addEventListener('click',event=>{const box=mCv.getBoundingClientRect(),cols=mCv.clientWidth<430?5:10,rows=40/cols;const col=Math.floor((event.clientX-box.left)/box.width*cols),row=Math.floor((event.clientY-box.top)/box.height*rows);const i=row*cols+col;if(col>=0&&col<cols&&row>=0&&row<rows){selectedSample=i;drawInspector();}});
$('mnistPause').onclick=()=>{paused=!paused;lastTime=performance.now();drawInspector();};
$('mnistStep').onclick=()=>{paused=true;advance();drawInspector();};
$('mnistReset').onclick=()=>{mnistState.S=mnistState.prior.map(r=>r.slice());initializeRun();};
$('mnistNew').onclick=()=>{mnistInit(true);initializeRun();};
$('mnistSpeed').onchange=()=>{lastTime=performance.now();};
function plot(id,series,logarithmic){
  const el=$(id),left=48,top=14,w=396,h=126,last=Math.max(1,iteration);
  const y=v=>top+h*(1-(logarithmic?(Math.log10(Math.max(v,1e-9))+9)/9:v));
  const ticks=logarithmic?[1,1e-3,1e-6,1e-9]:[1,.5,0];
  let svg=ticks.map(v=>'<path d="M'+left+' '+y(v)+'h'+w+'" stroke="#1a2340"/><text x="3" y="'+(y(v)+4)+'">'+(logarithmic?'10^'+Math.log10(v):v.toFixed(1))+'</text>').join('');
  svg+='<text x="48" y="163">0</text><text x="200" y="163">iteration</text><text x="420" y="163">'+iteration+'</text>';
  for(const {values,color} of series){const points=values.filter(p=>p[1]!==null).map(([i,v])=>(left+w*i/last).toFixed(2)+','+y(v).toFixed(2));if(points.length)svg+='<polyline fill="none" stroke="'+color+'" stroke-width="2" points="'+points.join(' ')+'"/><circle r="3" fill="'+color+'" cx="'+points.at(-1).split(',')[0]+'" cy="'+points.at(-1).split(',')[1]+'"/>';}
  el.innerHTML=svg;
}
function drawInspector(){
  mnistDraw();select.value=selectedSample;
  $('mnistPause').textContent=paused?'Resume':'Pause';$('mnistPause').setAttribute('aria-pressed',String(paused));$('mnistPause').disabled=settled||iteration>=MAX_STEPS;$('mnistStep').disabled=settled||iteration>=MAX_STEPS;
  const current=history.at(-1),status=settled?'Numerically stable':iteration>=MAX_STEPS?'Step limit reached':paused?'Paused':'Relaxing';
  $('fieldMetrics').innerHTML='<b>'+status+' · iteration '+iteration+'</b><br>Max change: '+(trace?trace.maxDelta.toExponential(3):'no update yet')+' · mean entropy: '+current.entropy.toFixed(3)+' bits<br>Unique predictions correct: '+current.correct+'/35 · tied: '+current.tied+'<br>Stable when max change &lt; 10⁻⁶ for five successive steps ('+stableSteps+'/5); limit '+MAX_STEPS+'.';
  const baselineCorrect=baseline.filter((b,i)=>!mnistSeeds.has(i)&&b.label===DIGITS[i].y).length;
  $('baselineMetrics').innerHTML='HRL <b>'+current.correct+'/35</b> · nearest seed <b>'+baselineCorrect+'/35</b><br>Nearest seed for this sample: #'+(baseline[selectedSample].seed+1)+' → '+DIGIT_CLASSES[baseline[selectedSample].label]+' · pixel distance '+baseline[selectedSample].distance.toFixed(2);
  const i=selectedSample,row=mnistState.S[i],prediction=uniqueLabel(row),seed=mnistSeeds.has(i);
  $('inspectSummary').textContent='Sample #'+(i+1)+' · dataset digit '+DIGITS[i].digit+' · '+(seed?'known seed':'unlabeled input')+' · '+(prediction<0?'tied; no unique choice':'current choice '+DIGIT_CLASSES[prediction]);
  const ctx=$('selectedDigit').getContext('2d');for(let r=0;r<8;r++)for(let c=0;c<8;c++){const v=Math.round(DIGITS[i].px[r*8+c]/16*255);ctx.fillStyle='rgb('+v+','+v+','+v+')';ctx.fillRect(c*10,r*10,10,10);}
  $('traceCaption').textContent=trace?'Update '+(iteration-1)+' → '+iteration+' · neighbors below show the same BEFORE state used in this update.':'Iteration 0 · seeded priors; no neighbor update has run yet.';
  $('strengthRows').innerHTML=DIGIT_CLASSES.map((label,j)=>{const prior=mnistState.prior[i][j],before=trace?trace.before[i][j]:row[j],after=row[j];return '<tr><th style="color:'+DCOL[j]+'">'+label+'</th><td>'+prior.toFixed(4)+'</td><td>'+before.toFixed(4)+'</td><td>'+(trace?trace.raw[i][j].toFixed(4):'—')+'</td><td>'+(trace?trace.support[i][j].toFixed(4):'—')+'</td><td>'+after.toFixed(4)+' <span class="strength" style="background:'+DCOL[j]+';width:'+Math.round(after*42)+'px"></span></td><td>'+(trace?(trace.delta[i][j]>=0?'+':'')+trace.delta[i][j].toExponential(2):'—')+'</td></tr>';}).join('');
  const winner=prediction<0?0:prediction;
  $('updateFormula').textContent='base = prior^0.6 × before^0.4\nnext = normalize(base × (1 + scaled support))'+(trace?'\nFor label '+DIGIT_CLASSES[winner]+': '+trace.base[i][winner].toFixed(6)+' × '+(1+trace.support[i][winner]).toFixed(6)+' ÷ '+trace.sums[i].toFixed(6)+' = '+row[winner].toFixed(6):'\nStep once to see the actual numeric substitution.')+(seed?'\nA one-hot prior anchors this seed: other labels keep zero strength.':'');
  $('updateFormula').style.whiteSpace='pre-wrap';
  const neighbors=mnistState.edges.filter(([a,b])=>a===i||b===i).map(([a,b])=>a===i?b:a).sort((a,b)=>a-b);
  const list=$('neighborList');list.replaceChildren();for(const n of neighbors){const item=document.createElement('li'),button=document.createElement('button');button.textContent='#'+(n+1)+(mnistSeeds.has(n)?' seed':'');button.onclick=()=>{selectedSample=n;drawInspector();select.focus();};item.append(button,document.createTextNode(' ['+(trace?trace.before[n]:mnistState.S[n]).map(v=>v.toFixed(3)).join(', ')+']'));list.append(item);}
  plot('deltaPlot',[{values:history.map(h=>[h.iteration,h.delta]),color:'#37e6ff'}],true);
  plot('strengthPlot',DIGIT_CLASSES.map((_,j)=>({values:history.map(h=>[h.iteration,h.S[i][j]]),color:DCOL[j]})),false);
  $('strengthPlot').setAttribute('aria-label','Sample '+(i+1)+' label-strength history through iteration '+iteration);
}
initializeRun();
function inspectorLoop(now){if(!paused&&now-lastTime>=Number($('mnistSpeed').value)){advance();lastTime=now;}requestAnimationFrame(inspectorLoop);}
requestAnimationFrame(inspectorLoop);
addEventListener('resize',drawInspector);
