const K=3, L0=24, RREP=30, NMAX=210, NMIN=16, W=620, H=620;
let nodes=new Map(), NID=0, T=0.5, gen=0, activity=0;
function rndp(){const p=[Math.random(),Math.random(),Math.random()];const s=p[0]+p[1]+p[2];return[p[0]/s,p[1]/s,p[2]/s];}
function dom(p){let m=0,mi=0;for(let l=0;l<K;l++)if(p[l]>m){m=p[l];mi=l;}return mi;}
function addNode(x,y,p){const id=NID++;nodes.set(id,{x,y,vx:0,vy:0,p:p||rndp(),age:0});return id;}
function nb(id){const n=nodes.get(id);return n.__nb||(n.__nb=new Set());}
function link(a,b){if(a===b)return;if(nodes.get(a)&&nodes.get(b)){nb(a).add(b);nb(b).add(a);}}
function removeNode(id){const n=nodes.get(id);if(!n)return;for(const j of nb(id)){const nj=nodes.get(j);nj&&nj.__nb&&nj.__nb.delete(id);}nodes.delete(id);}
function seed(){nodes=new Map();NID=0;gen=0;T=0.5;const cx=W/2,cy=H/2;
  for(let r=0;r<3;r++)for(let a=0;a<6;a++){const ang=a*Math.PI/3+r*0.4,rad=(r+1)*L0*0.9;addNode(cx+Math.cos(ang)*rad,cy+Math.sin(ang)*rad);}
  addNode(cx,cy);const arr=[...nodes.keys()];
  for(const a of arr)for(const b of arr){if(a<b){const na=nodes.get(a),nb2=nodes.get(b);if(Math.hypot(na.x-nb2.x,na.y-nb2.y)<L0*1.7)link(a,b);}}}
function relax(){const beta=1/Math.max(0.12,T);let changed=0,cnt=0;
  for(const [id,n] of nodes){const NB=nb(id);if(NB.size===0)continue;const sup=[0,0,0];
    for(const j of NB){const pj=nodes.get(j).p;sup[0]+=pj[0];sup[1]+=pj[1];sup[2]+=pj[2];}const inv=1/NB.size;sup[0]*=inv;sup[1]*=inv;sup[2]*=inv;
    const h=[sup[0]+0.35*(sup[1]+sup[2]),sup[1]+0.35*(sup[0]+sup[2]),sup[2]+0.35*(sup[0]+sup[1])];
    const d0=dom(n.p);let mx=Math.max(h[0],h[1],h[2]),z=0,np=[0,0,0];
    for(let l=0;l<K;l++){np[l]=Math.pow(n.p[l],0.2)*Math.exp(beta*(h[l]-mx));z+=np[l];}
    for(let l=0;l<K;l++)np[l]/=z;for(let l=0;l<K;l++)np[l]=Math.max(1e-4,np[l]+(Math.random()-0.5)*0.55*T);{const s=np[0]+np[1]+np[2];np[0]/=s;np[1]/=s;np[2]/=s;}n.p=np;n.age++;cnt++;if(dom(np)!==d0)changed++;}
  activity=cnt?changed/cnt:0;
  if(activity<0.03)T=Math.min(1.2,T*1.03);else if(activity>0.12)T=Math.max(0.15,T*0.97);}
