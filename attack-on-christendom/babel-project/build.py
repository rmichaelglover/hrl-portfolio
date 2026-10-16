#!/usr/bin/env python3
"""Rebuild a sourced theological argument and check its finite illustrations.

No physical experiment, proof of God's existence, or AI benchmark is performed.
"""
from pathlib import Path
import hashlib
import html
import json
import math
import re
import subprocess
import zipfile
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib import colors
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.utils import ImageReader
from reportlab.platypus import BaseDocTemplate, Frame, PageTemplate, Paragraph, Spacer, PageBreak, Image, KeepTogether, Table, TableStyle
from reportlab.platypus.tableofcontents import TableOfContents

ROOT=Path(__file__).resolve().parent
NAVY=colors.HexColor('#173849')
TEAL=colors.HexColor('#147d76')

def dump(name,data):
    (ROOT/name).write_text(json.dumps(data,indent=2,ensure_ascii=False)+'\n')

def rich(s):
    s=html.escape(s)
    s=re.sub(r'\*\*(.*?)\*\*',r'<b>\1</b>',s)
    s=re.sub(r'`([^`]+)`',r'<font name="Mono">\1</font>',s)
    s=re.sub(r'(https://[^\s<>]+)',lambda m:'<link color="#146d88" href="'+m[1]+'">'+m[1]+'</link>',s)
    return s

def illustrations():
    out=ROOT/'figures';out.mkdir(exist_ok=True)
    counts=[]
    for n in [1,2,3,4,5,6,8,10]:
        inputs=1<<n;functions=1<<inputs
        assert functions.bit_length()==inputs+1
        counts.append({'input_bits':n,'inputs':inputs,'truth_table_bits':inputs,'boolean_functions_exact':str(functions),'boolean_function_decimal_digits':len(str(functions))})
    assert counts[-1]['inputs']==1024
    overlap=1/math.sqrt(2);copied=overlap**2
    assert abs(copied-.5)<1e-15 and abs(overlap-copied)>.2
    examples=[{'initial_error':e,'tolerated_error':.1,'lambda':1.,'horizon':math.log(.1/e)} for e in [.01,.0001,.000001]]
    for e in examples:assert abs(e['initial_error']*math.exp(e['horizon'])-.1)<1e-14
    dump('calculations.json',{'status':'Exact finite counts and stipulated analytic illustrations; no empirical result or theological proof.','counting':counts,'hundred_bit_configurations_exact':str(1<<100),'cloning':{'initial_overlap':overlap,'proposed_copied_overlap':copied,'unitary_preservation_residual':abs(overlap-copied)},'sensitivity':examples,'checks_passed':True})
    plt.rcParams.update({'font.family':'DejaVu Sans','font.size':10,'axes.spines.top':False,'axes.spines.right':False})
    fig,axs=plt.subplots(1,2,figsize=(10,3.6),layout='constrained')
    n=np.arange(1,11)
    axs[0].plot(n,2.**n,'o-',color='#147d76');axs[0].set_yscale('log',base=2);axs[0].set(xlabel='Input bits n',ylabel='Input configurations / table bits',title='Finite inputs: 2ⁿ')
    axs[1].plot(n,(2.**n)*math.log10(2),'o-',color='#196c91');axs[1].set(xlabel='Input bits n',ylabel='log₁₀ of number of Boolean functions',title='Functions: 2^(2ⁿ)')
    for ax in axs:ax.grid(alpha=.2)
    for ext in ['png','pdf']:fig.savefig(out/f'counting.{ext}',dpi=200,bbox_inches='tight')
    plt.close(fig)
    fig,ax=plt.subplots(figsize=(10,3.5),layout='constrained');t=np.linspace(0,12,500)
    for e in examples:ax.semilogy(t,e['initial_error']*np.exp(t),label=f"Initial error {e['initial_error']:g}")
    ax.axhline(.1,color='black',linestyle='--',label='Stipulated tolerance 0.1');ax.set(xlabel='Illustrative time units',ylabel='Error in the stipulated model',title='Sensitivity example: δ(t) = δ(0) exp(t)');ax.legend(fontsize=8);ax.grid(alpha=.2)
    for ext in ['png','pdf']:fig.savefig(out/f'horizon.{ext}',dpi=200,bbox_inches='tight')
    plt.close(fig)

