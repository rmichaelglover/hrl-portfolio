"""Build the shared freestanding C++ kernel for the existing Glims browser."""
import argparse,subprocess,tempfile
from pathlib import Path
root=Path(__file__).resolve().parents[1]
p=argparse.ArgumentParser()
p.add_argument('--cxx',default='clang++-14')
p.add_argument('--linker',default='wasm-ld-14')
p.add_argument('--output',type=Path,default=root/'web/glims-motion.wasm')
a=p.parse_args();a.output.parent.mkdir(parents=True,exist_ok=True)
with tempfile.TemporaryDirectory(prefix='glims-wasm-') as directory:
 obj=Path(directory)/'motion.o'
 subprocess.run([a.cxx,'--target=wasm32','-std=c++17','-O2','-nostdlib','-fno-exceptions','-fno-rtti','-fno-builtin','-I',str(root/'include'),'-c',str(root/'web/glims_motion.cpp'),'-o',str(obj)],check=True)
 exports=['reset_motion','set_person','set_choice','set_neighbor','decide_motion','selected_motion','examined_motion','score_motion']
 subprocess.run([a.linker,'--no-entry',*[f'--export={name}' for name in exports],str(obj),'-o',str(a.output)],check=True)
print(a.output)
