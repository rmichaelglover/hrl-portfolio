#!/usr/bin/env python3
"""Build the research synthesis from an inspectable manuscript and local evidence.

No experiment is rerun by this builder. Figures redraw recorded results.
Requires Python, ReportLab, Matplotlib, Pillow, and Poppler for verification.
"""
from pathlib import Path
import csv
import hashlib
import html
import json
import re
import subprocess
import sys
import zipfile

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.utils import ImageReader
from reportlab.platypus import (
    BaseDocTemplate, Frame, PageTemplate, Paragraph, Spacer, PageBreak,
    Table, TableStyle, Image, KeepTogether,
)
from reportlab.platypus.tableofcontents import TableOfContents

HERE = Path(__file__).resolve().parent
PORT = HERE.parent
HOME = Path('/home/rmichaelglover')
ROOTS = {
    'portfolio': PORT,
    'publication-study': HOME/'relaxation-publication-study',
    'triadic-study': HOME/'triadic-unity-research',
    'original-python': HOME/'Code/relaxation-labeling/python',
    'ros-package': HOME/'ros2_ws/src/cypher_robot_mind',
    'cybersecurity': HOME/'hrl-cybersecurity-research',
    'oort-study': HOME/'dark-matter-oort-study',
    'milky-way-study': HOME/'dark-matter-milky-way-study',
}

