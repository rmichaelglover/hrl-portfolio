"""Check evidence counts and mathematical identities used in manuscript claims."""
from pathlib import Path
import csv,json,math
P=Path(__file__).resolve().parents[1]
def rows(name):return list(csv.DictReader((P/'data'/name).open()))
r=rows('compatibility.csv');assert len(r)==800
by={(int(x['seed']),x['condition']):x for x in r}
for seed in range(200):
 a=by[seed,'valid'];b=by[seed,'shared_wrong']
 assert abs(float(a['accuracy'])+float(b['accuracy'])-1)<1e-12
 assert abs(float(a['entropy'])-float(b['entropy']))<1e-12
 assert a['iterations']==b['iterations']
 assert all(by[seed,k]['converged']=='1' for k in ['prior','valid','shuffled','shared_wrong'])
assert len(rows('convergence.csv'))==400
policies=rows('policies.csv');assert len(policies)==5151
for row in policies:
 m=int(row['resources']);selection=int(row['selection'])
 if m<25:assert selection==0
 if m>25:assert selection==1
 assert selection in [0,1]
assert len(rows('forecasts.csv'))==20000
for row in rows('summaries.csv'):
 b=int(row['branches']);assert int(row['computed_observations'])==b+1
 assert abs(float(row['mean_health'])-(2*b+8)/(b+1))<1e-12
assert all(int(r['failures'])==0 for r in rows('invariants.csv'))
assert len(rows('oscillation.csv'))==120
stats=json.loads((P/'data'/'statistics.json').read_text())
assert stats['paired']['valid']['ci95'][0]>0
assert stats['paired']['shuffled']['ci95'][1]<0
print('Evidence audit passed: counts, symmetry, policy boundary, summaries, ledgers, intervals.')
