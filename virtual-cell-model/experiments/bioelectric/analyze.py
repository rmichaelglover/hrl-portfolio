#!/usr/bin/env python3
"""Reproduce physical-reference and synthetic body-circuit results."""
import csv
import hashlib
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
BIN=ROOT/'build/bioelectric_demo'
def run(name,*args):
    raw=subprocess.check_output([str(BIN),*args],text=True)
    (HERE/name).write_text(raw)
    rows=list(csv.DictReader(io.StringIO('\n'.join(line for line in raw.splitlines() if not line.startswith('#')))))
    for row in rows:
        for key in row:
            if key!='region':row[key]=float(row[key])
    return rows

def column(rows,key):return np.array([r[key] for r in rows])

normal=run('trajectories.csv')
spikes=run('spikes.csv','--spikes')
fine=run('fine-trajectories.csv','--fine')
fine_spikes=run('fine-spikes.csv','--fine','--spikes')
disconnected=run('disconnected-trajectories.csv','--disconnected')
high_leak=run('high-leak-trajectories.csv','--high-leak')
rc=run('rc-reference.csv','--rc')
reference=-45-20*np.exp(-column(rc,'time_ms')/20)
rc_error=float(np.max(np.abs(column(rc,'voltage_mv')-reference)))
assert rc_error<1e-10
assert disconnected[-1]['skin_spikes']>0 and disconnected[-1]['sensory_spikes']==0 and disconnected[-1]['motor_spikes']==0
assert high_leak[-1]['skin_spikes']>0 and high_leak[-1]['sensory_spikes']==0
for key in ['heart_mv','lungs_mv','skin_mv','mouth_mv']:
    np.testing.assert_allclose(column(disconnected,key),-65,atol=1e-12)

summary={'model':'Physical RC membrane, reduced integrate-and-fire events, delayed conductance routing; synthetic parameters and topology',
         'composition':{'owner':'HomoSapiens -> Body','brain_cells':2,'heart_cells':2,'lungs_cells':2,'skin_cells':2,'mouth_cells':2,'chemical_connections':6},
         'raii':'Rule of Zero; owned optional Brain, Organ/Tissue/Cell values, vectors and body-local CellId routes; no owning pointers in this layer',
         'baseline_step_ms':.05,'refined_step_ms':.01,'stimulus':{'inward_current_pa':350,'start_ms':20,'end_ms':80},
         'rc_reference_max_abs_error_mv':rc_error,'scenarios':{},
         'refinement':{},'scope':'Organ-labelled voltage compartments, not organ mechanics, gas exchange, a clinical brain or a human anatomical connectome. Microscopic IMPase rates do not set membrane properties.'}
for name,rows in [('connected',normal),('disconnected',disconnected),('higher_brain_leak',high_leak),('refined',fine)]:
    summary['scenarios'][name]={'spikes':{key:int(rows[-1][key]) for key in ['skin_spikes','sensory_spikes','motor_spikes']},
        'peak_depolarization_mv':{key:float(np.max(column(rows,key))+65) for key in ['heart_mv','lungs_mv','skin_mv','mouth_mv']}}
for key in ['heart_mv','lungs_mv','skin_mv','mouth_mv']:
    summary['refinement'][key+'_max_difference']=float(np.max(np.abs(column(normal,key)-column(fine,key))))
for label,selector in [('skin_sensor',lambda r:r['region']=='peripheral'),('sensory_brain',lambda r:r['region']=='brain' and r['cell_index']==0),('motor_brain',lambda r:r['region']=='brain' and r['cell_index']==1)]:
    initial=next(r['time_ms'] for r in spikes if selector(r))
    refined=next(r['time_ms'] for r in fine_spikes if selector(r))
    summary['refinement'][label+'_first_spike_ms']={'baseline':initial,'refined':refined,'absolute_difference':abs(initial-refined)}
assert all(summary['refinement'][key+'_max_difference']<.6 for key in ['heart_mv','lungs_mv','skin_mv','mouth_mv'])
assert summary['scenarios']['connected']['spikes']==summary['scenarios']['refined']['spikes']
(HERE/'summary.json').write_text(json.dumps(summary,indent=2)+'\n')

