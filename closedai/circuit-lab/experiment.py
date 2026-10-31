"""Planted nonlinear circuits. Offline labels are NOT LLM motives or posterior probabilities."""
from __future__ import annotations
import argparse,dataclasses,itertools,json,time,hashlib,platform
import scipy,sklearn
from pathlib import Path
import numpy as np
from scipy.optimize import linear_sum_assignment
from scipy.special import expit,softmax
from sklearn.linear_model import LogisticRegression,Ridge
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler
from threadpoolctl import threadpool_limits

ROLES=['pressure relay','boundary relay','task drive','authorization gate','action mediator','decoy branch']
N=6
PERMS=np.array(list(itertools.permutations(range(N))))
@dataclasses.dataclass(frozen=True)
class Observation:
    descriptors: np.ndarray
    graph: np.ndarray  # target,source; entries -1,0,+1; no labels or interventions
    circuit_id: int
@dataclasses.dataclass(frozen=True)
class Truth:
    labels: np.ndarray
    effects: np.ndarray
    mean_effects: np.ndarray
    permitted_effects: np.ndarray
    blocked_effects: np.ndarray

class Circuit:
    def __init__(self,seed:int,novel=False):
        self.seed=seed;self.rng=np.random.default_rng(seed);r=self.rng
        self.W=np.zeros((N,N));self.b=r.normal(0,.25,N)
        self.input_weights=r.uniform(2.2,3.8,2)
        for target,source,base in [(2,0,2.7),(2,1,-1.8),(3,1,2.8),(3,0,-.8),(4,2,2.9),(4,3,-2.3),(5,0,1.7),(5,1,1.8)]:
            self.W[target,source]=base*r.uniform(.65,1.35)
        # Variation in an optional internal edge; roles do not become row indices.
        if r.random()<.3:self.W[3,0]=0
        if r.random()<.3:self.W[2,1]=0
        self.b+=np.array([-.3,-.3,-.4,-1.,-.5,-1.])
        self.sim_weight=r.uniform(.7,1.5)
        self.output=np.array([0.,0.,1.2,-2.,3.,0.])*r.uniform(.7,1.3,N)
        self.output_bias=r.normal(-1.,.25)
        if novel:
            self.W[3,2]=r.uniform(1.5,3.)
            self.W[4,0]=-r.uniform(1.2,2.8)
        self.permutation=r.permutation(N)

    def forward(self,x,patch=None):
        a=np.zeros((len(x),N))
        for i in range(N):
            if i==0:z=self.input_weights[0]*x[:,0]+self.b[i]
            elif i==1:z=self.input_weights[1]*x[:,1]+self.b[i]
            else:z=a@self.W[i]+self.b[i]+(self.sim_weight*x[:,2] if i==2 else 0)
            a[:,i]=expit(z)
            if patch and patch[0]==i:a[:,i]=patch[1]
        return a,expit(a@self.output+self.output_bias)

    def dataset(self,seed,n_obs=64,n_do=256):
        r=np.random.default_rng(seed);common=r.normal(.2,1,n_obs)
        x=np.column_stack([common+r.normal(0,.25,n_obs),common+r.normal(0,.25,n_obs),r.normal(0,1,n_obs)])
        a,y=self.forward(x)
        reference=np.column_stack([x,y]);features=[]
        for i in range(N):
            corrs=[np.corrcoef(a[:,i],reference[:,j])[0,1] for j in range(4)]
            features.append([a[:,i].mean(),a[:,i].std(),*np.quantile(a[:,i],[.1,.9]),*corrs])
        # Measurement noise is applied to descriptors, not the original circuit.
        f=np.array(features)+r.normal(0,.055,(N,8))
        x_do=r.uniform(-1.5,1.5,(n_do,3));_,base=self.forward(x_do)
        effects=[];mean_effects=[];permitted=[];blocked=[]
        for i in range(N):
            delta=self.forward(x_do,(i,0.))[1]-base
            effects.append(float(delta.mean()))
            permitted.append(float(delta[x_do[:,1]<0].mean()))
            blocked.append(float(delta[x_do[:,1]>=0].mean()))
            mean_effects.append(float((self.forward(x_do,(i,float(a[:,i].mean())))[1]-base).mean()))
        p=self.permutation
        return Observation(f[p],np.sign(self.W[np.ix_(p,p)]).astype(int),self.seed),Truth(p.copy(),np.array(effects)[p],np.array(mean_effects)[p],np.array(permitted)[p],np.array(blocked)[p])

def topology(o):
    g=o.graph
    return np.column_stack([(g>0).sum(1),(g<0).sum(1),(g>0).sum(0),(g<0).sum(0)]) / (N-1)

def assignment(p):
    rows,cols=linear_sum_assignment(-np.log(np.clip(p,1e-12,1.)))
    result=np.empty(N,int);result[rows]=cols;return result

