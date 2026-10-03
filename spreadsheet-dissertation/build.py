"""Build the manuscript, result figure, PDF, plain text, and web publication."""
from pathlib import Path
from html import escape
from html.parser import HTMLParser
import csv, hashlib, json, re
import markdown
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
from reportlab.lib import colors
from reportlab.lib.styles import ParagraphStyle
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak, Table, TableStyle, Image, Preformatted

ROOT=Path(__file__).resolve().parent
summary=json.loads((ROOT/'results/summary.json').read_text())
manifest=json.loads((ROOT/'results/manifest.json').read_text())
lookup={(r['scenario'],r['method']):r for r in summary}
names={'column_mode':'Column mode','global_gmm':'Global GMM','isolation_forest':'Isolation Forest','structure_gmm':'Structure + GMM','format_gmm':'Formatting + GMM'}

result=['### 7.1 Executed results under stable semantic formatting','',
        '| Method | AP (95% interval) | AUROC | Precision at 54 | Recall at 54 |',
        '|---|---|---|---|---|']
for method,name in names.items():
    row=lookup['semantic',method]; lo,hi=row['ap_ci']
    result.append(f"| {name} | {row['ap']:.3f} ({lo:.3f}-{hi:.3f}) | {row['auroc']:.3f} | {row['precision_at_5pct']:.3f} | {row['recall_at_5pct']:.3f} |")
result+=['','### 7.2 Formatting sensitivity: mean average precision','',
         '| Method | Semantic | Noisy | Decorative | Reversed |','|---|---|---|---|---|']
for method,name in names.items():
    result.append('| '+name+' | '+' | '.join(f"{lookup[s,method]['ap']:.3f}" for s in ['semantic','noisy','decorative','reversed'])+' |')
result+=['','![Mean average precision across paired formatting conditions.](results/performance.png)','',
         '### 7.3 Defect-type recall at the 54-cell budget','',
         '| Method | Operator | Reference | Hardcode | Scale |','|---|---|---|---|---|']
for method,name in names.items():
    result.append('| '+name+' | '+' | '.join(f"{lookup['semantic',method]['recall_'+k]:.3f}" for k in ['wrong_operator','wrong_reference','hardcode','numeric_scale'])+' |')
with (ROOT/'results/runs.csv').open() as f: runs=list(csv.DictReader(f))
fmt=np.array([float(r['ap']) for r in runs if r['scenario']=='semantic' and r['method']=='format_gmm'])
col=np.array([float(r['ap']) for r in runs if r['scenario']=='semantic' and r['method']=='column_mode'])
diff=fmt-col; rng=np.random.default_rng(20261003)
ci=np.quantile(diff[rng.integers(0,12,size=(2000,12))].mean(axis=1),[.025,.975])
result+=['',f"The paired mean AP difference between formatting + GMM and column mode is {diff.mean():.3f}, with a workbook-bootstrap interval [{ci[0]:.3f}, {ci[1]:.3f}]. This interval reflects the twelve seeded content realizations conditional on the fitted model, not population-wide significance.",
         '',f"BIC selected {manifest['selected_components']} components. The complete pipeline executed in {manifest['elapsed_seconds']:.2f} seconds in the recorded local environment. The selected estimator reported convergence.",'']
text=(ROOT/'manuscript.md').read_text().replace('<!-- RESULTS -->','\n'.join(result))
(ROOT/'dissertation.md').write_text(text)

fig,ax=plt.subplots(figsize=(9,4.6)); xs=np.arange(4); width=.15
palette=['#555b66','#376ba8','#8a668f','#cc8834','#267c64']
for i,(method,name) in enumerate(names.items()):
    rows=[lookup[s,method] for s in ['semantic','noisy','decorative','reversed']]
    vals=np.array([r['ap'] for r in rows]); low=vals-np.array([r['ap_ci'][0] for r in rows]); high=np.array([r['ap_ci'][1] for r in rows])-vals
    ax.bar(xs+(i-2)*width,vals,width,label=name,color=palette[i],yerr=[low,high],capsize=2)
ax.set_xticks(xs,['Semantic','Noisy','Decorative','Reversed']); ax.set_ylim(0,1); ax.set_ylabel('Mean average precision'); ax.set_title('Formatting helps when its convention remains meaningful')
ax.spines[['top','right']].set_visible(False); ax.legend(ncol=3,fontsize=8,loc='upper right'); ax.grid(axis='y',alpha=.15); ax.set_axisbelow(True)
fig.tight_layout(); fig.savefig(ROOT/'results/performance.png',dpi=180); fig.savefig(ROOT/'results/performance.svg'); plt.close(fig)

