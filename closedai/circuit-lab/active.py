"""Budgeted synthetic intervention questions; held-out forecast targets cannot be queried."""
import json
from pathlib import Path
import numpy as np
from scipy.special import softmax
from threadpoolctl import threadpool_limits
from experiment import sample,fit_models,relax,sinkhorn,assignment

class QueryOracle:
    def __init__(self,effects,allowed,budget=2):
        self._effects=effects;self.allowed=set(map(int,allowed));self.budget=budget;self.asked=set()
    def query(self,i):
        if i not in self.allowed:raise ValueError('Forecast target cannot be queried')
        if i in self.asked:raise ValueError('Repeated query')
        if len(self.asked)>=self.budget:raise ValueError('Query budget exhausted')
        self.asked.add(i);return float(self._effects[i])

def beliefs(unary,graph,compat,gain):
    if gain==0:return sinkhorn(np.log(np.clip(unary,1e-12,1)))
    return relax(unary,graph,compat,gain)[0]

def policy(unary,graph,compat,gain,means,std,eligible,targets,oracle,rng,strategy):
    logits=np.log(np.clip(unary,1e-12,1));queried=set();out=[]
    for budget in range(3):
        support=beliefs(softmax(logits,axis=1),graph,compat,gain)
        predicted=means[assignment(support)]
        out.append((budget,predicted[targets].copy()))
        if budget==2:break
        options=[int(i) for i in eligible if i not in queried]
        if strategy=='random':chosen=options[int(rng.integers(len(options)))]
        else:
            expected=support@means
            variance=(support@(means*means))-expected*expected
            chosen=max(options,key=lambda i:variance[i])
        measured=oracle.query(chosen);queried.add(chosen)
        logits[chosen]+=-.5*((measured-means)/std)**2-np.log(std)
    return out

def run(out):
    out.mkdir(exist_ok=True,parents=True)
    train=sample(1000,120);models=fit_models(train);unary,_,_,_,means,_,compat=models
    gain=json.loads(Path('results/results.json').read_text())['selected_gain']
    effectgroups=[np.concatenate([t.effects[t.labels==r] for o,t in train]) for r in range(6)]
    std=np.array([max(.03,x.std()) for x in effectgroups]);records=[]
    for condition,novel in [('familiar',False),('novel_motif',True)]:
        for o,t in sample(40000,100,novel):
            rng=np.random.default_rng(o.circuit_id+1234);order=rng.permutation(6);eligible=order[:3];targets=order[3:]
            priors=unary.predict_proba(o.descriptors)
            for method,weight in [('unary',0.),('relaxation',gain)]:
                for strategy in ('random','disagreement'):
                    oracle=QueryOracle(t.effects,eligible)
                    forecasts=policy(priors,o.graph,compat,weight,means,std,eligible,targets,oracle,np.random.default_rng(o.circuit_id+34343),strategy)
                    for budget,pred in forecasts:
                        records.append(dict(condition=condition,circuit_id=o.circuit_id,method=method,strategy=strategy,budget=budget,
                            target_mae=float(np.abs(pred-t.effects[targets]).mean())))
    result=dict(data_origin='SYNTHETIC FOLLOW-UP; NOT LLM INTERVIEWS',circuits_per_condition=100,query_units=3,forecast_targets=3,max_queries=2,
        selected_gain=gain,summaries={},paired_policy_contrasts=[])
    for condition in ('familiar','novel_motif'):
        result['summaries'][condition]={}
        for method in ('unary','relaxation'):
            for strategy in ('random','disagreement'):
                key=method+'_'+strategy
                result['summaries'][condition][key]={str(b):float(np.mean([r['target_mae'] for r in records if r['condition']==condition and r['method']==method and r['strategy']==strategy and r['budget']==b])) for b in range(3)}
            d=[]
            for circuit in range(40000,40100):
                bystrategy={r['strategy']:r['target_mae'] for r in records if r['condition']==condition and r['method']==method and r['circuit_id']==circuit and r['budget']==2}
                d.append(bystrategy['disagreement']-bystrategy['random'])
            d=np.array(d);rng=np.random.default_rng(65000);boot=d[rng.integers(0,100,(1000,100))].mean(1)
            result['paired_policy_contrasts'].append(dict(condition=condition,method=method,contrast='disagreement minus random; budget 2',mean=float(d.mean()),ci95=list(map(float,np.quantile(boot,[.025,.975])))))
    (out/'results.json').write_text(json.dumps(result,indent=2));(out/'records.json').write_text(json.dumps(records,indent=2));print(json.dumps(result,indent=2))
if __name__=='__main__':
    with threadpool_limits(limits=1):run(Path('active-results'))
