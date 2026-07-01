// Headless verification of the clog sim physics: does a throughput threshold emerge as drive falls?
const N=360, RAD=4.2, R0=10.5, FW=580, FH=340, CY=FH/2;
const GAP=20, WALL=FH*0.46, WW=70;
const px=new Float64Array(N),py=new Float64Array(N),vx=new Float64Array(N),vy=new Float64Array(N);
function halfw(x){ const c=(x-FW/2)/WW; return GAP+(WALL-GAP)*(1-Math.exp(-c*c)); }
function seed(){ for(let i=0;i<N;i++){ px[i]=Math.random()*FW; py[i]=CY+(Math.random()*2-1)*halfw(px[i])*0.9; vx[i]=0.5; vy[i]=0; } }
let drive=0;
function step(){
  const cs=R0, nx=Math.ceil(FW/cs), ny=Math.ceil(FH/cs), cells=new Array(nx*ny);
  for(let i=0;i<N;i++){ const cx=Math.min(nx-1,px[i]/cs|0), cy=Math.min(ny-1,py[i]/cs|0), id=cy*nx+cx; (cells[id]||(cells[id]=[])).push(i); }
  for(let i=0;i<N;i++){ const cx=Math.min(nx-1,px[i]/cs|0), cy=Math.min(ny-1,py[i]/cs|0);
    for(let a=-1;a<=1;a++)for(let b=-1;b<=1;b++){ const ccx=cx+a,ccy=cy+b; if(ccx<0||ccy<0||ccx>=nx||ccy>=ny)continue;
      const lst=cells[ccy*nx+ccx]; if(!lst)continue;
      for(const j of lst){ if(j<=i)continue; let dxp=px[i]-px[j],dyp=py[i]-py[j]; const d2=dxp*dxp+dyp*dyp;
        if(d2<R0*R0&&d2>1e-4){ const d=Math.sqrt(d2),f=(R0-d)/d*0.18; dxp*=f;dyp*=f; vx[i]+=dxp;vy[i]+=dyp;vx[j]-=dxp;vy[j]-=dyp; } } } }
  let cross=0;
  for(let i=0;i<N;i++){ vx[i]+=drive; vx[i]*=0.90; vy[i]*=0.90; const ox=px[i]; px[i]+=vx[i]; py[i]+=vy[i];
    const h=halfw(px[i]); if(py[i]>CY+h){py[i]=CY+h;vy[i]*=-0.3;} if(py[i]<CY-h){py[i]=CY-h;vy[i]*=-0.3;}
    if(ox<FW/2 && px[i]>=FW/2) cross++;
    if(px[i]>=FW){ px[i]-=FW; py[i]=CY+(Math.random()*2-1)*WALL*0.85; vx[i]=drive*8; } if(px[i]<0) px[i]+=FW; }
  return cross;
}
seed();
console.log("driveG   throughput   meanSpeed");
const rows=[];
for(let g=60; g>=4; g-=4){
  drive=g/150;
  for(let w=0;w<120;w++) step();            // settle
  let th=0, ms=0, T=160;
  for(let w=0;w<T;w++){ th+=step(); let s=0; for(let i=0;i<N;i++) s+=Math.hypot(vx[i],vy[i]); ms+=s/N; }
  th/=T; ms/=T; rows.push([g,th,ms]);
  console.log(`${String(g).padStart(3)}     ${th.toFixed(3).padStart(7)}    ${ms.toFixed(3)}`);
}
const maxTh=Math.max(...rows.map(r=>r[1]));
let gcrit=null; for(const r of rows){ if(r[1]<0.45*maxTh){ gcrit=r[0]; break; } }
console.log(`\nmax throughput=${maxTh.toFixed(3)}; emergent threshold g_crit (throughput<45% of max) at driveG ~= ${gcrit}`);
