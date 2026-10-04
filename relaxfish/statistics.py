#!/usr/bin/env python3
"""Descriptive paired statistics for the fixed diagnostic, not a tournament claim."""
from pathlib import Path
import json,numpy as np
from scipy.stats import binomtest
R=Path(__file__).resolve().parent
p=json.loads((R/'data/results.json').read_text())['positions']
b=sum(x['models']['relaxfish']['agreement'] and not x['models']['static']['agreement'] for x in p)
c=sum(x['models']['static']['agreement'] and not x['models']['relaxfish']['agreement'] for x in p)
d=np.array([x['models']['static']['reference_gap_cp']-x['models']['relaxfish']['reference_gap_cp'] for x in p])
rng=np.random.default_rng(20261003);boot=np.array([np.mean(rng.choice(d,len(p))) for _ in range(10000)])
s={'discordant_relax_only':b,'discordant_static_only':c,'mcnemar_exact_p':binomtest(b,b+c,.5).pvalue if b+c else 1.,'paired_mean_gap_improvement_cp':float(d.mean()),'descriptive_bootstrap_95_mean_cp':np.quantile(boot,[.025,.975]).tolist(),'improved':int((d>0).sum()),'worse':int((d<0).sum()),'tied':int((d==0).sum()),'timing_ratio_medians':float(np.median([x['models']['relaxfish']['seconds'] for x in p])/np.median([x['models']['static']['seconds'] for x in p]))}
(R/'data/statistics.json').write_text(json.dumps(s,indent=2)+'\n')
print(json.dumps(s,indent=2))