body=markdown.markdown(text,extensions=['tables','toc'])
web_body=body.replace('<table>', '<div class="table-wrap"><table>').replace('</table>', '</table></div>')
class Plain(HTMLParser):
    def __init__(self): super().__init__(); self.parts=[]
    def handle_data(self,data): self.parts.append(data)
    def handle_endtag(self,tag):
        if tag in ['p','h1','h2','h3','li','tr','pre']: self.parts.append('\n\n')
        elif tag in ['td','th']: self.parts.append(' | ')
parser=Plain(); parser.feed(body); (ROOT/'dissertation.txt').write_text(''.join(parser.parts))

fontdir=Path('/usr/share/fonts/truetype/dejavu')
for name,file in [('Book','DejaVuSerif.ttf'),('BookBold','DejaVuSerif-Bold.ttf'),('BookItalic','DejaVuSerif-Italic.ttf'),('Mono','DejaVuSansMono.ttf')]:
    pdfmetrics.registerFont(TTFont(name,str(fontdir/file)))
pdfmetrics.registerFontFamily('Book',normal='Book',bold='BookBold',italic='BookItalic',boldItalic='BookBold')
styles={
    'body':ParagraphStyle('body',fontName='Book',fontSize=10,leading=15,spaceAfter=9),
    'h1':ParagraphStyle('h1',fontName='BookBold',fontSize=22,leading=29,spaceAfter=24,textColor=colors.HexColor('#143f53')),
    'h2':ParagraphStyle('h2',fontName='BookBold',fontSize=15,leading=21,spaceAfter=16,textColor=colors.HexColor('#143f53')),
    'h3':ParagraphStyle('h3',fontName='BookBold',fontSize=11,leading=16,spaceBefore=12,spaceAfter=10),
    'cell':ParagraphStyle('cell',fontName='Book',fontSize=8,leading=11),
    'code':ParagraphStyle('code',fontName='Mono',fontSize=8,leading=12,spaceAfter=12),
}
def inline(s):
    s=escape(s)
    s=re.sub(r'\*\*(.+?)\*\*',r'<b>\1</b>',s)
    # Long URLs must be breakable in print.
    s=re.sub(r'https?://\S+',lambda m:m[0].replace('/', '/<wbr/>').replace('-', '-<wbr/>'),s)
    return s
story=[]; blocks=text.strip().split('\n\n')
for block in blocks:
    if block.startswith('# '): story.append(Paragraph(inline(block[2:]),styles['h1']))
    elif block.startswith('## '):
        title=block[3:]
        if title not in ['Research manuscript in dissertation format']: story.append(PageBreak())
        story.append(Paragraph(inline(title),styles['h2']))
    elif block.startswith('### '): story.append(Paragraph(inline(block[4:]),styles['h3']))
    elif block.startswith('|'):
        rows=[]
        for line in block.splitlines():
            if re.fullmatch(r'[| :\-]+',line): continue
            rows.append([Paragraph(inline(cell.strip()),styles['cell']) for cell in line.strip('|').split('|')])
        widths=[130]+[(504-130)/(len(rows[0])-1)]*(len(rows[0])-1)
        table=Table(rows,colWidths=widths,repeatRows=1,hAlign='LEFT')
        table.setStyle(TableStyle([('BACKGROUND',(0,0),(-1,0),colors.HexColor('#e4edf1')),('VALIGN',(0,0),(-1,-1),'TOP'),('LINEBELOW',(0,0),(-1,0),.5,colors.HexColor('#8b9fa8')),('BOTTOMPADDING',(0,0),(-1,-1),8),('TOPPADDING',(0,0),(-1,-1),8),('ROWBACKGROUNDS',(0,1),(-1,-1),[colors.white,colors.HexColor('#f7f8f8')])]))
        story.extend([table,Spacer(1,12)])
    elif block.startswith('!['): story.extend([Image(str(ROOT/'results/performance.png'),width=504,height=258),Spacer(1,12)])
    elif block.startswith('    '): story.append(Preformatted('\n'.join(line[4:] for line in block.splitlines()),styles['code']))
    else: story.append(Paragraph(inline(block).replace('\n','<br/>'),styles['body']))
def footer(canvas,doc):
    canvas.saveState(); canvas.setFont('Book',8); canvas.setFillColor(colors.HexColor('#526770'))
    canvas.drawString(54,28,'Formatting-Aware Spreadsheet Auditing | HRL Portfolio')
    canvas.drawRightString(558,28,str(doc.page)); canvas.restoreState()
