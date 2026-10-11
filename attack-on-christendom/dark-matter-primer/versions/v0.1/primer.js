"use strict";
(() => {
 const slider=document.getElementById('halo-strength');
 const curve=a=>Array.from({length:150},(_,i)=>{const u=.3+3.7*i/149;const speed=Math.sqrt(1/u+a*a);return `${i?'L':'M'}${(60+u/4*550).toFixed(2)} ${(290-speed/2.4*260).toFixed(2)}`;}).join(' ');
 function update(){const a=Number(slider.value);document.getElementById('halo-value').textContent=a.toFixed(2);document.getElementById('central-curve').setAttribute('d',curve(0));document.getElementById('combined-curve').setAttribute('d',curve(a));document.getElementById('curve-output').textContent=`At r = 4r₀, central speed is 0.50v₀; combined speed is ${Math.sqrt(.25+a*a).toFixed(2)}v₀.`;}
 slider.addEventListener('input',update);update();
})();
