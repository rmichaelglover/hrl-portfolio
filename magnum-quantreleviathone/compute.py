from pathlib import Path
import json
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

B=Path(__file__).parent
(B/'figures').mkdir(exist_ok=True)
rows=[]
for n in range(2,21):
    a=np.zeros(2**n,dtype=np.complex128); a[0]=1
    # H on the least significant qubit, followed by controlled NOTs.
    x=a[0::2].copy(); y=a[1::2].copy()
    a[0::2]=(x+y)/np.sqrt(2); a[1::2]=(x-y)/np.sqrt(2)
    idx=np.arange(2**n)
    for target in range(1,n):
        lo=idx[((idx&1)!=0)&((idx&(1<<target))==0)]
        hi=lo^(1<<target)
        tmp=a[lo].copy(); a[lo]=a[hi]; a[hi]=tmp
    expected=np.zeros_like(a); expected[0]=expected[-1]=1/np.sqrt(2)
    error=float(np.max(np.abs(a-expected)))
    norm=float(np.vdot(a,a).real)
    assert error<1e-14 and abs(norm-1)<1e-14
    assert np.count_nonzero(a)==2
    rows.append(dict(qubits=n,dense_bytes=a.nbytes,sparse_payload_bytes=48,
                     max_amplitude_error=error,norm_squared=norm))
(B/'results.json').write_text(json.dumps(rows,indent=2))
fig,ax=plt.subplots(figsize=(8,3.3))
ax.semilogy([r['qubits'] for r in rows],[r['dense_bytes'] for r in rows],label='Dense complex128 amplitudes',color='#0072B2')
ax.semilogy([r['qubits'] for r in rows],[48]*len(rows),label='Two amplitudes + two uint64 indices',color='#D55E00')
ax.set(xlabel='Qubits',ylabel='Representation payload (bytes)',title='Same GHZ state, different classical representations')
ax.legend(); ax.grid(alpha=.2);fig.tight_layout()
fig.savefig(B/'figures/memory.pdf');fig.savefig(B/'figures/memory.png',dpi=160)
print(json.dumps(rows[-1]))
