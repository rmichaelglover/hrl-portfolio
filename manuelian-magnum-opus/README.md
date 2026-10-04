# The Tree, the Proof, and the Light

A Manuelian inquiry into knowledge, perspective, origins and enough.
Michael Emanuel Glover, developed in dialogue with Codex, 3 October 2026.

26-page manuscript, approximately 8,300 words, six mathematical/conceptual figures.
Prepared for author review. Formal arguments, philosophical interpretations and
Christian theological reflections are distinguished throughout.

## Read and edit

- `MAGNUM-OPUS.pdf`: typeset manuscript.
- `MAGNUM-OPUS.txt`: readable text with equations and figure captions.
- `MANUSCRIPT.md`: editable source.
- `MAGNUM-OPUS.tex`: LaTeX source.
- `figures/`: vector PDFs and 300-dpi PNGs.
- `verification.json`: exact operator results and numerical integration checks.

## Regenerate

The verification script uses NumPy, SymPy, SciPy and Matplotlib. It verifies the
four-state partition, exact discovery/resolution commutator, idempotence and
population preservation, finite Cantor-stage encoding injectivity through stage
10, and normalized analytic density examples. Finite-stage checking does not
establish infinite uncountability; the manuscript supplies the mathematical
argument. All plots are analytic illustrations or conceptual diagrams, not new
empirical findings.

```sh
OPENBLAS_NUM_THREADS=1 python3 verify_and_plot.py
python3 build.py
```

The PDF build uses pdflatex and standard TeX packages, with pdfinfo from Poppler.
The output separates conditional proof from ultimate philosophical justification;
it does not claim to decide the continuum hypothesis, solve the liar paradox,
complete physics or prove theological propositions.

References are included in the manuscript. A SHA-256 file inventory accompanies
the bundle so the released source, figures and checks can be identified.
