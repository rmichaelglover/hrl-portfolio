import numpy as np
import matplotlib.pyplot as plt

rng=np.random.default_rng(20261015)
N=12000
# 8 binary components in four pairs, with an interaction across pairs
X=rng.choice([-1.0,1.0],size=(N,8))
# Ground truth: local pair synergies and cross-scale interaction
pair=X[:,0::2]*X[:,1::2]
y=(0.15*X.sum(axis=1)+ 1.1*pair[:,0]+0.95*pair[:,1]+1.0*pair[:,2]+0.85*pair[:,3] + 0.9*pair[:,0]*pair[:,2] + rng.normal(0,0.3,N))
perm=rng.permutation(N)
train,test=perm[:9000],perm[9000:]

def fit_eval(F):
    A=np.column_stack([np.ones(len(train)),F[train]])
    b=np.linalg.lstsq(A,y[train],rcond=None)[0]
    pred=np.column_stack([np.ones(len(test)),F[test]])@b
    return float(np.mean((y[test]-pred)**2)),float(1-np.sum((y[test]-pred)**2)/np.sum((y[test]-np.mean(y[test]))**2))

# Additive: independent components, no relations
Fadd=X
# Coarse-graining: pair means, forfeiting within pair parity information
Fcoarse=X.reshape(N,4,2).mean(axis=2)
# GRRLE-inspired: candidate pair compatibility strengths + higher level compatibility
# Binary labels and exact pair compatibility are a transparent one-pass fixed compatibility model;
# NOT a trained iterative relaxation-labeling engine.
Frel=np.column_stack([Fcoarse,pair,pair[:,0]*pair[:,2]])
results={'Additive (raw parts)':fit_eval(Fadd),'Ordinary (pair averages)':fit_eval(Fcoarse),'Relational (pair + meta)':fit_eval(Frel)}
for k,(mse,r2) in results.items():print(f'{k}: MSE={mse:.5f}, R2={r2:.5f}')
print('noise variance',0.3**2)

fig,ax=plt.subplots(figsize=(8,4.8))
names=list(results)
vals=[results[k][1] for k in names]
ax.bar(names,vals)
ax.set_ylim(0,1.05)
ax.set_ylabel('Held-out R² (higher is better)')
ax.set_title('Predicting an interacting 8-component system (3,000 held-out cases)')
ax.tick_params(axis='x',labelrotation=15)
for i,v in enumerate(vals):ax.text(i,v+0.018,f'{v:.3f}',ha='center')
fig.tight_layout();fig.savefig('/mnt/data/meta_renormalization_results.png',dpi=170)
