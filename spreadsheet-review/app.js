'use strict';
const $=s=>document.querySelector(s);
let result=null,decisions=new Map(),worker=null,timer=null,run=0;
const labels={open:'Needs review',issue:'Issue to check',intentional:'Intentional',unsure:'Unsure'};
function el(tag,text,className){const n=document.createElement(tag);if(text!==undefined)n.textContent=text;if(className)n.className=className;return n;}
function message(text,error=false){$('#message').textContent=text;$('#message').className='message'+(error?' error':'');}
function stop(){if(worker)worker.terminate();worker=null;clearTimeout(timer);$('#cancel').hidden=true;$('#sample').disabled=false;$('#file').disabled=false;}
function reset(){run++;stop();document.body.classList.remove('has-result');$('#dropzone').hidden=false;result=null;decisions.clear();$('#results').hidden=true;$('#findings').replaceChildren();$('#coverage').replaceChildren();$('#file').value='';message('Your workbook is read in your browser. It is not uploaded.');}
function handleFile(file){
 if(!file)return;reset();if(!/\.xlsx$/i.test(file.name)){message('Choose an .xlsx file. Save older .xls files as .xlsx in Excel first.',true);return;}
 if(file.size>12*1024*1024){message('This pilot supports files up to 12 MB. Choose a smaller workbook or export.',true);return;}
 const token=run;message(`Reading ${file.name} locally…`);$('#sample').disabled=true;$('#file').disabled=true;$('#cancel').hidden=false;
 file.arrayBuffer().then(buffer=>{
  if(token!==run)return;
  worker=new Worker('worker.js');timer=setTimeout(()=>{if(token!==run)return;stop();message('This workbook took longer than 30 seconds. The review was stopped. Try a smaller workbook.',true);},30000);
  worker.onmessage=e=>{
   if(token!==run)return;stop();if(!e.data.ok){message(e.data.error,true);return;}
   result=e.data.result;document.body.classList.add('has-result');$('#dropzone').hidden=true;$('#results').hidden=false;$('#filename').textContent=result.filename;$('#filter').value='open';$('#search').value='';
   $('#sheet').replaceChildren(new Option('All worksheets',''));
   result.sheets.forEach(s=>$('#sheet').add(new Option(s.name+(s.hidden?' (hidden)':''),s.name)));
   $('#coverage').replaceChildren();const ul=el('ul');result.sheets.forEach(s=>ul.append(el('li',`${s.name}${s.hidden?' (hidden sheet)':''}: ${s.cells} populated cells, ${s.formulas} formulas inspected.`)));result.notes.forEach(n=>ul.append(el('li',n)));$('#coverage').append(ul);
   render();message('Review complete. Your original workbook was not changed.');$('#results-heading').tabIndex=-1;$('#results-heading').focus();
  };
  worker.onerror=()=>{if(token!==run)return;stop();message('The local workbook reader could not finish. Try a smaller, unencrypted .xlsx file.',true);};
  worker.postMessage({buffer,name:file.name},[buffer]);
 }).catch(()=>{if(token===run){stop();message('The file could not be read. Please select it again.',true);}});
}
function render(){
 if(!result)return;
 const open=result.findings.filter(f=>!decisions.has(f.id)).length;const summary=$('#summary');summary.replaceChildren();
 [[result.sheets.length,'worksheets inspected'],[result.findings.length,'findings to consider'],[open,'still to review']].forEach(([n,label])=>{const box=el('div',undefined,'stat');box.append(el('b',String(n)),el('span',label));summary.append(box);});
 const filter=$('#filter').value,sheet=$('#sheet').value,query=$('#search').value.toLowerCase();
 const items=result.findings.filter(f=>(!sheet||sheet===f.sheet)&&(!query||[f.address,f.sheet,f.title,f.reason,f.value].join(' ').toLowerCase().includes(query))&&(filter==='all'||filter==='open'&&!decisions.has(f.id)||filter==='high'&&f.priority==='high'||filter==='resolved'&&decisions.has(f.id)));
 $('#finding-count').textContent=`Showing ${items.length} of ${result.findings.length} findings. ${result.cells.toLocaleString()} populated cells and ${result.formulas.toLocaleString()} formulas inspected.`;
 const list=$('#findings');list.replaceChildren();
 if(!items.length){const box=el('div',undefined,'empty');box.append(el('h3',result.findings.length?'No findings in this view':'No flags from these checks'),el('p',result.findings.length?'Try another filter, or download the review with your decisions.':'Saved-error and formula-pattern checks found nothing to flag. Prices, business rules, charts, and calculated totals still need your normal review.'));list.append(box);}
 // Keep the review responsive on unusually repetitive workbooks; all findings remain in exports.
 for(const f of items.slice(0,200)){
  const decision=decisions.get(f.id)||'open';const card=el('article',undefined,`finding ${f.priority}${decision!=='open'?' reviewed':''}`);
  const header=el('header');header.append(el('span',`${f.sheet}!${f.address}`, 'location'),el('span',f.priority==='high'?'Saved error / reference':'Pattern to review','badge'));if(f.hidden)header.append(el('span','Hidden sheet','badge'));
  card.append(header,el('h3',f.title),el('p',f.reason),el('pre',f.value));
  if(f.evidence.length){const detail=el('details');detail.append(el('summary','Compare the four nearby formulas'));for(const peer of f.evidence)detail.append(el('pre',`${peer.address}  ${peer.value}`));card.append(detail);}
  const control=el('label',undefined,'decision');control.append(el('span','Your decision'));const select=el('select');select.setAttribute('aria-label',`Decision for ${f.sheet}!${f.address}`);for(const [v,label] of Object.entries(labels))select.add(new Option(label,v));select.value=decision;select.onchange=()=>{const selected=select.value;if(selected==='open')decisions.delete(f.id);else decisions.set(f.id,selected);render();const next=[...document.querySelectorAll('.decision select')].find(x=>x.getAttribute('aria-label')===select.getAttribute('aria-label'));(next||$('#filter')).focus();};control.append(select);card.append(control);list.append(card);
 }
 if(items.length>200)list.append(el('p','Showing the first 200 matches. Filter by worksheet or download the full review.','small'));
}
function exportData(){return {...result,findings:result.findings.map(f=>({...f,decision:decisions.get(f.id)||'open'}))};}
function download(kind){
 if(!result)return;const data=exportData();let content,type,extension;
 if(kind==='json'){content=JSON.stringify(data,null,2);type='application/json';extension='json';}
 else{content=['SPREADSHEET REVIEW — PILOT 0.1',data.filename,'Reviewed: '+data.created,'Original workbook unchanged. Formula calculations were not evaluated.',`Sheets: ${data.sheets.length} | Populated cells: ${data.cells} | Formulas: ${data.formulas}`,'',...data.findings.flatMap(f=>[`${f.sheet}!${f.address} — ${f.title}`,`Decision: ${labels[f.decision]}`,f.reason,`Saved cell: ${f.value}`,...f.evidence.map(e=>`Nearby ${e.address}: ${e.value}`),'']),'COVERAGE',...data.sheets.map(s=>`${s.name}${s.hidden?' (hidden)':''}: ${s.cells} cells; ${s.formulas} formulas`),...data.notes,'','This is a review aid. No flags does not certify correctness.'].join('\n');type='text/plain';extension='txt';}
 const url=URL.createObjectURL(new Blob([content],{type:type+';charset=utf-8'}));const a=el('a');a.href=url;a.download=data.filename.replace(/\.xlsx$/i,'')+'-review.'+extension;document.body.append(a);a.click();a.remove();setTimeout(()=>URL.revokeObjectURL(url),10000);
}
$('#file').onchange=e=>handleFile(e.target.files[0]);$('#sample').onclick=async()=>{try{const r=await fetch('sample-lighting-quote.xlsx');if(!r.ok)throw Error();handleFile(new File([await r.blob()],'Fictional lighting quote.xlsx'));}catch{message('The sample could not load. You can still choose your own .xlsx workbook.',true);}};
$('#another').onclick=()=>$('#file').click();
$('#cancel').onclick=()=>{reset();message('Review cancelled. No workbook changes were made.');};$('#clear').onclick=reset;
for(const id of ['filter','sheet','search'])$('#'+id).addEventListener(id==='search'?'input':'change',render);
$('#download').onclick=()=>download('text');$('#json').onclick=()=>download('json');
const zone=$('#dropzone');for(const type of ['dragenter','dragover'])zone.addEventListener(type,e=>{e.preventDefault();zone.classList.add('drag');});for(const type of ['dragleave','drop'])zone.addEventListener(type,e=>{e.preventDefault();zone.classList.remove('drag');});zone.addEventListener('drop',e=>handleFile(e.dataTransfer.files[0]));
