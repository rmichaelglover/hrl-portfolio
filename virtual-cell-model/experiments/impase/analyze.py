#!/usr/bin/env python3
"""Fit conditional IMPase assay models to traceable digitized primary measurements."""
import csv
import hashlib
import json
from pathlib import Path
import subprocess
import textwrap

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
import numpy as np
from scipy.optimize import least_squares

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
OUT = HERE / 'results'
OUT.mkdir(exist_ok=True)
RNG = np.random.default_rng(20261111)
MODELS = {
    'hill': (0, ['V', 'Ka', 'h'], [.08, .2, 1.8]),
    'hill_inhibition': (1, ['V', 'Ka', 'h', 'Kmg'], [.08, .2, 1.8, 5]),
    'single_site_inhibition': (2, ['V', 'Ka', 'Kmg'], [.08, .2, 5]),
    'competitive': (3, ['V', 'Km', 'Kis'], [.1, 1.7, 1]),
    'uncompetitive': (4, ['V', 'Km', 'Kii'], [.1, 1.7, .4]),
    'pure_noncompetitive': (5, ['V', 'Km', 'Ki'], [.1, 1.7, 1]),
    'mixed': (6, ['V', 'Km', 'Kis', 'Kii'], [.1, 1.7, 3, .4]),
}

def read_data():
    with (HERE / 'data/digitized.csv').open() as f:
        rows = list(csv.DictReader(f))
    for row in rows:
        for key in ['pixel_x', 'pixel_y', 'substrate_mm', 'magnesium_mm', 'lithium_mm', 'rate_abs_per_min']:
            row[key] = float(row[key])
    return rows

def predict(name, values, rows):
    p = dict(zip(MODELS[name][1], values))
    s = np.array([r['substrate_mm'] for r in rows])
    m = np.array([r['magnesium_mm'] for r in rows])
    li = np.array([r['lithium_mm'] for r in rows])
    if name in ['hill', 'hill_inhibition', 'single_site_inhibition']:
        h = p.get('h', 1)
        denominator = (p['Ka'] / m) ** h + 1
        if 'Kmg' in p:
            denominator += m / p['Kmg']
        return p['V'] / denominator
    alpha = np.ones(len(rows))
    alpha_prime = np.ones(len(rows))
    if name in ['competitive', 'mixed']:
        alpha += li / p['Kis']
    if name in ['uncompetitive', 'mixed']:
        alpha_prime += li / p['Kii']
    if name == 'pure_noncompetitive':
        alpha = alpha_prime = 1 + li / p['Ki']
    return p['V'] * s / (alpha * p['Km'] + alpha_prime * s)

def observed(rows, reciprocal):
    rates = np.array([r['rate_abs_per_min'] for r in rows])
    return 1 / rates if reciprocal else rates

def objective_prediction(name, p, rows, reciprocal):
    rates = predict(name, p, rows)
    return 1 / rates if reciprocal else rates

def fit(name, rows, reciprocal, starts=8, initial=None):
    keys = MODELS[name][1]
    seed = np.array(MODELS[name][2] if initial is None else initial)
    lower = np.array([1e-5 if k == 'V' else .05 if k == 'h' else .001 for k in keys])
    upper = np.array([10 if k == 'V' else 8 if k == 'h' else 1000 for k in keys])
    y = observed(rows, reciprocal)
    scale = 100 / 154 if reciprocal else .08 / 168.25
    best = None
    for i in range(starts):
        start = np.clip(seed * (np.exp(RNG.normal(0, .6, len(seed))) if i else 1), lower * 1.001, upper / 1.001)
        result = least_squares(lambda z: (objective_prediction(name, np.exp(z), rows, reciprocal)-y)/scale,
                               np.log(start), bounds=(np.log(lower), np.log(upper)),
                               max_nfev=2500, ftol=1e-10, xtol=1e-10, gtol=1e-10)
        if best is None or np.sum(result.fun**2) < np.sum(best.fun**2):
            best = result
    return best

def cpp_predictions(name, parameters, rows):
    p = dict(zip(MODELS[name][1], parameters))
    lines = []
    for row in rows:
        values = [MODELS[name][0], p['V'], p.get('Ka', p.get('Km')), p.get('h', 1),
                  p.get('Kmg', 1), p.get('Kis', p.get('Ki', 1)), p.get('Kii', 1),
                  row['substrate_mm'], row['magnesium_mm'], row['lithium_mm']]
        lines.append(','.join(map(str, values)))
    output = subprocess.check_output([str(ROOT / 'build/impase_assay')], input='\n'.join(lines)+'\n', text=True)
    return np.array([float(line) for line in output.splitlines()])

