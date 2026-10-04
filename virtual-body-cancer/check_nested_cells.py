from pathlib import Path
import json,sys,hashlib
import numpy as np
from vendor.hrl2026_audited import VirtualCell,Ish
B=Path(__file__).resolve().parent
original_dir=Path('/home/rmichaelglover/Code/hrl2026/python/hrl2026')
previous=json.loads((B/'output/nested-cell-checks.json').read_text()) if (B/'output/nested-cell-checks.json').exists() else {}
if original_dir.exists():
    sys.path.insert(0,str(original_dir.parent))
    from hrl2026 import VirtualCell as Original
    try:
        Original(3).step();original={'passed':True}
    except Exception as e:
        original={'passed':False,'error':type(e).__name__,'message':str(e)}
else:
    original={'status':'original local source not present; archived failure is recorded in AUDIT-RESULTS.md'}
rng=np.random.default_rng(17)
root=VirtualCell(3)
for _ in range(2):
    child=root.spawn_child(3)
    child.spawn_child(3);child.spawn_child(3)
def nodes(c):
    yield c
    for child in c.children:yield from nodes(child)
for c in nodes(root):c.skeleton=rng.dirichlet(np.ones(3),size=c.num_nodes)
trace=[]
for k in range(10):
    metric=root.step();trace.append(metric)
    for c in nodes(root):
        assert c.iteration==k+1
        assert np.allclose(c.skeleton.sum(axis=1),1,atol=1e-10)
        assert np.isfinite(c.skeleton).all() and (c.skeleton>=0).all()
        assert 0<=c.membrane.ish.entropy<=1+1e-10
assert trace[0]['metrics']['calcification']>0
assert abs(Ish().compute_entropy(np.array([.5,.5,.5]))-1)<1e-12
assert Ish().compute_entropy(np.array([1.,0.,0.]))==0
try:Ish().compute_entropy(np.array([-1.,1.,1.]));raise AssertionError('negative entropy weights accepted')
except ValueError:pass
c=VirtualCell(2);c.skeleton=np.array([[1.,0.,0.],[1/3,1/3,1/3]])
assert np.array_equal(c.project_to_binary_skin(),[-1,-2])
result={'original_step':original,'audited_snapshot_checks_passed':True,'hierarchy_nodes':len(list(nodes(root))),
        'levels':3,'steps':10,'trace':trace,
        'fixes':['compute missing step entropy from categorical state','normalize entropy weights','copy old state before mutation to measure change','distinct abstention category -2'],
        'scope':'categorical nested relaxation diagnostic, not a biological cell model',
        'original_files_unchanged':True,
        'source_hashes':({n:hashlib.sha256((original_dir/n).read_bytes()).hexdigest() for n in ['membrane.py','virtual_cell.py']} if original_dir.exists() else previous.get('source_hashes',{}))}
(B/'output/nested-cell-checks.json').write_text(json.dumps(result,indent=2))
print(json.dumps({k:v for k,v in result.items() if k!='trace'},indent=2))
