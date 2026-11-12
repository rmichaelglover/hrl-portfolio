"""Receptor sensing and delayed regulation: explicit synthetic mechanisms."""
from pathlib import Path
import csv,json
import numpy as np
HERE=Path(__file__).resolve().parent
DT=.1
DELAY=10
N=200
KON=1.0
KOFF=1.0

def environment(seed,regime,steps=2400):
    rng=np.random.default_rng(seed)
    if regime=='smooth':
        noise=np.zeros(steps)
        for i in range(1,steps):noise[i]=.98*noise[i-1]+rng.normal(0,.015)
        return np.exp(.65*np.sin(np.arange(steps)*DT*2*np.pi/18)+noise)
    if regime=='independent':return np.exp(rng.normal(0,.5,steps))
    raise ValueError(regime)

def receptor_trace(c,seed):
    rng=np.random.default_rng(seed);bound=N//2;observed=[]
    for concentration in c:
        rate=KON*concentration+KOFF
        equilibrium=KON*concentration/rate
        transition=-np.expm1(-rate*DT)
        # Exact two-state transition probabilities for fixed concentration per bin.
        arrivals=rng.binomial(N-bound,equilibrium*transition)
        departures=rng.binomial(bound,(1-equilibrium)*transition)
        bound+=arrivals-departures
        observed.append(bound)
    return np.asarray(observed)

def run(c,counts,method):
    c=np.asarray(c,dtype=float);counts=np.asarray(counts)
    if method not in ('memoryless','filtered','predictive'):
        raise ValueError('Unknown controller')
    if c.shape!=counts.shape or len(c)<=210 or not np.all(np.isfinite(c)) or np.any(c<=0):
        raise ValueError('Invalid concentration trajectory')
    if not np.all(np.isfinite(counts)) or np.any(counts<0) or np.any(counts>N) or np.any(counts!=np.floor(counts)):
        raise ValueError('Invalid receptor counts')
    # Jeffreys smoothing avoids an infinite inverse occupancy estimate.
    p=(counts+.5)/(N+1);sensed=(KOFF/KON)*p/(1-p)
    filtered=np.log(sensed[0]);previous=filtered;x=1.;queue=[1.]*DELAY
    records=[]
    for i,current in enumerate(sensed):
        if method=='memoryless':prediction=current
        else:
            previous=filtered
            filtered+=(-np.expm1(-DT/1.0))*(np.log(current)-filtered)
            velocity=np.clip((filtered-previous)/DT,-.5,.5)
            prediction=np.exp(filtered+(DELAY*DT*velocity if method=='predictive' else 0))
        prediction=float(np.clip(prediction,.15,6))
        command=float(np.clip((1+.8*(1-x))/prediction,.1,6))
        applied=queue.pop(0);queue.append(command)
        # Internal amount in fmol, influx in fmol/s, efflux coefficient 1/s.
        influx=applied*c[i];old=x;x=x*np.exp(-DT)+influx*(-np.expm1(-DT))
        # Assumed one ATP hydrolysis per admitted molecule; fmol ATP ledger.
        atp=influx*DT
        future=float(c[i+DELAY]) if i+DELAY<len(c) else None
        records.append(dict(time_s=(i+1)*DT,external_concentration=float(c[i]),bound_receptors=int(counts[i]),
                            forecast=prediction,future_concentration=future,internal_amount=x,
                            command=command,applied=applied,atp_fmol=atp,incoming_fmol=influx*DT,outgoing_fmol=old+influx*DT-x))
    valid=records[200:-DELAY]
    return dict(prediction_rmse=float(np.sqrt(np.mean([(r['forecast']-r['future_concentration'])**2 for r in valid]))),
                regulation_rmse=float(np.sqrt(np.mean([(r['internal_amount']-1)**2 for r in valid]))),
                atp_fmol=float(sum(r['atp_fmol'] for r in valid))),records

def main():
    results=[];example=[]
    for regime in ['smooth','independent']:
        for seed in list(range(20))+list(range(100,120)):
            c=environment(1000+seed,regime);counts=receptor_trace(c,9000+seed)
            for method in ['memoryless','filtered','predictive']:
                metrics,trace=run(c,counts,method);results.append(dict(regime=regime,seed=seed,split="development" if seed<100 else "held_out",method=method,**metrics))
                if seed==0 and regime=='smooth':example.extend(dict(method=method,**row) for row in trace)
    summary={}
    for regime in ['smooth','independent']:
        summary[regime]={}
        for method in ['memoryless','filtered','predictive']:
            rows=[r for r in results if r['regime']==regime and r['method']==method and r['split']=='held_out']
            summary[regime][method]={metric:dict(mean=float(np.mean([r[metric] for r in rows])),
                                               sd=float(np.std([r[metric] for r in rows],ddof=1)))
                                     for metric in ['prediction_rmse','regulation_rmse','atp_fmol']}
    for name,rows in [('runs.csv',results),('example.csv',example)]:
        with (HERE/name).open('w') as f:
            w=csv.DictWriter(f,fieldnames=list(rows[0]),lineterminator='\n');w.writeheader();w.writerows(rows)
    (HERE/'summary.json').write_text(json.dumps(summary,indent=2)+'\n')
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    fig,axs=plt.subplots(1,3,figsize=(12,4),layout='constrained')
    methods=['memoryless','filtered','predictive']
    for ax,metric in zip(axs,['prediction_rmse','regulation_rmse','atp_fmol']):
        for j,regime in enumerate(summary):
            ax.bar(np.arange(3)+j*.36,[summary[regime][m][metric]['mean'] for m in methods],width=.36,label=regime,
                   yerr=[summary[regime][m][metric]['sd'] for m in methods],capsize=2)
        ax.set_xticks(np.arange(3)+.18,methods,rotation=20);ax.set_title(metric.replace('_',' '))
    axs[0].legend();fig.suptitle('Fixed controllers, 20 held-out paired synthetic environments; error bars: seed SD')
    fig.savefig(HERE/'comparison.png',dpi=160);fig.savefig(HERE/'comparison.pdf');plt.close(fig)
    print(json.dumps(summary,indent=2))
if __name__=='__main__':main()
