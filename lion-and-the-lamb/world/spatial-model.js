(function(root,factory){const api=factory();if(typeof module==='object'&&module.exports)module.exports=api;else root.WorldZones=api;})(globalThis,function(){
'use strict';const colors=['#e8ce99','#baceaf','#e0e6d9','#d9dfe2'];
function classify(density,low=10,high=300){if(!Number.isFinite(low)||!Number.isFinite(high)||low<0||high<=low)throw Error('Thresholds must satisfy 0 ≤ low < high');if(density===null||!Number.isFinite(density)||density<0)return 3;return density>=high?0:density>=low?1:2;}
function bboxIntersects(a,b){return a[0]<=b[2]&&a[2]>=b[0]&&a[1]<=b[3]&&a[3]>=b[1];}
return{classify,colors,bboxIntersects};});
