from pathlib import Path
import json,hashlib,platform,shutil
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from experiment import sample,fit_models,relax,assignment,corrupt,ROLES
r=json.loads(Path('results/results.json').read_text());a=json.loads(Path('active-results/results.json').read_text())
out=Path('publication');out.mkdir(exist_ok=True)
methods=['unary','topology_classifier','relaxation','shuffled_graph','exact_graph_map','direct_effect_ridge']
labels={'unary':'Unary labels','topology_classifier':'Topology classifier','relaxation':'Relaxation','shuffled_graph':'Shuffled graph','exact_graph_map':'Exact graph MAP','direct_effect_ridge':'Direct-effect ridge'}
conditions=['in_distribution','descriptor_noise','graph_corruption','novel_motif']
cnames=['Familiar circuits','Noisy descriptors','Damaged graph','Novel causal motif']
plt.rcParams.update({'font.family':'DejaVu Sans','font.size':10,'axes.spines.top':False,'axes.spines.right':False,'figure.facecolor':'#f5f3e9','axes.facecolor':'#f5f3e9'})
fig,axes=plt.subplots(1,3,figsize=(15,4.6),layout='constrained')
colors={'unary':'#8b9386','relaxation':'#cc572a','exact_graph_map':'#365e59','direct_effect_ridge':'#958164'}
for method in colors:
 axes[0].plot(range(4),[r['summaries'][c][method]['effect_mae'] for c in conditions],marker='o',label=labels[method],color=colors[method])
axes[0].set_xticks(range(4),['Familiar','Noisy\nfeatures','Damaged\ngraph','New\nmotif']);axes[0].set_ylabel('Mean absolute error (probability units)');axes[0].set_title('A. Forecasting intervention effects');axes[0].legend(fontsize=8);axes[0].set_ylim(bottom=0)
for condition,color in [('familiar','#365e59'),('novel_motif','#cc572a')]:
 for strategy,ls in [('random','--'),('disagreement','-')]:
  d=a['summaries'][condition]['relaxation_'+strategy]
  axes[1].plot(range(3),[d[str(i)] for i in range(3)],linestyle=ls,marker='o',color=color,label=condition.replace('_',' ')+' / '+strategy)
