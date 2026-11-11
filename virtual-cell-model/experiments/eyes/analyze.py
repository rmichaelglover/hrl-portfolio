#!/usr/bin/env python3
"""Reproduce the eye/observer scenarios; do not treat simulator provenance as percepts."""
import csv
import io
import json
from pathlib import Path
import subprocess
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]
scenarios={}
for scenario in ['light','one-eye','closed','endogenous','decline']:
    raw=subprocess.check_output([str(ROOT/'build/vision_demo'),scenario],text=True)
    (HERE/f'{scenario}.csv').write_text(raw)
    rows=list(csv.DictReader(io.StringIO('\n'.join(x for x in raw.splitlines() if not x.startswith('#')))))
    scenarios[scenario]={key:np.array([float(row[key]) for row in rows]) for key in rows[0]}
normal=scenarios['light'];decline=scenarios['decline']
for key in normal:
    if key!='integrated_feature':np.testing.assert_allclose(normal[key],decline[key],rtol=0,atol=0)
assert decline['integrated_feature'].max()==0
assert normal['integrated_feature'].max()>0
for key in ['left_photoevents','right_photoevents']:
    assert scenarios['closed'][key].max()==0
for side in ['left','right']:
    if scenarios['closed'][side+'_endogenous'].max()==0:
        assert scenarios['closed'][side+'_ganglion'].max()==0
assert scenarios['one-eye']['left_photoevents'].max()==0
assert scenarios['one-eye']['right_photoevents'].max()>0
np.testing.assert_array_equal(scenarios['one-eye']['right_photoevents'],normal['right_photoevents'])
np.testing.assert_array_equal(scenarios['one-eye']['right_ganglion'],normal['right_ganglion'])
assert scenarios['endogenous']['left_photoevents'].max()==0
assert scenarios['endogenous']['left_ganglion'].max()>0
assert normal['left_rod_mv'].min()<-40
summary={'status':'Reduced rod-like binocular detection plus classical uncertain source inference and an explicit proposed attended-integration rule',
         'physical_units':{'position':'m','power':'W','wavelength':'nm','time':'ms','voltage':'mV','conductance':'nS'},
         'composition':{'eyes':2,'retinal_cells_per_eye':3,'body_electrical_cells':16,'body_organ_components':7},
         'seed':20261111,'source':{'isotropic_power_w':1e-10,'wavelength_nm':500,'position_m':[0,0,1],'on_ms':[200,600]},
         'scenarios':{},
         'origin_inference':'Independent-Poisson likelihoods are illustrative hypotheses. Observer sees event counts, duration and supplied interoceptive count, never simulator photon/endogenous truth flags.',
         'qrf_status':'Classical physical reference frames inspired by Fields, Glazebrook and Levin (2022); no quantum-state or quantum-reference-frame dynamics simulated.',
         'will_status':'Explicit attention/integration policy; no control of immune rejection, tissue compatibility or medication tolerability.'}
for name,data in scenarios.items():
    summary['scenarios'][name]={'left_photoevents':int(data['left_photoevents'][-1]),'right_photoevents':int(data['right_photoevents'][-1]),
        'left_endogenous_events':int(data['left_endogenous'][-1]),'right_endogenous_events':int(data['right_endogenous'][-1]),
        'left_ganglion_spikes':int(data['left_ganglion'][-1]),'right_ganglion_spikes':int(data['right_ganglion'][-1]),
        'brain_spikes':int(data['brain_spikes'][-1]),'minimum_left_rod_mv':float(data['left_rod_mv'].min()),
        'final_attended_feature':float(data['integrated_feature'][-1])}
(HERE/'summary.json').write_text(json.dumps(summary,indent=2)+'\n')
plt.rcParams.update({'font.size':10,'axes.spines.top':False,'axes.spines.right':False})
fig,axes=plt.subplots(2,2,figsize=(11,8),layout='constrained')
t=normal['time_ms']
for key,label in [('left_rod_mv','Left receptor'),('right_rod_mv','Right receptor')]:axes[0,0].plot(t,normal[key],label=label)
axes[0,0].axvspan(200,600,color='#ac502e',alpha=.1)
axes[0,0].set(title='A  Light hyperpolarizes rod-like receptors',xlabel='Time (ms)',ylabel='Membrane potential (mV)');axes[0,0].legend(fontsize=8)
for name in ['light','one-eye','closed','endogenous']:
    data=scenarios[name];axes[0,1].plot(t,data['left_ganglion']+data['right_ganglion'],label=name)
axes[0,1].set(title='B  Retinal output depends on more than light',xlabel='Time (ms)',ylabel='Cumulative ganglion spikes');axes[0,1].legend(fontsize=8)
for name in ['light','endogenous','closed']:
    axes[1,0].step(t,scenarios[name]['p_external'],where='post',label=name)
axes[1,0].set(title='C  Source attribution without an origin oracle',xlabel='Time (ms)',ylabel='Illustrative probability external',ylim=(-.05,1.05));axes[1,0].legend(fontsize=8)
for name in ['light','decline']:
    axes[1,1].plot(t,scenarios[name]['integrated_feature'],label=name)
axes[1,1].set(title='D  Chosen integration changes representation',xlabel='Time (ms)',ylabel='Attended feature (dimensionless)');axes[1,1].legend(fontsize=8)
for ax in axes.flat:ax.grid(alpha=.15)
fig.suptitle('Alex: a pair of Eyes, a physical boundary, and an imperfect observer\nIllustrative optical/cellular parameters, likelihoods and integration policy',fontsize=13)
fig.savefig(HERE/'eyes-observer.png',dpi=180);fig.savefig(HERE/'eyes-observer.pdf',metadata={'CreationDate':None,'ModDate':None})
with PdfPages(HERE/'EYES_OBSERVER_REPORT.pdf',metadata={'Title':'Eyes, reference frames and attended representations','Author':'Michael Emanuel Glover; implementation and analysis with assistant','CreationDate':None,'ModDate':None}) as pdf:pdf.savefig(fig)
plt.close(fig)
print(json.dumps(summary,indent=2))