plt.rcParams.update({'font.size':10,'axes.spines.top':False,'axes.spines.right':False})
fig,axes=plt.subplots(2,2,figsize=(11,8),layout='constrained')
t=column(normal,'time_ms')
for key,label in [('skin_sensor_mv','Skin sensory compartment'),('sensory_brain_mv','Brain sensory relay'),('motor_brain_mv','Brain output relay')]:
    axes[0,0].plot(t,column(normal,key),label=label)
axes[0,0].axvspan(20,80,alpha=.08,color='green');axes[0,0].set(title='A  Membrane potentials (1 ms samples)',xlabel='Time (ms)',ylabel='Membrane potential (mV)');axes[0,0].legend(fontsize=7)
for index,(label,selector) in enumerate([('Skin sensory',lambda r:r['region']=='peripheral'),('Brain sensory',lambda r:r['region']=='brain' and r['cell_index']==0),('Brain output',lambda r:r['region']=='brain' and r['cell_index']==1)]):
    times=[r['time_ms'] for r in spikes if selector(r)]
    axes[0,1].scatter(times,[index]*len(times),marker='|',s=160)
axes[0,1].set(yticks=[0,1,2],yticklabels=['Skin sensory','Brain sensory','Brain output'],xlabel='Time (ms)',title='B  Recorded threshold events',ylim=(-.5,2.5))
for key,label in [('heart_mv','Heart'),('lungs_mv','Lungs'),('skin_mv','Skin'),('mouth_mv','Mouth')]:
    axes[1,0].plot(t,column(normal,key)+65,label=label)
axes[1,0].set(title='C  Organ-labelled passive targets',xlabel='Time (ms)',ylabel='Depolarization from baseline (mV)');axes[1,0].legend(fontsize=8)
for rows,label,style in [(normal,'Connected, 0.05 ms','-'),(fine,'Connected, 0.01 ms','--'),(disconnected,'No connections',':'),(high_leak,'Higher brain leak','-.')]:
    axes[1,1].plot(t,column(rows,'mouth_mv')+65,style,label=label)
axes[1,1].set(title='D  Circuit controls and time refinement',xlabel='Time (ms)',ylabel='Mouth target depolarization (mV)');axes[1,1].legend(fontsize=8)
for ax in axes.flat:ax.grid(alpha=.12)
fig.suptitle('A value-owned bioelectric Body\nPhysical membrane law; illustrative cells, routing and parameters',fontsize=14)
fig.savefig(HERE/'body-circuit.png',dpi=180);fig.savefig(HERE/'body-circuit.pdf',metadata={'CreationDate':None,'ModDate':None})

physical,ax=plt.subplots(1,2,figsize=(11,4.5),layout='constrained')
ax[0].plot(column(rc,'time_ms'),reference,label='Analytical RC response')
ax[0].scatter(column(rc,'time_ms')[::5],column(rc,'voltage_mv')[::5],marker='x',label='C++ membrane')
ax[0].set(title='A  RC step response',xlabel='Time (ms)',ylabel='Voltage (mV)');ax[0].legend()
ratios=np.geomspace(.01,100,200)
for z in [1,-1,2]:ax[1].semilogx(ratios,1000*8.31446261815324*310.15/(z*96485.33212)*np.log(ratios),label=f'Valence {z:+d}')
ax[1].set(title='B  Ideal Nernst reference, 37 °C',xlabel='Outside / inside activity ratio',ylabel='Equilibrium potential (mV)');ax[1].legend()
for a in ax:a.grid(alpha=.15)
physical.suptitle('Physical references, not fitted organ physiology',fontsize=13)
physical.savefig(HERE/'physical-references.png',dpi=180);physical.savefig(HERE/'physical-references.pdf',metadata={'CreationDate':None,'ModDate':None})
with PdfPages(HERE/'BIOELECTRIC_BODY_REPORT.pdf',metadata={'Title':'A value-owned bioelectric Body','Author':'Michael Emanuel Glover; implementation and analysis with assistant','CreationDate':None,'ModDate':None}) as pdf:
    pdf.savefig(fig);pdf.savefig(physical)
plt.close('all')
print(json.dumps(summary,indent=2))