def sinkhorn(logits):
    z=np.exp(logits-np.max(logits));z=np.clip(z,1e-15,None)
    for _ in range(35):
        z/=z.sum(1,keepdims=True);z/=z.sum(0,keepdims=True)
    return z/z.sum(1,keepdims=True)

def fit_compat(train):
    counts=np.ones((3,N,N))*.75
    for o,t in train:
        for i in range(N):
            for j in range(N):
                if i!=j:counts[o.graph[i,j]+1,t.labels[i],t.labels[j]]+=1
    return np.log(counts/counts.sum(0,keepdims=True))

def relax(unary,graph,compat,gain,max_steps=120):
    logits=np.log(np.clip(unary,1e-12,1));p=sinkhorn(logits)
    converged=False
    for iteration in range(max_steps):
        message=np.zeros_like(p)
        for i in range(N):
            for j in range(N):
                if i!=j:message[i]+=(compat[graph[i,j]+1]@p[j]+compat[graph[j,i]+1].T@p[j])/(N-1)
        proposal=sinkhorn(logits+gain*message)
        updated=.45*p+.55*proposal
        delta=np.max(np.abs(updated-p));p=updated
        if delta<1e-7:converged=True;break
    return p,iteration+1,converged

def exact_map(unary,graph,compat,gain):
    value=np.log(np.clip(unary,1e-12,1))[np.arange(N)[None,:],PERMS].sum(1)
    for i in range(N):
        for j in range(N):
            if i!=j:value+=gain*compat[graph[i,j]+1,PERMS[:,i],PERMS[:,j]]/(N-1)
    return PERMS[value.argmax()].copy()

def fit_models(train):
    x=np.concatenate([o.descriptors for o,t in train]);xt=np.concatenate([np.column_stack([o.descriptors,topology(o)]) for o,t in train])
    y=np.concatenate([t.labels for o,t in train]);effects=np.concatenate([t.effects for o,t in train]);mean_effects=np.concatenate([t.mean_effects for o,t in train])
    unary=make_pipeline(StandardScaler(),LogisticRegression(C=.5,max_iter=1000)).fit(x,y)
    augmented=make_pipeline(StandardScaler(),LogisticRegression(C=.5,max_iter=1000)).fit(xt,y)
    regression=make_pipeline(StandardScaler(),Ridge(alpha=10.)).fit(xt,effects)
    mean_regression=make_pipeline(StandardScaler(),Ridge(alpha=10.)).fit(xt,mean_effects)
    templates=np.array([effects[y==role].mean() for role in range(N)])
    mean_templates=np.array([mean_effects[y==role].mean() for role in range(N)])
    return unary,augmented,regression,mean_regression,templates,mean_templates,fit_compat(train)

def tune(models,validation):
    unary,_,_,_,templates,_,compat=models;grid=[0.,.25,.5,1.,2.,4.,8.];scores={}
    for gain in grid:
        errors=[]
        for o,t in validation:
            p=unary.predict_proba(o.descriptors);support,_,_=relax(p,o.graph,compat,gain)
            # Final prediction uses hard one-to-one labels for every labeling method.
            predicted=templates[assignment(support)]
            errors.append(np.abs(predicted-t.effects).mean())
        scores[str(gain)]=float(np.mean(errors))
    best=min(grid,key=lambda g:scores[str(g)])
    return best,scores

def corrupt(o,condition):
    r=np.random.default_rng(o.circuit_id+777777)
    if condition=='descriptor_noise':return dataclasses.replace(o,descriptors=o.descriptors+r.normal(0,.12,o.descriptors.shape))
    if condition=='graph_corruption':
        g=o.graph.copy()
        mask=(r.random((N,N))<.3)&(~np.eye(N,dtype=bool))
        g[mask]=r.integers(-1,2,mask.sum())
        return dataclasses.replace(o,graph=g)
    return o

def evaluate(models,gain,dataset,condition):
    unary,aug,reg,mean_reg,templates,mean_templates,compat=models;records=[]
    for original,t in dataset:
        o=corrupt(original,condition);start=time.perf_counter();p=unary.predict_proba(o.descriptors)
        topo=aug.predict_proba(np.column_stack([o.descriptors,topology(o)]))
        rel,steps,converged=relax(p,o.graph,compat,gain)
        r=np.random.default_rng(o.circuit_id+88888);perm=r.permutation(N)
        broken,_,_=relax(p,o.graph[np.ix_(perm,perm)],compat,gain)
        methods={'unary':assignment(p),'topology_classifier':assignment(topo),'relaxation':assignment(rel),
                 'shuffled_graph':assignment(broken),'exact_graph_map':exact_map(p,o.graph,compat,gain),
                 'zero_gain':assignment(relax(p,o.graph,compat,0)[0])}
        elapsed=time.perf_counter()-start
        for name,labels in methods.items():
            pred=templates[labels];mean_pred=mean_templates[labels]
            records.append(metric(name,o,t,pred,mean_pred,float(np.mean(labels==t.labels)),converged if name=='relaxation' else None,steps if name=='relaxation' else None,elapsed))
        xt=np.column_stack([o.descriptors,topology(o)])
        records.append(metric('direct_effect_ridge',o,t,reg.predict(xt),mean_reg.predict(xt),None,None,None,elapsed))
        # Expected uniform intervention prediction does not get arbitrary label indices.
        pred=np.repeat(templates.mean(),N);mp=np.repeat(mean_templates.mean(),N)
        records.append(metric('uniform',o,t,pred,mp,1/N,None,None,elapsed))
    return records

