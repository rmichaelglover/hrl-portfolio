#!/usr/bin/env python3
"""Exploratory size/policy follow-up, run sequentially after experiment.py."""
from pathlib import Path
import hashlib
import json
import time
import numpy as np
from experiment import ROOT, geometry, MutualBestLabeler, FinalizationPolicy


def main():
    rows=[]
    for n in [48,64]:
        c,prior,truth=geometry(n,20261016)
        ref=None;base_seconds=None;base_work=None
        for name,policy in [('off',FinalizationPolicy(mode='off')),
                            ('audited',FinalizationPolicy()),
                            ('permanent',FinalizationPolicy(mode='permanent')),
                            ('aggressive_audited',FinalizationPolicy.aggressive()),
                            ('aggressive_permanent',FinalizationPolicy.aggressive(mode='permanent'))]:
            samples=[]
            for repeat in range(3):
                start=time.perf_counter()
                r=MutualBestLabeler(c,prior,one_to_one=True,policy=policy,
                                    prior_strength=.18,max_iterations=120,tol=1e-8).run()
                samples.append(time.perf_counter()-start)
            seconds=float(np.median(samples))
            if name=='off':ref=r;base_seconds=seconds;base_work=r.statistics['support_multiply_adds']
            row={'n':n,'seed':20261016,'mode':name,'seconds':seconds,'timing_samples':samples,
                 'speedup':base_seconds/seconds,'iterations':r.iterations,'finalized':int(r.finalized.sum()),
                 'assignment_disagreements':int(np.sum(r.assignments!=ref.assignments)),
                 'locked_disagreements':int(np.sum(r.assignments[r.finalized]!=ref.assignments[r.finalized])),
                 'correct':int(np.sum(r.assignments==truth)),'reference_correct':int(np.sum(ref.assignments==truth)),
                 'work_ratio':r.statistics['support_multiply_adds']/base_work,
                 'full_update_residual':r.full_update_residual,'stop_reason':r.stop_reason,'policy':policy.__dict__}
            rows.append(row)
            print({k:v for k,v in row.items() if k not in ['timing_samples','policy']},flush=True)
    sources=[Path(__file__),ROOT/'experiment.py',ROOT.parent/'hrl/finalization.py']
    result={'kind':'Additional exploratory size/policy probe; one seed per size; not a confirmatory benchmark.',
            'timing':'Three repeats, all cases/methods sequential; includes constructor/cache/audit costs. Input generation excluded.',
            'source_sha256':{str(p):hashlib.sha256(p.read_bytes()).hexdigest() for p in sources},'runs':rows}
    (ROOT/'data/large-pilot.json').write_text(json.dumps(result,indent=2)+'\n')
    lines=['# Larger-field exploratory probe','',
           'One seed at 48 and 64 objects, with the same input construction and update as the first pilot. The aggressive preset was added during development; this is an exploratory follow-up, not an independently registered confirmation. All timings include constructor copies, cache packing, audits, and result assembly.','',
           '| Objects | Policy | Seconds | Speedup | Work ratio | Finalized | Disagreements |',
           '| ---: | --- | ---: | ---: | ---: | ---: | ---: |']
    for r in rows:lines.append(f"| {r['n']} | {r['mode']} | {r['seconds']:.5f} | {r['speedup']:.3f}× | {r['work_ratio']:.3f} | {r['finalized']} | {r['assignment_disagreements']} |")
    lines+=['','These are two particular synthetic constellations, not a proof of general speedup or correctness. A full-update residual can remain nonzero after assignment finalization. The delayed-swap failure and recovery case remains in REPORT.md.']
    (ROOT/'LARGE-PROBE.md').write_text('\n'.join(lines)+'\n')


if __name__=='__main__':main()
