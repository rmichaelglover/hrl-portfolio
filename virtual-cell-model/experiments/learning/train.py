#!/usr/bin/env python3
"""Run actual C++ training, checkpoint on validation, then evaluate held-out recordings."""
from pathlib import Path
import argparse,csv,hashlib,io,json,subprocess
import numpy as np
from scipy.stats import rankdata
HERE=Path(__file__).resolve().parent

def f1(y,pred):
    values=[]
    for label in (0,1):
        tp=np.sum((y==label)&(pred==label));fp=np.sum((y!=label)&(pred==label));fn=np.sum((y==label)&(pred!=label))
        values.append(float(2*tp/(2*tp+fp+fn)) if 2*tp+fp+fn else 0.)
    return float(np.mean(values))

def measures(y,p,threshold=.5):
    y=np.asarray(y,int);p=np.asarray(p,float);pred=(p>=threshold).astype(int);clipped=np.clip(p,1e-12,1-1e-12)
    positive=int(y.sum());negative=len(y)-positive
    auc=float((rankdata(p)[y==1].sum()-positive*(positive+1)/2)/(positive*negative)) if positive and negative else None
    # Tie-aware average precision: include each complete equal-score group.
    order=np.argsort(-p,kind='stable');ys=y[order];ps=p[order];tp=np.cumsum(ys)
    ends=np.r_[np.nonzero(np.diff(ps))[0],len(ps)-1];last=0;ap=0.
    for end in ends:
        recalled=int(tp[end])-last;ap+=recalled*float(tp[end]/(end+1));last=int(tp[end])
    ap=ap/positive if positive else None
    ece=0.
    for bin in range(10):
        mask=(p>=bin/10)&((p<(bin+1)/10) if bin<9 else (p<=1))
        if mask.any():ece+=mask.mean()*abs(p[mask].mean()-y[mask].mean())
    recalls=[np.mean(pred[y==label]==label) for label in (0,1) if np.any(y==label)]
    return dict(n=len(y),rem=positive,threshold=threshold,accuracy=float(np.mean(pred==y)),macro_f1=f1(y,pred),
                balanced_accuracy=float(np.mean(recalls)),roc_auc=auc,average_precision=ap,
                nll=float(-np.mean(y*np.log(clipped)+(1-y)*np.log1p(-clipped))),brier=float(np.mean((p-y)**2)),ece_10_bins=float(ece))

def predict(binary,model,data):
    result=subprocess.check_output([str(binary),'predict',str(model),str(data)],text=True)
    return list(csv.DictReader(io.StringIO(result)))

def threshold_on_validation(rows):
    y=np.array([int(r['label']) for r in rows]);p=np.array([float(r['p_rem']) for r in rows])
    return float(max(np.arange(.05,.951,.05),key=lambda t:(f1(y,p>=t),-abs(t-.5))))