# Each entry has a primary inspected source and selected supporting artifacts.
SOURCES = [
('S01','Public HRL engine and historical applications','portfolio',['hrl/core.py','README.md','hrl/tracking.py','tests/test_core.py','tests/test_tracking.py']),
('S02','Signed sparse support, chirality audit, and causal forecasting','publication-study',['PAPER.md','results/signed_results.json','results/chirality_results.json','results/forecast_results.json','benchmark_signed.py','benchmark_chirality.py']),
('S03','Triadic uncertainty: exact coordinates, controls, and contraction','triadic-study',['REPORT.md','THEORY.md','PROTOCOL.md','FOLLOWUP_PROTOCOL.md','sparse_trool.py','contractive.py']),
('S04','Generic sparse pair and triangle factor engine','original-python',['hrl_generic/README.md','hrl_generic/selftest.py']),
('S05','Simplicial Relax architecture','portfolio',['SIMPLICIAL_RELAX.md']),
('S06','GRRLE Strong executable recursive substrate','portfolio',['grrle-strong/README.md','grrle-strong/python/grrle.py','grrle-strong/python/test_grrle.py']),
('S07','Reciprocal grounding, original study','portfolio',['reciprocal-grounding/WHITEPAPER.md','reciprocal-grounding/data/results.json','reciprocal-grounding/data/runs.csv','hrl/reciprocal.py']),
('S08','Meta-renormalization experiments 001 and 002','portfolio',['meta-renormalization/WHITEPAPER.md','meta-renormalization/data/results.json','meta-renormalization/data/experiment001.json','hrl/meta_discovery.py']),
('S09','Recursive grounding supplement','portfolio',['reciprocal-grounding/RECURSION.md','reciprocal-grounding/data/recursive-results.json','reciprocal-grounding/data/recursive-runs.csv','hrl/recursive_grounding.py']),
('S10','Wearable posture aggregate and implementation','portfolio',['body_pos_data.json','body_pos_testbed.py','hrl/body_pos.py']),
('S11','Recovered train-brake labeling exhibit','portfolio',['beena/index.html']),
('S12','Growing-graph morphology and remodeling','portfolio',['morphogenesis-grow/REPORT.md','morphogenesis_v3.py','morphogenesis_v4.py','morphogenesis/proposal.md']),
('S13','Simplicial morphology','portfolio',['simplicial.py','simplicial3d.py','simplicial3d_data.json','simplicial/roadmap.md']),
('S14','Virtual-body audit, nested repairs, and constant-exposure feasibility','portfolio',['virtual-body-cancer/AUDIT-RESULTS.md','virtual-body-cancer/output/nested-cell-checks.json','virtual-body-cancer/output/extinction-feasibility.json','virtual-body-cancer/analyze_extinction.py']),
('S15','Measured CRISPR group-split ranking','portfolio',['virtual-body-cancer/output/crispr-benchmark.json','virtual-body-cancer/benchmark_existing_crispr.py','virtual-body-cancer/output/feature-extraction-provenance.json']),
('S16','AnnoCTR real-model training pilot','cybersecurity',['PILOT-REPORT.md','DATA-LABELING-PROTOCOL.md']),
('S17','Causal forecast protocol and results','publication-study',['FORECAST_PROTOCOL.md','results/forecast_results.json','benchmark_forecast.py']),
('S18','HyperStar synthetic econometric benchmark','publication-study',['results/hyperstar_benchmark/REPORT.md','results/hyperstar_benchmark/summary.csv','hyperstar_benchmark.py']),
('S19','Economic accounting, frozen WDI descriptions, and synthetic scenarios','portfolio',['magnum-economicus/MANUSCRIPT.md','magnum-economicus/results.json','magnum-economicus/experiment.py']),
('S20','Formatting-aware spreadsheet audit','portfolio',['spreadsheet-dissertation/manuscript.md','spreadsheet-dissertation/results/summary.json','spreadsheet-dissertation/results/runs.csv','spreadsheet-dissertation/experiment.py']),
('S21','WikiMRGRELE lexical/byte experiments and typed ablation','original-python',['wikimrgrele/README.md','wikimrgrele/TYPED_ABLATION_RESULTS.md','wikimrgrele/output/typed_ablation/results.json']),
('S22','Frozen-proposal ProMaster vision checkpoint','original-python',['vision_grrle/README.md']),
('S23','Controlled-English inference and source explorer','portfolio',['ecc-plus/README.md','ecc-plus/corpora/manifest.json','ecc-plus/test-engine.cjs']),
('S24','Relaxfish fixed-position pilot','portfolio',['relaxfish/README.md','relaxfish/data/statistics.json','relaxfish/data/summary.json','relaxfish/data/positions.csv']),
('S25','Corpus-trained relaxed chess brain','portfolio',['relaxed-chess-brain/README.md','relaxed-chess-brain/brain.json','relaxed-chess-brain/build_brain.py']),
('S26','Local reinforced argument-chess results','original-python',['argument_chess/RESULTS.md','argument_chess/REINFORCED_RELAXATION.md']),
('S27','Local tactical chess follow-up','original-python',['argument_chess/TACTICAL_RESULTS.md','argument_chess/TACTICAL_EXPERIMENT.md']),
('S28','Magnum Chessicus bounds and certificates','portfolio',['magnum-chessicus/README.md','magnum-chessicus/results.json','magnum-chessicus/verification.json','magnum-chessicus/data/certificates.json']),
('S29','Local research-guided bounded mate solver','portfolio',['relaxed-chess-brain/solver/README.md','relaxed-chess-brain/solver/solve.py','relaxed-chess-brain/solver/test_solve.py']),
('S30','Rolling chess model and whole-game records','ros-package',['CHESS_PHYSICS.md','cypher_robot_mind/chess_physics.py','cypher_robot_mind/chess_autoplay.py']),
('S31','Merger, lifecycle, and bounded-capture implementation','ros-package',['cypher_robot_mind/hole_topology.py','cypher_robot_mind/chess_lab_node.py']),
('S32','ROS robot and chess validation','ros-package',['VALIDATION.md','README.md']),
('S33','Hyperspace anchored graph mathematics','portfolio',['hyperspace/README.md','hyperspace/paper.tex','hyperspace/metrics.json','hyperspace/convergence.csv']),
('S34','Triadic closure assessment and toy extension','publication-study',['TRIADIC_CLOSURE_EVALUATION.md','results/closure_results.json','results/triangulated_results.json']),
('S35','TQC III bridge evaluation','publication-study',['TQC_III_EVALUATION.md','paper/TQC_III_REPORT.tex']),
('S36','TQC IV typed closure and refinement','publication-study',['paper/TQC_IV_REPORT.tex','src/triangulated_closure.py','benchmark_triangulated.py']),
('S37','Compact GHZ-family representation','portfolio',['magnum-quantreleviathone/MANUSCRIPT.md','magnum-quantreleviathone/results.json','magnum-quantreleviathone/compute.py']),
('S38','Spherical Oort-shell and halo comparison','oort-study',['README.md','results.json','model.py']),
('S39','Milky Way rotation-curve comparison','milky-way-study',['README.md','results.json','model.py']),
('S40','Frozen vertical-force discriminator','milky-way-study',['discrimination-report.md','discrimination-results.json','discrimination-plan.json','working-propositions.md','discrimination.py']),
('S41','HydroGRRLE routed storage and relational interpretation','original-python',['hydro_grrle/README.md']),
('S42','Wave Worlds acoustic path model','portfolio',['wave-worlds/README.md','wave-worlds/model.js']),
('S43','Musical hyperobject and projective field','portfolio',['hyperobject/README.md','hyperobject/hyperobject.json']),
('S44','Geographic chess variant and whole-world initialization','portfolio',['tiny-creek-chess/README.md']),
('S45','Virtual Earth seeded ecological testbed','portfolio',['virtual-earth/README.md','virtual-earth/model.js']),
('S46','HRL Lab numerical inspector','portfolio',['hrl-lab/README.md','hrl-lab/relaxation.js']),
('S47','Genesis SDSS sparse segmentation','portfolio',['genesis/sdss/build_sdss.py','genesis/sdss/data.json']),
('S48','Genesis connectome communities and constructed activity','portfolio',['genesis/brain/build_brain.py','genesis/brain/data.json','genesis/cord/build_cord.py']),
('S49','Genesis SPARC and radial-acceleration displays','portfolio',['genesis/sparc/build_sparc.py','genesis/sparc/data.json','genesis/rar/build_rar.py','genesis/rar/data.json']),
('S50','Genesis correlated cosmological seed construction','portfolio',['genesis/planck/build_planck.py','genesis/planck/data.json']),
]

