"""Exhaustive finite checks, with their scope stated explicitly."""
from itertools import product
from pathlib import Path
import json
P=Path(__file__).resolve().parent
# One individual, four predicates; retain exactly the definitional models.
models=[]
for adult,man,married,bachelor in product([False,True],repeat=4):
 if bachelor==(adult and man and not married):
  models.append(dict(adult=adult,man=man,married=married,bachelor=bachelor))
assert len(models)==8
assert all(not m['bachelor'] or not m['married'] for m in models)
assert any(not m['bachelor'] for m in models)
# One word and two possible meanings: three nonempty relations satisfy existence.
meaning_models=[{'meaning_a':a,'meaning_b':b} for a,b in product([False,True],repeat=2) if a or b]
assert len(meaning_models)==3
assert any(m['meaning_a'] and m['meaning_b'] for m in meaning_models)
assert any(m['meaning_a'] and not m['meaning_b'] for m in meaning_models)
# Circular biconditionals can be consistent without uniquely fixing truth.
circular=[{'p':p,'q':q} for p,q in product([False,True],repeat=2) if p==q]
assert len(circular)==2
results={'bachelor_definition':{'models':models,'bachelor_implies_unmarried':True,'existence_entailed':False},'meaning_axiom':{'models':meaning_models,'unique_meaning_entailed':False,'ambiguity_entailed':False},'circular_definition':{'models':circular,'consistent':True,'unique_interpretation':False},'scope':'Exhaustive checks for the specified finite toy domains. General claims require the proofs in Investigation.md; no claim to have formalized all English or decided arbitrary first-order theories.'}
(P/'results.json').write_text(json.dumps(results,indent=2));print('PASS: 8 definitional models, 3 meaning models, 2 circular models; countermodels verified.')