def main():
    parser=argparse.ArgumentParser();parser.add_argument('--data',type=Path,required=True);parser.add_argument('--output',type=Path,required=True)
    parser.add_argument('--binary',type=Path,default=HERE.parents[1]/'build/relaxation_learning');args=parser.parse_args()
    args.output.mkdir(parents=True,exist_ok=True)
    config=dict(steps=[0,6],seeds=[73,91,117],max_epochs=160,learning_rate=.02,l2=.001,
                checkpoint='minimum validation NLL; patience 35',threshold_grid=[round(float(t),2) for t in np.arange(.05,.951,.05)],
                transform='training-only log-EOG mean/std',graph='offline bidirectional normalized adjacent epochs within 64-node chunks',
                code_sha256={name:hashlib.sha256((HERE/name).read_bytes()).hexdigest() for name in ['train.py','prepare.py']},
                header_sha256=hashlib.sha256((HERE.parents[1]/'include/trainable_relaxation.hpp').read_bytes()).hexdigest(),
                data_manifest_sha256=hashlib.sha256((args.data/'manifest.json').read_bytes()).hexdigest())
    (args.output/'protocol.json').write_text(json.dumps(config,indent=2)+'\n')
    trained=[]
    # Complete model and threshold selection before opening test predictions.
    for seed in config['seeds']:
        for steps,name in [(0,'unary'),(6,'relaxation')]:
            stem=f'{name}-{seed}';model=args.output/(stem+'.model');history=args.output/(stem+'-history.csv')
            command=[str(args.binary),'train',str(args.data/'train.txt'),str(args.data/'validation.txt'),str(model),str(history),str(steps),'160',str(seed),'.02']
            report=json.loads(subprocess.check_output(command,text=True))
            validation=predict(args.binary,model,args.data/'validation.txt');threshold=threshold_on_validation(validation)
            trained.append(dict(name=name,seed=seed,model=str(model),history=str(history),threshold=threshold,**report))
            print(json.dumps(dict(phase='validation',name=name,seed=seed,**report)),flush=True)
    (args.output/'selected.json').write_text(json.dumps(trained,indent=2)+'\n')
    with (args.data/'test.rows.csv').open() as f:mapping=list(csv.DictReader(f))
    with (args.data/'test-shuffled.rows.csv').open() as f:shuffled_mapping=list(csv.DictReader(f))
    results=[]
    for entry in trained:
        for variant,file,identities in [('normal','test.txt',mapping)]+([('shuffled','test-shuffled.txt',shuffled_mapping)] if entry['name']=='relaxation' else []):
            rows=predict(args.binary,Path(entry['model']),args.data/file)
            if len(rows)!=len(identities):raise ValueError('Prediction mapping mismatch')
            for row,identity in zip(rows,identities):row.update(identity)
            y=np.array([int(r['label']) for r in rows]);p=np.array([float(r['p_rem']) for r in rows])
            recording=np.array([r['recording'] for r in rows])
            record_metrics={record:measures(y[recording==record],p[recording==record],entry['threshold']) for record in sorted(set(recording))}
            name=entry['name'] if variant=='normal' else 'relaxation_shuffled'
            results.append(dict(name=name,seed=entry['seed'],overall=measures(y,p,entry['threshold']),
                                per_recording=record_metrics,last_delta_max=max(float(r['last_delta']) for r in rows),
                                recording_mean_macro_f1=float(np.mean([m['macro_f1'] for m in record_metrics.values()]))))
            with (args.output/f'{name}-{entry["seed"]}-predictions.csv').open('w') as f:
                writer=csv.DictWriter(f,fieldnames=list(rows[0]),lineterminator='\n');writer.writeheader();writer.writerows(rows)
    train_labels=np.loadtxt(args.data/'train.txt',skiprows=1,usecols=2);prevalence=float(train_labels.mean())
    y=np.loadtxt(args.data/'test.txt',skiprows=1,usecols=2).astype(int)
    report=dict(protocol=config,training_prevalence=prevalence,constant_prevalence_baseline=measures(y,np.full(len(y),prevalence)),
                trained=trained,test_results=results,note='Exploratory recording-disjoint evaluation, not verified participant-disjoint or clinical validation; all study results remain local.')
    (args.output/'results.json').write_text(json.dumps(report,indent=2)+'\n')
    figures(args.output,trained,results)
    print(json.dumps([dict(name=r['name'],seed=r['seed'],macro_f1=r['overall']['macro_f1'],nll=r['overall']['nll'],roc_auc=r['overall']['roc_auc']) for r in results],indent=2))

def figures(output,trained,results):
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    fig,axes=plt.subplots(1,2,figsize=(11,4),layout='constrained')
    for entry in trained:
        with open(entry['history']) as f:rows=list(csv.DictReader(f))
        axes[0].plot([int(r['epoch']) for r in rows],[float(r['validation_nll']) for r in rows],label=f'{entry["name"]} {entry["seed"]}')
    axes[0].set(xlabel='Training epoch',ylabel='Validation NLL',title='Selection uses validation only');axes[0].legend(fontsize=7)
    names=['unary','relaxation','relaxation_shuffled'];means=[];stds=[]
    for name in names:
        values=[r['overall']['macro_f1'] for r in results if r['name']==name];means.append(np.mean(values));stds.append(np.std(values,ddof=1))
    axes[1].bar(names,means,yerr=stds,capsize=3,color=['#627f8a','#60866b','#b47c58']);axes[1].set(ylim=(0,1),ylabel='Pooled test macro F1',title='Two held-out recordings; error bars: initialization SD');axes[1].tick_params(axis='x',rotation=15)
    fig.savefig(output/'training-and-test.png',dpi=170);fig.savefig(output/'training-and-test.pdf');plt.close(fig)
if __name__=='__main__':main()
