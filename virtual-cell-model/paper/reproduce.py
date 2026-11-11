#!/usr/bin/env python3
"""Rebuild the frozen-model experiments, illustrations, manuscript and archives."""
from pathlib import Path
import argparse,subprocess,os,shutil,hashlib,json,platform,tarfile,zipfile
P=Path(__file__).resolve().parent
parser=argparse.ArgumentParser();parser.add_argument('--experiments',action='store_true',help='Regenerate CSV measurements from frozen C++ model')
args=parser.parse_args()
def run(command,**kwargs):
 print('+',' '.join(map(str,command)),flush=True)
 subprocess.run(list(map(str,command)),check=True,cwd=P,**kwargs)
model=P/'reproduction'/'model';build=P/'reproduction'/'build'
if args.experiments:
 build.mkdir(exist_ok=True)
 run(['g++','-std=c++17','-O2','-Wall','-Wextra','-Wpedantic','-I',model/'include',P/'experiments'/'benchmark.cpp','-o',build/'benchmark'])
 run([build/'benchmark',P/'data'])
 run(['cmake','-S',model,'-B',build/'tests'])
 run(['cmake','--build',build/'tests'])
 run(['ctest','--test-dir',build/'tests','--output-on-failure'])
run(['python3',P/'experiments'/'analyze.py'],stdout=subprocess.DEVNULL)
run(['python3',P/'experiments'/'audit.py'])
env=os.environ.copy();env['SOURCE_DATE_EPOCH']='1794355200';env['FORCE_SOURCE_DATE']='1'
for _ in range(3):
 with (P/'latex-build.log').open('w') as log:
  run(['pdflatex','-interaction=nonstopmode','-halt-on-error','main.tex'],stdout=log,stderr=subprocess.STDOUT,env=env)
log=(P/'main.log').read_text()
for message in ['undefined references','Citation `','Overfull \\hbox','LaTeX Warning: Reference']:
 if message in log:raise RuntimeError('Unresolved LaTeX diagnostic: '+message)
shutil.copy2(P/'main.pdf',P/'VIRTUAL_CELL_MANUSCRIPT.pdf')
inputs=[P/'main.tex',*sorted((P/'figures').glob('*.pdf')),*sorted((P/'source').glob('*.tex'))]
with tarfile.open(P/'virtual-cell-arxiv-source.tar.gz','w:gz') as tar:
 for path in inputs:tar.add(path,arcname=path.relative_to(P))
# Source/data manifest excludes generated build directories and archive recursion.
paths=[P/'main.tex',P/'reproduce.py',P/'README.md',P/'SUBMISSION_NOTES.md',P/'VIRTUAL_CELL_MANUSCRIPT.pdf']
for directory in ['experiments','data','figures','source','reproduction/model']:
 paths.extend(x for x in (P/directory).rglob('*') if x.is_file() and '__pycache__' not in x.parts)
paths=sorted(set(paths))
(P/'MANIFEST.sha256').write_text('\n'.join(hashlib.sha256(x.read_bytes()).hexdigest()+'  '+x.relative_to(P).as_posix()for x in paths)+'\n')
with zipfile.ZipFile(P/'virtual-cell-reproducibility.zip','w',zipfile.ZIP_DEFLATED) as z:
 for path in paths+[P/'MANIFEST.sha256']:
  z.write(path,Path('virtual-cell-paper')/path.relative_to(P))
print('Ready: VIRTUAL_CELL_MANUSCRIPT.pdf, virtual-cell-arxiv-source.tar.gz, virtual-cell-reproducibility.zip')