def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def dump(name, data):
    (HERE/name).write_text(json.dumps(data, indent=2, ensure_ascii=False)+'\n')

def evidence_register():
    records=[]
    for sid,title,root,paths in SOURCES:
        files=[]
        for relative in paths:
            p=ROOTS[root]/relative
            if not p.is_file():
                raise FileNotFoundError(f'{sid}: {p}')
            files.append({'path':relative,'bytes':p.stat().st_size,'sha256':sha(p)})
        records.append({'id':sid,'title':title,'root':root,'files':files})
    dump('evidence-register.json', {
        'edition_date':'2026-10-16','author':'Michael Emanuel Glover',
        'scope':'Selected inspected research artifacts; not a complete drive census or independent replication.',
        'roots':{k:str(v) for k,v in ROOTS.items()}, 'sources':records,
    })
    return '\n\n'.join(f"**{x['id']}. {x['title']}.** {x['root']}: `{x['files'][0]['path']}`." for x in records)

def figures():
    out=HERE/'figures';out.mkdir(exist_ok=True)
    plt.rcParams.update({'font.family':'DejaVu Sans','font.size':10,'axes.spines.top':False,'axes.spines.right':False,'axes.titleweight':'bold','savefig.facecolor':'white'})
    blue='#196c91'; teal='#148578'; orange='#b36322'; gray='#667782'
    def save(fig,name):
        fig.savefig(out/f'{name}.png',dpi=200,bbox_inches='tight')
        fig.savefig(out/f'{name}.pdf',bbox_inches='tight');plt.close(fig)
    fig,axs=plt.subplots(1,2,figsize=(10,3.9),layout='constrained')
    axs[0].bar(['Dense','Factorized\ndense','Sparse'],[.1805,.0418,.00649],color=[gray,blue,teal]);axs[0].set_ylabel('Median runtime (seconds)');axs[0].set_title('1,024-node recorded benchmark')
    axs[1].bar(['Dense kernel','Sparse operators'],[75497472,203848],color=[gray,teal]);axs[1].set_yscale('log');axs[1].set_ylabel('Payload bytes (log scale)');axs[1].set_title('Same structured update')
    save(fig,'sparse')
    fig,ax=plt.subplots(figsize=(10,4),layout='constrained')
    labels=['Pair-supported','Hidden fourth order','Correlated inputs','Additive control'];x=np.arange(4)
    ax.bar(x-.18,[97.90,17.20,81.35,66.40],.36,label='Hierarchical',color=teal)
    ax.bar(x+.18,[97.86,91.28,99.08,65.79],.36,label='Exhaustive degree-four',color=blue)
    ax.set_xticks(x,labels);ax.set_ylim(0,112);ax.set_ylabel('Mean held-out explained variance (%)');ax.set_title('Interaction grammar: success and blind spots');ax.legend(loc='lower right');save(fig,'discovery')
    fig,axs=plt.subplots(1,2,figsize=(10,4),layout='constrained')
    for label,cov,acc,col in [('Forward',50.12,95.01,gray),('Reciprocal',41.50,98.80,teal),('Copied reverse',53.87,98.14,blue),('No relaxation',39.25,98.73,orange)]:
        axs[0].scatter(cov,acc,s=70,color=col);axs[0].annotate(label,(cov,acc),xytext=(4,-14 if label=='No relaxation' else 6),textcoords='offset points',fontsize=9)
    axs[0].set(xlim=(35,65),ylim=(93.5,100),xlabel='Coverage (%)',ylabel='Accepted accuracy (%)',title='Original independent-view study')
    axs[1].bar(['Independent\nviews','Shared wrong\ndictionary'],[98.80,0],color=[teal,orange]);axs[1].set_ylim(0,105);axs[1].set_ylabel('Accepted accuracy (%)');axs[1].set_title('Agreement can preserve shared error');axs[1].text(1,4,'0 / 338 correct',ha='center',fontsize=10)
    save(fig,'grounding')
    summary=json.loads((PORT/'spreadsheet-dissertation/results/summary.json').read_text())
    scenarios=['semantic','decorative','reversed']
    # Use exact scenario labels from the artifact; refuse silent substitutions.
    assert set(scenarios)<=set(r['scenario'] for r in summary)
    vals=[next(r['ap'] for r in summary if r['scenario']==s and r['method']=='format_gmm') for s in scenarios]
    fig,axs=plt.subplots(1,2,figsize=(10,4),layout='constrained')
    axs[0].bar(['Semantic','Decorative','Reversed'],vals,color=[teal,gray,orange]);axs[0].set_ylim(0,.85);axs[0].set_ylabel('Mean average precision');axs[0].set_title('Formatting-aware model')
    rows=[next(r for r in summary if r['scenario']=='semantic' and r['method']==m) for m in ['column_mode','global_gmm','format_gmm']]
    x=np.arange(3)
    axs[1].bar(x-.18,[r['ap'] for r in rows],.36,color=blue,label='Average precision')
    axs[1].bar(x+.18,[r['recall_at_5pct'] for r in rows],.36,color=teal,label='Recall: 54-cell budget')
    axs[1].set_xticks(x,['Column rule','Global GMM','Format GMM']);axs[1].set_ylim(0,1);axs[1].legend(fontsize=8);axs[1].set_title('Different metrics, different rankings');save(fig,'spreadsheets')
    fig,ax=plt.subplots(figsize=(9.7,3.7),layout='constrained')
    ax.loglog([2,4,8,16,32],[3.25e-4,2.03e-5,1.27e-6,7.95e-8,4.89e-9],'o-',color=teal)
    ax.set_xticks([2,4,8,16,32],['2','4','8','16','32']);ax.set(xlabel='Mesh parameter n',ylabel='Absolute action error',title='Flat-background U(1): target action 0.25');ax.grid(alpha=.2);save(fig,'refinement')
    fig,axs=plt.subplots(1,2,figsize=(10,3.9),layout='constrained')
    axs[0].bar(['Lighter baryons','Heavier baryons'],[1.96,2.28],color=[blue,teal]);axs[0].set_ylabel('Rotation-fit RMS (km/s)');axs[0].set_title('Previously fitted interval')
    axs[1].bar(['Lighter baryons','Heavier baryons'],[1792.06,2258.55],color=[blue,teal]);axs[1].set_ylabel('Predicted |Kz|, (km/s)²/kpc');axs[1].set_title('Frozen vertical-force prediction')
    save(fig,'astronomy')
    dump('figure-data.json',{
        'note':'Redrawn historical results, not new benchmark executions; rounded values follow source reports.',
        'sparse':{'source':'S02','seconds':[.1805,.0418,.00649],'bytes':[75497472,203848]},
        'discovery':{'source':'S08','hierarchy':[97.90,17.20,81.35,66.40],'exhaustive':[97.86,91.28,99.08,65.79]},
        'grounding':{'source':'S07','forward':[50.12,95.01],'reciprocal':[41.50,98.80],'copied_reverse':[53.87,98.14],'no_relaxation':[39.25,98.73]},
        'spreadsheets':{'source':'S20','scenarios':scenarios,'format_ap':vals,'semantic_comparison':rows},
        'refinement':{'source':'S34/S36','n':[2,4,8,16,32],'error':[3.25e-4,2.03e-5,1.27e-6,7.95e-8,4.89e-9]},
        'astronomy':{'source':'S40','rotation_rms':[1.96,2.28],'vertical_force':[1792.06,2258.55]},
    })

