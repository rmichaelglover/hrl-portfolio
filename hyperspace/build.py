"""Build the paper and figures with checked experiment outputs."""
from pathlib import Path
import json, subprocess, sys
root=Path(__file__).resolve().parent
subprocess.run([sys.executable,str(root/'experiments.py')],check=True)
m=json.loads((root/'metrics.json').read_text())
g=m['Geographic cycle'];h=m['Cycle + information links']
text=rf'''\begin{{center}}\begin{{tabular}}{{lrr}}\toprule
Quantity & Cycle & With shortcuts\\\midrule
Spectral radius $\rho(Q)$ & {g['rho']:.6f} & {h['rho']:.6f}\\
Largest expected absorption time & {g['max_expected_absorption_steps']:.2f} & {h['max_expected_absorption_steps']:.2f}\\
First update with error $<10^{{-3}}$ & $>4000$ & {h['first_step_below_0.001']}\\\bottomrule
\end{{tabular}}\end{{center}}
The triangular-lattice free-node residual was {m['ternary']['harmonic_residual']:.2e} in the entrywise maximum norm.
'''
(root/'results.tex').write_text(text)
for _ in range(2):subprocess.run(['pdflatex','-interaction=nonstopmode','-halt-on-error','-jobname=HYPERSPACE', 'paper.tex'],cwd=root,check=True,stdout=subprocess.DEVNULL)
log=(root/'HYPERSPACE.log').read_text()
for problem in ['Missing character','Overfull \\hbox','Overfull \\vbox','LaTeX Warning: There were undefined references']:
    if problem in log:raise RuntimeError('Rendering check failed: '+problem)
print('PASS: compiled twice; no missing glyphs, overfull boxes, or undefined references.')

info=subprocess.check_output(["pdfinfo",str(root/"HYPERSPACE.pdf")],text=True)
pages=int(next(line.split(":")[1] for line in info.splitlines() if line.startswith("Pages:")))
assert pages>=10, f"Only {pages} pages"
print(f"PASS: {pages} pages, including bibliography.")
