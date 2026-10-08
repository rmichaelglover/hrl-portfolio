(function(root,factory){const api=factory();if(typeof module==='object'&&module.exports)module.exports=api;else root.EarthAtlas=factory();})(typeof globalThis!=='undefined'?globalThis:this,function(){
'use strict';
const directions=['N','NE','E','SE','S','SW','W','NW'];
function distance(a,b){const rad=Math.PI/180,dl=(b[1]-a[1])*rad,dn=(b[0]-a[0])*rad,h=Math.sin(dl/2)**2+Math.cos(a[1]*rad)*Math.cos(b[1]*rad)*Math.sin(dn/2)**2;return 6371*2*Math.asin(Math.sqrt(Math.min(1,h)));}
function prepare(data){data.polar=new Set(data.polar_links.map(([a,b])=>a<b?`${a}:${b}`:`${b}:${a}`));return data;}
function next(data,n,d){const to=data.regions[n]?.routes[d]?.[0];if(to===undefined)return null;const polar=data.polar.has(n<to?`${n}:${to}`:`${to}:${n}`);return{to,d:polar?(4-d+8)%8:d,polar};}
function routes(data,source,piece='R',heading=0){if(!data.regions[source])return[];const out=new Map();function add(to,path,kind='route',dir=heading){if(to!==source&&!out.has(to))out.set(to,{to,path,kind,dir});}
if(['R','B','Q'].includes(piece)){const dirs=piece==='R'?[0,2,4,6]:piece==='B'?[1,3,5,7]:[0,1,2,3,4,5,6,7];for(let d of dirs){let at=source;const visited=new Set([at]),path=[];while(true){const st=next(data,at,d);if(!st||visited.has(st.to))break;at=st.to;d=st.d;visited.add(at);path.push(at);add(at,[...path],'route',d);}}}
if(piece==='K'){for(let d=0;d<8;d++)for(const to of data.regions[source].routes[d].slice(0,d%2===0?3:1))add(to,[to],'route',d);}
if(piece==='N'){for(const d of[0,2,4,6])for(const sign of[-1,1]){const a=next(data,source,d);if(!a)continue;const b=next(data,a.to,a.d);if(!b)continue;const c=next(data,b.to,(b.d+sign*2+8)%8);if(c)add(c.to,[a.to,b.to,c.to],'jump',c.d);}}
if(piece==='P'){for(const to of data.regions[source].routes[heading].slice(0,3)){const st=next(data,source,heading);add(to,[to],'advance',st?.to===to?st.d:heading);}for(const d of[(heading+7)%8,(heading+1)%8]){const to=data.regions[source].routes[d][0];if(to!==undefined)add(to,[to],'capture direction',heading);}}
return[...out.values()];}
function journeyDistance(data,from,path){let total=0;for(const n of path){total+=distance(data.regions[from].center,data.regions[n].center);from=n;}return total;}
return{directions,prepare,next,routes,distance,journeyDistance};
});
