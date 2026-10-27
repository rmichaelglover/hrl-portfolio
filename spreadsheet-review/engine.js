/* Read-only checks. No formula evaluation, recalculation, or workbook mutation. */
(function(root){
'use strict';
const LIMIT=150000;
function colIndex(s){let n=0;for(const c of s)n=n*26+c.charCodeAt(0)-64;return n-1;}
function decode(a){const m=/^([A-Z]+)([1-9]\d*)$/.exec(a);return m?{r:+m[2]-1,c:colIndex(m[1])}:null;}
function withoutStrings(s){return s.replace(/"(?:[^"]|"")*"/g,'"TEXT"');}
function signature(formula,address){
 const p=decode(address);if(!p)return null;
 // Table references, array formulas, and named ranges need richer parsing.
 if(/[\[\]{}]/.test(formula))return null;
 const strings=[];
 let s=formula.replace(/"(?:[^"]|"")*"/g,m=>{strings.push(m);return `§${strings.length-1}§`;});
 // Match reference tokens, preserving quoted/unquoted sheet qualifiers and absolute anchors.
 s=s.replace(/((?:'(?:[^']|'')+'|[A-Za-z_][A-Za-z0-9_.]*)!)?(\$?)([A-Z]{1,3})(\$?)([1-9]\d*)(?![A-Za-z0-9_]|\s*\()/gi,(all,sheet,ac,col,ar,row,offset,text)=>{
  const before=text[offset-1];if(before&&/[A-Za-z0-9_.$]/.test(before))return all;
  const c=colIndex(col.toUpperCase()),r=+row-1;if(c>16383||r>1048575)return all;
  return (sheet||'').toUpperCase()+`R${ar?'$'+r:r-p.r}C${ac?'$'+c:c-p.c}`;
 });
 return s.replace(/\s+/g,'').toUpperCase().replace(/§(\d+)§/g,(_,n)=>strings[+n]);
}
function auditWorkbook(wb,filename){
 const findings=[],sheets=[],notes=[];let cells=0,formulas=0,external=0,unsupported=0;
 for(let si=0;si<wb.SheetNames.length;si++){
  const name=wb.SheetNames[si],ws=wb.Sheets[name],columns=new Map();let count=0,fs=0;
  const hidden=!!wb.Workbook?.Sheets?.[si]?.Hidden;
  for(const [address,cell] of Object.entries(ws)){
   const pos=decode(address);if(!pos||!cell||(cell.t==='z'&&!cell.f))continue;
   if(++cells>LIMIT)throw new Error('This workbook has more than 150,000 populated cells. Please review a smaller workbook or export.');count++;
   const formula=typeof cell.f==='string'?cell.f:null;
   const value=formula?'='+formula:(cell.w??String(cell.v??''));
   const add=(kind,priority,title,reason,evidence=[])=>findings.push({id:`${si}:${address}:${kind}`,sheet:name,address,kind,priority,title,reason,evidence,value:String(value).slice(0,1500),hidden});
   let broken=false;
   if(formula){formulas++;fs++;broken=/#REF!/i.test(withoutStrings(formula));
    if(broken)add('broken-reference','high','Broken formula reference','The saved formula contains #REF! outside a quoted text string. Excel cannot use that reference.');
    if(/\[[^\]]+\][^!]*!/.test(withoutStrings(formula)))external++;
   }
   if(cell.t==='e'&&!broken)add('saved-error','high','Excel saved an error here','The workbook stores an Excel error value in this cell. Check it in Excel; this review does not recalculate formulas.');
   const sig=formula?signature(formula,address):null;if(formula&&!sig)unsupported++;
   if(!columns.has(pos.c))columns.set(pos.c,[]);
   columns.get(pos.c).push({address,row:pos.r,cell,formula,sig});
  }
  // Consider immediate populated row neighbors, never infer across blank/merged section breaks.
  const merged=ws['!merges']||[];
  for(const entries of columns.values()){
   entries.sort((a,b)=>a.row-b.row);const rows=new Map(entries.map(x=>[x.row,x]));
   for(const current of entries){
    if(current.cell.t==='e'||(current.formula&&!current.sig))continue;
    if(merged.some(m=>{const p=decode(current.address);return p.r>=m.s.r&&p.r<=m.e.r&&p.c>=m.s.c&&p.c<=m.e.c;}))continue;
    const peers=[-2,-1,1,2].map(d=>rows.get(current.row+d));
    if(peers.some(x=>!x||!x.formula||!x.sig))continue;
    const expected=peers[0].sig;if(!peers.every(x=>x.sig===expected))continue;
    // Require valid reference normalization and four agreeing formulas on both sides.
    if(current.formula&&current.sig!==expected){
     if(/#REF!/i.test(withoutStrings(current.formula)))continue;
     findings.push({id:`${si}:${current.address}:formula-pattern`,sheet:name,address:current.address,kind:'formula-pattern',priority:'review',title:'Formula differs from nearby rows',reason:'The two formulas above and two below follow the same relative-reference pattern. This formula follows another pattern. It may be an intentional exception.',evidence:peers.map(x=>({address:x.address,value:'='+x.formula})),value:'='+current.formula,hidden});
    }else if(!current.formula&&current.cell.t==='n'){
     findings.push({id:`${si}:${current.address}:literal`,sheet:name,address:current.address,kind:'literal',priority:'review',title:'Number inside a formula sequence',reason:'Four surrounding rows contain the same formula pattern, but this cell contains a number. It could be an intentional fixed amount or a formula replaced by a value.',evidence:peers.map(x=>({address:x.address,value:'='+x.formula})),value:String(current.cell.v),hidden});
    }
   }
  }
  sheets.push({name,cells:count,formulas:fs,hidden});
 }
 if(external)notes.push(`${external} formula(s) reference another workbook. Linked workbooks were not opened or checked.`);
 if(unsupported)notes.push(`${unsupported} formula(s) use table/array syntax excluded from pattern comparisons; their broken-reference and saved-error checks still ran.`);
 notes.push('Formulas were not recalculated. Pivot tables, charts, macros, Power Query, connections, named-range logic, and business rules were not audited.');
 findings.sort((a,b)=>(a.priority==='high'?0:1)-(b.priority==='high'?0:1)||a.sheet.localeCompare(b.sheet)||decode(a.address).r-decode(b.address).r||decode(a.address).c-decode(b.address).c);
 return {version:'0.1.0',filename,created:new Date().toISOString(),cells,formulas,sheets,findings,notes};
}
function zipPreflight(buffer){
 const v=new DataView(buffer);let e=-1;
 for(let i=v.byteLength-22;i>=Math.max(0,v.byteLength-65557);i--){if(v.getUint32(i,true)===0x06054b50){e=i;break;}}
 if(e<0)throw new Error('This is not a readable .xlsx workbook. Old .xls files and encrypted workbooks are not supported.');
 const n=v.getUint16(e+10,true),offset=v.getUint32(e+16,true);
 if(n===65535||offset===0xffffffff||n>3000)throw new Error('This workbook uses an unsupported or oversized ZIP container.');
 let at=offset,total=0;
 for(let i=0;i<n;i++){
  if(at+46>v.byteLength||v.getUint32(at,true)!==0x02014b50)throw new Error('The Excel file container is damaged or unsupported.');
  if(v.getUint16(at+8,true)&1)throw new Error('Password-protected workbooks are not supported.');
  const size=v.getUint32(at+24,true);if(size===0xffffffff)throw new Error('ZIP64 workbooks are not supported in this pilot.');total+=size;
  if(total>60*1024*1024)throw new Error('This workbook expands beyond the pilot’s 60 MB processing limit.');
  at+=46+v.getUint16(at+28,true)+v.getUint16(at+30,true)+v.getUint16(at+32,true);
 }
}
const api={auditWorkbook,signature,zipPreflight};root.SheetReview=api;if(typeof module!=='undefined')module.exports=api;
})(typeof globalThis!=='undefined'?globalThis:this);
