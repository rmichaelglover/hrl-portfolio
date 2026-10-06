(function(root){'use strict';
function words(text){return text.match(/[\p{L}\p{M}]+(?:['’\-][\p{L}\p{M}]+)*/gu)||[];}
function match(value,query,sensitive){return (sensitive?value:value.toLocaleLowerCase('en')).includes(sensitive?query:query.toLocaleLowerCase('en'));}
function wordIndex(records){const map=new Map();for(const r of records)for(const w of words(r.text)){const row=map.get(w);if(row)row.count++;else map.set(w,{word:w,count:1});}return [...map.values()].sort((a,b)=>b.count-a.count||a.word.localeCompare(b.word));}
function search(records,{query='',group='',caseSensitive=false,headwordOnly=false,offset=0,limit=24,wholeWord=false}){const rows=[];let total=0;for(const r of records){if(group&&r.group!==group)continue;const yes=!query||(headwordOnly?r.headwords.some(w=>caseSensitive?w===query:w.toLocaleLowerCase('en')===query.toLocaleLowerCase('en')):wholeWord?words(r.text).some(w=>caseSensitive?w===query:w.toLocaleLowerCase('en')===query.toLocaleLowerCase('en')):match(r.text,query,caseSensitive));if(yes){if(total>=offset&&rows.length<limit)rows.push(r);total++;}}return {rows,total};}
const api={words,wordIndex,search,match};if(typeof module!=='undefined'&&module.exports)module.exports=api;root.CorpusCore=api;
})(typeof window==='undefined'?globalThis:window);
