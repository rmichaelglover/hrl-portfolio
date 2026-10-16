# Relationships That Compute

**Michael Emanuel Glover · 16 October 2026 · Research synthesis v1.0**

Research results across the HRL portfolio, including local studies and prototypes not yet incorporated into the public site. Personal essays and fictional stories are excluded from the results narrative.

- `RELATIONSHIPS-THAT-COMPUTE.pdf`: complete typeset white paper with contents, numbered sections, tables, figures, appendices, and source register.
- `WHITE-PAPER.md`: editable author manuscript.
- `RELATIONSHIPS-THAT-COMPUTE.txt`: extracted text for searching and review.
- `evidence-register.json`: selected primary sources and supporting files with SHA-256 hashes.
- `claim-checks.json`: selected numerical checks against inspected sources.
- `verification.json`: test suites rerun for the synthesis.
- `figure-data.json` and `figures/`: plotted values and standalone PNG/PDF figures.
- `document-checks.json` and `MANIFEST.json`: page count, coverage checks, artifact hashes.
- `RESEARCH-SYNTHESIS-SOURCE.zip`: paper, source, figures, and review evidence; underlying research datasets and code remain in their original projects.

Run `python3 build.py` in this folder to rebuild. Dependencies: Python 3, NumPy, Matplotlib, ReportLab, Pillow, fontTools, DejaVu fonts, and Poppler `pdfinfo`/`pdftotext`. The evidence register uses the local research roots declared at the start of the script; adjust those for another machine. No network access is needed. The build redraws historical results and does not rerun the research experiments.

Authorship is Michael Emanuel Glover's. Cypher/Codex assisted with evidence inspection, computation, drafting, and production. Original studies and third-party work keep their existing attribution and licensing. The published edition is at https://rmichaelglover.github.io/hrl-portfolio/research-synthesis-2026/. No deployment or publication is performed by the builder itself.