axes[1].set_xticks(range(3));axes[1].set_xlabel('Queries to eligible units');axes[1].set_ylabel('Error on fixed, unqueried target units');axes[1].set_title('B. Asking more is not enough');axes[1].legend(fontsize=8);axes[1].set_ylim(bottom=0)
d=r['summaries']['in_distribution']['relaxation'];axes[2].bar(['Permitted\ncontext','Blocked\ncontext'],[d['chosen_permitted_change'],d['chosen_blocked_change']],color=['#cc572a','#365e59']);axes[2].axhline(0,color='#263e36',lw=1);axes[2].set_title('C. Suppression is not a selective fix');axes[2].set_ylabel('Actual change in output probability');axes[2].text(.5,.92,'Chosen ablation reduces both contexts',transform=axes[2].transAxes,ha='center',fontsize=9)
fig.suptitle('Relaxation-assisted circuit interpretation · Synthetic planted circuits only',fontsize=14)
for ext in ['png','svg','pdf']:fig.savefig(out/('study-figure.'+ext),dpi=180)
plt.close(fig)
svg_path=out/'study-figure.svg'
svg_path.write_text('\n'.join(line.rstrip() for line in svg_path.read_text().splitlines())+'\n')
rows='\n'.join('| '+name+' | '+' | '.join(f"{r['summaries'][c][m]['effect_mae']:.5f}" for c in conditions)+' |' for m,name in [(m,labels[m]) for m in methods])
active_rows='\n'.join('| '+condition+' / '+method+' / '+strategy+' | '+' | '.join(f"{a['summaries'][condition][method+'_'+strategy][str(b)]:.5f}" for b in range(3))+' |' for condition in ['familiar','novel_motif'] for method in ['unary','relaxation'] for strategy in ['random','disagreement'])
ci=r['paired_bootstrap']['in_distribution'][0]
report=f'''# Labels are not mechanisms: a controlled study of relaxation-assisted circuit interpretation

Manny Glover / ClosedAI · AI-assisted research prototype · 31 October 2026

**Status: executed synthetic study, not peer reviewed. No language model weights, Mythos internals, or human subjects were used.**

## Main findings

1. On 100 held-out familiar circuits, categorical relaxation reduced mean absolute intervention-effect prediction error from **0.06731 to 0.04484** relative to unary labeling, a **33.4% reduction in this error metric**. The paired difference was {ci['mean']:.5f}, with a circuit-bootstrap 95% interval [{ci['ci95'][0]:.5f}, {ci['ci95'][1]:.5f}]. This is not a 33.4% reduction in real-world AI risk.
2. The learned graph model with exact permutation search matched relaxation's familiar-condition result. This supports the value of the provided relational information, not a unique benefit of iterative relaxation or a new state-of-the-art method.
3. Both familiar and novel-motif circuits achieved 100% planted-label accuracy under relaxation, while intervention forecast error rose from **0.04484 to 0.13761** in the novel motif. Knowing a feature's assigned role did not determine the magnitude of its causal effect.
4. The selected intervention had **the same mean regret as unary labeling** in the familiar condition (0.00764). Better effect forecasts did not improve the downstream choice in this benchmark.
5. The selected ablation lowered output probability by **0.37098 in permitted contexts** and **0.20371 in blocked contexts**. It suppressed activity in both: this does not demonstrate a selective safety repair.
6. In a separate follow-up using new circuits, label-disagreement-guided queries provided **no gain for relaxation in the familiar family** and slightly worsened its forecast error in the novel motif. The query scheme updated label beliefs but could not revise its learned mechanism-effect templates.

## Why this question matters

The circuit-tracing paper uses readable features and graphs to propose computational mechanisms, then tests them with interventions. Our proposal is narrower: use relaxation labeling as an analysis layer over ambiguous labels. This study asks whether that layer helps predict intervention outcomes when the true computation is available for scoring.

It does not train a cross-layer transcoder, reconstruct an LLM circuit, identify an intention, or replicate Anthropic's experiments. It uses six-unit, multi-stage sigmoid circuits with designer-assigned roles. Their mathematical nonlinearity does not make them a realistic language model.

## Experimental setup

The planted roles are pressure relay, boundary relay, task drive, authorization gate, action mediator, and a decoy branch disconnected from the output. Names refer to the designer's formulas, not empirically discovered psychological states. We randomize internal unit indices and continuously vary coefficients and biases. Some internal edges are optional.

The analyst sees noisy activation descriptors and signed directed adjacency. Descriptors summarize means, spread, quantiles, and correlations with three observed inputs and output under correlated observational inputs. Test intervention effects are measured under independently sampled, balanced inputs. Access to input references, a known six-role taxonomy, and a one-to-one assignment constraint makes this much simpler than real feature interpretation.

Training: 120 circuits. Validation: 50 independent circuits. Primary test: 100 circuits reused across familiar/noise/corruption observation conditions, plus 100 separate novel-motif variants. Thus the four test conditions are **not 400 independent circuits**. Follow-up query test: 100 new familiar circuits and 100 new novel variants, using a fresh seed range. Generated conditions share parameters/seeds where specified in the designs.

Fit scaling, classifier parameters, graph compatibilities, and role-effect templates on training only. Select graph strength from the fixed grid 0, .25, .5, 1, 2, 4, 8 by validation intervention error; **selected strength: {r['selected_gain']}**. Freeze it before test. No test labels or intervention outcomes enter the primary inference functions. Synthetic primary and active-design notes are included with the code; these are local recorded designs, not an independently registered study.

## What the algorithms do

Unary inference classifies each unit from its descriptors, then uses maximum-weight one-to-one assignment. The topology baseline adds generic signed in/out degrees. Relational compatibility is estimated from signed edge/nonedge patterns between training roles. Categorical relaxation alternates compatibility messages and soft one-to-one normalization, damping updates before hard assignment. It is a new experimental variant inspired by the local GRRLE engine, **not a direct call to RelaxEngine or the existing GRRLE implementation**.

Exact graph MAP enumerates all 720 permutations under the same discrete objective. Shuffled-graph inference independently scrambles the observed adjacency while retaining descriptors. Zero gain reproduces unary assignment. A supervised ridge baseline forecasts effects directly without assigning roles. The uniform reference predicts the mean training role effect.

For every label-based method, predicted intervention effects come from training mean effects for each assigned role. This deliberately simple prediction layer is shared across methods. Its failure under changed wiring is a limitation of the analysis pipeline, not proof that relaxation itself causes that failure.

The primary causal measurement is the average output probability change after clamping one unit to zero and recomputing all downstream units in the original planted circuit. We also record mean-replacement interventions. Zero ablation can be off-distribution; neither intervention proves a historical training cause. The output is a scalar synthetic action propensity, not an actual harmful act.

## Primary results

Mean absolute error in output-probability changes; lower is better.

| Method | Familiar | Noisy descriptors | Damaged graph | Novel motif |
|---|---:|---:|---:|---:|
{rows}

All relaxation runs met the recorded numerical stopping criterion. That says the inference stabilized, not that its explanation was causally complete. Novel-motif labels were perfect because the supplied role taxonomy remained identifiable, while new interactions changed how those roles affected the output.

The exact search sometimes outperformed relaxation when observations or graphs were damaged. The experiment therefore offers no claim of globally optimal relaxation inference. More expressive nonlinear direct-effect baselines and graph-neural baselines were not tested; the ridge and degree-classifier comparisons do not exhaust alternatives.

## Budgeted questioning follow-up

Each circuit has three query-eligible units and three fixed prediction targets. Targets cannot be queried. At budgets 0, 1, and 2, score the same target set. A query reveals one eligible unit's measured ablation effect. The analyst updates label scores using a Gaussian likelihood estimated from training role effects, with a fixed 0.03 standard-deviation floor.

The disagreement policy selects the eligible unit with the largest variance among role-effect templates under its current supports. This is **not calibrated expected information gain**. The random policy uses a separate seeded order. This is querying a synthetic experiment, not asking a language model for its stated reasons.

| Condition / inference / query policy | 0 queries | 1 query | 2 queries |
|---|---:|---:|---:|
{active_rows}

For novel-motif relaxation, disagreement minus random at budget 2 was +0.00228 error, with bootstrap interval [0.00000, 0.00505]. This is a small generator-specific degradation, not a broad statistical claim about active learning. The unary policy comparisons had intervals including zero. Label uncertainty alone is insufficient when labels are already correct and the mechanism-to-effect mapping is wrong.

## Interpretation: what should RelaxEngine ask next?

Separate **label uncertainty** (what role does this feature play?) from **mechanism uncertainty** (how does this particular network implement that role?) and **model mismatch** (does our hypothesis family omit an interaction?). A useful investigator must be able to reject or revise its hypothesis family, not just increase confidence in its existing labels.

The next question should sometimes be: “Which observation would falsify our current interaction model?” A causal response that is inconsistent with every predicted role should trigger an explicit mismatch state or abstention. This study has identified the need for such a mechanism; it has **not implemented and validated that improvement**.

Further steps: repeat with other generators; add mechanisms that intentionally share or split roles; compare one-pass message passing and stronger nonlinear effect predictors; distinguish role prediction from direct quantitative circuit models; then test on instrumented trained networks with held-out intervention outcomes. No claim about Mythos can be made without evidence from Mythos or a carefully justified transfer argument.

## Reproducibility and limits

Eight implementation tests passed: causal-null decoy; actual downstream recomputation; zero-gain equivalence; exact-search reference; unit-permutation equivariance; reproducibility/access separation; query budget/target exclusion; fixed-target policy behavior. These check implementation properties, not the truth of the research hypothesis.

Independent-circuit paired bootstraps use 1,000 resamples. Intervals are conditional on this generator, not evidence of external validity. We did not correct exploratory contrasts for multiple comparisons and do not claim population-level significance outside the benchmark. Runtime in the raw records is shared across methods per circuit, not a method-specific speed benchmark.

The primary code's SHA-256 is `{r['source_sha256']}`. The executed environment was Python {r['environment']['python']}, NumPy {r['environment']['numpy']}, SciPy {r['environment']['scipy']}, scikit-learn {r['environment']['sklearn']}. No dependencies were downloaded for this execution.

## Files and sources

- `DESIGN.md`, `ACTIVE-DESIGN.md`: prospective primary and follow-up designs, with the exploratory endpoint explicitly dated relative to the disjoint smoke run.
- `experiment.py`, `active.py`: reproducible computational experiments.
- `test_experiment.py`, `test_active.py`: implementation tests.
- `results/results.json`, `results/records.json`, `active-results/results.json`, `active-results/records.json`: aggregates and per-circuit outcomes, including null/unfavorable results.
- `study-figure.svg`, `study-figure.png`, `study-figure.pdf`: standalone figures.
- [Circuit Tracing: Revealing Computational Graphs in Language Models](https://www.transformer-circuits.pub/2025/attribution-graphs/methods.html), 27 March 2025. Inspiration and methodological distinction; no claim of replication.
- Local foundations: the HRL portfolio's `hyperobject/relax_recursive_engine.py` and the separate relaxation-labeling repository's `python/grrle/engine.py`. Those programs are not executed by this benchmark.

AI assistance was used for design, code, analysis, and drafting. This is an initial public computational research note with reproducible artifacts, not a peer-reviewed paper or an independent audit of an AI vendor.
'''
(out/'REPORT.md').write_text(report)
# Saved replay examples: inference gets observations, then results are joined with truth for display only.
models=fit_models(sample(1000,120));unary,_,_,_,means,_,compat=models;examples=[]
for condition,novel in [('in_distribution',False),('graph_corruption',False),('novel_motif',True)]:
 for o,t in sample(20000,3,novel):
  o=corrupt(o,condition);p=unary.predict_proba(o.descriptors);support,_,_=relax(p,o.graph,compat,r['selected_gain']);pred=assignment(support)
  examples.append(dict(condition=condition,circuit_id=o.circuit_id,graph=o.graph.tolist(),roles=ROLES,
   predicted_labels=pred.tolist(),true_labels=t.labels.tolist(),predicted_effects=means[pred].tolist(),actual_effects=t.effects.tolist()))
(out/'examples.json').write_text(json.dumps(examples,indent=2))
print('Report, figures, and 9 saved replay examples written.')
