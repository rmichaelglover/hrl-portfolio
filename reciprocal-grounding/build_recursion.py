#!/usr/bin/env python3
"""Produce recursive-study figures and the measured white-paper supplement."""
from pathlib import Path
import json
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
ROOT=Path(__file__).resolve().parent
D=json.loads((ROOT/'data/recursive-results.json').read_text())
COLORS=['#647b8a','#1d6b99','#178365','#d58926','#b94f58']
plt.rcParams.update({'font.size':10,'axes.spines.top':False,'axes.spines.right':False,'figure.dpi':140})
def save(fig,name):
    for ext in ['png','pdf']:fig.savefig(ROOT/f'figures/{name}.{ext}',bbox_inches='tight')
    plt.close(fig)
def pct(x):return 'undefined' if x is None else f'{100*x:.2f}%'
def result(s,m):return next(r for r in D['results'] if r['scenario']==s and r['method']==m)
fig,axes=plt.subplots(1,2,figsize=(11,4.5),layout='constrained')
rows=[result('Independent observations',m) for m in D['methods']]
for ax,key,title in zip(axes,['coverage','test_loss'],['Fresh-observation matching coverage','Held-out coordinate reconstruction loss']):
    values=[r[key] for r in rows];ax.bar(range(5),values,color=COLORS);ax.set_xticks(range(5),[m.replace(' ','\n') for m in D['methods']],fontsize=8);ax.set_title(title)
    for i,v in enumerate(values):ax.text(i,v+.015 if key=='coverage' else v+.035,pct(v) if key=='coverage' else f'{v:.3f}',ha='center',fontsize=9)
    ax.set_ylim(0,1 if key=='coverage' else max(values)*1.18)
fig.suptitle('Recursive study · seeds 100–139 · same identities, fresh observations\nThresholds selected on separate seeds; this is a different dataset from the first study')
save(fig,'recursion-outcomes')
fig,axes=plt.subplots(1,2,figsize=(11,4.3),layout='constrained')
for method,color in zip(['Guarded recursion','No validation','Unregularized recursion'],[COLORS[2],COLORS[3],COLORS[4]]):
    trace=D['example']['Independent observations'][method];history=trace['history']
    for ax,key in zip(axes,['validation_loss','identity_loss']):
        ax.plot([r['round'] for r in history],[r[key] for r in history],label=method,color=color)
        selected=history[trace['selected_round']];ax.scatter([selected['round']],[selected[key]],color=color,s=40,zorder=3)
for ax,title in zip(axes,['Validation measurement loss','Distance from training identity centers']):ax.set_title(title);ax.set_xlabel('Recursive round');ax.grid(alpha=.15)
axes[0].legend(fontsize=8);fig.suptitle('Checkpoint diagnostics · seed 100 · independent observations\nDots mark the returned checkpoint; validation measurements never supply update gradients')
save(fig,'recursion-checkpoints')
fig,axes=plt.subplots(1,2,figsize=(10,4.6),layout='constrained')
base=D['example']['Independent observations']['Single observation'];guard=D['example']['Independent observations']['Guarded recursion']
for ax,key,title in zip(axes,['things','names'],['Thing representations','Name representations']):
    before=np.array(base[key][0]);after=np.array(guard[key][0]);ax.scatter(before[:,0],before[:,1],s=25,color='#93a5b0',label='Initial observation');ax.scatter(after[:,0],after[:,1],s=28,color='#178365',label='Selected recursive state')
    for a,b in zip(before,after):ax.annotate('',xy=b[:2],xytext=a[:2],arrowprops={'arrowstyle':'->','color':'#547c70','lw':.7})
    ax.set_title(title);ax.set_xlabel('Feature coordinate 0');ax.set_ylabel('Feature coordinate 1');ax.legend(fontsize=8)