def perturb(rows):
    perturbed = []
    for row in rows:
        row = dict(row)
        x = row['pixel_x'] + RNG.uniform(-2, 2)
        y = row['pixel_y'] + RNG.uniform(-2, 2)
        if row['dataset'] == 'ins1p_magnesium':
            row['magnesium_mm'] = (x-495)*8/(724.5-495)
            row['rate_abs_per_min'] = (278.5-y)*.08/(278.5-110.25)
        else:
            row['substrate_mm'] = 1 / ((x-509.5)*2/(719.5-509.5))
            row['rate_abs_per_min'] = 1 / ((557.5-y)*100/(557.5-403.5))
        perturbed.append(row)
    return perturbed

def main():
    rows = read_data()
    report = {'status': 'Conditional bovine enzyme-assay calibration; no human behavioral inference',
              'seed': 20261111, 'data_sha256': hashlib.sha256((HERE/'data/digitized.csv').read_bytes()).hexdigest(),
              'coordinate_perturbation': '150 refits with independent uniform +/-2 pixel perturbations; 5th–95th percentiles are sensitivity ranges, not experimental confidence intervals',
              'datasets': {}}
    fits = {}
    for dataset, names in [('ins1p_magnesium', ['hill', 'hill_inhibition', 'single_site_inhibition']),
                           ('ribose_lithium', ['competitive', 'uncompetitive', 'pure_noncompetitive', 'mixed'])]:
        selected = [r for r in rows if r['dataset'] == dataset]
        train = [r for r in selected if r['split'] == 'train']
        test = [r for r in selected if r['split'] == 'test']
        reciprocal = dataset == 'ribose_lithium'
        entry = {'n_train': len(train), 'n_test': len(test),
                 'objective_units': 'reciprocal Delta A360/min' if reciprocal else 'Delta A360/min', 'models': {}}
        for name in names:
            optimum = fit(name, train, reciprocal)
            parameters = np.exp(optimum.x)
            pred_train = objective_prediction(name, parameters, train, reciprocal)
            residual = pred_train - observed(train, reciprocal)
            rss = float(residual @ residual)
            n = len(train)
            # Gaussian residual variance is estimated: count it as one parameter.
            k = len(parameters) + 1
            aic = n * np.log(rss/n) + 2*k
            aicc = aic + 2*k*(k+1)/(n-k-1) if n>k+1 else None
            test_residual = objective_prediction(name, parameters, test, reciprocal)-observed(test, reciprocal)
            singular = np.linalg.svd(optimum.jac, compute_uv=False)
            cpp = cpp_predictions(name, parameters, selected)
            np.testing.assert_allclose(cpp, predict(name, parameters, selected), rtol=2e-12, atol=1e-14)
            entry['models'][name] = {'parameters': dict(zip(MODELS[name][1], map(float, parameters))),
                'train_rmse': float(np.sqrt(rss/n)), 'test_rmse': float(np.sqrt(np.mean(test_residual**2))),
                'test_native_rate_rmse': float(np.sqrt(np.mean((predict(name,parameters,test)-observed(test,False))**2))),
                'test_native_rate_nrmse_mean': float(np.sqrt(np.mean((predict(name,parameters,test)-observed(test,False))**2))/np.mean(observed(test,False))),
                'aicc': None if aicc is None else float(aicc), 'log_parameter_jacobian_condition': float(singular[0]/singular[-1]),
                'cpp_python_max_error': float(np.max(np.abs(cpp-predict(name,parameters,selected)))),
                'optimizer_success': bool(optimum.success)}
            entry['models'][name]['parameters_at_optimization_bound'] = [
                key for key,active in zip(MODELS[name][1],optimum.active_mask) if active != 0]
            fits[name] = (parameters, optimum, selected, train, test, reciprocal)
        eligible = [name for name in names if entry['models'][name]['aicc'] is not None]
        best = min(eligible, key=lambda name: entry['models'][name]['aicc'])
        entry['selected_by_training_aicc'] = best
        p = fits[best][0]
        draws = []
        for _ in range(150):
            draws.append(np.exp(fit(best, perturb(train), reciprocal, starts=1, initial=p).x))
        draws = np.array(draws)
        entry['digitization_parameter_ranges'] = {
            key: list(map(float, np.quantile(draws[:,i],[.05,.5,.95])))
            for i,key in enumerate(MODELS[best][1])}
        entry['held_out_predictions'] = [dict(id=r['id'], substrate_mm=r['substrate_mm'],
            magnesium_mm=r['magnesium_mm'], lithium_mm=r['lithium_mm'],
            observed_rate=r['rate_abs_per_min'], predicted_rate=float(prediction))
            for r,prediction in zip(test,predict(best,p,test))]
        report['datasets'][dataset] = entry
        print(dataset, 'selected:', best, 'parameters:', entry['models'][best]['parameters'], flush=True)
    (OUT/'fit-results.json').write_text(json.dumps(report,indent=2,allow_nan=False)+'\n')
    create_figures(rows, fits, report)
    write_report(report)
    # Numerical data in CSV independently consumable without Python imports.
    with (OUT/'held-out-predictions.csv').open('w') as f:
        records = [dict(dataset=dataset,**row) for dataset,e in report['datasets'].items() for row in e['held_out_predictions']]
        writer=csv.DictWriter(f,fieldnames=records[0]);writer.writeheader();writer.writerows(records)
    print('All fitted C++ predictions agree with Python. Results:',OUT)

