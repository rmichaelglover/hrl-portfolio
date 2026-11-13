const fs=require('fs'),cp=require('child_process');
(async()=>{
const wasm=process.argv[2],native=process.argv[3];
const expected=JSON.parse(cp.execFileSync(native,{encoding:'utf8'}));
const {instance:{exports:k}}=await WebAssembly.instantiate(fs.readFileSync(wasm),{});
for(let f=0;f<32;f++){
 k.reset_motion(2,f%2);
 const bx=1+.1*(f%3),choices=[[[.6,0,2+f*.001],[0,0,0],[0,.2,-.1]],[[bx-.6,0,2],[bx,0,0],[bx,-.2,-.1]]];
 k.set_person(0,0,0,.43,1.7555555555555555,1.2828234474671283,.7);
 k.set_person(1,bx,0,.43,1.7555555555555555,1.2828234474671283,.7);
 choices.forEach((c,i)=>c.forEach(([x,z,u],j)=>k.set_choice(i,j,x,z,u,1)));
 k.set_neighbor(0,.4,.5,.4,-.5,.3);
 const feasible=!!k.decide_motion(f),e=expected[f];
 if(feasible!==e.feasible||(feasible&&[0,1].some(i=>k.selected_motion(i)!==e.chosen[i])))throw Error('Native/WASM mismatch at fixture '+f);
}
console.log('32 native C++ / WebAssembly decision fixtures agree.');
})();