fig.suptitle('Identity refinement · view 1, seed 100 · two feature coordinates only\nMovement shows representation changes, not changes to physical things or proof of meanings')
save(fig,'recursive-representations')
table='\n'.join('| '+' | '.join([r['method'],pct(r['accuracy']),pct(r['coverage']),f"{r['test_loss']:.4f}",f"{r['selected_round']:.1f}"])+ ' |' for r in rows)
stress='\n'.join('| '+' | '.join([s,pct(result(s,'Guarded recursion')['accuracy']),pct(result(s,'Guarded recursion')['coverage']),f"{result(s,'Guarded recursion')['test_loss']:.4f}"])+ ' |' for s in D['scenarios'][1:])
g=result('Independent observations','Guarded recursion');b=result('Independent observations','Robust self-only')
text=f'''## Recursive Grounding: representation refinement with explicit anti-overfitting controls

Research prototype v2 supplement · October 15, 2026 · R. Michael Glover

### R1. The added recursion

The new module recursively revisits a finite three-level hierarchy: observation leaves, thing/name representations, and reciprocal relation hypotheses. Relations feed back into representations; updated representations regenerate the relation graphs and label evidence at the next round. This is GRRLE-inspired recurrent refinement, not a port of the generic span-lattice implementation or an infinite-depth construction. Things becoming more like themselves means more stable representations of repeated measurements. Names becoming more like things means revising their feature representatives toward supported referents. The physical things themselves are not modified.

Each direction retains a separate sensor space. Let X and W denote current thing and name coordinates, with X0 and W0 their coordinate-wise median training observations. Let C contain geometric-mean strengths only for mutually accepted pairs that persist over two consecutive rounds. All other entries are zero. Proposals are:

```text
T_X = (lambda X0 + beta C W) / (lambda + beta row_sum(C))
T_W = (lambda W0 + beta transpose(C) X) / (lambda + beta column_sum(C))
X_next = project_ball(X0, radius, X + damping * (T_X - X))
W_next = project_ball(W0, radius, W + damping * (T_W - W))
```

Division is row-wise. Unsupported rows fall back to their original training identity center. Default lambda=1, beta=0.25, damping=0.45 and radius=0.8. Both sides update simultaneously from the previous state. The initial state is the first training observation; the initial checkpoint may lie outside the proposal drift bound. Every later bounded proposal lies within radius 0.8 of its fixed training center. Input evidence is copied and never overwritten.

### R2. Overfitting is explicitly combatted

The guarded configuration uses robust within-identity medians, fixed identity anchoring, damped updates, a total displacement bound from the original centers, two-round persistence before cross-feedback, retained unknown labels, a finite 24-round budget, and validation checkpoint selection. After four rounds without a validation-loss improvement above 1e-5 it stops and returns its best checkpoint, including the possibility of returning round zero. Validation coordinates affect only checkpoint selection and stopping, never proposal coordinates, matching labels, or gradients. Repeated selection on finite validation data can itself overfit; these controls are not a guarantee against it.

A separate final matching gate requires three fresh logit-perturbation checks. Once relations feed back into both sides, their later agreement is coupled evidence and must not be counted as independent confirmation. Recursion is not an independent verifier and does not promote its own confidence to external truth.

### R3. Separate observations and separate questions

Each synthetic identity has five training measurements, three checkpoint-validation measurements, and three sealed test measurements per sensor view. There are 20 things (four unmatched), 16 name identifiers, five dimensions, thing noise standard deviation 0.9, and name noise standard deviation 0.7. Prototypes and unknown distractors use the same generating distributions as v1. The same identities recur across these splits: this tests fresh observations, not unseen objects, words, semantic categories, or languages.

The checkpoint objective is mean squared distance from both sets of representation coordinates to validation measurements of those same identities. It does not receive hidden thing-to-name correspondence labels. Held-out coordinate loss uses test measurements; latent mean-square error is an additional evaluation-only diagnostic in JSON. Fresh-observation matching uses the mean of each thing's three sealed test measurements against learned name representatives. It deliberately does not use the fitted thing coordinates as query inputs. The test observations never enter recursion, stopping, or threshold selection.

Seeds 0–19 select matching thresholds separately for each method on independent observations, targeting empirical accepted accuracy of at least 95% with ten accepts on the same grid as v1. Thresholds are frozen for seeds 100–139 under three conditions. Within each seed, checkpoint-validation measurements are distinct from that cross-seed threshold-calibration cohort. Neither validation procedure consumes the sealed test observations. Test tables contain 800 things per condition. CSV has 600 seed/method/condition rows; accuracy intervals use the same whole-seed bootstrap as v1.

The single-observation baseline uses the first training leaf. Robust self-only uses the medians of all five training leaves, with no cross-feedback. This same-evidence baseline separates recursive cross-refinement from merely acquiring more measurements. No validation runs all 24 rounds with identity constraints retained. Unregularized recursion removes the self anchor, drift bound, persistence and checkpoint selection, uses beta=1 and damping=0.9, and runs 24 rounds. It is a bundled stress ablation, not an isolated estimate of any one guard's contribution. The no-validation ablation isolates checkpoint selection more closely.

### R4. Measured recursive results

Independent observations, fresh test queries, frozen calibration thresholds:

| Method | Accepted accuracy | Coverage | Test coordinate loss | Mean returned round |
| --- | --- | --- | --- | --- |
{table}

![Recursive coverage and held-out reconstruction loss](figures/recursion-outcomes.png)

Guarded recursion reaches {pct(g['accuracy'])} accepted accuracy at {pct(g['coverage'])} coverage, compared with {pct(b['accuracy'])} at {pct(b['coverage'])} for robust self-only. The coverage difference is {100*(g['coverage']-b['coverage']):.2f} percentage points. Coordinate loss changes from {b['test_loss']:.4f} to {g['test_loss']:.4f}. These results are for a different repeated-measurement dataset from v1; comparisons with v1's 98.80% result are not controlled comparisons.

The guard ablations are mixed. No-validation and unregularized recursion are competitive on this small dataset; unregularized recursion can obtain lower coordinate loss. Thus these experiments demonstrate implemented safeguards and a denoising/refinement effect, but do not prove that every guard improves accuracy, that guarded recursion is optimal, or that recursion universally prevents overfitting. Hyperparameters were not tuned to make a guard win on these test seeds. More noise regimes, sensor biases, capacities and independent datasets are required.

![Recursive checkpoint diagnostics](figures/recursion-checkpoints.png)

Training-outlier stress corrupts the first training measurement of a quarter of identities with Gaussian noise of standard deviation 5, leaving other measurements and validation/test splits unchanged. Robust self-only already provides much of the protection. Shared-wrong-dictionary stress applies the same cyclic wrong naming convention to both views, including their name observations. Coordinate validation can favor that internally consistent representation without recovering the intended correspondence.

| Condition | Guarded accepted accuracy | Coverage | Test coordinate loss |
| --- | --- | --- | --- |
{stress}

![Changes in thing and name representations](figures/recursive-representations.png)

The plots show a representative seed rather than asserting that a single trajectory represents every run. Full histories, selected rounds, representation coordinates, counts, uncertainty intervals and source hashes are downloadable. Checkpoint traces end when the corresponding guarded run stops; no average over a changing set of surviving runs is plotted.

### R5. Verification, limits and reproduction

Tests cover deterministic refinement, non-mutation, finite normalized inference, bounded post-initial proposals, validation rollback, finite recursion, self-only behavior, persistence, input validation, and separation of validation from the proposal path. A successful coordinate checkpoint is not a proof of semantic truth. Unknowns remain an explicit abstention option, and the unique-instance matching assumption remains in force.

Run recursive_experiment.py, build_recursion.py and build_report.py from the repository root. The first script records its configuration, exact seed splits, library versions, hashes and complete histories. Plotting and report tools are separate from the NumPy runtime. Interactive depth controls inspect stored checkpoints and do not run hidden training or alter the frozen study. The existing GRRLE Strong exhibit documents the broader recursive design; this module is a small specialized recurrent hierarchy, not a port of that implementation.

A next study should preregister architecture and stopping choices, vary validation-set size, hold out entire identities and semantic categories, and test many-to-many naming. Independent measurements or a separate verifier are still required before treating a recursively reinforced relation as a provisional external fact.
'''
(ROOT/'RECURSION.md').write_text(text)
print('Built recursion supplement and three PNG/PDF figure pairs.')
