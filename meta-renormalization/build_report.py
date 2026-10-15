#!/usr/bin/env python3
"""Build scientific figures, a Markdown report and a standalone PDF."""
from pathlib import Path
import html
import json
import re
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import SimpleDocTemplate,Paragraph,Image,Table,TableStyle,Spacer,Preformatted
ROOT=Path(__file__).resolve().parent
D=json.loads((ROOT/'data/results.json').read_text())
COLORS=['#718295','#ba954c','#178365','#925fa8','#327cb8']
plt.rcParams.update({'font.size':10,'axes.spines.top':False,'axes.spines.right':False,'figure.dpi':140})
def row(s,m):return next(r for r in D['results'] if r['scenario']==s and r['method']==m)
def save(fig,name):
    for ext in ['png','pdf']:fig.savefig(ROOT/f'figures/{name}.{ext}',bbox_inches='tight')
    plt.close(fig)
def pct(x):return f'{100*x:.2f}%'
fig,axes=plt.subplots(2,2,figsize=(11,8),layout='constrained')
for ax,scenario in zip(axes.flat,D['scenarios']):
    rows=[row(scenario,m) for m in D['methods']];v=np.array([r['explained_variance'] for r in rows]);ci=np.array([r['explained_variance_ci95'] for r in rows]);ax.bar(range(5),v,color=COLORS);ax.errorbar(range(5),v,yerr=[v-ci[:,0],ci[:,1]-v],fmt='none',ecolor='#293441',capsize=3);ax.set_ylim(0,1.1);ax.set_title(scenario);ax.set_ylabel('Held-out explained variance');ax.set_xticks(range(5),['Additive','Pair\naverages','Relaxed\nhierarchy','No-relax\nhierarchy','Exhaustive\npolynomial'],fontsize=8)
    for i,value in enumerate(v):ax.text(i,value+.035,f'{100*value:.1f}%',ha='center',fontsize=8)
fig.suptitle('Experiment 002 · 20 independent seeds per condition\n12,000 samples per seed; final 3,000 sealed for testing; 95% whole-seed bootstrap intervals')
save(fig,'held-out-performance')
fig,axes=plt.subplots(1,2,figsize=(11,4.4),layout='constrained')
rows=[row('Pair-supported hierarchy',m) for m in D['methods']]
axes[0].bar(range(5),[r['mse'] for r in rows],color=COLORS);axes[0].set_yscale('log');axes[0].axhline(.09,color='#333',ls='--',label='Expected noise MSE 0.09');axes[0].set_ylabel('Test MSE (log scale)');axes[0].legend(fontsize=8)
axes[1].bar(range(5),[r['parameters'] for r in rows],color=COLORS);axes[1].set_ylabel('Fitted parameters, including intercept')
for ax in axes:ax.set_xticks(range(5),['Additive','Pair\naverages','Relaxed\nhierarchy','No-relax\nhierarchy','Exhaustive\npolynomial'],fontsize=8)
fig.suptitle('Pair-supported condition · predictive accuracy and representation size')
save(fig,'error-and-size')
fig,axes=plt.subplots(1,2,figsize=(11,4.2),layout='constrained')
for scenario,color in zip(D['scenarios'],['#178365','#bb5e60','#327cb8','#ba954c']):
    history=D['examples'][scenario]['histories']['Hierarchical relaxation'];axes[0].plot([h['round'] for h in history],[h['validation_mse'] for h in history],marker='o',label=scenario,color=color);axes[1].plot([h['round'] for h in history],[len(h['selected']) for h in history],marker='o',color=color)
