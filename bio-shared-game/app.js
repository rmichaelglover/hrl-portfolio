(async()=>{
 const status=document.querySelector('#decision');
 try{
  const responses=await Promise.all(['demo/observations.csv','demo/tasks.json','demo/results.json'].map(p=>fetch(p)));
  if(responses.some(r=>!r.ok))throw Error('Replay data unavailable');
  const [csv,tasks,result]=await Promise.all([responses[0].text(),responses[1].json(),responses[2].json()]);
  const lines=csv.trim().split(/\r?\n/),keys=lines.shift().split(',');
  const observations=lines.map(l=>Object.fromEntries(l.split(',').map((v,i)=>[keys[i],v])));
  const select=document.querySelector('#trial');Object.keys(tasks).forEach(id=>{const o=document.createElement('option');o.value=id;o.textContent=id;select.append(o)});
  function render(){
   const rows=observations.filter(r=>r.trial===select.value),rates=rows.map(r=>+r.events/+r.visible_seconds),best=Math.max(...rates);
   const winners=rows.filter((r,i)=>Math.abs(rates[i]-best)<1e-9);const choice=winners.length===1&&best>0?winners[0].candidate:null;
   const tbody=document.querySelector('#rows');tbody.replaceChildren();rows.forEach((r,i)=>{const tr=document.createElement('tr');if(r.candidate===choice)tr.className='selected';[r.candidate,r.events,r.visible_seconds,rates[i].toFixed(3),tasks[select.value][r.candidate]].forEach(v=>{const td=document.createElement('td');td.textContent=v;tr.append(td)});tbody.append(tr)});
   status.textContent=choice?`Decoded choice: ${choice}. Digital cost: ${tasks[select.value][choice]}.`:'Decoder abstains: tied or absent evidence.';
  }
  select.addEventListener('change',render);render();
  const labels={decoded_cost:'Mean decoded cost',random_expected_cost:'Uniform-random expected cost',shuffled_mapping_cost:'Shuffled mapping mean cost',exact_best_cost:'Exact best-route mean cost'};
  const items=[...Object.entries(result.means).map(([k,v])=>[labels[k],v.toFixed(2)]),['Accepted-decision coverage',(100*result.coverage).toFixed(1)+'%'],['Trials scored',result.scored_count+' / '+result.decision_count]];
  items.forEach(([label,value])=>{const box=document.createElement('div');box.className='score';const strong=document.createElement('strong'),span=document.createElement('span');strong.textContent=value;span.textContent=label;box.append(strong,span);document.querySelector('#scores').append(box)});
 }catch(e){status.textContent='The replay could not load. Download the files below to run it locally.';}
})();
