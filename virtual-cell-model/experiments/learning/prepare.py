#!/usr/bin/env python3
"""Prepare recording-disjoint measured EOG data; fit transforms on training only."""
from pathlib import Path
import argparse,csv,hashlib,json,subprocess,sys
import numpy as np
HERE=Path(__file__).resolve().parent
FEATURES=[f'eog_{side}_{kind}' for side in ('left','right') for kind in ('rms_uv','slope_rms_uv_per_s','peak_to_peak_uv')]
SCORABLE={'AWAKE','N1','N2','N3','N4','REM'}

def digest(p):
    h=hashlib.sha256()
    with Path(p).open('rb') as f:
        for b in iter(lambda:f.read(1048576),b''):h.update(b)
    return h.hexdigest()

def read_recording(path,alias):
    with Path(path).open() as f:raw=list(csv.DictReader(f))
    result=[];excluded={'unknown_stage':0,'flatline':0,'nonfinite':0}
    for epoch,row in enumerate(raw):
        if row['stage'] not in SCORABLE:excluded['unknown_stage']+=1;continue
        if any(row[f'eog_{s}_flatline'].lower()=='true' for s in ('left','right')):
            excluded['flatline']+=1;continue
        features=np.array([float(row[k]) for k in FEATURES])
        if not np.all(np.isfinite(features)) or np.any(features<0):excluded['nonfinite']+=1;continue
        result.append(dict(recording=alias,epoch=epoch,label=int(row['stage']=='REM'),features=np.log1p(features)))
    if not result:raise ValueError('Recording has no usable epochs')
    return result,excluded

def fit_transform(rows):
    x=np.stack([r['features'] for r in rows]);mean=x.mean(axis=0);std=x.std(axis=0)
    return mean,np.where(std<1e-8,1.,std)

def chunks(rows,size=64):
    output=[];current=[];identity=None
    for row in rows:
        if identity!=row['recording'] or len(current)==size:
            if current:output.append(current)
            current=[];identity=row['recording']
        current.append(row)
    if current:output.append(current)
    return output

def write_data(path,rows,mean,std,shuffle_seed=None):
    rng=np.random.default_rng(shuffle_seed);groups=chunks(rows);mapping=[]
    with Path(path).open('w') as f:
        f.write(f'{len(rows)} {len(FEATURES)}\n')
        for group,chunk in enumerate(groups):
            indices=rng.permutation(len(chunk)) if shuffle_seed is not None else range(len(chunk))
            for node,index in enumerate(indices):
                row=chunk[index];values=np.clip((row['features']-mean)/std,-6,6)
                # Shuffle x and y together; only adjacency changes, not their pairing.
                epoch=node if shuffle_seed is not None else row['epoch']
                f.write(f"{group} {epoch} {row['label']} "+' '.join(format(v,'.17g') for v in values)+'\n')
                mapping.append(dict(sequence=group,node=node,recording=row['recording'],epoch=row['epoch']))
    with Path(path).with_suffix('.rows.csv').open('w') as f:
        w=csv.DictWriter(f,fieldnames=list(mapping[0]),lineterminator='\n');w.writeheader();w.writerows(mapping)
    return mapping

def main():
    p=argparse.ArgumentParser();p.add_argument('--config',type=Path,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args()
    config=json.loads(a.config.read_text());a.output.mkdir(parents=True,exist_ok=True)
    # Exact file identities are checked across all splits before extraction/training.
    identities=[str(Path(r['edf']).resolve()) for split in ('train','validation','test') for r in config[split]]
    if len(identities)!=len(set(identities)):raise ValueError('Recording appears in multiple splits')
    all_rows={};records=[];file_hashes=set()
    for split in ('train','validation','test'):
        rows=[]
        for index,record in enumerate(config[split]):
            alias=f'{split}-{index+1}';out=a.output/'extracted'/alias
            command=[sys.executable,str(HERE.parent/'observation/sleep_extract.py'),'--session',alias,'--output',str(out)]
            for key in ('edf','stages','events'):command+=['--'+key,record[key]]
            subprocess.run(command,check=True,stdout=subprocess.DEVNULL)
            summary=json.loads((out/'summary.json').read_text())
            source_hash=summary['source_sha256']['edf']
            if source_hash in file_hashes:raise ValueError('Duplicate EDF content across recording aliases')
            file_hashes.add(source_hash)
            usable,excluded=read_recording(out/'epochs.csv',alias);rows.extend(usable)
            records.append(dict(split=split,alias=alias,source_sha256=summary['source_sha256'],usable=len(usable),
                                rem=sum(r['label'] for r in usable),excluded=excluded,stage_offset_seconds=summary['stage_offset_seconds']))
        all_rows[split]=rows
    mean,std=fit_transform(all_rows['train'])
    for split,rows in all_rows.items():write_data(a.output/(split+'.txt'),rows,mean,std)
    write_data(a.output/'test-shuffled.txt',all_rows['test'],mean,std,shuffle_seed=442)
    manifest=dict(task='Offline REM versus non-REM among scorable nonflatline epochs',features=FEATURES,
                  transform='log1p; training-only mean/std; clip standardized values to [-6,6]',mean=mean.tolist(),std=std.tolist(),
                  records=records,chunk_size=64,graph='Normalized adjacent-epoch edges; no edges across gaps, chunks or recordings',
                  source_hashes={k:digest(HERE/k) for k in ('prepare.py',)},participant_identity_verified=False)
    (a.output/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
    print(json.dumps({s:dict(epochs=len(rows),rem=sum(r['label'] for r in rows)) for s,rows in all_rows.items()},indent=2))
if __name__=='__main__':main()
