/* Royal-capture crazyhouse on Fusion's province graph. Original engine unchanged. */
(function(root,factory){const base=typeof module==='object'&&module.exports?require('../../worlds-of-kings-fusion/engine.js'):root.WorldKings;const api=factory(base);if(typeof module==='object'&&module.exports)module.exports=api;else root.WorldKings=api;})(globalThis,function(Base){
'use strict';
let atlas;const TYPES=['P','N','B','R','Q'],DIRS=[[0,-1],[1,0],[0,1],[-1,0]],DIAGS=[[1,-1],[1,1],[-1,1],[-1,-1]];
const copy=s=>JSON.parse(JSON.stringify(s)),occ=(s,n)=>s.pieces.find(p=>p.at===n),ruined=(s,n)=>s.scorched.includes(n),allied=(s,a,b)=>a===b;
function configure(data,codes=['USA','FRA','KOR']){Base.configure(data,codes);atlas=data;}
function fresh(){return {...Base.fresh(),nuclearVersion:1,pockets:[0,1,2].map(()=>({P:0,N:0,B:0,R:0,Q:0})),scorched:[],heat:{},fires:[],disarmed:false,detente:null,ply:0,strikes:[0,0,0],captures:[0,0,0],dropCount:[0,0,0]};}
function pseudo(s,p,attack=false){
 const out=[],seen=new Set();function offer(st,path){const at=st.at;if(at===p.at||ruined(s,at))return false;const q=occ(s,at);if(q&&q.owner===p.owner)return false;if(seen.has(at))return !q;seen.add(at);out.push({to:at,path,dx:st.dx,dy:st.dy,capture:!!q});return !q;}
 if(['R','B','Q'].includes(p.type))for(const [dx0,dy0]of p.type==='R'?DIRS:p.type==='B'?DIAGS:[...DIRS,...DIAGS]){
  let at=p.at,dx=dx0,dy=dy0;const visited=new Set([at]),path=[];for(let n=0;n<Base.cells.length;n++){const st=Base.step(at,dx,dy);at=st.at;dx=st.dx;dy=st.dy;if(visited.has(at))break;visited.add(at);path.push(at);if(!offer(st,[...path]))break;}
 }
 if(p.type==='K')for(const [dx,dy]of[...DIRS,...DIAGS]){const st=Base.step(p.at,dx,dy);offer(st,[st.at]);}
 if(p.type==='N')for(const [dx,dy]of DIRS)for(const sign of[-1,1]){const a=Base.step(p.at,dx,dy),b=Base.step(a.at,a.dx,a.dy),c=Base.step(b.at,-b.dy*sign,b.dx*sign);if(a.at===p.at||b.at===a.at||c.at===b.at)continue;offer(c,[a.at,b.at,c.at]);}
 if(p.type==='P'){
  const f=Base.step(p.at,p.dx,p.dy),l=Base.step(p.at,p.dx-p.dy,p.dy+p.dx),r=Base.step(p.at,p.dx+p.dy,p.dy-p.dx);
  for(const st of[l,r]){const q=occ(s,st.at);if(q&&q.owner!==p.owner)offer({...st,dx:f.dx,dy:f.dy},[st.at]);}
  if(!occ(s,f.at))offer(f,[f.at]);
 }
 return out;
}
function legal(s,p){return !p||s.phase!=='play'||!s.players[p.owner]?.alive?[]:pseudo(s,p);}
function allLegal(s,owner){return s.pieces.filter(p=>p.owner===owner).flatMap(p=>legal(s,p).map(m=>({...m,piece:p.id})));}
function canDrop(s,type,to,owner=s.turn){return s.phase==='play'&&s.players[owner]?.alive&&TYPES.includes(type)&&s.pockets[owner][type]>0&&!!Base.cells[to]&&!occ(s,to)&&!ruined(s,to)&&(type!=='P'||!Base.cells[to].promotion);}
function hasAction(s,owner){return allLegal(s,owner).length>0||TYPES.some(t=>s.pockets[owner][t]>0&&Base.cells.some(c=>canDrop(s,t,c.id,owner)));}
function reserveTo(s,p,actor){if(p.owner!==actor)return actor;return s.players.find(v=>v.alive&&v.id!==actor)?.id??null;}
function capture(s,at,actor,fire=false){const p=occ(s,at);if(!p)return;const receiver=reserveTo(s,p,actor);s.pieces=s.pieces.filter(q=>q.id!==p.id);if(receiver!==null)s.captures[receiver]++;if(p.type!=='K'&&receiver!==null)s.pockets[receiver][p.promoted?'P':p.type]++;s.log.push(`${fire?'Fire captures':'Capture:'} ${s.players[p.owner].name} ${p.type} in ${Base.cells[at].name}${p.type==='K'?' · king held':receiver===null?'':` → ${s.players[receiver].name} reserve`}.`);}
function burn(s,at,owner){if(ruined(s,at))return;capture(s,at,owner,true);s.scorched.push(at);s.heat[at]=3;}
function frontier(seen,front){const next=new Set();for(const n of front)for(const id of atlas.regions[n].neighbors)if(!seen.has(id))next.add(id);return [...next];}
function forecast(s,origin){const seen=new Set([origin]),waves=[{wave:0,squares:ruined(s,origin)?[]:[origin]}];let front=[origin];for(let n=1;n<=3;n++){front=frontier(seen,front);front.forEach(i=>seen.add(i));waves.push({wave:n,squares:front.filter(i=>!ruined(s,i))});}return waves;}
function nextFire(s){return [...new Set(s.fires.flatMap(f=>frontier(new Set(f.seen),f.front).filter(i=>!ruined(s,i))))];}
function tick(s){
 for(const k of Object.keys(s.heat)){s.heat[k]--;if(s.heat[k]<=0)delete s.heat[k];}
 const burning=new Map();for(const f of s.fires){const seen=new Set(f.seen);f.front=frontier(seen,f.front);f.front.forEach(i=>seen.add(i));f.seen=[...seen];f.left--;for(const i of f.front)if(!burning.has(i))burning.set(i,f.owner);}
 // Older front owns an overlap; each occupied space is captured only once.
 for(const [i,owner]of burning)burn(s,i,owner);s.fires=s.fires.filter(f=>f.left>0&&f.front.length);
}
function crowns(s){for(const p of s.players)if(p.alive&&!s.pieces.some(q=>q.owner===p.id&&q.type==='K')){p.alive=false;p.score=0;s.log.push(`${p.name}'s king is held. Its remaining pieces stay on the globe as capturable, inactive pieces.`);}const alive=s.players.filter(p=>p.alive);if(alive.length<=1){s.phase='finished';s.winner=alive.map(p=>p.id);alive.forEach(p=>p.score=1);s.log.push(alive.length?`${alive[0].name} holds the remaining crown.`:'All crowns captured. Draw.');}}
function advance(s,newFire=null){tick(s);if(newFire)s.fires.push(newFire);s.ply++;s.detente=null;crowns(s);if(s.phase==='finished')return;let next=(s.turn+1)%3;while(!s.players[next].alive)next=(next+1)%3;if(next<=s.turn)s.round++;s.turn=next;}
function requirePlay(s){if(s.phase!=='play')throw Error('Start a match first.');}
function moving(s,pieceId,to){requirePlay(s);const p=s.pieces.find(q=>q.id===pieceId);if(!p||p.owner!==s.turn||!s.players[p.owner].alive)throw Error('Choose a piece belonging to the current country.');const m=legal(s,p).find(m=>m.to===to);if(!m)throw Error('That destination is unavailable.');return {p,m};}
function move(s,pieceId,to,promotion='Q'){
 if(!['Q','R','B','N'].includes(promotion))throw Error('Choose a promotion piece.');const {p,m}=moving(s,pieceId,to),from=p.at,type=p.type;capture(s,to,p.owner);
 if(p.type==='P'){if(Base.cells[from].country===p.owner&&Base.cells[to].country===null)p.departed=true;p.dx=m.dx;p.dy=m.dy;}
 p.at=to;if(p.type==='P'&&(Base.cells[to].promotion||p.departed&&Base.cells[to].country===null&&[Base.step(to,p.dx,p.dy),Base.step(to,p.dx-p.dy,p.dy+p.dx),Base.step(to,p.dx+p.dy,p.dy-p.dx)].some(st=>Base.cells[st.at].country!==null&&Base.cells[st.at].country!==p.owner))){p.type=promotion;p.promoted=true;}
 let prev=from;for(const n of m.path){s.km[p.owner]+=Base.distance(prev,n);prev=n;}s.log.push(`${s.players[p.owner].name}: ${type} ${Base.cells[from].name} → ${Base.cells[to].name}${p.type!==type?' · promotes to '+p.type:''}.`);s.pass=[];advance(s);return m;
}
function strikeTargets(s,p){return s.disarmed||p?.type!=='Q'?[]:legal(s,p).filter(m=>occ(s,m.to)?.owner!==p.owner&&occ(s,m.to));}
function strike(s,pieceId,to){const {p,m}=moving(s,pieceId,to);if(p.type!=='Q'||s.disarmed||!occ(s,to)||occ(s,to).owner===p.owner)throw Error('Only an armed queen can strike an enemy along an open queen route.');const owner=p.owner;s.log.push(`${s.players[owner].name}: queen strike on ${Base.cells[to].name}; queen stays in ${Base.cells[p.at].name}.`);burn(s,to,owner);s.strikes[owner]++;s.pass=[];advance(s,{origin:to,owner,front:[to],seen:[to],left:3});return m;}
function drop(s,type,to){requirePlay(s);if(!canDrop(s,type,to))throw Error('Choose an empty, unscorched territory and an available reserve piece. Pawns cannot drop on polar promotion spaces.');const owner=s.turn;s.pockets[owner][type]--;const p=Base.addPiece(s,owner,type,to);p.promoted=false;s.dropCount[owner]++;s.pass=[];s.log.push(`${s.players[owner].name}: reserve ${type} drops in ${Base.cells[to].name}.`);advance(s);return p;}
function pass(s){requirePlay(s);if(hasAction(s,s.turn))throw Error('Moves or reserve drops remain.');if(!s.pass.includes(s.turn))s.pass.push(s.turn);s.log.push(`${s.players[s.turn].name} has no available action and passes.`);advance(s);if(s.phase==='play'&&!s.fires.length&&s.players.filter(p=>p.alive).every(p=>s.pass.includes(p.id))){s.phase='finished';s.winner=[];s.log.push('No living country can act. Draw.');}}
function offerDetente(s){requirePlay(s);if(s.disarmed)throw Error('Détente is already in force.');s.detente={by:s.turn,votes:[s.turn]};s.log.push(`${s.players[s.turn].name} offers détente to all living countries.`);}
function vote(s,owner,yes=true){requirePlay(s);if(!s.detente||!s.players[owner]?.alive||s.detente.votes.includes(owner))throw Error('No unanswered offer for this country.');if(!yes){s.log.push(`${s.players[owner].name} declines détente.`);s.detente=null;return;}s.detente.votes.push(owner);s.log.push(`${s.players[owner].name} accepts détente.`);if(s.players.filter(p=>p.alive).every(p=>s.detente.votes.includes(p.id))){s.disarmed=true;s.fires=[];s.heat={};s.detente=null;s.log.push('All living countries agree: strikes and fire spread stop. Captures and drops continue; scorched territories remain.');}}
function valid(s){return !!(s&&s.nuclearVersion===1&&Array.isArray(s.pieces)&&s.pieces.every(p=>Number.isInteger(p.at)&&!!Base.cells[p.at]&&'KQRBNP'.includes(p.type)&&Number.isInteger(p.owner)&&p.owner>=0&&p.owner<3)&&s.players?.length===3&&s.pockets?.length===3&&s.pockets.every(p=>TYPES.every(t=>Number.isInteger(p[t])&&p[t]>=0))&&Array.isArray(s.scorched)&&s.scorched.every(i=>Number.isInteger(i)&&!!Base.cells[i])&&Array.isArray(s.fires)&&s.heat&&['play','finished'].includes(s.phase)&&Number.isInteger(s.turn)&&s.turn>=0&&s.turn<3&&new Set(s.pieces.map(p=>p.at)).size===s.pieces.length);}
return {configure,get W(){return Base.W},get H(){return Base.H},get COUNTRIES(){return Base.COUNTRIES},get cells(){return Base.cells},step:Base.step,fresh,clone:copy,allied,occupant:occ,addPiece:Base.addPiece,deploy:Base.deploy,pseudo,legal,allLegal,inCheck:()=>false,move,strike,strikeTargets,drop,canDrop,hasAction,pass,forecast,nextFire,offerDetente,vote,valid,distance:Base.distance,TYPES};
});
