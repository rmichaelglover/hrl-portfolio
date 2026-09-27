/* Fresnel power reflectances for a smooth, lossless, nonmagnetic interface.
 * Angles in degrees, measured from the surface normal. No fitted data. */
(function(root){
function fresnel(n1,n2,degrees){
 if(![n1,n2,degrees].every(Number.isFinite)||n1<=0||n2<=0||degrees<0||degrees>=90)throw Error('Positive indices and angle in [0,90) required');
 const theta=degrees*Math.PI/180,c=Math.cos(theta),st=n1/n2*Math.sin(theta);
 if(n1===n2)return {rs:0,rp:0,r:0,t:1,angle:degrees,tir:false};
 if(st>=1)return {rs:1,rp:1,r:1,t:0,angle:null,tir:true};
 const ct=Math.sqrt(1-st*st);
 const rs=((n1*c-n2*ct)/(n1*c+n2*ct))**2;
 const rp=((n2*c-n1*ct)/(n2*c+n1*ct))**2;
 return {rs,rp,r:(rs+rp)/2,t:1-(rs+rp)/2,angle:Math.asin(st)*180/Math.PI,tir:false};
}
function absorbing(n,k){if(![n,k].every(Number.isFinite)||n<=0||k<0)throw Error('n>0 and k>=0 required');return ((n-1)**2+k*k)/((n+1)**2+k*k);}
root.Optics={fresnel,absorbing};if(typeof module!=='undefined')module.exports=root.Optics;
})(globalThis);