class Doc(BaseDocTemplate):
    def afterFlowable(self,f):
        if isinstance(f,Paragraph) and getattr(f,'heading',False):
            key=f'section-{f.number}';self.canv.bookmarkPage(key);self.canv.addOutlineEntry(f.getPlainText(),key,0,False);self.notify('TOCEntry',(0,f.getPlainText(),self.page,key))

def decorate(c,d):
    c.saveState();c.setFont('Sans',8);c.setFillColor(NAVY)
    if d.page>1:
        c.drawString(49,762,'NO MACHINE WILL BE GOD');c.drawRightString(563,762,'THE BABEL PROJECT · GLOVER LABS')
        c.setStrokeColor(colors.HexColor('#c7d5d9'));c.line(49,753,563,753)
    c.setFillColor(colors.HexColor('#506b76'));c.drawString(49,29,'Michael Emanuel Glover · 16 October 2026 · v1.0');c.drawRightString(563,29,str(d.page));c.restoreState()

def pdf(text):
    fonts=Path('/usr/share/fonts/truetype/dejavu')
    for name,file in [('Body','DejaVuSerif.ttf'),('BodyBold','DejaVuSerif-Bold.ttf'),('Sans','DejaVuSans.ttf'),('SansBold','DejaVuSans-Bold.ttf'),('Mono','DejaVuSansMono.ttf')]:pdfmetrics.registerFont(TTFont(name,str(fonts/file)))
    pdfmetrics.registerFontFamily('Body',normal='Body',bold='BodyBold',italic='Body',boldItalic='BodyBold')
    pdfmetrics.registerFontFamily('Sans',normal='Sans',bold='SansBold',italic='Sans',boldItalic='SansBold')
    styles={
        'body':ParagraphStyle('body',fontName='Body',fontSize=10.5,leading=15.4,spaceAfter=10,textColor=colors.HexColor('#1a2d36')),
        'h2':ParagraphStyle('h2',fontName='SansBold',fontSize=16,leading=21,spaceBefore=18,spaceAfter=11,textColor=NAVY,keepWithNext=True),
        'title':ParagraphStyle('title',fontName='SansBold',fontSize=38,leading=43,spaceAfter=25,textColor=NAVY),
        'sub':ParagraphStyle('sub',fontName='Sans',fontSize=20,leading=27,spaceAfter=23,textColor=TEAL),
        'caption':ParagraphStyle('caption',fontName='Sans',fontSize=9,leading=12,spaceAfter=14,textColor=colors.HexColor('#506b76')),
        'cell':ParagraphStyle('cell',fontName='Sans',fontSize=8.6,leading=12),
        'thead':ParagraphStyle('thead',fontName='SansBold',fontSize=8.6,leading=12,textColor=colors.white),
        'ref':ParagraphStyle('ref',fontName='Body',fontSize=9.3,leading=13.4,spaceAfter=10,splitLongWords=True),
    }
    doc=Doc(str(ROOT/'NO-MACHINE-WILL-BE-GOD.pdf'),pagesize=(612,792),leftMargin=49,rightMargin=49,topMargin=57,bottomMargin=49,title='No Machine Will Be God: The Babel Project',author='Michael Emanuel Glover',subject='A philosophical and theological argument with explicit scientific boundaries')
    doc.addPageTemplates(PageTemplate(id='body',frames=Frame(49,49,514,686,leftPadding=0,rightPadding=0,topPadding=0,bottomPadding=0),onPage=decorate))
    story=[Spacer(1,70),Paragraph('NO MACHINE<br/>WILL BE GOD',styles['title']),Paragraph('The Babel Project,<br/>Anti-Reductionism,<br/>and the Difference Between<br/>Making and Sustaining',styles['sub']),Paragraph('Michael Emanuel Glover',styles['h2']),Paragraph('Glover Labs · 16 October 2026<br/>Philosophical and theological companion paper',styles['body']),Spacer(1,30),Paragraph('“Build the good workshop. Care for the people in it. Receive its bounty with gratitude. Refuse to worship its machinery.”',styles['body']),PageBreak()]
    toc=TableOfContents();toc.levelStyles=[ParagraphStyle('toc',fontName='Sans',fontSize=9,leading=12,spaceBefore=4,rightIndent=25)]
    story.extend([Paragraph('Contents',styles['h2']),toc,PageBreak()])
    lines=text.splitlines();i=0;number=0;refs=False
    while not lines[i].startswith('**Authorship'):i+=1
    while i<len(lines):
        line=lines[i].strip()
        if not line:i+=1;continue
        if line.startswith('## '):
            title=line[3:];number+=1;refs=title=='References and reading record'
            if refs:story.append(PageBreak())
            f=Paragraph(rich(title),styles['h2']);f.heading=True;f.number=number;story.append(f);i+=1;continue
        if line.startswith('!['):
            m=re.fullmatch(r'!\[(.*?)\]\((.*?)\)',line);path=ROOT/m[2];w,h=ImageReader(str(path)).getSize()
            story.append(KeepTogether([Image(str(path),width=514,height=514*h/w),Spacer(1,6),Paragraph(rich(m[1]),styles['caption'])]));i+=1;continue
        if line.startswith('|'):
            rows=[]
            while i<len(lines) and lines[i].strip().startswith('|'):
                cells=[x.strip() for x in lines[i].strip().strip('|').split('|')]
                if not all(re.fullmatch(r'[-: ]+',x) for x in cells):rows.append(cells)
                i+=1
            t=Table([[Paragraph(rich(x),styles['thead' if j==0 else 'cell']) for x in row] for j,row in enumerate(rows)],colWidths=[185,160,169],repeatRows=1)
            t.setStyle(TableStyle([('BACKGROUND',(0,0),(-1,0),NAVY),('VALIGN',(0,0),(-1,-1),'TOP'),('ROWBACKGROUNDS',(0,1),(-1,-1),[colors.HexColor('#edf4f4'),colors.white]),('LEFTPADDING',(0,0),(-1,-1),7),('RIGHTPADDING',(0,0),(-1,-1),7),('TOPPADDING',(0,0),(-1,-1),7),('BOTTOMPADDING',(0,0),(-1,-1),7)]));story.extend([t,Spacer(1,12)]);continue
        p=[line];i+=1
        while i<len(lines) and lines[i].strip() and not lines[i].startswith(('##','![','|')):p.append(lines[i].strip());i+=1
        story.append(Paragraph(rich(' '.join(p)),styles['ref' if refs else 'body']))
    doc.multiBuild(story)

