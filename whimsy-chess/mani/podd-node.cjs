#!/usr/bin/env node
'use strict';
const fs=require('node:fs/promises'),http=require('node:http'),{randomBytes}=require('node:crypto');
const P=require('./podd.js'),E=require('./engine.js');
const LIMIT=8*1024*1024;
async function read(file){const stat=await fs.stat(file);if(stat.size>LIMIT)throw Error('JSON input exceeds 8 MB.');return JSON.parse(await fs.readFile(file,'utf8'));}
async function dispatch(request){
 if(!request||typeof request!=='object'||Array.isArray(request)||request.jsonrpc!=='2.0'||!Object.hasOwn(request,'id')||!(request.id===null||typeof request.id==='string'||Number.isSafeInteger(request.id))||typeof request.method!=='string'||!request.params||typeof request.params!=='object'||Array.isArray(request.params))return {jsonrpc:'2.0',id:null,error:{code:-32600,message:'Expected a JSON-RPC 2.0 request with id, method and object params.'}};
 const {id,params:p}=request;try{let result;switch(request.method){
 case 'podd_create':result=await P.create(p.challenge);break;
 case 'podd_verify':result=await P.verifyFull(p.bundle);break;
 case 'podd_sample':result={indices:await P.sampleIndices(p.receipt,p.seed,p.count),seed:p.seed};break;
 case 'podd_open':result=await P.makeAudit(p.bundle,p.indices);break;
 case 'podd_verifyAudit':result=await P.verifyAudit(p.audit,p.expectedIndices);break;
 default:return {jsonrpc:'2.0',id,error:{code:-32601,message:'Unknown method.'}};
 }return {jsonrpc:'2.0',id,result};}catch(e){return {jsonrpc:'2.0',id,error:{code:-32602,message:e.message}};}
}
function server(){let busy=false;return http.createServer(async(req,res)=>{
 const send=(status,value)=>{res.writeHead(status,{'Content-Type':'application/json','Cache-Control':'no-store','X-Content-Type-Options':'nosniff'});res.end(JSON.stringify(value));};
 if(!/^127\.0\.0\.1:\d+$/.test(req.headers.host||'')||req.headers.origin){send(403,{error:'Loopback clients only; browser cross-origin requests are disabled.'});return;}
 if(req.method!=='POST'||req.url!=='/rpc'){send(404,{error:'POST /rpc'});return;}
 if(!/^application\/json(?:;|$)/i.test(req.headers['content-type']||'')){send(415,{error:'Use application/json.'});return;}
 if(busy){send(503,{error:'Verifier busy. Retry later.'});return;}
 busy=true;let size=0,parts=[];
 try{for await(const chunk of req){size+=chunk.length;if(size>LIMIT){send(413,{error:'Input exceeds 8 MB.'});return;}parts.push(chunk);}let payload;try{payload=JSON.parse(Buffer.concat(parts).toString('utf8'));}catch{send(400,{jsonrpc:'2.0',id:null,error:{code:-32700,message:'Invalid JSON.'}});return;}send(200,await dispatch(payload));}catch(e){if(!res.writableEnded)send(400,{error:e.message});}finally{busy=false;}
 });}
async function main(argv){const [cmd,...args]=argv;let result;
 switch(cmd){
 case 'example':result=E.example();break;
 case 'create':if(args.length!==1)throw Error('create CHALLENGE.json');result=await P.create(await read(args[0]));break;
 case 'verify':if(args.length!==1)throw Error('verify BUNDLE.json');result=await P.verifyFull(await read(args[0]));break;
 case 'sample':{if(args.length<1||args.length>3)throw Error('sample BUNDLE.json [COUNT] [SEED_HEX]');const b=await read(args[0]),seed=args[2]||randomBytes(32).toString('hex'),count=args[1]===undefined?Math.min(5,b.receipt.iterations):Number(args[1]);result={receiptId:b.receipt.receiptId,seed,indices:await P.sampleIndices(b.receipt,seed,count),note:'Seed must be chosen by an auditor after commitment; this tool does not authenticate publication time.'};break;}
 case 'open':{if(args.length!==2)throw Error('open BUNDLE.json SAMPLE.json');const b=await read(args[0]),s=await read(args[1]);if(s.receiptId!==b.receipt.receiptId)throw Error('Sample is for a different receipt.');const expected=await P.sampleIndices(b.receipt,s.seed,s.indices.length);if(P.canonical(expected)!==P.canonical(s.indices))throw Error('Sample indices do not match the seed.');result=await P.makeAudit(b,s.indices);break;}
 case 'audit':{if(args.length!==2)throw Error('audit AUDIT.json SAMPLE.json');const a=await read(args[0]),s=await read(args[1]);if(s.receiptId!==a.receipt.receiptId)throw Error('Sample is for a different receipt.');const expected=await P.sampleIndices(a.receipt,s.seed,s.indices.length);if(P.canonical(expected)!==P.canonical(s.indices))throw Error('Sample indices do not match the seed.');result=await P.verifyAudit(a,expected);break;}
 case 'serve':{const port=args[0]===undefined?8891:Number(args[0]);if(!Number.isInteger(port)||port<1024||port>65535||args.length>1)throw Error('serve [PORT 1024–65535]');const s=server();s.requestTimeout=15000;s.headersTimeout=10000;s.listen(port,'127.0.0.1',()=>process.stderr.write('PoDD local verifier: http://127.0.0.1:'+port+'/rpc\n'));return;}
 default:throw Error('Usage: node podd-node.cjs example | create CHALLENGE.json | verify BUNDLE.json | sample BUNDLE.json [COUNT] [SEED_HEX] | open BUNDLE.json SAMPLE.json | audit AUDIT.json SAMPLE.json | serve [PORT]');
 }
 process.stdout.write(JSON.stringify(result,null,2)+'\n');
}
if(require.main===module)main(process.argv.slice(2)).catch(e=>{process.stderr.write(e.message+'\n');process.exitCode=1;});
module.exports={dispatch,server};