function commonCount(a,b){let c=0;const nb2=nb(b);for(const x of nb(a))if(nb2.has(x))c++;return c;}
function morph(){const ids=[...nodes.keys()],N=ids.length;let cx=0,cy=0;
  for(const id of ids){const n=nodes.get(id);cx+=n.x;cy+=n.y;}cx/=N;cy/=N;
  const groomP=0.02+0.06*(N/NMAX);
  for(const id of ids){const n=nodes.get(id);if(!n)continue;const deg=nb(id).size;const undec=Math.max(...n.p)<0.45;
    if(N>NMIN&&((undec&&n.age>6&&Math.random()<groomP)||deg<=1&&Math.random()<0.3))removeNode(id);}
  const growP=0.5*(1-N/NMAX);
  if(growP>0){const seen=new Set();
    for(const a of [...nodes.keys()]){for(const b of nb(a)){if(a>=b)continue;const key=a+'-'+b;if(seen.has(key))continue;seen.add(key);
      if(commonCount(a,b)>1)continue;const na=nodes.get(a),nb2=nodes.get(b);if(dom(na.p)!==dom(nb2.p))continue;
      if(Math.random()>growP*0.25)continue;const mx=(na.x+nb2.x)/2,my=(na.y+nb2.y)/2;
      let nx=-(nb2.y-na.y),ny=(nb2.x-na.x);const nl=Math.hypot(nx,ny)||1;nx/=nl;ny/=nl;
      if((mx-cx)*nx+(my-cy)*ny<0){nx=-nx;ny=-ny;}
      const c=addNode(mx+nx*L0*0.85,my+ny*L0*0.85,na.p.slice());link(c,a);link(c,b);if(nodes.size>=NMAX)break;}if(nodes.size>=NMAX)break;}}
  const arr=[...nodes.keys()],NN=arr.length;
  if(NN>NMAX*0.72&&Math.random()<0.13){let coh=0;for(const id of arr)coh+=Math.max(...nodes.get(id).p);coh/=NN;
    if(coh>0.66){let far=-1,fd=-1;for(const id of arr){const n=nodes.get(id);const d=(n.x-cx)**2+(n.y-cy)**2;if(d>fd){fd=d;far=id;}}
      const patch=new Set([far]);let fringe=[far];
      for(let h=0;h<2;h++){const nx=[];for(const u of fringe)for(const v of nb(u))if(!patch.has(v)&&patch.size<14){patch.add(v);nx.push(v);}fringe=nx;}
      if(patch.size>=5&&patch.size<NN-6){for(const u of patch)for(const v of [...nb(u)])if(!patch.has(v)){nb(u).delete(v);nb(v).delete(u);}gen++;}}}
  if(nodes.size<NMIN){const a=[...nodes.keys()];if(a.length){const s=nodes.get(a[0]);addNode(s.x+8,s.y+6,rndp());}else seed();}}
function physics(){const ids=[...nodes.keys()];
  for(const id of ids){const n=nodes.get(id);for(const j of nb(id)){if(j<=id)continue;const m=nodes.get(j);
    let dx=m.x-n.x,dy=m.y-n.y,d=Math.hypot(dx,dy)||1e-3;const f=(d-L0)/d*0.06;dx*=f;dy*=f;n.vx+=dx;n.vy+=dy;m.vx-=dx;m.vy-=dy;}}
  for(const id of ids){const n=nodes.get(id);n.vx*=0.86;n.vy*=0.86;n.x+=n.vx;n.y+=n.vy;
    const M=14;if(n.x<M){n.x=M;n.vx*=-.4;}if(n.x>W-M){n.x=W-M;n.vx*=-.4;}if(n.y<M){n.y=M;n.vy*=-.4;}if(n.y>H-M){n.y=H-M;n.vy*=-.4;}}}
seed();
console.log("step  cells   T     activity  buds");
let bad=0, minN=999, maxN=0;
for(let s=1;s<=2500;s++){ relax(); physics(); if(s%8===0) morph();
  for(const [id,n] of nodes) if(!isFinite(n.x)||!isFinite(n.p[0])) bad++;
  minN=Math.min(minN,nodes.size); maxN=Math.max(maxN,nodes.size);
  if(s%250===0) console.log(`${String(s).padStart(4)}  ${String(nodes.size).padStart(4)}  ${T.toFixed(2)}   ${(activity*100).toFixed(0).padStart(3)}%     ${gen}`);
}
console.log(bad? `\nBAD (NaN) count: ${bad}` : `\nALIVE & STABLE: no NaNs; cells ranged ${minN}..${maxN}, final=${nodes.size}, buds=${gen}`);
