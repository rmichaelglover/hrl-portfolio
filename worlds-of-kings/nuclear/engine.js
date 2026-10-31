(function(root,factory){const api=factory();if(typeof module==='object'&&module.exports)module.exports=api;else root.NuclearChess=api;})(typeof globalThis!=='undefined'?globalThis:this,function(){
'use strict';
const TYPES=['P','N','B','R','Q'],other=c=>c==='w'?'b':'w',xy=i=>[i%8,Math.floor(i/8)],inside=(x,y)=>x>=0&&x<8&&y>=0&&y<8,square=i=>'abcdefgh'[i%8]+(8-Math.floor(i/8)),clone=x=>JSON.parse(JSON.stringify(x));
function blank(){return {version:1,board:Array(64).fill(null),turn:'w',pockets:{w:{P:0,N:0,B:0,R:0,Q:0},b:{P:0,N:0,B:0,R:0,Q:0}},ruins:[],heat:{},waves:[],disarmed:false,offer:null,result:null,ply:0,log:[],stats:{strikes:{w:0,b:0},captures:{w:0,b:0},drops:{w:0,b:0},fireCaptures:0}};}
function piece(c,t,promoted=false){return {c,t,promoted,moved:false};}
function setup(kind='classic'){
 const s=blank();
 if(kind==='crossing'){
  for(const [sq,c,t] of [['b2','w','K'],['d4','w','Q'],['c2','w','N'],['a1','w','R'],['g7','b','K'],['f6','b','Q'],['d6','b','R'],['e6','b','B'],['h7','b','P']])s.board[fromSquare(sq)]=piece(c,t);
  s.pockets.w.N=1;s.pockets.b.P=2;
 }else{
  const row='RNBQKBNR';for(let x=0;x<8;x++){s.board[x]=piece('b',row[x]);s.board[8+x]=piece('b','P');s.board[48+x]=piece('w','P');s.board[56+x]=piece('w',row[x]);}
  if(kind==='pockets')for(const c of ['w','b']){s.pockets[c].N=2;s.pockets[c].P=3;s.pockets[c].Q=1;}
 }
 s.log.push(kind==='crossing'?'The crossing · White to move. Try Qxd6 or preview a queen strike on d6.':kind==='pockets'?'Loaded reserves · extra queens, knights, and pawns are ready to drop.':'Fresh board · capture the opposing king to win.');return s;
}
function fromSquare(v){return 'abcdefgh'.indexOf(v[0])+8*(8-Number(v[1]));}
function blocked(s,i){return s.ruins.includes(i);}
function moves(s,from){
 const p=s.board[from];if(!p||p.c!==s.turn||s.result)return [];
 const [x,y]=xy(from),out=[];
 function add(a,b){if(!inside(a,b))return false;const i=b*8+a;if(blocked(s,i))return false;const target=s.board[i];if(!target||target.c!==p.c)out.push({kind:'move',from,to:i});return !target;}
 if(p.t==='P'){
  const d=p.c==='w'?-1:1,ny=y+d;
  if(inside(x,ny)&&!s.board[ny*8+x]&&!blocked(s,ny*8+x)){out.push({kind:'move',from,to:ny*8+x});const yy=y+2*d;if(y===(p.c==='w'?6:1)&&!p.moved&&!s.board[yy*8+x]&&!blocked(s,yy*8+x))out.push({kind:'move',from,to:yy*8+x});}
  for(const dx of [-1,1])if(inside(x+dx,ny)){const i=ny*8+x+dx;if(s.board[i]&&s.board[i].c!==p.c&&!blocked(s,i))out.push({kind:'move',from,to:i});}
 }else if(p.t==='N'){for(const [dx,dy] of [[1,2],[2,1],[-1,2],[-2,1],[1,-2],[2,-1],[-1,-2],[-2,-1]])add(x+dx,y+dy);}
 else if(p.t==='K'){for(let dx=-1;dx<=1;dx++)for(let dy=-1;dy<=1;dy++)if(dx||dy)add(x+dx,y+dy);}
 else{
  const directions=p.t==='B'?[[1,1],[1,-1],[-1,1],[-1,-1]]:p.t==='R'?[[1,0],[-1,0],[0,1],[0,-1]]:[[1,0],[-1,0],[0,1],[0,-1],[1,1],[1,-1],[-1,1],[-1,-1]];
  for(const [dx,dy] of directions)for(let n=1;n<8;n++)if(!add(x+dx*n,y+dy*n))break;
 }
 return out;
}
function actions(s){
 if(s.result)return [];const out=[];
 for(let i=0;i<64;i++){out.push(...moves(s,i));const p=s.board[i];if(p&&p.c===s.turn&&p.t==='Q'&&!s.disarmed)for(const a of moves(s,i))if(s.board[a.to]&&s.board[a.to].c!==p.c)out.push({...a,kind:'strike'});}
 for(const type of TYPES)if(s.pockets[s.turn][type]>0)for(let to=0;to<64;to++)if(!s.board[to]&&!blocked(s,to)&&(type!=='P'||(to>=8&&to<56)))out.push({kind:'drop',type,to});
 return out;
}
function capture(s,i,byFire=false){
 const p=s.board[i];if(!p)return;
 s.board[i]=null;const taker=other(p.c);s.stats.captures[taker]++;
 if(byFire)s.stats.fireCaptures++;
 if(p.t!=='K')s.pockets[taker][p.promoted?'P':p.t]++;
 s.log.push((byFire?'Fire captures ':'Capture: ')+(p.c==='w'?'White ':'Black ')+p.t+' on '+square(i)+(p.t==='K'?' · crown held.':' → '+(taker==='w'?'White':'Black')+' reserve.'));
}
function ignite(s,i){if(blocked(s,i))return;capture(s,i,true);s.ruins.push(i);s.heat[i]=3;}
function ring(origin,d){const [x,y]=xy(origin),out=[];for(let a=0;a<8;a++)for(let b=0;b<8;b++)if(Math.abs(x-a)+Math.abs(y-b)===d)out.push(b*8+a);return out;}
function forecast(s,origin){return [0,1,2,3].map(d=>({wave:d,squares:ring(origin,d).filter(i=>!blocked(s,i)),pieces:ring(origin,d).filter(i=>!blocked(s,i)&&s.board[i]).map(i=>({square:i,...s.board[i]}))}));}
function nextWave(s){return [...new Set(s.waves.flatMap(w=>ring(w.origin,w.age+1).filter(i=>!blocked(s,i))))];}
function advanceFire(s){
 for(const key of Object.keys(s.heat)){s.heat[key]--;if(s.heat[key]<=0)delete s.heat[key];}
 const all=new Set();for(const w of s.waves){w.age++;for(const i of ring(w.origin,w.age))all.add(i);}
 for(const i of all)ignite(s,i);
 s.waves=s.waves.filter(w=>w.age<3);
}
function finish(s){
 const kings={w:s.board.some(p=>p&&p.c==='w'&&p.t==='K'),b:s.board.some(p=>p&&p.c==='b'&&p.t==='K')};
 if(!kings.w&&!kings.b)s.result={winner:null,reason:'Both crowns captured in the same turn. Draw.'};
 else if(!kings.w||!kings.b)s.result={winner:kings.w?'w':'b',reason:'Opposing king captured.'};
 else if(!actions(s).length)s.result={winner:null,reason:'No available moves or drops. Draw.'};
}
function apply(state,action){
 if(!action||!actions(state).some(a=>a.kind===action.kind&&a.from===action.from&&a.to===action.to&&a.type===action.type))throw Error('That action is not available.');
 const s=clone(state),actor=s.turn;let newWave=null;
 if(action.kind==='drop'){
  s.pockets[actor][action.type]--;s.board[action.to]=piece(actor,action.type);s.board[action.to].moved=true;s.stats.drops[actor]++;s.log.push((actor==='w'?'White':'Black')+' drops '+action.type+' @ '+square(action.to)+'.');
 }else if(action.kind==='strike'){
  s.log.push((actor==='w'?'White':'Black')+' queen on '+square(action.from)+' strikes '+square(action.to)+'.');
  ignite(s,action.to);newWave={origin:action.to,age:0};s.stats.strikes[actor]++;
 }else{
  const p=s.board[action.from];capture(s,action.to);s.board[action.to]=p;s.board[action.from]=null;p.moved=true;
  s.log.push((actor==='w'?'White':'Black')+' '+p.t+' '+square(action.from)+' → '+square(action.to)+'.');
  if(p.t==='P'&&(action.to<8||action.to>=56)){p.t=['Q','R','B','N'].includes(action.promotion)?action.promotion:'Q';p.promoted=true;s.log.push('Pawn promotes to '+p.t+'.');}
 }
 // Existing fronts advance simultaneously, including after a king capture.
 advanceFire(s);if(newWave)s.waves.push(newWave);
 s.offer=null;s.turn=other(actor);s.ply++;finish(s);return s;
}
function offer(state){if(state.result||state.disarmed)return state;const s=clone(state);s.offer=s.turn;s.log.push((s.turn==='w'?'White':'Black')+' offers détente.');return s;}
function accept(state){if(!state.offer||state.result||state.disarmed)throw Error('There is no active offer.');const s=clone(state);s.disarmed=true;s.waves=[];s.heat={};s.offer=null;s.log.push('Both sides accept détente. Strikes and fire spread stop. Captures and drops continue; scorched squares remain.');return s;}
function decline(state){const s=clone(state);s.offer=null;s.log.push('Détente declined. Play continues.');return s;}
function threats(s,color){const t={...s,turn:other(color),result:null},king=s.board.findIndex(p=>p&&p.c===color&&p.t==='K');return king>=0&&actions(t).some(a=>a.to===king);}
function chooseBot(s,random=Math.random){
 const available=actions(s);if(!available.length)return null;const me=s.turn,values={P:1,N:3,B:3,R:5,Q:9,K:10000};
 const immediate=available.find(a=>s.board[a.to]&&s.board[a.to].t==='K');if(immediate)return immediate;
 const impending=new Set(nextWave(s));let best=null,score=-Infinity;
 for(const a of available){
  let v=random()*.7;const target=s.board[a.to];if(target)v+=values[target.t]*2;
  if(a.kind==='drop')v+=.4+(a.type==='N'?1:0);
  if(a.from!==undefined&&impending.has(a.from))v+=values[s.board[a.from].t]*2;
  if(impending.has(a.to))v-=a.kind==='drop'?values[a.type]*2:values[s.board[a.from].t]*2;
  if(a.kind==='strike'){
   v-=3;for(const f of forecast(s,a.to).slice(1))for(const p of f.pieces)v+=(p.c===me?-1.6:.35)*values[p.t];
  }
  const [x,y]=xy(a.to);v+=(3.5-Math.abs(x-3.5)+3.5-Math.abs(y-3.5))*.08;
  if(a.kind==='move'&&s.board[a.from].t==='P')v+=.3;
  if(a.kind!=='strike'){
   const b=s.board.slice(),p=a.kind==='drop'?piece(me,a.type):b[a.from];if(a.from!==undefined)b[a.from]=null;b[a.to]=p;
   if(threats({...s,board:b},me))v-=500;
  }
  if(v>score){score=v;best=a;}
 }
 return best;
}
function valid(s){return !!(s&&s.version===1&&Array.isArray(s.board)&&s.board.length===64&&['w','b'].includes(s.turn)&&s.pockets&&['w','b'].every(c=>s.pockets[c]&&TYPES.every(t=>Number.isInteger(s.pockets[c][t])&&s.pockets[c][t]>=0))&&s.board.every(p=>p===null||(['w','b'].includes(p.c)&&'PNBRQK'.includes(p.t)))&&Array.isArray(s.ruins)&&s.ruins.every(i=>Number.isInteger(i)&&i>=0&&i<64)&&Array.isArray(s.waves)&&s.waves.every(w=>Number.isInteger(w.origin)&&w.origin>=0&&w.origin<64&&Number.isInteger(w.age)&&w.age>=0&&w.age<3)&&s.heat&&s.stats&&Array.isArray(s.log));}
return {TYPES,other,square,fromSquare,clone,blank,piece,setup,moves,actions,apply,forecast,nextWave,offer,accept,decline,threats,chooseBot,valid};
});
