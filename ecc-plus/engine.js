(function(root){
'use strict';
const clean=s=>s.trim().toLowerCase().replace(/[.!]$/,'').trim();
const term=s=>/^[a-z][a-z -]*$/.test(s)&&s.length<80;
function compile(text){
 const facts=[],rules=[],rejected=[];
 text.split(/\r?\n/).forEach((raw,i)=>{const s=clean(raw);if(!s)return;let m;
 if((m=s.match(/^every (.+?) is (not )?(.+)$/))&&term(m[1])&&term(m[3]))rules.push({subject:m[1],predicate:m[3],negative:!!m[2],line:i+1,source:raw.trim()});
 else if((m=s.match(/^(.+?) is (not )?(.+)$/))&&term(m[1])&&term(m[3]))facts.push({subject:m[1],predicate:m[3],negative:!!m[2],line:i+1,source:raw.trim()});
 else rejected.push({line:i+1,source:raw,reason:'Outside the supported grammar. Use “Every bachelor is unmarried” or “Manny is a bachelor” (omit the article: “Manny is bachelor”).'});
 });
 const key=f=>JSON.stringify([f.subject,f.predicate,f.negative]);const known=new Map();const steps=[];
 function add(f,reason,premises){const k=key(f);if(known.has(k))return false;const item={...f,id:steps.length+1,reason,premises};known.set(k,item);steps.push(item);return true;}
 facts.forEach(f=>add(f,'Given premise',[]));
 let changed=true;while(changed){changed=false;for(const f of [...known.values()])if(!f.negative)for(const r of rules)if(f.predicate===r.subject){changed=add({subject:f.subject,predicate:r.predicate,negative:r.negative,line:r.line,source:r.source},'Universal rule applied',[f.id])||changed;}}
 const conflicts=[];for(const f of known.values())if(!f.negative){const opposite=known.get(key({...f,negative:true}));if(opposite)conflicts.push([f.id,opposite.id]);}
 return {rules,steps,rejected,conflicts,status:rejected.length?'incomplete':conflicts.length?'conflict':'compiled'};
}
function query(result,text){const s=clean(text),m=s.match(/^(.+?) is (not )?(.+)$/);if(!m||!term(m[1])||!term(m[3]))return {status:'unsupported'};const neg=!!m[2];const matching=result.steps.filter(f=>f.subject===m[1]&&f.predicate===m[3]);const yes=matching.find(f=>f.negative===neg),no=matching.find(f=>f.negative!==neg);return {status:yes&&no?'both':yes?'supported':no?'opposed':'unresolved',yes:yes?.id,no:no?.id};}
const api={compile,query};if(typeof module!=='undefined'&&module.exports)module.exports=api;root.ECC=api;
})(typeof window==='undefined'?globalThis:window);
