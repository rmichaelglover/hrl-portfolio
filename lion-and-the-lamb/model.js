(function(root,factory){const api=factory();if(typeof module==='object'&&module.exports)module.exports=api;else root.LionLamb=api;})(globalThis,function(){
'use strict';
const clip=x=>Math.max(0,Math.min(1,x));
// Illustrative dimensionless dynamics. Coefficients are hypotheses, not fitted bear data.
function simulate(options={}){
 const o={days:60,care:.8,retreat:.8,enrichment:.8,attractants:.1,exposure:.2,protected:true,bears:1,...options};
 for(const k of['care','retreat','enrichment','attractants','exposure'])if(!Number.isFinite(o[k])||o[k]<0||o[k]>1)throw Error('Inputs must lie in [0,1]');
 if(![1,2].includes(o.bears)||!Number.isInteger(o.days)||o.days<1||o.days>365)throw Error('Invalid horizon or animal count');
 let h=.35,f=.10,s=.45;const rows=[];
 for(let day=0;day<=o.days;day++){
 const crowd=(o.bears-1)*(1-o.retreat)*.15;
 const welfare=clip(.30*o.care+.25*o.retreat+.25*o.enrichment+.20*(1-s));
 // Habituation never removes the contact factor or declares a bear safe.
 const encounter=clip(o.exposure*(.35+.35*h+.30*f)*(o.protected?.12:1));
 rows.push({day,habituation:h,foodAssociation:f,stress:s,welfare,encounter});
 h=clip(h+.035*o.exposure*(1-h)-.008*(1-o.exposure)*h);
 f=clip(f+.06*o.attractants*(1-f)-.02*(1-o.attractants)*f);
 s=clip(s+.035*(.35*o.exposure+.35*(1-o.retreat)+.30*(1-o.enrichment)+crowd)*(1-s)-.045*(.5*o.care+.5*o.retreat)*s);
 }
 return {options:o,rows,domestication:'Not modeled: individual experience cannot establish inherited domestication.'};
}
return{simulate};});