def rich(text):
    text=html.escape(text)
    text=re.sub(r'\*\*(.+?)\*\*',r'<b>\1</b>',text)
    text=re.sub(r'`(.+?)`',r'<font name="Mono" size="8.3">\1</font>',text)
    text=re.sub(r'\[([^\]]+)\]\(([^)]+)\)',r'<link href="\2" color="#196c91">\1</link>',text)
    return text

def register_fonts():
    root=Path('/usr/share/fonts/truetype/dejavu')
    for name,file in [('Body','DejaVuSerif.ttf'),('BodyBold','DejaVuSerif-Bold.ttf'),('BodyItalic','DejaVuSerif-Italic.ttf'),('Sans','DejaVuSans.ttf'),('SansBold','DejaVuSans-Bold.ttf'),('Mono','DejaVuSansMono.ttf')]:
        pdfmetrics.registerFont(TTFont(name,str(root/file)))
    pdfmetrics.registerFontFamily('Body',normal='Body',bold='BodyBold',italic='BodyItalic',boldItalic='BodyBold')
    pdfmetrics.registerFontFamily('Sans',normal='Sans',bold='SansBold',italic='Sans',boldItalic='SansBold')

NAVY=colors.HexColor('#173849');TEAL=colors.HexColor('#147d76')
STYLES={}