axes[0].set_yscale('log');axes[0].set_ylabel('Selection-validation MSE (log scale)');axes[0].legend(fontsize=8);axes[1].set_ylabel('Selected interaction objects')
for ax in axes:ax.set_xlabel('Promotion round');ax.grid(alpha=.15)
fig.suptitle('Finite structure-discovery histories · representative seed 0\nSelection validation is adaptively reused; final test samples are not queried')
save(fig,'discovery-history')
main=row('Pair-supported hierarchy','Hierarchical relaxation');poly=row('Pair-supported hierarchy','Exhaustive polynomial');hidden=row('Hidden fourth order','Hierarchical relaxation');hidden_poly=row('Hidden fourth order','Exhaustive polynomial')
table='\n'.join('| '+' | '.join([r['method'],pct(r['explained_variance']),f"{r['mse']:.5f}",f"{r['parameters']:.1f}"])+ ' |' for r in rows)
stress='\n'.join('| '+' | '.join([s,pct(row(s,'Hierarchical relaxation')['explained_variance']),pct(row(s,'Exhaustive polynomial')['explained_variance']),f"{row(s,'Hierarchical relaxation')['support_recall']:.2f}" if row(s,'Hierarchical relaxation')['support_recall'] is not None else 'not applicable'])+' |' for s in D['scenarios'])
text=f'''# Meta-Renormalization: Experiment 002
## Autonomous interaction discovery within an explicit candidate grammar

R. Michael Glover · HRL Portfolio · October 2026 · Seeded synthetic experiment

### Abstract

Experiment 001 supplied a relational model with interaction features matched to its generating equation. Experiment 002 removes the identity of the generating supports from the learner. It proposes all raw-component pairs, labels interaction hypotheses active or inactive through damped context-dependent relaxation, and promotes selected disjoint pairs into canonical fourth-order objects. In 20 independent-input seeds, the learner recovers all five generating interaction supports and achieves {pct(main['explained_variance'])} mean held-out explained variance with MSE {main['mse']:.5f}, using 14 fitted parameters. An exhaustive degree-four multilinear model obtains {pct(poly['explained_variance'])} with 163 parameters. Disabling relaxation yields the same predictions in this condition: the result demonstrates restricted structure discovery, not the necessity of relaxation. Pure hidden fourth-order interactions and correlated inputs expose strong failures relative to exhaustive enumeration.

### 1. Provenance of Experiment 001

The supplied Experiment 001 summary described eight components and 12,000 observations, reporting 9,000 training and 3,000 test observations, additive/coarse/relational explained variance of 2.3%, 2.4%, and 98.2%, and MSE 4.75248, 4.74778, and 0.08968. Its source file and coefficients a_j were not available in the workspace. Those are reported reference values, not an independently reproduced run here. The new generator below is fully specified, seeded, executed, and published. Its different coefficients and random supports mean its metrics should not numerically equal Experiment 001.

The important lesson of the first report is preserved: representing interactions known to generate the target can produce a large gain over additive summaries. That alone does not demonstrate autonomous discovery, a learned compatibility function, or an iterative relaxation process.

### 2. New systems and sealed evaluation

For each seed 0 through 19, draw 12,000 eight-component standard Gaussian observations. Randomly permute component indices into four disjoint pairs, draw each pair coefficient uniformly in magnitude from 0.6 to 1.2 with a random sign, and randomly choose two of those pairs for a fourth-order term with coefficient 0.9. Add a linear contribution 0.15 times the sum of all components and independent Gaussian noise with standard deviation 0.3.

```text
y = 0.15 sum_i x_i + sum_j a_j product_(i in pair_j) x_i
    + 0.9 product_(i in meta_support) x_i + epsilon
```

Four conditions are evaluated: pair-supported hierarchy; a pure hidden fourth-order interaction with no pair contributions; correlated inputs with pairwise correlation 0.4; and an additive-only control. The hidden supports and coefficients are not passed to the learner. They are used only for final evaluation and an explicitly identified example inspection.

The first 6,000 observations fit coefficients. The next 3,000 select structure. The final 3,000 form the sealed test set. After selecting structure, coefficients are refitted on all 9,000 non-test observations. No test targets determine promotion, stopping, or constants. Selection validation is adaptively queried and is not claimed to be an unbiased error estimate. Constants are fixed across conditions and seeds. We do not claim an independent preregistration of this study.

### 3. What the learner is and is not given

All eight individual components are always present as linear leaves. All 28 unordered pairs are proposed without knowing which pairs generated the data. A pair can become a selected higher-level object. Two selected disjoint pairs can then propose a canonical product over four unique components. Equivalent parenthesizations are deduplicated.

The candidate grammar is supplied in advance. Degrees above four, repeated powers, arbitrary functions, latent physical laws, and unrestricted compatibility kernels are not discovered. This is a specialized GRRLE-inspired learner, not a port of the general GRRLE implementation. The learned aspect is which interaction hypotheses receive support and are selected; the syntax of parent-child compatibility and its bounded weight are designed, not learned from scratch.

### 4. Predictive evidence and actual relaxation

At each round, fit the current selected model to fitting observations. Residualize each new candidate feature against that model, solve its one-term least-squares coefficient on fitting data, and compute the exact change in selection-validation MSE if that term is added and the model refitted. Existing hypotheses receive evidence from the validation cost of removing and refitting their term. Thus selected parents remain nodes in the relation graph rather than being replaced by a constant reward.

Let g_h be a candidate or retention gain, c=max(1e-8, 0.002 Var(y_fit)), and T=max(1e-8, 0.02 Var(y_fit)). Initialize active strength with a sigmoid, then use active/inactive labels and bounded parent-child compatibility support:

```text
z_h = (g_h - c) / T
p_h(0) = sigmoid(z_h)
p_h(t+1) = 0.5 p_h(t) + 0.5 sigmoid(z_h + support_h(p(t)))
```

Each directed parent-child compatibility has weight 0.15. Iterate until maximum change is below 1e-8 or 60 iterations. A new candidate must have positive validation gain exceeding c and active strength above 0.8. Bounded compatibility cannot bypass the positive-gain gate. Select the eligible candidate with highest relaxed strength, with gain and canonical index order breaking ties. Stop when none qualifies or 12 interactions have been selected. Unknown/inactive hypotheses remain unselected; the algorithm is not forced to explain every component with an interaction.

Active strengths are numerical label weights, not calibrated probabilities of a true causal relationship. This is iterative relaxation and finite recursive promotion. However, merely including such iterations does not establish that they improve prediction. The no-relaxation ablation uses the same grammar, evidence, gain gate, strength gate and fitting protocol, but replaces the recurrent label update with its initial evidence strengths.

### 5. Baselines and measured results

Additive regression fits eight components plus an intercept. Fixed pair averages fits four predetermined adjacent-component averages plus an intercept. That is a deliberately lossy coarse projection, not a full physical renormalization-group algorithm. The exhaustive baseline fits every square-free monomial of degrees one through four: 162 features plus an intercept. It receives the same observations, no generating-support indices, and uses all 9,000 non-test observations. Its representation is broader than the hierarchy's promoted subset but lies within the same maximum-degree language.

Independent-input pair-supported results, averaged over 20 seeds:

| Method | Explained variance | Test MSE | Fitted parameters |
| --- | --- | --- | --- |
{table}

![Held-out performance across four conditions](figures/held-out-performance.png)

Explained variance is 1-Var(y-prediction)/Var(y). R-squared is 1-MSE/Var(y); both are stored separately. The expected conditional noise MSE is 0.09, while realized test noise MSE varies by seed and is recorded. This is an expectation, not a strict lower bound on every finite-sample observed error. The fitted model also has coefficient-estimation error. Figure intervals resample whole seeds 1,000 times and describe mean performance for this synthetic seed distribution, not a universal guarantee.

![Test error and model size](figures/error-and-size.png)

The hierarchy recovers the four generating pair supports and the generating fourth-order support in every independent-input seed. This support-set recovery is stronger than merely supplying those supports to a regression. Nevertheless, the no-relaxation hierarchy selects the same predictive structure here. The data do not establish a causal benefit from relaxation beyond the supplied grammar and greedy predictive selection.

### 6. Failures, identifiability and limits

| Condition | Hierarchical explained variance | Exhaustive polynomial | Hierarchical support recall |
| --- | --- | --- | --- |
{stress}

When a fourth-order term has no useful pair-level parents, the hierarchy never proposes it. It obtains {pct(hidden['explained_variance'])} explained variance while exhaustive enumeration obtains {pct(hidden_poly['explained_variance'])}. Correlated inputs create misleading lower-order relationships and greedy commitments; the exhaustive baseline is substantially better there. A future method needs alternative promotion proposals, pruning or revisiting prior structure, and stronger regularized-search baselines. The current learner does not prune selected terms.

Multiplication also creates an identifiability limit:

```text
(x1*x2)*(x3*x4) = (x1*x3)*(x2*x4) = x1*x2*x3*x4
```

Prediction alone cannot distinguish those parent trees. Support-set recovery therefore means recovering the observable component subset, not proving the unique latent hierarchy or causal mechanism. Main pair terms can supply additional evidence, but not a general proof of the intended tree.

![Discovery histories for seed zero](figures/discovery-history.png)

The proposed inequality V(MetaRenorm(X)) >= V(Additive(X)) remains a hypothesis about defined tasks and evaluation distributions, not a theorem. Extra model capacity can overfit, candidate grammars can miss true interactions, and validation reuse can favor spurious structure. This study uses one narrow family of synthetic equations, 20 seeds, fixed noise and a particular hypothesis language. It does not establish performance on real scientific data, autonomous causal discovery, or a general renormalization method.

### 7. Reproduction and next tests

The NumPy learner is hrl/meta_discovery.py. The generator, actual benchmark run, CSV counts, full example histories, source SHA256 hashes, software versions, and figure/report builder are published. Run experiment.py, then build_report.py from the repository root. Tests check recovery without supplied supports, the pure-interaction blind spot, deterministic runs, non-mutation, inactive behavior on additive controls, bounded relaxation, exact validation-gain accounting, equivalent quartic trees, and input validation.

Next tests should compare sparse polynomial regression, hierarchical interaction selection and beam search; hold out equation families, not just observations; vary dimension and noise; and permit higher-order proposals without detectable lower-level effects. Pairwise and higher-order compatibility should eventually be learned and independently tested rather than assumed to have the current form. Those are future experiments, not results asserted here.

### Related work

Hierarchical interaction modeling and heredity constraints are established research areas. This experiment claims a reproducible portfolio prototype, not priority for interaction selection or hierarchical regression. See J. Bien, J. Taylor and R. Tibshirani, A Lasso for Hierarchical Interactions (2013), https://pmc.ncbi.nlm.nih.gov/articles/PMC4527358/, and H. Hazimeh and R. Mazumder, Learning Hierarchical Interactions at Scale (2020), https://proceedings.mlr.press/v108/hazimeh20a.html. The portfolio's GRRLE Strong source and interpretation notes provide the local design context. Formal comparisons with such methods remain necessary.
'''
(ROOT/'WHITEPAPER.md').write_text(text)
styles=getSampleStyleSheet();styles['BodyText'].fontSize=9;styles['BodyText'].leading=13;styles['BodyText'].spaceAfter=8;styles['Code'].fontSize=8;styles['Code'].leading=11
story=[];lines=text.splitlines();i=0
while i<len(lines):
    line=lines[i]
    if not line:i+=1;continue
    if line.startswith('```'):
        code=[];i+=1
        while i<len(lines) and not lines[i].startswith('```'):code.append(lines[i]);i+=1
        story.append(Preformatted('\n'.join(code),styles['Code']));story.append(Spacer(1,8));i+=1;continue
    if line.startswith('!['):
        path=re.search(r'\((.*?)\)',line).group(1);image=Image(str(ROOT/path));scale=min(480/image.imageWidth,330/image.imageHeight);image.drawWidth=image.imageWidth*scale;image.drawHeight=image.imageHeight*scale;story.append(image);story.append(Spacer(1,10));i+=1;continue
    if line.startswith('|'):
        rows=[]
        while i<len(lines) and lines[i].startswith('|'):
            cells=[v.strip() for v in lines[i].strip('|').split('|')]
            if not all(re.fullmatch('[-: ]+',v) for v in cells):rows.append([Paragraph(html.escape(v),styles['BodyText']) for v in cells])
            i+=1
        table=Table(rows,colWidths=[170,115,100,95],repeatRows=1);table.setStyle(TableStyle([('BACKGROUND',(0,0),(-1,0),colors.HexColor('#e3eee8')),('GRID',(0,0),(-1,-1),.3,colors.HexColor('#bbc8c1')),('VALIGN',(0,0),(-1,-1),'TOP')]));story.append(table);story.append(Spacer(1,10));continue
    style='Title' if line.startswith('# ') else 'Heading2' if line.startswith('##') else 'BodyText'
    story.append(Paragraph(html.escape(line.lstrip('# ')),styles[style]));i+=1

def footer(canvas,doc):
    canvas.saveState();canvas.setFont('Helvetica',8);canvas.drawString(44,26,'Meta-Renormalization | Experiment 002 | Synthetic observations');canvas.drawRightString(568,26,str(doc.page));canvas.restoreState()
SimpleDocTemplate(str(ROOT/'WHITEPAPER.pdf'),pagesize=(612,792),leftMargin=44,rightMargin=44,topMargin=40,bottomMargin=44,title='Meta-Renormalization: Experiment 002',author='R. Michael Glover').build(story,onFirstPage=footer,onLaterPages=footer)
print('Built three figure pairs, Markdown paper, and PDF.')
