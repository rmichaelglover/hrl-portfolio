#!/usr/bin/env python3
"""Rebuild, validate, analyze and package the empirically grounded assay extension."""
from pathlib import Path
import hashlib
import subprocess
import sys
import zipfile

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]

def run(*command):
    subprocess.run(command, cwd=ROOT, check=True)

def package():
    files = [ROOT/name for name in ['CMakeLists.txt', 'README.md', 'MODEL_UPDATE.md', 'LITHIUM_RESEARCH.md']]
    for folder in ['include', 'src', 'tests', 'experiments/lithium', 'experiments/impase', 'experiments/enzyme-cycle', 'experiments/bioelectric', 'experiments/eyes', 'experiments/relaxation', 'experiments/household', 'experiments/observation', 'ros2', 'experiments/receptor', 'experiments/learning']:
        files.extend(p for p in (ROOT/folder).rglob('*') if p.is_file()
                     and '__pycache__' not in p.parts and p.suffix != '.zip'
                     and p.name != 'MANIFEST.sha256')
    files = sorted(set(files))
    manifest = ''.join(hashlib.sha256(p.read_bytes()).hexdigest()+'  '+str(p.relative_to(ROOT))+'\n'
                       for p in files)
    (HERE/'MANIFEST.sha256').write_text(manifest)
    files.append(HERE/'MANIFEST.sha256')
    archive=HERE/'impase-assay-reproducibility.zip'
    with zipfile.ZipFile(archive, 'w', zipfile.ZIP_DEFLATED) as z:
        for p in files:
            info=zipfile.ZipInfo(str(Path('virtual-cell')/p.relative_to(ROOT)),(2026,11,11,0,0,0))
            info.compress_type=zipfile.ZIP_DEFLATED
            info.external_attr=0o644 << 16
            z.writestr(info,p.read_bytes())
    print(f'Packaged {len(files)} files: {archive}')

if __name__=='__main__':
    if '--package-only' not in sys.argv:
        run('cmake','-S','.', '-B','build')
        run('cmake','--build','build','-j','2')
        run('ctest','--test-dir','build','--output-on-failure')
        run(sys.executable,'experiments/impase/analyze.py')
        run(sys.executable,'-m','unittest','discover','-s','experiments/impase','-p','test_*.py','-v')
    package()