class PaperDoc(BaseDocTemplate):
    def afterFlowable(self, flow):
        if isinstance(flow,Paragraph) and getattr(flow,'toc_heading',False):
            text=flow.getPlainText(); key='section-'+str(getattr(flow,'section_index',0))
            self.canv.bookmarkPage(key)
            self.canv.addOutlineEntry(text,key,level=0,closed=False)
            self.notify('TOCEntry',(0,text,self.page,key))

def page_decoration(canvas,doc):
    canvas.saveState()
    w,h=doc.pagesize
    if doc.page>1:
        canvas.setStrokeColor(colors.HexColor('#c7d5d9'));canvas.setLineWidth(.5);canvas.line(49,h-39,w-49,h-39)
        canvas.setFillColor(NAVY);canvas.setFont('Sans',8)
        canvas.drawString(49,h-30,'RELATIONSHIPS THAT COMPUTE')
        canvas.drawRightString(w-49,h-30,'GLOVER LABS · RESEARCH SYNTHESIS')
    canvas.setFillColor(colors.HexColor('#55717d'));canvas.setFont('Sans',8)
    canvas.drawString(49,29,'Michael Emanuel Glover · 16 October 2026 · v1.0')
    canvas.drawRightString(w-49,29,str(doc.page));canvas.restoreState()