def create_figures(rows,fits,report):
    plt.rcParams.update({'font.size':10,'axes.spines.top':False,'axes.spines.right':False})
    fig,axes=plt.subplots(2,2,figsize=(11,8),layout='constrained')
    for col,dataset in enumerate(report['datasets']):
        entry=report['datasets'][dataset];best=entry['selected_by_training_aicc']
        p,optimum,selected,train,test,reciprocal=fits[best]
        ax=axes[0,col]
        if not reciprocal:
            grid=np.geomspace(.05,9,300)
            grid_rows=[dict(selected[0],magnesium_mm=x) for x in grid]
            for name in entry['models']:
                ax.plot(grid,predict(name,fits[name][0],grid_rows),label=name.replace('_',' '))
            for subset,marker,label in [(train,'o','Fit'),(test,'s','Held out')]:
                ax.scatter([r['magnesium_mm'] for r in subset],observed(subset,False),marker=marker,
                           facecolors='white' if marker=='s' else '#193b37',edgecolors='#193b37',s=45,label=label,zorder=5)
            ax.set(xlabel='Nominal magnesium (mM)',ylabel='Rate (Delta A360/min)',title='A  Ins1P: Mg activation and inhibition')
        else:
            for li,color in zip([0,.5,1,1.5],['#333333','#39847c','#456cad','#b75234']):
                subset=[r for r in selected if r['lithium_mm']==li]
                inverse=np.linspace(0,2,200)
                grid_rows=[dict(subset[0],substrate_mm=1/max(x,1e-8)) for x in inverse]
                ax.plot(inverse,1/predict(best,p,grid_rows),color=color,linestyle='--' if li==1.5 else '-')
                ax.scatter([1/r['substrate_mm'] for r in subset],observed(subset,True),color=color,
                           marker='s' if li==1.5 else 'o',label=f'Li {li:g} mM'+(' (held out)' if li==1.5 else ''),zorder=5)
            ax.set(xlabel='1 / ribose-5-phosphate (1/mM)',ylabel='1 / rate',title='B  Lithium: held-out inhibitor concentration')
        ax.legend(fontsize=7)
        residual_ax=axes[1,col]
        for subset,marker,label in [(train,'o','Fit'),(test,'s','Held out')]:
            predicted=predict(best,p,subset)
            residual_ax.scatter(observed(subset,False),predicted-observed(subset,False),marker=marker,label=label)
        residual_ax.axhline(0,color='gray',lw=1)
        residual_ax.set(xlabel='Observed rate (Delta A360/min)',ylabel='Predicted minus observed rate',title=f'{"C" if col==0 else "D"}  Native-rate residuals: {best.replace("_"," ")}')
        residual_ax.legend(fontsize=8)
    fig.suptitle('Measured enzyme kinetics: conditional calibration and held-out checks\nDigitized markers, not original replicate data',fontsize=14)
    save_figure(fig,'fig01-calibration')

    fig,axes=plt.subplots(2,2,figsize=(11,8),layout='constrained')
    for col,(dataset,entry) in enumerate(report['datasets'].items()):
        names=list(entry['models']);labels=[n.replace('_','\n') for n in names]
        aicc=np.array([entry['models'][n]['aicc'] for n in names])
        axes[0,col].bar(labels,aicc-aicc.min(),color='#397d73')
        axes[0,col].set(ylabel='Delta training AICc (lower is better)',title=f'{"A" if col==0 else "B"}  {dataset.replace("_"," ")}')
        axes[1,col].bar(labels,[entry['models'][n]['test_native_rate_rmse'] for n in names],color='#b65c39')
        axes[1,col].set(ylabel='Held-out RMSE (Delta A360/min)',title=f'{"C" if col==0 else "D"}  Held-out prediction')
    fig.suptitle('Competing kinetic descriptions\nSelection uses training data; test points are evaluated afterward',fontsize=14)
    save_figure(fig,'fig02-model-comparison')

    fig,axes=plt.subplots(1,2,figsize=(11,5),layout='constrained')
    for ax,(dataset,entry) in zip(axes,report['datasets'].items()):
        ranges=entry['digitization_parameter_ranges']; keys=list(ranges)
        values=np.array(list(ranges.values()))
        ax.errorbar(np.arange(len(keys)),values[:,1],yerr=[values[:,1]-values[:,0],values[:,2]-values[:,1]],fmt='o',capsize=5,color='#397d73')
        ax.set_yscale('log');ax.set_xticks(np.arange(len(keys)),keys)
        ax.set(ylabel='Parameter value (mixed units; logarithmic)',title=dataset.replace('_',' '))
        ax.grid(alpha=.15)
    fig.suptitle('Sensitivity to reading the figure\n150 refits with +/-2-pixel coordinate perturbations; 5th–95th percentiles',fontsize=13)
    save_figure(fig,'fig03-digitization-sensitivity')

    with PdfPages(OUT/'IMPASE_ASSAY_REPORT.pdf',metadata={'Title':'IMPase: evidence before behavior','Author':'Michael Emanuel Glover; analysis developed with assistant','CreationDate':None,'ModDate':None}) as pdf:
        page=plt.figure(figsize=(8.27,11.69))
        text='IMPase: evidence before behavior\n\nMichael Emanuel Glover / Virtual Cell research extension\n\n'
        text+='Thirty traceable figure markers from recombinant bovine enzyme assays support conditional rate-law comparison. Seven Mg points and fifteen lithium points are used for fitting; three Mg points and five points at a held-out lithium concentration are evaluated afterward.\n\n'
        for dataset,entry in report['datasets'].items():
            best=entry['selected_by_training_aicc'];m=entry['models'][best]
            text+=f'{dataset}: {best}\nHeld-out native-rate RMSE: {m["test_native_rate_rmse"]:.5g} Delta A360/min.\n\n'
        text+='These are within-figure retrospective checks, not an independent replication. Coordinate perturbations quantify digitization sensitivity, not experimental standard errors.\n\nThe assay enzyme is bovine, not human. Rates remain in their measured optical units. No fitted rate is converted into mood, neuronal firing or a universal physiological parameter.\n\nSource: Strasser, Pelton and Ganzhorn (1995), Biochemical Journal 307:585–593, doi:10.1042/bj3070585.\n\nRead REPORT.md for full methods, interpretation, parameter units, identifiability, source conditions, prediction tables and the next experiment.'
        wrapped='\n'.join(textwrap.fill(paragraph,78) if paragraph else '' for paragraph in text.split('\n'))
        page.text(.09,.94,wrapped,va='top',fontsize=11,linespacing=1.6)
        pdf.savefig(page);plt.close(page)
        # Figures already created remain open until this report is written.
        for number in plt.get_fignums():
            pdf.savefig(plt.figure(number))
        plt.close('all')