def metric(name,o,t,pred,mean_pred,accuracy,converged,steps,elapsed):
    chosen=int(np.argmin(pred))
    return dict(method=name,circuit_id=o.circuit_id,label_accuracy=accuracy,
        effect_mae=float(np.abs(pred-t.effects).mean()),mean_replacement_mae=float(np.abs(mean_pred-t.mean_effects).mean()),
        intervention_regret=float(t.effects[chosen]-np.min(t.effects)),
        effect_sign_accuracy=float(np.mean(np.sign(pred)==np.sign(t.effects))),
        chosen_permitted_change=float(t.permitted_effects[chosen]),chosen_blocked_change=float(t.blocked_effects[chosen]),
        converged=converged,steps=steps,shared_inference_seconds=elapsed)

def summarize(records):
    out={}
    for method in sorted({r['method'] for r in records}):
        rows=[r for r in records if r['method']==method];out[method]={}
        for key in ('label_accuracy','effect_mae','mean_replacement_mae','intervention_regret','effect_sign_accuracy','chosen_permitted_change','chosen_blocked_change','steps','converged'):
            values=[r[key] for r in rows if r[key] is not None]
            out[method][key]=float(np.mean(values)) if values else None
        out[method]['n_circuits']=len(rows)
    return out

def paired_ci(records,a,b,key='effect_mae',seed=65000):
    maps={name:{r['circuit_id']:r[key] for r in records if r['method']==name} for name in (a,b)}
    ids=sorted(set(maps[a])&set(maps[b]));d=np.array([maps[a][i]-maps[b][i] for i in ids]);rng=np.random.default_rng(seed)
    means=d[rng.integers(0,len(d),(1000,len(d)))].mean(1)
    return dict(contrast=a+' minus '+b,metric=key,mean=float(d.mean()),ci95=list(map(float,np.quantile(means,[.025,.975]))),n_independent_circuits=len(ids))

def sample(start,n,novel=False):return [Circuit(seed,novel).dataset(seed+900000) for seed in range(start,start+n)]

def run(out,smoke=False):
    out.mkdir(parents=True,exist_ok=True);clock=time.perf_counter()
    counts=(20,8,12) if smoke else (120,50,100)
    offset=300000 if smoke else 0
    train=sample(offset+1000,counts[0]);val=sample(offset+10000,counts[1]);test=sample(offset+20000,counts[2]);novel=sample(offset+20000,counts[2],True)
    models=fit_models(train);gain,val_scores=tune(models,val)
    summaries={};all_records={};contrasts={}
    for condition,data in [('in_distribution',test),('descriptor_noise',test),('graph_corruption',test),('novel_motif',novel)]:
        records=evaluate(models,gain,data,condition);all_records[condition]=records;summaries[condition]=summarize(records)
        contrasts[condition]=[paired_ci(records,'relaxation',baseline) for baseline in ('unary','topology_classifier','direct_effect_ridge','shuffled_graph')]
    result=dict(experiment='planted-nonlinear-circuit-labeling-001',data_origin='SYNTHETIC PLANTED CIRCUITS; NOT MYTHOS OR AN LLM',smoke=smoke,
        source_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        environment=dict(python=platform.python_version(),numpy=np.__version__,scipy=scipy.__version__,sklearn=sklearn.__version__),
        counts=dict(train=counts[0],validation=counts[1],test_per_condition=counts[2]),selected_gain=gain,validation_mae_by_gain=val_scores,
        primary_endpoint='Circuit-mean absolute error of zero-ablation output-probability change; lower is better',
        summaries=summaries,paired_bootstrap=contrasts,wall_seconds=time.perf_counter()-clock,
        interpretation='Support scores are not calibrated probabilities. Generator-level results do not establish LLM validity or training causes.')
    (out/'results.json').write_text(json.dumps(result,indent=2));(out/'records.json').write_text(json.dumps(all_records,indent=2))
    print(json.dumps({k:v for k,v in result.items() if k not in ('summaries','paired_bootstrap')},indent=2))
    for condition,summary in summaries.items():
        print(condition,{m:round(v['effect_mae'],5) for m,v in summary.items()})
    return result

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--out',type=Path,default=Path('results'));p.add_argument('--smoke',action='store_true');a=p.parse_args()
    with threadpool_limits(limits=1):run(a.out,a.smoke)