def build_pdf(text):
    register_fonts()
    STYLES.update({
        'body':ParagraphStyle('Body',fontName='Body',fontSize=10.3,leading=15.0,spaceAfter=9,textColor=colors.HexColor('#1a2d36'),splitLongWords=True),
        'h2':ParagraphStyle('H2',fontName='SansBold',fontSize=16,leading=20,spaceBefore=20,spaceAfter=11,textColor=NAVY,keepWithNext=True),
        'h3':ParagraphStyle('H3',fontName='SansBold',fontSize=12,leading=16,spaceBefore=12,spaceAfter=8,textColor=TEAL,keepWithNext=True),
        'table':ParagraphStyle('Cell',fontName='Sans',fontSize=8.2,leading=11,spaceAfter=0,splitLongWords=True),
        'thead':ParagraphStyle('HeadCell',fontName='SansBold',fontSize=8.2,leading=11,textColor=colors.white),
        'caption':ParagraphStyle('Caption',fontName='Sans',fontSize=8.6,leading=12,spaceAfter=13,textColor=colors.HexColor('#4c6672')),
        'source':ParagraphStyle('Source',fontName='Body',fontSize=9.2,leading=12.5,spaceAfter=7,textColor=colors.HexColor('#1a2d36'),splitLongWords=True),
        'cover':ParagraphStyle('Cover',fontName='SansBold',fontSize=35,leading=40,textColor=NAVY,spaceAfter=20),
        'subtitle':ParagraphStyle('Subtitle',fontName='Sans',fontSize=19,leading=26,textColor=TEAL,spaceAfter=24),
    })
    width=514
    doc=PaperDoc(str(HERE/'RELATIONSHIPS-THAT-COMPUTE.pdf'),pagesize=(612,792),leftMargin=49,rightMargin=49,topMargin=57,bottomMargin=49,title='Relationships That Compute: Research Results Across the HRL Portfolio',author='Michael Emanuel Glover',subject='Evidence-grounded research synthesis including local unpublished work')
    frame=Frame(49,49,width,686,leftPadding=0,rightPadding=0,topPadding=0,bottomPadding=0)
    doc.addPageTemplates(PageTemplate(id='main',frames=frame,onPage=page_decoration))
    story=[Spacer(1,70),Paragraph('RELATIONSHIPS<br/>THAT COMPUTE',STYLES['cover']),Paragraph('Research Results Across<br/>the HRL Portfolio',STYLES['subtitle']),Paragraph('Michael Emanuel Glover',STYLES['h2']),Paragraph('Glover Labs · Independent research<br/>16 October 2026 · Version 1.0',STYLES['body']),Spacer(1,25),Paragraph('Formal results. Measured observations. Controlled experiments. Executable systems.',STYLES['h3']),Paragraph('Including local research not yet incorporated into the public portfolio. A synthesis of results, their evidence, and the next tests that can change the conclusions.',STYLES['body']),Spacer(1,20),Paragraph('“Show the rule. Show the data. Show the counterexample. Preserve what remains unresolved.”',STYLES['body']),PageBreak()]
    toc=TableOfContents();toc.levelStyles=[ParagraphStyle('TOC',fontName='Sans',fontSize=8.5,leading=11.7,spaceBefore=2.5,leftIndent=0,firstLineIndent=0,rightIndent=24)]
    story.extend([Paragraph('Contents',STYLES['h2']),toc,PageBreak()])
    lines=text.splitlines();i=0;section_index=0;source_mode=False
    # Front matter is rendered after contents; cover already carries title/author.
    while i<len(lines) and not lines[i].startswith('**Authorship.'):i+=1
    while i<len(lines):
        line=lines[i].strip()
        if not line:i+=1;continue
        if line.startswith('## '):
            section_index+=1
            source_mode=line=='## Source register'
            if line.startswith('## Appendix A') or line=='## Source register':story.append(PageBreak())
            p=Paragraph(rich(line[3:]),STYLES['h2']);p.toc_heading=True;p.section_index=section_index;story.append(p);i+=1;continue
        if line.startswith('### '):story.append(Paragraph(rich(line[4:]),STYLES['h3']));i+=1;continue
        if line.startswith('!['):
            m=re.fullmatch(r'!\[(.*?)\]\((.*?)\)',line)
            path=HERE/m.group(2);iw,ih=ImageReader(str(path)).getSize();height=width*ih/iw
            story.append(KeepTogether([Image(str(path),width=width,height=height),Spacer(1,7),Paragraph(rich(m.group(1)),STYLES['caption'])]));i+=1;continue
        if line.startswith('|'):
            rows=[]
            while i<len(lines) and lines[i].strip().startswith('|'):
                cells=[c.strip() for c in lines[i].strip().strip('|').split('|')]
                if not all(re.fullmatch(r'[:\- ]+',c) for c in cells):rows.append(cells)
                i+=1
            n=len(rows[0]);weights={3:[.29,.22,.49],4:[.40,.20,.20,.20],5:[.36,.16,.16,.16,.16]}.get(n,[1/n]*n)
            if rows[0][0]=='Method' and n==4:weights=[.40,.20,.20,.20]
            table=Table([[Paragraph(rich(c),STYLES['thead' if j==0 else 'table']) for c in row] for j,row in enumerate(rows)],colWidths=[width*x for x in weights],repeatRows=1,hAlign='LEFT')
            table.setStyle(TableStyle([('BACKGROUND',(0,0),(-1,0),NAVY),('VALIGN',(0,0),(-1,-1),'TOP'),('LEFTPADDING',(0,0),(-1,-1),7),('RIGHTPADDING',(0,0),(-1,-1),7),('TOPPADDING',(0,0),(-1,-1),7),('BOTTOMPADDING',(0,0),(-1,-1),7),('ROWBACKGROUNDS',(0,1),(-1,-1),[colors.HexColor('#edf4f4'),colors.white]),('LINEBELOW',(0,0),(-1,0),.5,TEAL)]))
            story.extend([table,Spacer(1,12)]);continue
        para=[line];i+=1
        while i<len(lines) and lines[i].strip() and not lines[i].startswith(('##','![','|')):
            para.append(lines[i].strip());i+=1
        story.append(Paragraph(rich(' '.join(para)),STYLES['source' if source_mode else 'body']))
    doc.multiBuild(story)

