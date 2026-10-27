'use strict';
(async()=>{
 const response=await fetch('results.json');if(!response.ok)throw new Error('Results unavailable');
 const data=await response.json();const select=document.querySelector('#scenario');
 const names={original:'Original toy example',horizontal:'Horizontal ellipse','near-wrap':'Rotation near 180°',noisier:'Double sensor noise','more-clutter':'300 clutter points',stress:'500 clutter points + double noise'};
 const methods={original_grid:['Original grid','#f0996b'],all_points:['All-points fit','#7f92aa'],ransac:['RANSAC','#bd9bec'],refined:['Refined','#79e2cf']};
 for(const e of data.examples){const option=document.createElement('option');option.value=e.name;option.textContent=names[e.name];select.append(option);}
 function render(){
  const e=data.examples.find(x=>x.name===select.value);let svg='<rect x="50" y="20" width="550" height="550" fill="#101e30" stroke="#52677f"/>';
  const X=x=>50+x*5.5,Y=y=>570-y*5.5;
  for(let n=0;n<=100;n+=20){svg+=`<path d="M${X(n)},20 V570 M50,${Y(n)} H600" stroke="#24374e"/><text x="${X(n)}" y="594" fill="#aabcce" text-anchor="middle">${n}</text><text x="38" y="${Y(n)+5}" fill="#aabcce" text-anchor="end">${n}</text>`;}
  svg+='<defs><clipPath id="bounds"><rect x="50" y="20" width="550" height="550"/></clipPath></defs><g clip-path="url(#bounds)">';
  e.points.forEach((p,i)=>{svg+=`<circle cx="${X(p[0])}" cy="${Y(p[1])}" r="${i<70?2.8:2}" fill="${i<70&&document.querySelector('#target').checked?'#55aaff':'#8c9bad'}" opacity=".7"/>`;});
  function path(p,color,dash=''){const[x,y,a,b,t]=p;let d='';for(let i=0;i<=240;i++){const u=i*Math.PI/120;const px=x+a*Math.cos(u)*Math.cos(t)-b*Math.sin(u)*Math.sin(t),py=y+a*Math.cos(u)*Math.sin(t)+b*Math.sin(u)*Math.cos(t);d+=`${i?'L':'M'}${X(px)},${Y(py)} `;}return `<path d="${d}" fill="none" stroke="${color}" stroke-width="2.6" stroke-dasharray="${dash}"/>`;}
  for(const method of ['original_grid','ransac','refined'])svg+=path(e.fits[method],methods[method][1],method==='original_grid'?'8 5':'');
  svg+=path(e.truth,'#f6f5ec','3 5')+'</g>';document.querySelector('#plot').innerHTML=svg;
  document.querySelector('#scene-note').textContent=`70 target samples · ${e.clutter} clutter points · noise σ ${e.sigma} · rotation ${(e.truth[4]*180/Math.PI).toFixed(0)}°. Blue point labels are never supplied to the fitters.`;
  document.querySelector('#metrics').innerHTML=data.results.filter(r=>r.scenario===e.name&&r.seed===42).map(r=>`<tr><td>${methods[r.method][0]}</td><td>${r.boundary_rmse.toFixed(3)}</td><td>${r.center_error.toFixed(3)}</td><td>${r.angle_error_deg.toFixed(2)}°</td><td>${(100*r.precision).toFixed(1)}% / ${(100*r.recall).toFixed(1)}%</td></tr>`).join('');
 }
 select.addEventListener('change',render);document.querySelector('#target').addEventListener('change',render);render();
})().catch(err=>{document.querySelector('#scene-note').textContent='Could not load results. Open the comparison figure or full report below.';console.error(err);});