def save_figure(fig,name):
    fig.savefig(OUT/f'{name}.png',dpi=180)
    fig.savefig(OUT/f'{name}.pdf',metadata={'CreationDate':None,'ModDate':None})

def write_report(report):
    text='''# IMPase: evidence before behavior

Originating framework, project direction and biochemical research objective:
**Michael Emanuel Glover**. The assistant performed literature retrieval,
manual figure digitization, implementation, fitting and report preparation.

## The empirical step

We have moved from hypothetical parameters to a conditional, testable enzyme
assay analysis. Thirty published figure markers are reconstructed with explicit
pixel coordinates. They are not invented replicates. The program fits multiple
rate laws and evaluates measurements excluded from fitting. A C++ implementation
agrees numerically with every fitted Python rate prediction.

The first evidence is recombinant **bovine** IMPase, not a human patient or human
cell. Our result is an assay calibration with a local predictive check. It does
not yet establish a human physiological mechanism or treatment-response model.

## Source conditions and provenance

[Strasser, Pelton & Ganzhorn (1995)](https://pmc.ncbi.nlm.nih.gov/articles/PMC1136688/),
Biochemical Journal 307:585–593, doi:10.1042/bj3070585.
Figure 1 provides natural-substrate Mg rates; Figure 6a provides ribose/Li rates.
Assays: 37 °C, pH 7.5, 50 mM Tris/HCl and 0.1 mM EGTA; coupled A360 readout.
Figure 1: 0.5 mM Ins1P, 6 nM enzyme. Figure 6a: 3 mM nominal Mg, 87 nM enzyme.
Original rate replicates and their errors are unavailable here. Source-image
URLs and SHA-256 hashes, axis calibration, marker identities, and split labels
are retained in `data/`. Ambiguous overlapping low-Mg symbols are excluded.

The chosen digitization tolerance is ±2 pixels on both axes. It is an explicit
reading-error sensitivity, not an experimentally estimated noise model. Mg and
Li concentrations are nominal additions, not computed free-ion activities.
Optical rates remain Delta A360/min; no unreported path length is assumed.

## Competing equations

For magnesium M, compare:

```
Hill:              v = V / [(Ka/M)^h + 1]
Hill + inhibition: v = V / [(Ka/M)^h + 1 + M/Kmg]
Single-site:       v = V / [Ka/M + 1 + M/Kmg]
```

The last is the h=1 nested case. Ka is a conditional half-activation parameter,
not a proven microscopic dissociation constant. V is a fitted conditional scale.
The single-site label names the h=1 curve, not an established count of metal
ions bound to IMPase. The activation-only Hill fit hits its h=8 upper bound;
this does not repair its inability to turn downward at high Mg.

For substrate S and lithium L, use the general mixed rate law:

```
alpha = 1 + L/Kis
alpha_prime = 1 + L/Kii
v = V*S / [alpha*Km + alpha_prime*S]
```

Competitive fixes alpha_prime=1; uncompetitive fixes alpha=1; pure
noncompetitive constrains Kis=Kii; mixed allows them to differ. These are
phenomenological classes. An uncompetitive initial-rate pattern alone cannot
determine whether the microscopic lithium-bound state contains substrate or
product. No enzyme-state binding assignment is inferred from a curve fit.

Each dataset has its own scale and parameters. Ribose and Ins1P data are not
pooled as though the substrates were interchangeable. The natural-substrate
Mg experiment contains no lithium; the lithium fits concern ribose specifically.

## Fitting, selection and validation

Positive parameters are optimized in logarithmic coordinates with eight starts.
Training residuals use the actual digitized plot coordinate: rate for Figure 1,
reciprocal rate for Figure 6a. This treats an equal pixel error on its native
axis equally. It does not imply experimental rate errors were homoscedastic.
Reciprocal-space fitting is appropriate here for the reading-error question;
raw initial-rate measurements should instead use their experimental likelihood.

AICc counts kinetic parameters plus one estimated residual variance parameter.
The winner is selected on training AICc alone. Test RMSE is evaluated afterward,
with native-rate errors supplied for both datasets. Split labels were fixed
before numerical fitting, but after visually inspecting the published figures:
this is a retrospective within-figure validation, not prospective replication.
The withheld lithium series is 1.5 mM, extrapolating beyond training 0–1 mM.

'''
    for dataset,entry in report['datasets'].items():
        text+=f'## Results: {dataset}\n\n'
        text+=f'Training markers: {entry["n_train"]}; held-out markers: {entry["n_test"]}. Selected: **{entry["selected_by_training_aicc"]}**.\n\n'
        text+='| Model | Training AICc | Test RMSE in fit coordinate | Test rate RMSE |\n|---|---:|---:|---:|\n'
        for name,m in entry['models'].items():
            text+=f'| {name} | {m["aicc"]:.4f} | {m["test_rmse"]:.6g} | {m["test_native_rate_rmse"]:.6g} |\n'
        text+='\nRate RMSE units are Delta A360/min. AICc values compare models within this dataset only.\n\n'
        selected=entry['models'][entry['selected_by_training_aicc']]
        text+='| Parameter | Fit | Pixel sensitivity 5th–95th percentile |\n|---|---:|---:|\n'
        for key,value in selected['parameters'].items():
            low,median,high=entry['digitization_parameter_ranges'][key]
            text+=f'| {key} | {value:.6g} | {low:.6g}–{high:.6g} |\n'
        text+='\nV is Delta A360/min; concentration constants are mM; h is dimensionless. Sensitivity ranges are not confidence intervals.\n\n'
        text+=f'Log-parameter Jacobian condition number: {selected["log_parameter_jacobian_condition"]:.4g}. This local numerical diagnostic does not prove global or structural identifiability.\n\n'
        text+='| Held-out ID | Observed rate | Predicted rate |\n|---|---:|---:|\n'
        for r in entry['held_out_predictions']:
            text+=f'| {r["id"]} | {r["observed_rate"]:.6g} | {r["predicted_rate"]:.6g} |\n'
        text+='\n'
    text+='''## What the evidence changes

The natural-substrate dataset turns over at high magnesium, so a saturating
activation-only curve misses important structure. A Hill exponent is optional
complexity: retain it only if the available measurements support it. Sparse
low-Mg coverage limits what these selected markers can tell us about cooperativity.
The full source study reports cooperative activation. Our h=1 selection on just
seven training markers does not overturn that finding: the small-sample AICc
penalty is severe and ambiguous low-Mg markers were deliberately omitted. The
cooperative inhibitory fit has lower held-out error here. The evidence supports
activation plus inhibition more strongly than a unique activation exponent.
The ribose dataset tests whether both slope and intercept changes are needed;
its fitted lithium constants must not be transferred to Ins1P or humans.

The old synthetic model is preserved as a separate demonstration. Its constants
have not been silently replaced with bovine optical-assay constants. A complete
coupling needs enzyme abundance, free-ion speciation, assay-to-cell transfer,
product effects, compartmentation, and the actual substrate in question.

[Leech et al. (1993)](https://doi.org/10.1111/j.1432-1033.1993.tb17707.x)
reported product-associated lithium effects and substrate-dependent inhibition,
including a change at higher lithium. This motivates testing product-release
states rather than automatically interpreting uncompetitive kinetics as binding
only to an enzyme–substrate complex.

## Assumptions that still need testing

- Calibration is specific to preparation, buffer, temperature, pH and substrate.
- Apparent constants combine several processes; they are not atomistic energies.
- Small within-figure holdouts share experimental and digitization systematics.
- Pixel perturbations cannot recover missing biological replication or error bars.
- Model selection is conditional on this candidate family and its error objective.
- Two-metal activation, product retention, pH-dependent speciation, and transient
  bursts need experiments that distinguish them; more states are not automatically
  more identifiable.

## Next measurement to seek

The next empirical target is a natural-substrate lithium × magnesium × substrate
initial-rate matrix with matched enzyme preparation and known pH and temperature.
Add phosphate as an intervention, then a transient product-release time course.
Fit steady-state and transient observations jointly only when their conditions
are compatible. Hold out an entire concentration or experiment, report predictive
error and uncertainty, and test whether additional states improve prediction.

An informative design samples low and high substrate with and without lithium:
competitive and uncompetitive limits separate there. To identify Mg activation
and inhibition separately, include measurements below the rise, around the peak,
and beyond the fall. Independent human recombinant IMPA1 data are needed before
claiming species transfer. The existing Person architecture can later consume
validated cellular observables without equating an assay rate to a mental state.

## Reproduce and inspect

From the project root:

```sh
cmake -S . -B build
cmake --build build -j 2
ctest --test-dir build --output-on-failure
python3 experiments/impase/analyze.py
python3 -m unittest discover -s experiments/impase -p 'test_*.py' -v
```

Python analysis requires NumPy, SciPy and Matplotlib. `requirements.txt` records
versions used. The C++ library itself has no external runtime dependencies.
Files: `data/digitized.csv`, `data/provenance.json`, `results/fit-results.json`,
`results/held-out-predictions.csv`, three four-/two-panel figures in PDF/PNG,
and `results/IMPASE_ASSAY_REPORT.pdf`. The source article is linked, not bundled.
'''
    (HERE/'REPORT.md').write_text(text)

if __name__=='__main__':
    main()