def numerical_checks():
    checks=[]
    def check(name,ok,source):
        checks.append({'claim':name,'passed':bool(ok),'source':source})
        assert ok,name
    d=json.loads((PORT/'body_pos_data.json').read_text())
    check('Wearable aggregate: 23 subjects and 85.2% mean accuracy',d['n_subj']==23 and abs(d['mean_acc']-.852)<1e-12,'S10')
    d=json.loads((PORT/'magnum-chessicus/results.json').read_text())
    check('Initial chess search remains unresolved at depth three',d['initial_search'][-1]['nodes']==9323 and d['initial_search'][-1]['lower']==-1 and d['initial_search'][-1]['upper']==1,'S28')
    check('Three accepted small chess certificates',d['certificate_checks']['accepted']==3 and d['certificate_checks']['incorrect_mate_witness_rejected'],'S28')
    d=json.loads((PORT/'relaxfish/data/statistics.json').read_text())
    check('Relaxfish exact agreement test p=.125',abs(d['mcnemar_exact_p']-.125)<1e-12,'S24')
    d=json.loads((PORT/'hyperspace/metrics.json').read_text())
    check('Anchored graph absorption comparison',abs(d['Geographic cycle']['max_expected_absorption_steps']-800)<1e-8 and abs(d['Cycle + information links']['max_expected_absorption_steps']-326.77858615626013)<1e-8,'S33')
    d=json.loads((PORT/'magnum-quantreleviathone/results.json').read_text())
    check('Nineteen checked GHZ circuits with 20-qubit payload comparison',len(d)==19 and d[-1]['qubits']==20 and d[-1]['dense_bytes']==16777216 and d[-1]['sparse_payload_bytes']==48,'S37')
    d=json.loads((PORT/'magnum-economicus/results.json').read_text())
    check('Economic snapshot: 150 nonmissing and 30 missing',d['source_nonnull_observations']==150 and d['missing_observations']==30,'S19')
    d=json.loads((PORT/'rolling-chess-ros/whole-game-validation.json').read_text())
    check('Recorded full rolling games: 65 and 161 plies',[r['plies'] for r in d]==[65,161] and all(r['collisions']==0 for r in d),'S30/S32')
    d=json.loads((PORT/'genesis/sdss/data.json').read_text())
    check('SDSS algorithmic partition totals 25,000',d['N']==25000 and d['counts']=={'void':4504,'filament':14091,'cluster':6405},'S47')
    d=json.loads((PORT/'genesis/brain/data.json').read_text())
    check('Connectome partition has lower modularity than recorded comparator',d['n']==399 and d['Q']==.439 and d['Qnx']==.509,'S48')
    d=json.loads((PORT/'genesis/rar/data.json').read_text())
    check('RAR display source coverage',d['n_gal']==165 and d['n_pts']==3343,'S49')
    d=json.loads((ROOTS['publication-study']/'results/signed_results.json').read_text())
    large=d['scaling'][-1]
    check('100,000-node actual sparse operators versus hypothetical dense bytes',large['n']==100000 and large['operator_bytes']==19999168 and large['hypothetical_dense_kernel_bytes']==720000000000,'S02')
    d=json.loads((PORT/'meta-renormalization/data/results.json').read_text())
    relaxed=next(r for r in d['results'] if r['scenario']=='Pair-supported hierarchy' and r['method']=='Hierarchical relaxation')
    ablated=next(r for r in d['results'] if r['scenario']=='Pair-supported hierarchy' and r['method']=='Hierarchy without relaxation')
    check('Principal discovery gain cannot be attributed to relaxation',relaxed['mse']==ablated['mse'] and relaxed['parameters']==14 and relaxed['support_recall']==1,'S08')
    d=json.loads((PORT/'reciprocal-grounding/data/results.json').read_text())
    good=next(r for r in d['results'] if r['scenario']=='Independent views' and r['method']=='Reciprocal')
    wrong=next(r for r in d['results'] if r['scenario']=='Shared wrong dictionary' and r['method']=='Reciprocal')
    check('Reciprocal JSON match counts and shared-error failure',good['correct']==328 and good['accepted']==332 and wrong['correct']==0 and wrong['accepted']==338,'S07')
    text=(PORT/'reciprocal-grounding/WHITEPAPER.md').read_text()
    check('Reciprocal match counts and shared-error counterexample',all(s in text for s in ['328/332','381/401','338']),'S07')
    text=(PORT/'meta-renormalization/WHITEPAPER.md').read_text()
    check('Discovery principal and failure results retained',all(s in text for s in ['97.90%','0.09076','17.20%','91.28%','81.35%','99.08%']),'S08')
    text=(ROOTS['cybersecurity']/'PILOT-REPORT.md').read_text()
    check('Cybersecurity pooling remains stronger than HRL in the pilot','0.608' in text and '0.548' in text,'S16')
    text=(PORT/'virtual-body-cancer/AUDIT-RESULTS.md').read_text()
    check('CRISPR split metrics and infeasible exposure thresholds preserved',all(s in text for s in ['0.480544','0.403291','5.181195','0.136364']),'S14/S15')
    dump('claim-checks.json',{'scope':'Selected key numerical claims checked against source JSON or exact source-report values; not a rerun of scientific benchmarks.','checks':checks})

