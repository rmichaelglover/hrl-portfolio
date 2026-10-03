"""Checks the benchmark's ground truth, parser, and paired experimental design."""
from pathlib import Path
import json
import numpy as np
import openpyxl
from experiment import workbook, evaluate, refs, extract, ROOT, SEED, ROWS

wb, labels=workbook(SEED,'semantic',False)
v=evaluate(wb)
for r in range(2,ROWS+2):
    assert np.isclose(v['Ledger',r,3],v['Ledger',r,1]*v['Ledger',r,2])
    assert np.isclose(v['Ledger',r,5],v['Ledger',r,3]+v['Ledger',r,4])
    assert np.isclose(v['Ledger',r,6],sum(v['Ledger',i,5] for i in range(2,r+1)))
assert np.isclose(v['Summary',1,2],sum(v['Ledger',r,5] for r in range(2,ROWS+2)))
assert len(refs('=SUM(Ledger!E2:E181)','Summary'))==ROWS
for i in range(12):
    standard, expected=workbook(SEED+100+i,'semantic',True)
    assert len(expected)==24
    for scenario in ['noisy','decorative','reversed']:
        alternate, labels=workbook(SEED+100+i,scenario,True)
        assert labels==expected
        assert [[c.value for c in row] for row in alternate['Ledger']]==[[c.value for c in row] for row in standard['Ledger']]
manifest=json.loads((ROOT/'results/manifest.json').read_text())
assert manifest['converged']
all_labels=json.loads((ROOT/'results/labels.json').read_text())
for scenario in ['semantic','noisy','decorative','reversed']:
    cells,edges=extract(ROOT/f'results/workbooks/{scenario}-00.xlsx',all_labels[f'{scenario}-00.xlsx'])
    assert len(cells)==1080 and sum(c['label'] for c in cells)==24
    assert edges>1000
print('PASS: arithmetic evaluator, range expansion, 24 distinct defect labels, paired formatting scenarios, XLSX round trip, fitted-model convergence.')
