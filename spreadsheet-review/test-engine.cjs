const test=require('node:test'),assert=require('node:assert/strict'),fs=require('node:fs'),path=require('node:path');
const XLSX=require('./vendor/xlsx.full.min.js'),{auditWorkbook,signature,zipPreflight}=require('./engine.js');
const wb=()=>{const sheet={};for(let r=1;r<=10;r++)sheet['D'+r]={t:'n',f:`B${r}*C${r}`,v:12};return {SheetNames:['Quotes'],Sheets:{Quotes:sheet}};};
test('relative, absolute, strings, and sheet references stay semantically distinct',()=>{
 assert.equal(signature('B3*$C$2','D3'),signature('B4*$C$2','D4'));
 assert.notEqual(signature('B3*C3','D3'),signature('B2*C3','D3'));
 assert.notEqual(signature('IF(B3="A1",C3,0)','D3'),signature('IF(B4="A2",C4,0)','D4'));
 assert.equal(signature("'Price list'!B3*C3",'D3'),signature("'Price list'!B4*C4",'D4'));
 assert.equal(signature('SUM(Table1[Price])','D3'),null);
});
test('flags broken references but not quoted REF text',()=>{
 const b=wb();b.Sheets.Quotes.A1={f:'IF(TRUE,"#REF!",0)',t:'n'};b.Sheets.Quotes.A2={f:'#REF!*2',t:'n'};
 assert.deepEqual(auditWorkbook(b,'q.xlsx').findings.map(f=>f.address),['A2']);
});
test('detects wrong operator and hardcode with four agreeing peers',()=>{
 const b=wb();b.Sheets.Quotes.D4.f='B4+C4';b.Sheets.Quotes.D8={t:'n',v:42};
 const findings=auditWorkbook(b,'q.xlsx').findings;
 assert.ok(findings.some(f=>f.address==='D4'&&f.kind==='formula-pattern'));
 assert.ok(findings.some(f=>f.address==='D8'&&f.kind==='literal'));
});
test('does not infer across section gaps or flag negative inputs',()=>{
 const b=wb();delete b.Sheets.Quotes.D3;b.Sheets.Quotes.D4={t:'n',v:42};b.Sheets.Quotes.B4={t:'n',v:-2};
 assert.equal(auditWorkbook(b,'q.xlsx').findings.length,0);
});
test('does not rewrite input objects or certify correct arithmetic',()=>{
 const b=wb();const before=JSON.stringify(b);const out=auditWorkbook(b,'q.xlsx');assert.equal(JSON.stringify(b),before);assert.equal(out.findings.length,0);assert.ok(out.notes.some(n=>n.includes('not recalculated')));
});
test('includes hidden sheet stored errors',()=>{
 const b=wb();b.Workbook={Sheets:[{Hidden:1}]};b.Sheets.Quotes.B3={t:'e',v:7,w:'#DIV/0!'};
 const f=auditWorkbook(b,'q.xlsx').findings.find(x=>x.address==='B3');assert.ok(f.hidden);assert.equal(f.kind,'saved-error');
});
test('fictional XLSX yields four explained findings and preserves bytes',()=>{
 const p=path.join(__dirname,'sample-lighting-quote.xlsx'),bytes=fs.readFileSync(p),before=Buffer.from(bytes);
 const array=bytes.buffer.slice(bytes.byteOffset,bytes.byteOffset+bytes.byteLength);zipPreflight(array);
 const b=XLSX.read(bytes,{type:'buffer',cellFormula:true,sheetStubs:true}),out=auditWorkbook(b,'sample.xlsx');
 assert.deepEqual(out.findings.map(f=>f.address).sort(),['C18','D11','D16','D6']);assert.ok(bytes.equals(before));assert.ok(fs.readFileSync(p).equals(before));
});
test('rejects non-XLSX containers before parsing',()=>{assert.throws(()=>zipPreflight(new TextEncoder().encode('not an excel workbook file').buffer),/not a readable/);});
test('rejects expanded ZIP payloads before decompressing',()=>{
 const bytes=fs.readFileSync(path.join(__dirname,'sample-lighting-quote.xlsx'));const copy=Uint8Array.from(bytes);const view=new DataView(copy.buffer);
 let offset=-1;for(let i=0;i<copy.length-4;i++)if(view.getUint32(i,true)===0x02014b50){offset=i;break;}
 assert.ok(offset>=0);view.setUint32(offset+24,61*1024*1024,true);assert.throws(()=>zipPreflight(copy.buffer),/60 MB/);
});
test('reports structured/external coverage without treating them as errors',()=>{
 const b=wb();b.Sheets.Quotes.A1={t:'n',f:'SUM(Table1[Amount])'};b.Sheets.Quotes.A2={t:'n',f:"'[Other.xlsx]Prices'!A1"};const r=auditWorkbook(b,'q.xlsx');assert.equal(r.findings.length,0);assert.ok(r.notes.some(s=>s.includes('another workbook')));assert.ok(r.notes.some(s=>s.includes('table/array')));
});
