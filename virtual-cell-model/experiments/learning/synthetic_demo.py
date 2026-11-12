#!/usr/bin/env python3
"""Export a public synthetic verification trace; no measured study data."""
from pathlib import Path
import argparse,csv,json,subprocess,tempfile
HERE=Path(__file__).resolve().parent

def main():
    p=argparse.ArgumentParser();p.add_argument('--binary',type=Path,default=HERE.parents[1]/'build/relaxation_learning');a=p.parse_args()
    with tempfile.TemporaryDirectory() as folder:
        folder=Path(folder);data=folder/'synthetic.txt';model=folder/'synthetic.model';history=folder/'history.csv'
        data.write_text('4 2\n0 0 0 -1 0\n0 1 0 -1 .1\n1 0 1 1 0\n1 1 1 1 .1\n')
        result=json.loads(subprocess.check_output([str(a.binary),'train',str(data),str(data),str(model),str(history),'6','100','73','.02'],text=True))
        (HERE/'synthetic-history.csv').write_text(history.read_text())
        probe=json.loads(subprocess.check_output([str(a.binary),'probe'],text=True))
        (HERE/'synthetic-check.json').write_text(json.dumps(dict(training=result,gradient_probe=probe,
            note='Synthetic implementation verification; the same four examples supply training and checkpoint loss. Not a generalization evaluation.'),indent=2)+'\n')
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    with (HERE/'synthetic-history.csv').open() as f:rows=list(csv.DictReader(f))
    fig,ax=plt.subplots(figsize=(8,4),layout='constrained')
    ax.plot([int(r['epoch']) for r in rows],[float(r['validation_nll']) for r in rows],color='#3c695a')
    ax.set(xlabel='C++ optimizer step',ylabel='Same-fixture negative log likelihood',title='Backpropagation through six relaxation steps: synthetic verification')
    fig.savefig(HERE/'synthetic-learning.png',dpi=170);fig.savefig(HERE/'synthetic-learning.pdf');plt.close(fig)
    print(json.dumps(result,indent=2))
if __name__=='__main__':main()
