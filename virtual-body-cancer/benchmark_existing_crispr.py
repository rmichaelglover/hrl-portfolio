"""Audit a REAL local assay dataset. Prediction benchmark, not cancer efficacy."""
from pathlib import Path
import os,hashlib,json,time
import numpy as np
import pandas as pd
from scipy.stats import spearmanr
from sklearn.model_selection import GroupKFold
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import Ridge
from sklearn.neighbors import NearestNeighbors
from vendor.hrl_engine import HRL,pairwise_factor
B=Path(__file__).resolve().parent
from vendor import crispr_sequence_features as existing
bundled=B/'data/doench2016.csv'
DATA=Path(os.environ.get('VIRTUAL_BODY_CRISPR_DATA',str(bundled if bundled.exists() else Path.home()/'.cache/crispr_autoresearch/doench2016.csv')))
DATA_URL='https://raw.githubusercontent.com/MicrosoftResearch/Azimuth/master/azimuth/data/FC_plus_RES_withPredictions.csv'
raw=pd.read_csv(DATA)
df=raw.dropna(subset=['30mer','score_drug_gene_rank','Target gene']).copy()
df=df[df['30mer'].str.fullmatch('[ACGT]{30}')].reset_index(drop=True)
seq=df['30mer'].to_numpy();y=df['score_drug_gene_rank'].to_numpy(float)
mono=existing.one_hot(seq);features=existing.build_features(mono)
# Existing function appends four metadata/stacking +21 drug/gene columns.
# Remove ALL of them including predictions fitted with unknown provenance.
metadata=existing._gene_features(mono).shape[1]+existing._drug_gene_features(mono).shape[1]
X=features[:,:-metadata]
assert metadata==25
# Independent executable feature-provenance check: mutate only metadata providers.
oldg,oldd=existing._gene_features,existing._drug_gene_features
existing._gene_features=lambda z:np.full((len(z),4),999.)
existing._drug_gene_features=lambda z:np.full((len(z),21),999.)
assert np.array_equal(X,existing.build_features(mono)[:,:-metadata])
existing._gene_features,existing._drug_gene_features=oldg,oldd
# Identify sequence leakage in the historical row-based split.
rng=np.random.default_rng(42);order=rng.permutation(len(df));nt=int(.2*len(df));nv=int(.1*len(df))
historical_test=set(seq[order[:nt]]);historical_train=set(seq[order[nt+nv:]])
audit={'rows':len(df),'unique_sequences':len(set(seq)),'genes':int(df['Target gene'].nunique()),
       'historical_test_sequences_also_in_training':len(historical_test&historical_train),
       'historical_test_sequences':len(historical_test),'removed_metadata_columns':metadata,
       'sequence_only_features':X.shape[1],'metadata_independence_check':True,
       'historical_selection_warning':'results.tsv repeatedly compares the same test metric while selecting models; it is not an untouched final test',
       'source_file_sha256':hashlib.sha256(DATA.read_bytes()).hexdigest()}
print(json.dumps(audit,indent=2),flush=True)
centers=np.linspace(0,1,8)
C=np.exp(-((centers[:,None]-centers[None,:])/.15)**2)
# Feature-only transductive graph fixed before evaluation; no test labels.
neighbors=NearestNeighbors(n_neighbors=4,n_jobs=1).fit(mono.reshape(len(df),-1)).kneighbors(return_distance=False)
edges=sorted({tuple(sorted((i,int(j)))) for i,row in enumerate(neighbors) for j in row[:3] if i!=j})
factor=pairwise_factor(np.array(edges),C)
records=[];folds=[]
for protocol,groups in [('sequence_disjoint',seq),('gene_disjoint',df['Target gene'].to_numpy())]:
    predictions={k:np.full(len(df),np.nan) for k in ['onehot_ridge','existing_sequence_features_ridge','hrl_sequence_graph']}
    for fold,(train,test) in enumerate(GroupKFold(n_splits=5).split(X,y,groups)):
        assert not set(groups[train])&set(groups[test])
        assert not set(seq[train])&set(seq[test]),'sequence overlap across gene partition'
        t=time.perf_counter()
        simple=Ridge(alpha=10).fit(mono.reshape(len(df),-1)[train],y[train])
        predictions['onehot_ridge'][test]=simple.predict(mono.reshape(len(df),-1)[test])
        scale=StandardScaler().fit(X[train]);Xs=scale.transform(X)
        model=Ridge(alpha=100).fit(Xs[train],y[train]);prior_score=model.predict(Xs)
        predictions['existing_sequence_features_ridge'][test]=prior_score[test]
        # Training assays supervise anchors; held-out assay labels never enter HRL.
        means=np.clip(prior_score,0,1);means[train]=y[train]
        sd=np.full(len(df),.12);sd[train]=.02
        prior=np.exp(-.5*((centers[None,:]-means[:,None])/sd[:,None])**2)+1e-12
        prior/=prior.sum(axis=1,keepdims=True)
        fit=HRL(len(df),8,[factor],prior,prior_strength=.85,max_iterations=80,tol=1e-7).run()
        assert np.isfinite(fit.strengths).all() and np.allclose(fit.strengths.sum(axis=1),1)
        predictions['hrl_sequence_graph'][test]=(fit.strengths@centers)[test]
        score={k:float(spearmanr(y[test],v[test]).statistic) for k,v in predictions.items()}
        folds.append({'protocol':protocol,'fold':fold,'train_rows':len(train),'test_rows':len(test),'test_genes':sorted(set(df['Target gene'].iloc[test])),
                      'spearman':score,'hrl_converged':bool(fit.converged),'hrl_iterations':int(fit.iterations),'seconds':time.perf_counter()-t})
        print(protocol,fold,score,'converged',fit.converged,flush=True)
    for name,v in predictions.items():
        assert np.isfinite(v).all()
        records.append({'protocol':protocol,'model':name,'pooled_oof_spearman':float(spearmanr(y,v).statistic),
                        'mean_fold_spearman':float(np.mean([f['spearman'][name] for f in folds if f['protocol']==protocol])),
                        'MAE':float(np.mean(np.abs(y-v)))})
    # Row IDs and scores only: do not publish guide sequences or clinical claims.
    pd.DataFrame({'source_row':df.index,'observed_rank':y,**predictions}).to_csv(B/f'output/crispr-{protocol}-oof.csv',index=False)
result={'status':'new exploratory benchmark of locally cached measured assay ranks', 'data_audit':audit,'metrics':records,'folds':folds,
        'design':'fixed 5-fold group splits; no new hyperparameter selection; feature-only transductive graph; train-only feature scaling; no test labels in inference',
        'provenance':{'paper':'https://doi.org/10.1038/nbt.3437','dataset_url':DATA_URL,'feature_code':'vendor/crispr_sequence_features.py',
                      'feature_code_sha256':hashlib.sha256((B/'vendor/crispr_sequence_features.py').read_bytes()).hexdigest()},
        'limitations':['Assay response rank, not proof of cutting efficiency for every context, tumor eradication, organism safety or a cure.',
                       'No held-out external laboratory or prospective experiment; split choices and dataset were available to prior project development.',
                       'Graph homophily by sequence similarity is an assumption being tested, not established biology.',
                       'Gene-grouped normalized ranks are the supplied dataset target; no drug response or cancer vulnerability is inferred.']}
(B/'output/crispr-benchmark.json').write_text(json.dumps(result,indent=2))
print(json.dumps(records,indent=2),flush=True)
