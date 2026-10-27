#!/usr/bin/env python3
"""Build the licensed reusable RL core for Ubuntu, independently of research archives."""
import argparse,gzip,hashlib,json,shutil,subprocess,tarfile,tempfile
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];SOURCE=(Path(__file__).resolve().parent/'source') if (Path(__file__).resolve().parent/'source').is_dir() else ROOT/'packaging/sources/relaxation-labeling';VERSION='0.1.0-1';NAME='python3-relaxation-labeling'
def build(out):
 out=Path(out).resolve();out.mkdir(parents=True,exist_ok=True)
 manifest=json.loads((SOURCE/'PROVENANCE.json').read_text())
 for name,digest in manifest['files'].items():
  if hashlib.sha256((SOURCE/name).read_bytes()).hexdigest()!=digest:raise RuntimeError('Source checksum mismatch: '+name)
 with tempfile.TemporaryDirectory(prefix='hrl-core-deb-') as temp:
  stage=Path(temp)/'stage';lib=stage/'usr/lib/python3/dist-packages';lib.mkdir(parents=True)
  for name in ['relax.py','triangles_gt_squares.py']:shutil.copy2(SOURCE/name,lib/name)
  docs=stage/f'usr/share/doc/{NAME}';examples=docs/'examples';examples.mkdir(parents=True)
  shutil.copy2(SOURCE/'example_clusters.py',examples/'example_clusters.py')
  for name in ['README.md','NOTICE','LICENSE','PROVENANCE.json']:shutil.copy2(SOURCE/name,docs/name)
  shutil.copytree(SOURCE/'tests',docs/'tests',ignore=shutil.ignore_patterns('__pycache__','.pytest_cache'))
  (docs/'copyright').write_text('Copyright 2026 Manny Glover (R. Michael Glover)\nLicense: AGPL-3.0; commercial licensing separately available.\n\n'+(SOURCE/'NOTICE').read_text()+'\n'+(SOURCE/'LICENSE').read_text())
  (docs/'README.Debian').write_text('Ubuntu package of the classic pairwise/order-three relaxation-labeling core.\nNot the hierarchical HRL engine or recursive GRRLE engine.\n\nRun relaxation-labeling-demo, or import RelaxationLabeling from relax.\nThe Debian dependency floor NumPy 1.21.5 is tested on Ubuntu 22.04; upstream Python packaging declares NumPy >=1.23. No upstream code was changed.\n')
  (docs/'changelog.Debian.gz').write_bytes(gzip.compress((f'{NAME} ({VERSION}) stable; urgency=medium\n\n  * Initial Ubuntu package of reviewed upstream core.\n\n -- Michael Emanuel Glover <glover.michaele@gmail.com>  Mon, 26 Oct 2026 21:30:00 -0400\n').encode(),mtime=0))
  bindir=stage/'usr/bin';bindir.mkdir(parents=True)
  (bindir/'relaxation-labeling-demo').write_text('#!/usr/bin/python3 -B\nfrom pathlib import Path\nimport runpy,sys\nroot=Path(__file__).resolve().parent.parent\nsys.path.insert(0,str(root/"lib/python3/dist-packages"))\nrunpy.run_path(str(root/"share/doc/python3-relaxation-labeling/examples/example_clusters.py"),run_name="__main__")\n');(bindir/'relaxation-labeling-demo').chmod(0o755)
  control=stage/'DEBIAN';control.mkdir();size=sum(p.stat().st_size for p in stage.rglob('*') if p.is_file())//1024
  (control/'control').write_text(f'''Package: {NAME}
Version: {VERSION}
Section: python
Priority: optional
Architecture: all
Maintainer: Michael Emanuel Glover <glover.michaele@gmail.com>
Depends: python3 (>= 3.10), python3-numpy (>= 1.21.5)
Installed-Size: {size}
Homepage: https://github.com/rmichaelglover/relaxation-labeling-python
Description: NumPy relaxation-labeling core and clustered-object demonstration
 Reusable pairwise and order-three compatibility-based labeling engine,
 with a runnable demonstration and Python API. This is the classic RL
 core, not the complete hierarchical HRL or recursive GRRLE research suite.
 Licensed under AGPL-3.0; see installed copyright and NOTICE files.
''')
  (control/'md5sums').write_text(''.join(hashlib.md5(p.read_bytes()).hexdigest()+'  '+p.relative_to(stage).as_posix()+'\n' for p in sorted(stage.rglob('*')) if p.is_file() and control not in p.parents))
  package=out/f'{NAME}_{VERSION}_all.deb';subprocess.run(['dpkg-deb','--root-owner-group','--build',str(stage),str(package)],check=True)
  archive=out/f'{NAME}_{VERSION}_source.tar.gz'
  with tarfile.open(archive,'w:gz') as tar:
   
   for name in sorted([*manifest['files'],'PROVENANCE.json']):tar.add(SOURCE/name,arcname='source/'+name)
   tar.add(Path(__file__),arcname='build_core_deb.py')
  print(package);print(archive)
if __name__=='__main__':
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--output',type=Path,default=ROOT/'linux');a=p.parse_args();build(a.output)
