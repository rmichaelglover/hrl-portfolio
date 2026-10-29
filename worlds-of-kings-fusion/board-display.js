/* Display-only world deployment and lossless screen clustering. */
(function(root){
'use strict';
const stock=['K','Q','R','R','B','B','N','N',...Array(8).fill('P')];
function initialize(data){
 const pieces=[];
 for(const country of data.countries){
  const spaces=country.spaces.filter(id=>!data.regions[id].promotion).slice().sort((a,b)=>data.regions[b].neighbors.length-data.regions[a].neighbors.length||a-b);
  // Small territories use their available spaces; no stacked or invented provinces.
  spaces.slice(0,16).forEach((at,i)=>pieces.push({id:`${country.id}:${i}`,country:country.id,type:stock[i],at}));
 }
 return pieces;
}
function cluster(pieces,project,{zoom=1,selected=null}={}){
 const groups=[],size=48;
 const ordered=pieces.slice().sort((a,b)=>(b.at===selected)-(a.at===selected)||(a.type==='K'?-1:0)-(b.type==='K'?-1:0));
 for(const piece of ordered){const point=project(piece);if(!point)continue;
  let group=groups.find(g=>g.country===piece.country&&(zoom<2.5||Math.hypot(g.x-point[0],g.y-point[1])<size));
  // Country clusters cannot overlap other countries; merge by proximity at crowded borders.
  if(!group)group=groups.find(g=>Math.hypot(g.x-point[0],g.y-point[1])<size);
  if(group)group.pieces.push(piece);else groups.push({x:point[0],y:point[1],country:piece.country,pieces:[piece]});
 }
 return groups;
}
const api={initialize,cluster};if(typeof module==='object'&&module.exports)module.exports=api;else root.KingsBoardDisplay=api;
})(globalThis);
