"""Build the two public research readers and their reproducible source bundle."""
from pathlib import Path
import html
import zipfile
import markdown

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
CSS = '''
:root{color-scheme:light;--ink:#172b35;--accent:#086c70}
*{box-sizing:border-box}body{margin:0;background:#f5f3ec;color:var(--ink);font:18px/1.75 Georgia,serif}
nav,main,footer{max-width:980px;margin:auto;padding:24px}nav{font:15px/1.6 system-ui;display:flex;flex-wrap:wrap;gap:18px;border-bottom:1px solid #ccd3ce}
a{color:var(--accent);text-underline-offset:3px}h1,h2,h3{font-family:system-ui;line-height:1.2;letter-spacing:-.025em}h1{font-size:clamp(2.2rem,6vw,4rem);margin-top:40px}h2{margin-top:48px}h3{margin-top:36px}p{max-width:78ch}pre{overflow:auto;background:#e6ebe6;padding:20px;font:14px/1.6 monospace;border-radius:8px}code{font-size:.86em}table{display:block;overflow:auto;border-collapse:collapse;font:14px/1.6 system-ui;width:100%}th,td{padding:10px;border-bottom:1px solid #c7d2cd;text-align:left}blockquote,.intro{border-left:4px solid var(--accent);padding:12px 22px;background:#e8ede5}footer{font:14px/1.6 system-ui;border-top:1px solid #ccd3ce}section{margin-top:56px}@media print{body{background:white;font-size:11pt}nav,.downloads{display:none}main{padding:0;max-width:none}h1{font-size:28pt}pre,table{break-inside:avoid}a{color:inherit}}
'''


def render(title, content):
    return f'''<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>{html.escape(title)} — Michael Emanuel Glover</title>
<meta name="description" content="Relaxed Communications and mutual-best early finalization: research by Michael Emanuel Glover, with conditional mathematics, implementation and reproducible synthetic measurements.">
<style>{CSS}</style></head><body>
<nav aria-label="Research navigation"><a href="../">HRL portfolio</a><a href="theory.html">Relaxed Communications</a><a href="./">Mutual-best finalization</a><a href="SOURCE.zip">Source &amp; data ZIP</a></nav>
<main>{content}</main><footer>Michael Emanuel Glover · October 16, 2026 · Research proposal and finite experimental results. Computational assistance: Cypher.</footer></body></html>'''


def md(name):
    return markdown.markdown((HERE / name).read_text(), extensions=['tables', 'fenced_code'])


theory = md('RELAXED-COMMUNICATIONS.md')
theory += '<p class="downloads"><a href="RELAXED-COMMUNICATIONS.md">Download the Markdown manuscript</a> · <a href="SOURCE.zip">Source and experimental data</a></p>'
(HERE / 'theory.html').write_text(render('Relaxed Communications', theory))
intro = '''<h1>Mutual-best early finalization</h1><p><strong>Michael Emanuel Glover</strong> · Implementation and measured research · October 16, 2026</p>
<p class="intro">Which label is best for this object—and which object is best for this label? When a strong mutual match persists, settle it early and retain its influence while spending computation elsewhere.</p>
<p>The opt-in implementation uses three eligible sweeps by default, caches frozen soft distributions, and permits reopening through audits. All 81 repository tests passed. The larger exploratory aggressive-audited cases achieved 3.69× and 3.94× speedups; smaller workloads showed mixed performance. Finalized assignments can have a nonzero full-update residual.</p>
<p><a href="theory.html">Read the companion theory: Relaxed Communications</a> · <a href="SOURCE.zip">Download runnable source, tests and data</a> · <a href="https://github.com/rmichaelglover/hrl-portfolio/tree/main/mutual-finalization">Browse source on GitHub</a></p>'''
body = intro + '<section>' + md('REPORT.md') + '</section><section>' + md('LARGE-PROBE.md') + '</section><section>' + md('README.md') + '</section>'
body = body.replace('href="../tests/test_finalization.py"', 'href="https://github.com/rmichaelglover/hrl-portfolio/blob/main/tests/test_finalization.py"')
(HERE / 'index.html').write_text(render('Mutual-best early finalization', body))
paths = [ROOT/'pyproject.toml', *sorted((ROOT/'hrl').glob('*.py')), ROOT/'tests/test_finalization.py']
paths += [p for p in sorted(HERE.rglob('*')) if p.is_file() and p.suffix in {'.py','.md','.json','.csv','.html'} and '__pycache__' not in p.parts]
with zipfile.ZipFile(HERE/'SOURCE.zip', 'w', zipfile.ZIP_DEFLATED) as bundle:
    for p in paths:
        bundle.write(p, p.relative_to(ROOT))
print('Built two readers and SOURCE.zip')