doc=SimpleDocTemplate(str(ROOT/'dissertation.pdf'),pagesize=(612,792),leftMargin=54,rightMargin=54,topMargin=52,bottomMargin=48,
                      title='Gaussian Mixture Models and Formatting-Aware Statistical Methods for Auditing Linked Excel Spreadsheets',author='Michael Emanuel Glover; developed with Codex')
doc.build(story,onFirstPage=footer,onLaterPages=footer)

css='''
:root{color-scheme:light;--ink:#182f3c;--muted:#526774;--paper:#fafbf9;--line:#d7e0e2;--accent:#186452}*{box-sizing:border-box}body{margin:0;background:var(--paper);color:var(--ink);font:17px/1.8 Georgia,serif}main{max-width:980px;margin:auto;padding:30px clamp(16px,4vw,42px) 80px}nav,.downloads,.status,footer{font:14px/1.7 system-ui,sans-serif}nav{display:flex;gap:24px;flex-wrap:wrap}a{color:var(--accent);text-underline-offset:4px}a:focus-visible{outline:3px solid #a56823;outline-offset:4px}.downloads{display:flex;gap:12px;flex-wrap:wrap;margin:26px 0}.downloads a{padding:8px 14px;border:1px solid var(--line);border-radius:6px;background:white}h1{font-size:clamp(30px,5vw,49px);line-height:1.22;margin-top:42px}h2{font-size:27px;line-height:1.4;margin-top:50px;border-top:1px solid var(--line);padding-top:24px}h3{font-size:21px;line-height:1.4}table{display:block;overflow-x:auto;border-collapse:collapse;width:100%;font:14px/1.6 system-ui,sans-serif;margin:24px 0}td,th{text-align:left;padding:10px;border-bottom:1px solid var(--line);white-space:nowrap}th{background:#e4edf1}tr:nth-child(even){background:#f0f4f1}img{width:100%;height:auto}pre{overflow-x:auto;background:#edf1ef;padding:18px;font-size:13px}p,li{overflow-wrap:anywhere}.status{padding:14px 18px;background:#eaf1ee;border-left:4px solid var(--accent)}footer{margin-top:50px;border-top:1px solid var(--line);padding-top:20px;color:var(--muted)}@media print{nav,.downloads{display:none}body{font-size:11pt}main{max-width:none;padding:0}h2{break-before:page}table{display:table;font-size:8pt}td,th{white-space:normal}a{color:inherit}}
'''
css+='main{width:100%;min-width:0}.table-wrap{width:100%;max-width:100%;overflow-x:auto}table{display:table}.downloads a{max-width:100%}@media print{.table-wrap{overflow:visible}}'
html=f'''<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Formatting-Aware Spreadsheet Auditing — Dissertation | HRL Portfolio</title><meta name="description" content="A substantive research manuscript on Gaussian mixtures, spreadsheet dependencies, semantic formatting, and reproducible auditing experiments."><link rel="canonical" href="https://rmichaelglover.github.io/hrl-portfolio/spreadsheet-dissertation/"><meta property="og:title" content="Formatting-Aware Spreadsheet Auditing"><meta property="og:description" content="Dissertation-format research with executed synthetic Excel experiments, open code, and downloadable PDF."><meta property="og:type" content="article"><style>{css}</style></head><body><main><nav aria-label="Breadcrumb"><a href="../">HRL Portfolio</a><a href="../essays/">Essays and research</a></nav><div class="downloads"><a href="dissertation.pdf">Download PDF</a><a href="dissertation.txt">Plain text</a><a href="dissertation.md">Markdown</a><a href="results/workbooks.zip">56 Excel workbooks + labels</a><a href="experiment.py">Experiment code</a><a href="results/runs.csv">All results</a></div>{web_body}<footer><a href="verify.py">Verification code</a> · <a href="results/manifest.json">Reproducibility manifest</a> · <a href="results/summary.json">Summary and confidence intervals</a> · <a href="results/performance.svg">Export figure (SVG)</a></footer></main></body></html>'''
(ROOT/'index.html').write_text(html)
hashes={str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in [ROOT/'experiment.py',ROOT/'verify.py',ROOT/'manuscript.md',ROOT/'dissertation.pdf',ROOT/'results/runs.csv',ROOT/'results/summary.json']}
(ROOT/'results/artifact-hashes.json').write_text(json.dumps(hashes,indent=2))
print('Built PDF, complete manuscript, plain text, web page, figure, and artifact hashes.')
