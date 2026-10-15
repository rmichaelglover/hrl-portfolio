#!/usr/bin/env python3
"""Build Markdown and a standalone PDF from the measured JSON artifact."""
from pathlib import Path
import html
import json
import re
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image, Table, TableStyle, Preformatted, KeepTogether
ROOT=Path(__file__).resolve().parent
D=json.loads((ROOT/'data/results.json').read_text())
def pct(x):return 'undefined' if x is None else f'{100*x:.2f}%'
def row(s,m):return next(r for r in D['results'] if r['scenario']==s and r['method']==m)
clean=[row('Independent views',m) for m in D['methods']]
rec=row('Independent views','Reciprocal');fwd=row('Independent views','Forward');bad=row('Shared wrong dictionary','Reciprocal')
table='\n'.join('| '+ ' | '.join([r['method'],pct(r['accuracy']),pct(r['coverage']),f"{r['correct']}/{r['accepted']}",f"{pct(r['accuracy_ci95'][0])}–{pct(r['accuracy_ci95'][1])}"])+ ' |' for r in clean)
stress='\n'.join('| '+' | '.join([s,pct(row(s,'Reciprocal')['accuracy']),pct(row(s,'Reciprocal')['coverage']),str(row(s,'Reciprocal')['accepted'])])+' |' for s in D['scenarios'][1:])
text=f'''# Reciprocal Grounding
## Things as objects, words as objects, agreement as provisional ground truth

R. Michael Glover · HRL Portfolio · October 15, 2026 · Research prototype v1

### Abstract

We implement a proposal in which things receive word labels in one experiment, while words receive thing labels in another. Independently supplied evidence is relaxed in each direction. Mutual unique winners, two directional strength thresholds, margins, and perturbation stability define a conservative acceptance rule. Accepted pairs are candidates for provisional ground truth, subject to a separate audit and revocation. On a synthetic instance-matching benchmark with unknown distractors, reciprocal acceptance achieves {pct(rec['accuracy'])} accuracy at {pct(rec['coverage'])} coverage on held-out independent-view seeds. Forward-only acceptance achieves {pct(fwd['accuracy'])} at {pct(fwd['coverage'])}. These are different operating points, not a controlled claim of superiority. A shared wrong dictionary produces {bad['correct']} correct pairs among {bad['accepted']} reciprocal accepts. A copied-reverse baseline also performs strongly, demonstrating that mutual uniqueness can filter errors without adding independent evidence. Results support further testing of reciprocal selection, not a general truth-discovery guarantee or a novelty claim.

### 1. Proposal and scope

The motivating proposal is to exchange the roles of objects and labels: names classify things, then things classify names. Where differently informed experiments agree, promote the relationship to a revisable anchor. This report operationalizes a narrow version: unique word identifiers and distinct thing instances with a one-to-one hidden correspondence, plus unmatched things. It does not resolve natural-language meaning, synonyms, polysemy, or many instances sharing a class name. Those require a broader relation model.

Ground truth in this experiment is the simulator's hidden generating assignment. Provisional ground truth in the proposed workflow is a stored, evidence-backed working assignment. Neither internal coherence nor the score alone is treated as external truth.

### 2. Two separate relaxation problems

Let F have shape n by (m+1), assigning words to things; let R have shape m by (n+1), assigning things to words. Each final column represents unknown. Each direction receives its own logits L, an object relation graph A, and a label relation graph B. Both graphs are nonnegative, have zero diagonals, and are row-normalized; isolated rows remain zero. Starting at softmax(L), use the damped update:

```text
S = A @ P_real @ transpose(B)
P_next = (1-d) P + d softmax(L + g [S, 0])
```

Here d=0.5 and g=2.0. The fixed prior logits are respected at every update; the unknown label receives no graph reinforcement. Stop at maximum absolute change below 1e-7 or 80 iterations. This is a graph-factorized relaxation variant, separate from the existing four-index HRL engine. It is not asserted to reproduce that engine's update. Nonnegative finite strengths and row normalization are enforced. Convergence on these runs is reported, not proved for arbitrary graphs.

### 3. Reciprocal acceptance and audit

For a proposed pair (i,j), define the geometric-mean score:

```text
agreement(i,j) = sqrt(F[i,j] * R[j,i])
```

Accept only if j is thing i's unique strongest label, i is word j's unique strongest label, neither winner is unknown, both strengths meet threshold tau, both winning margins exceed 0.06 including the unknown competitor, and the same mutual winners survive three logit perturbation runs. Scores rank candidates; the threshold gates each direction separately. The score is not a calibrated probability. No Bayesian independence claim follows from multiplying strengths.

Perturbations add Gaussian noise of standard deviation 0.12 to the original logits, keep the relation graphs fixed, and rerun relaxation. This tests small numerical/evidence perturbations, not independent observations or resistance to all distribution shifts. The unrelaxed ablation uses the same perturbation draws.

The audit API accepts a separate verifier and emits candidate, rejected, or revoked provenance records. The representative example uses the simulator's hidden labels as an oracle solely to demonstrate this interface. That oracle is not available to a real grounding system and is not used for fitting or selection. The anchor_logits helper can add a bounded logit bonus to audited pairs in both directions, starting each round from fresh base evidence. Revoking a pair removes its bonus on the next fresh rebuild; conflicting one-to-one anchors are rejected. Sharing anchors couples the views, so subsequent agreement is not fresh independent confirmation. This release does not feed pseudo-labels back automatically, benchmark multiple anchor-growth rounds, or guarantee an independent real-world verifier.

Mutual unique winners imply that no two accepted things share one word, and no accepted thing has two words. This is an acceptance restriction, not a learned general semantic principle. A stable, confident wrong permutation satisfies every reciprocal test: agreement cannot by itself establish correctness.

### 4. Benchmark protocol

Each seed generates 16 latent word prototypes in five dimensions, with coordinates drawn from a zero-mean normal distribution of standard deviation 1.4. Sixteen things are a hidden permutation of those prototypes; four unmatched things come from a distant normal distribution with mean 6 and standard deviation 1. Observations of each thing receive Gaussian noise of standard deviation 0.65; word prototypes receive noise of standard deviation 0.25. Label logits are negative squared Euclidean distance divided by twice 0.65 squared. Unknown has fixed logit -4. Relation weights are exp(-squared-distance/10).

The synthetic dimensions are feature channels, not real words or measured objects. Separate view noise is drawn independently conditional on the shared latent construction. This does not establish independence of final errors, since the underlying instance identities and geometry are shared.

Four conditions are fixed in advance of this report: independent views; thing-observation noise correlated at 0.95; both word dictionaries cyclically shifted by the same incorrect permutation; and an uninformative reverse view drawn independently of the true matching. The copied-reverse ablation transposes the forward real-label strengths, appends null weight 0.03, and row-normalizes. It contributes no independent evidence. All methods retain unknown handling, margin tests, and matched logit-perturbation stability where applicable.

Seeds 0–19, only in the independent-view condition, select each method's threshold separately on a grid from 0.20 through 1.00 in steps of 0.025. Choose maximum validation coverage subject to empirical accepted accuracy at least 95% and at least 10 accepts; otherwise use threshold 1. This validation target is not a finite-sample risk guarantee. Freeze thresholds and evaluate seeds 100–139 in each condition. Per condition there are 800 things, including 160 unmatched distractors. Confidence intervals resample 40 whole seeds with replacement 1,000 times, preserving within-seed dependence; they are percentile intervals, not guarantees. Run-level counts are published as CSV.

### 5. Measured results

Independent views, frozen validation-selected thresholds:

| Method | Accepted accuracy | Coverage | Correct / accepted | Accuracy 95% interval |
| --- | --- | --- | --- | --- |
{table}

![Accuracy and coverage with seed-bootstrap intervals](figures/accuracy-coverage.png)

The reciprocal rule rejects more items than the forward baseline while making fewer errors among those accepted. Its accuracy interval overlaps other strong methods. The copied-reverse baseline has both a strong accuracy and larger coverage here; it cannot be interpreted as independent confirmation. The small difference between reciprocal selection with and without relaxation does not establish a general benefit from the graph update. No parameter sweep or external benchmark validates that benefit.

For a coverage-sensitive comparison, the published risk–coverage curves rank eligible pairs by each method's score and plot observed error versus accepted fraction. Curves end at the available candidate count; no missing coverage is fabricated. These pooled descriptive curves are not calibrated operating policies and have no simultaneous confidence bands. Comparing only the chosen threshold operating points would confound accuracy with abstention.

Reciprocal stress results under the same frozen threshold:

| Condition | Accepted accuracy | Coverage | Accepted |
| --- | --- | --- | --- |
{stress}

![Risk versus coverage under four conditions](figures/risk-coverage.png)

The shared wrong dictionary is the central counterexample: both directions can confidently agree on the wrong meanings. Correlated noise reduces the protection provided by distinct views. An uninformative reverse view leaves very few accepts, so the accuracy estimate there is based on only a small sample. This is a loss of useful coverage, not successful broad grounding. Unknown acceptance counts are included in the JSON and CSV; correct abstention is not counted as a correct accepted correspondence.

![Prior, relaxed forward, and reciprocal strength fields](figures/strength-fields.png)

The representative matrices show seed 100. Their unknown columns are omitted from the figure but retained in every decision and in the downloadable state. All {D['base_nonconverged']} base-view nonconvergences are counted across the 320 held-out directional fits; zero here does not imply a general convergence theorem. Perturbation convergence is not included in that count.

### 6. Why agreement can help, and why it can fail

In an idealized categorical thought experiment, suppose two predictors each choose one of m labels. They are correct with probabilities a and b, their correctness events are independent, and each wrong prediction is uniform over the other m-1 labels and independent of the other predictor. Then:

```text
Pr(correct | agreement) = a*b / (a*b + (1-a)*(1-b)/(m-1))
Pr(agreement) = a*b + (1-a)*(1-b)/(m-1)
```

This follows by separating agreement into both-correct and same-wrong-label events. It is an explanatory special case, not a theorem about the implemented reverse mapping or its scores. Shared wrong-label preferences violate its assumptions. Two identical predictors obtain no independent corroboration by agreeing. Our shared-dictionary experiment makes the failure concrete.

### 7. Reproducibility and limitations

Run the experiment, plots, and report builders from the repository root. JSON stores parameters, seed ranges, thresholds, raw strengths for one example, base convergence diagnostics, environment versions, and SHA256 hashes of the engine and experiment script. CSV contains all 800 held-out seed/method/condition count rows. Reproducing on a different numerical runtime may change last-bit values and threshold-boundary outcomes. No claim of measurement outside the synthetic generator is made.

Limitations include a small synthetic benchmark, a strong unique-instance matching assumption, fixed dimensionality and noise scales, a coarse threshold grid, no external semantic dataset, no independent real-world verifier, no learning of relation graphs, no proof of convergence or calibrated confidence, and no multi-round anchor-feedback benchmark. Computational cost is increased by fitting two views and three perturbations of each. Dense graph products scale roughly as O(n^2*m+n*m^2) per update, with O(n^2+m^2+n*m) storage per direction; sparse graphs are future work. The separate four-index engine is not allocated here.

### 8. Relationship to prior work and next experiments

Relaxation labeling has a long history in context-dependent assignment, including Hummel and Zucker's foundational analysis [1]. Co-training uses distinct views and pseudo-label exchange [2]. Selective classification explicitly studies the trade-off between accepted prediction risk and coverage [3]. This prototype combines reciprocal role reversal, graph relaxation, abstention, perturbation checks, and an audit interface in the HRL portfolio. We do not claim those ingredients, the geometric mean, or the broad concept of two-view agreement are new. A systematic novelty assessment remains open.

Next experiments should use real referring expressions and physical observations; compare against mutual-nearest-neighbor matching and stronger assignment baselines; vary error correlation, object counts, graph quality and unknown rates; evaluate many-to-many relations; and run bounded anchor growth with genuinely separate evidence. Keep test labels hidden until final evaluation, measure both accepted error and coverage, and publish failures alongside gains.

### References

[1] R. Hummel and S. Zucker. On the Foundations of Relaxation Labeling Processes. IEEE TPAMI, 1983. https://doi.org/10.1109/TPAMI.1983.4767390

[2] A. Blum and T. Mitchell. Combining Labeled and Unlabeled Data with Co-Training. COLT, 1998. https://publications.ri.cmu.edu/combining-labeled-and-unlabeled-data-with-co-training

[3] Y. Geifman and R. El-Yaniv. Selective Classification for Deep Neural Networks. NeurIPS, 2017. https://papers.neurips.cc/paper_files/paper/2017/hash/4a8423d5e91fda00bb7e46540e2b0cf1-Abstract.html
'''
(ROOT/'WHITEPAPER.md').write_text(text)
styles=getSampleStyleSheet();styles['BodyText'].fontSize=9;styles['BodyText'].leading=13;styles['BodyText'].spaceAfter=8
styles['Code'].fontSize=8;styles['Code'].leading=11;styles['Title'].fontSize=25;styles['Heading2'].spaceBefore=15
story=[];lines=text.splitlines();i=0
while i<len(lines):
    line=lines[i]
    if not line.strip():i+=1;continue
    if line.startswith('```'):
        block=[];i+=1
        while i<len(lines) and not lines[i].startswith('```'):block.append(lines[i]);i+=1
        story.append(Preformatted('\n'.join(block),styles['Code']));story.append(Spacer(1,8));i+=1;continue
    if line.startswith('!['):
        name=re.search(r'\((.*?)\)',line).group(1);image=Image(str(ROOT/name));ratio=min(470/image.imageWidth,350/image.imageHeight);image.drawWidth=image.imageWidth*ratio;image.drawHeight=image.imageHeight*ratio;story.append(image);story.append(Spacer(1,10));i+=1;continue
    if line.startswith('|'):
        rows=[]
        while i<len(lines) and lines[i].startswith('|'):
            cells=[v.strip() for v in lines[i].strip('|').split('|')]
            if not all(re.fullmatch(r'[-: ]+',v) for v in cells):rows.append([Paragraph(html.escape(v),styles['BodyText']) for v in cells])
            i+=1
        widths=[100,75,60,75,160] if len(rows[0])==5 else [235,85,75,75]
        t=Table(rows,colWidths=widths,repeatRows=1,hAlign='LEFT');t.setStyle(TableStyle([('BACKGROUND',(0,0),(-1,0),colors.HexColor('#e0eae7')),('VALIGN',(0,0),(-1,-1),'TOP'),('GRID',(0,0),(-1,-1),.3,colors.HexColor('#bacac5')),('LEFTPADDING',(0,0),(-1,-1),5)]));story.append(t);story.append(Spacer(1,12));continue
    if line.startswith('# '):story.append(Paragraph(html.escape(line[2:]),styles['Title']))
    elif line.startswith('## '):story.append(Paragraph(html.escape(line[3:]),styles['Heading2']))
    elif line.startswith('### '):story.append(Paragraph(html.escape(line[4:]),styles['Heading2']))
    else:story.append(Paragraph(html.escape(line),styles['BodyText']))
    i+=1

def footer(canvas,doc):
    canvas.saveState();canvas.setFont('Helvetica',8);canvas.setFillColor(colors.HexColor('#51625b'));canvas.drawString(44,28,'Reciprocal Grounding | HRL Portfolio | Synthetic benchmark');canvas.drawRightString(568,28,str(doc.page));canvas.restoreState()
SimpleDocTemplate(str(ROOT/'WHITEPAPER.pdf'),pagesize=(612,792),rightMargin=44,leftMargin=44,topMargin=40,bottomMargin=45,title='Reciprocal Grounding',author='R. Michael Glover').build(story,onFirstPage=footer,onLaterPages=footer)
print('Built WHITEPAPER.md and WHITEPAPER.pdf from measured results.')