def main():
    register=evidence_register()
    source=HERE/'WHITE-PAPER.md'
    text=source.read_text()
    if '{{SOURCE_REGISTER}}' in text:
        text=text.replace('{{SOURCE_REGISTER}}',register);source.write_text(text)
    else:
        text=text.split('## Source register')[0]+'## Source register\n\nThe following primary project artifacts are identified by source ID. Complete supporting-file hashes are in `evidence-register.json`.\n\n'+register+'\n'
        source.write_text(text)
    figures();numerical_checks();build_pdf(text)
    subprocess.run(['pdftotext','-layout',str(HERE/'RELATIONSHIPS-THAT-COMPUTE.pdf'),str(HERE/'RELATIONSHIPS-THAT-COMPUTE.txt')],check=True)
    info=subprocess.check_output(['pdfinfo',str(HERE/'RELATIONSHIPS-THAT-COMPUTE.pdf')],text=True)
    pages=int(re.search(r'^Pages:\s+(\d+)',info,re.M).group(1));assert pages>=20
    extracted=(HERE/'RELATIONSHIPS-THAT-COMPUTE.txt').read_text()
    assert '\ufffd' not in extracted
    assert all(f'{n}. ' in extracted for n in range(1,44))
    assert '{{SOURCE_REGISTER}}' not in text
    cited=set(re.findall(r'S\d\d',text));assert cited=={s[0] for s in SOURCES}
    # All glyphs used in prose and tables must exist in the embedded font family.
    from fontTools.ttLib import TTFont as FontToolsFont
    cmap=FontToolsFont('/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf').getBestCmap()
    missing=sorted({c for c in text if ord(c)>127 and ord(c) not in cmap})
    assert not missing,missing
    dump('document-checks.json',{'title':'Relationships That Compute','author':'Michael Emanuel Glover','date':'2026-10-16','pages':pages,'manuscript_words':len(text.split()),'numbered_sections':43,'appendices':6,'source_groups':len(SOURCES),'source_files':sum(len(x[3]) for x in SOURCES),'figure_pairs':6,'minimum_pages_verified':True,'replacement_characters':0,'missing_prose_glyphs':missing,'all_source_ids_present':True,'scientific_benchmarks_rerun':False})
    selected=[]
    for p in sorted(HERE.rglob('*')):
        if p.is_file() and p.name not in ['MANIFEST.json','RESEARCH-SYNTHESIS-SOURCE.zip'] and '__pycache__' not in p.parts:
            selected.append({'path':str(p.relative_to(HERE)),'bytes':p.stat().st_size,'sha256':sha(p)})
    dump('MANIFEST.json',{'author':'Michael Emanuel Glover','date':'2026-10-16','files':selected})
    with zipfile.ZipFile(HERE/'RESEARCH-SYNTHESIS-SOURCE.zip','w',zipfile.ZIP_DEFLATED) as z:
        for f in selected:z.write(HERE/f['path'],f['path'])
        z.write(HERE/'MANIFEST.json','MANIFEST.json')
    print(json.dumps({'pages':pages,'words':len(text.split()),'sources':len(SOURCES),'files':sum(len(x[3]) for x in SOURCES),'pdf':str(HERE/'RELATIONSHIPS-THAT-COMPUTE.pdf')},indent=2))

if __name__=='__main__':main()