def main():
    text=(ROOT/'WHITE-PAPER.md').read_text();illustrations();pdf(text)
    p=ROOT/'NO-MACHINE-WILL-BE-GOD.pdf'
    subprocess.run(['pdftotext','-layout',str(p),str(ROOT/'NO-MACHINE-WILL-BE-GOD.txt')],check=True)
    info=subprocess.check_output(['pdfinfo',str(p)],text=True);pages=int(re.search(r'^Pages:\s+(\d+)',info,re.M)[1]);assert pages>=20
    extracted=(ROOT/'NO-MACHINE-WILL-BE-GOD.txt').read_text();assert '\ufffd' not in extracted
    assert text.count('(Cypher)')==extracted.count('(Cypher)')
    assert all(f'{n}. ' in extracted for n in range(1,31))
    assert all(f'R{n}.' in extracted for n in range(1,16))
    from fontTools.ttLib import TTFont as FT
    cmap=FT('/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf').getBestCmap()
    missing=sorted({c for c in text if ord(c)>127 and ord(c) not in cmap});assert not missing,missing
    dump('document-checks.json',{'title':'No Machine Will Be God','author':'Michael Emanuel Glover','date':'2026-10-16','pages':pages,'words':len(text.split()),'numbered_sections':30,'appendices':3,'references':15,'cypher_markers':text.count('(Cypher)'),'marker_count_preserved_in_pdf':True,'figures':2,'missing_prose_glyphs':missing,'mathematical_illustrations_checked':True,'empirical_theological_proof_claimed':False,'publication_status':'Attack on Christendom · Christian Apologetics journal edition; this builder does not deploy.'})
    files=[]
    for f in sorted(ROOT.rglob('*')):
        if f.is_file() and f.name not in ['MANIFEST.json','BABEL-PROJECT-SOURCE.zip'] and '__pycache__' not in f.parts:files.append({'path':str(f.relative_to(ROOT)),'bytes':f.stat().st_size,'sha256':hashlib.sha256(f.read_bytes()).hexdigest()})
    dump('MANIFEST.json',{'author':'Michael Emanuel Glover','files':files})
    with zipfile.ZipFile(ROOT/'BABEL-PROJECT-SOURCE.zip','w',zipfile.ZIP_DEFLATED) as z:
        for f in files:z.write(ROOT/f['path'],f['path'])
        z.write(ROOT/'MANIFEST.json','MANIFEST.json')
    print(json.dumps({'pages':pages,'words':len(text.split()),'cypher_markers':text.count('(Cypher)'),'pdf':str(p)},indent=2))

if __name__=='__main__':main()
