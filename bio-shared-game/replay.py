"""Offline aggregate camera-event decoder; no camera or animal control."""
import argparse,csv,json,math,random
from collections import defaultdict
from pathlib import Path

def decode(rows, confidence_min=.8):
    groups=defaultdict(list)
    for row in rows: groups[(row['trial'],row['party'])].append(row)
    decisions=[]
    for (trial,party),group in sorted(groups.items()):
        rates={};valid=True
        for r in group:
            c=r['candidate'];n=float(r['events']);s=float(r['visible_seconds']);q=float(r['confidence'])
            if c in rates or not all(map(math.isfinite,(n,s,q))) or n<0 or not n.is_integer() or s<=0 or not 0<=q<=1:
                raise ValueError('Invalid or duplicate observation')
            valid &= q>=confidence_min;rates[c]=n/s
        best=max(rates.values());winners=[c for c,v in rates.items() if math.isclose(v,best)]
        choice=winners[0] if valid and len(winners)==1 and best>0 and len(rates)>1 else None
        decisions.append(dict(trial=trial,party=party,choice=choice,rates=rates))
    return decisions

def evaluate(decisions,tasks,seed=7):
    rng=random.Random(seed);scores=[]
    for d in decisions:
        costs=tasks[d['trial']]
        if set(costs)!=set(d['rates']):raise ValueError('Candidate sets differ')
        if any(not math.isfinite(v) or v<0 for v in costs.values()):raise ValueError('Invalid cost')
        if d['choice'] is None:continue
        labels=list(costs);null=[]
        for _ in range(1000):
            shuffled=labels[:];rng.shuffle(shuffled)
            null.append(costs[shuffled[labels.index(d['choice'])]])
        scores.append(dict(trial=d['trial'],party=d['party'],decoded_cost=costs[d['choice']],
            random_expected_cost=sum(costs.values())/len(costs),
            shuffled_mapping_cost=sum(null)/len(null),exact_best_cost=min(costs.values())))
    keys=('decoded_cost','random_expected_cost','shuffled_mapping_cost','exact_best_cost')
    return dict(decision_count=len(decisions),scored_count=len(scores),
        coverage=len(scores)/len(decisions) if decisions else 0,
        means={k:sum(s[k] for s in scores)/len(scores) if scores else None for k in keys},scores=scores,
        interpretation='Offline association only. No causal benefit or animal intelligence established.')

def demo(out):
    out.mkdir(parents=True,exist_ok=True);rng=random.Random(19);rows=[];tasks={}
    for i in range(40):
        trial=f'synthetic-{i:03d}';costs={c:rng.randint(2,15) for c in 'ABC'};tasks[trial]=costs
        for c,cost in costs.items():
            # Deliberately inject the association; favorable results prove nothing biological.
            rows.append(dict(trial=trial,party='synthetic-ant-traffic',candidate=c,
                events=max(0,35-2*cost+rng.randint(-3,3)),visible_seconds=30,confidence=.95))
    with (out/'observations.csv').open('w',newline='') as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
    (out/'tasks.json').write_text(json.dumps(tasks,indent=2));result=evaluate(decode(rows),tasks)
    result['data_origin']='SYNTHETIC: generator explicitly assigns more traffic to cheaper routes'
    (out/'results.json').write_text(json.dumps(result,indent=2));return result

if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--demo',type=Path)
    p.add_argument('--observations',type=Path);p.add_argument('--tasks',type=Path)
    p.add_argument('--output',type=Path,default=Path('results.json'));a=p.parse_args()
    if a.demo:r=demo(a.demo)
    elif a.observations and a.tasks:
        with a.observations.open() as f:d=decode(list(csv.DictReader(f)))
        r=evaluate(d,json.loads(a.tasks.read_text()));a.output.write_text(json.dumps(r,indent=2))
    else:p.error('Use --demo DIR or --observations CSV --tasks JSON')
    print(json.dumps({k:v for k,v in r.items() if k!='scores'},indent=2))
