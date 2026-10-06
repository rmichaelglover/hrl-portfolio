const assert=require('node:assert/strict');const {compile,query}=require('./engine.js');
let r=compile('Every bachelor is unmarried\nEvery unmarried is not married\nManny is bachelor');assert.equal(query(r,'Manny is not married').status,'supported');assert.equal(query(r,'Manny is married').status,'opposed');assert.equal(query(r,'Papa is bachelor').status,'unresolved');assert.equal(r.steps.length,3);assert.deepEqual(r.steps[2].premises,[2]);
r=compile('Every bachelor is unmarried');assert.equal(r.steps.length,0); // Definitions do not create individuals.
r=compile('Every a is b\nEvery b is a\nManny is a');assert.equal(r.steps.length,2); // Cycles terminate.
r=compile('Manny is good\nManny is not good');assert.equal(query(r,'Manny is good').status,'both');assert.equal(query(r,'Manny is immortal').status,'unresolved'); // No explosion.
r=compile('Every a is b\nManny is not b');assert.equal(query(r,'Manny is not a').status,'unresolved'); // No unstated contraposition.
r=compile('Manny is good\nPerhaps all words have meanings');assert.equal(r.rejected.length,1);assert.equal(r.status,'incomplete');
assert.equal(query(r,'Who is Manny?').status,'unsupported');
console.log('PASS: chained derivations, provenance, open-world queries, no invented existence, cycle termination, conflicts, no explosion/contraposition, unsupported input.');
