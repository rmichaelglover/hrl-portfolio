#!/usr/bin/env python3
"""Build Ubuntu's python3-hrl package from the portfolio's tracked NumPy engine."""
import argparse,gzip,hashlib,json,shutil,subprocess,tarfile,tempfile
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
NAME='python3-hrl';VERSION='0.1.0-1'
TESTS=['core','tracking','consensus','body_pos','som','morphogenesis','meta_discovery','recursive_grounding','reciprocal','meggers','finalization']
def source_files(root):
 return sorted([*root.glob('hrl/*.py'),root/'hrl/README.md',root/'examples/core_demo.py',*[root/f'tests/test_{name}.py' for name in TESTS],*[root/name for name in ['LICENSE','LICENSING.md','TRUST-OF-TRUSTS.md','README.md','pyproject.toml']],root/'packaging/build_hrl_deb.py'])
def build(root,out):
 root=Path(root).resolve();out=Path(out).resolve();out.mkdir(parents=True,exist_ok=True)
 files=source_files(root)
 for p in files:
  if not p.is_file():raise FileNotFoundError(p)
 try:commit=subprocess.check_output(['git','-C',str(root),'rev-parse','HEAD'],text=True,stderr=subprocess.DEVNULL).strip()
 except subprocess.CalledProcessError:commit='source archive; use file checksums'
 manifest={'source_repository':'https://github.com/rmichaelglover/hrl-portfolio','base_commit':commit,'files':{p.relative_to(root).as_posix():hashlib.sha256(p.read_bytes()).hexdigest() for p in files}}
 with tempfile.TemporaryDirectory(prefix='ubuntu-hrl-') as tmp:
  stage=Path(tmp)/'stage';lib=stage/'usr/lib/python3/dist-packages/hrl';lib.mkdir(parents=True)
  for p in root.glob('hrl/*.py'):shutil.copy2(p,lib/p.name)
  docs=stage/f'usr/share/doc/{NAME}';(docs/'examples').mkdir(parents=True);(docs/'tests').mkdir()
  shutil.copy2(root/'hrl/README.md',docs/'README.md');shutil.copy2(root/'examples/core_demo.py',docs/'examples/core_demo.py')
  for name in TESTS:shutil.copy2(root/f'tests/test_{name}.py',docs/f'tests/test_{name}.py')
  for name in ['LICENSE','LICENSING.md','TRUST-OF-TRUSTS.md']:shutil.copy2(root/name,docs/name)
  (docs/'PROVENANCE.json').write_text(json.dumps(manifest,indent=2)+'\n')
  (docs/'copyright').write_text('Copyright 2026 R. Michael Glover\nLicense: MIRL-1.0, source-available.\nNo license has been changed by packaging.\n\n'+(root/'LICENSE').read_text())
  (docs/'README.Debian').write_text('NumPy-only HRL engine from hrl-portfolio. Run hrl-demo, or import hrl.\nOptional NLI/LLM integrations require separate dependencies and model/service access; they are not installed automatically. No GRRLE recursive text engine or research datasets are bundled.\n')
  (docs/'changelog.Debian.gz').write_bytes(gzip.compress((f'{NAME} ({VERSION}) stable; urgency=medium\n\n  * Initial Ubuntu package; preserve existing MIRL-1.0 terms.\n\n -- Michael Emanuel Glover <glover.michaele@gmail.com>  Mon, 26 Oct 2026 21:30:00 -0400\n').encode(),mtime=0))
  bin=stage/'usr/bin';bin.mkdir(parents=True);launcher=bin/'hrl-demo'
  launcher.write_text('#!/usr/bin/python3 -B\nfrom pathlib import Path\nimport runpy,sys\nroot=Path(__file__).resolve().parent.parent\nsys.path.insert(0,str(root/"lib/python3/dist-packages"))\nrunpy.run_path(str(root/"share/doc/python3-hrl/examples/core_demo.py"),run_name="__main__")\n');launcher.chmod(0o755)
  meta=stage/'DEBIAN';meta.mkdir();size=sum(p.stat().st_size for p in stage.rglob('*') if p.is_file())//1024
  (meta/'control').write_text(f'''Package: {NAME}
Version: {VERSION}
Section: non-free/python
Priority: optional
Architecture: all
Maintainer: Michael Emanuel Glover <glover.michaele@gmail.com>
Depends: python3 (>= 3.10), python3-numpy (>= 1.21)
Installed-Size: {size}
Homepage: https://rmichaelglover.github.io/hrl-portfolio/
Description: HRL engine with persistent priors and a noise label
 NumPy-based contextual labeling with point correspondence, temporal
 tracking, model consensus and additional experimental modules.
 Includes a runnable hrl-demo and Python API. Optional NLI and LLM
 dependencies are not installed. MIRL-1.0 source-available license.
''')
  (meta/'md5sums').write_text(''.join(hashlib.md5(p.read_bytes()).hexdigest()+'  '+p.relative_to(stage).as_posix()+'\n' for p in sorted(stage.rglob('*')) if p.is_file() and meta not in p.parents))
  deb=out/f'{NAME}_{VERSION}_all.deb';subprocess.run(['dpkg-deb','--root-owner-group','--build',str(stage),str(deb)],check=True)
  source=out/f'{NAME}_{VERSION}_source.tar.gz'
  with tarfile.open(source,'w:gz') as tar:
   for p in files:tar.add(p,arcname=p.relative_to(root).as_posix())
  print(deb);print(source)
if __name__=='__main__':
 parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--source-root',type=Path,default=ROOT);parser.add_argument('--output',type=Path,default=ROOT/'linux');args=parser.parse_args();build(args.source_root,args.output)
