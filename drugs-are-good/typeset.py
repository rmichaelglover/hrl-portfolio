from pathlib import Path
import json,re,subprocess,hashlib,zipfile

def escape(text):
    text=text.replace('’',"'").replace('—','-').replace('–','-')
    return ''.join({'&':r'\&','%':r'\%','_':r'\_','#':r'\#'}.get(c,c) for c in text)

def build(base,title,pages,author='Michael Emanuel Glover'):
    B=Path(base);out=[r'''\documentclass[10pt]{article}
\usepackage[a4paper,margin=.72in,headheight=15pt]{geometry}
\usepackage[T1]{fontenc}\usepackage[utf8]{inputenc}\usepackage{lmodern,microtype,amsmath,amssymb,graphicx,xcolor,booktabs,tabularx,hyperref,fancyhdr}
\definecolor{ink}{HTML}{153F50}\definecolor{accent}{HTML}{0072B2}
\setlength{\parindent}{0pt}\setlength{\parskip}{7pt}\setlength{\emergencystretch}{3em}
\hypersetup{colorlinks=true,urlcolor=accent}
\pagestyle{fancy}\fancyhf{}\fancyhead[L]{\small\color{ink}GLOVER | INDEPENDENT RESEARCH WHITE PAPER}\fancyhead[R]{\small 2026}\fancyfoot[C]{\thepage}
\begin{document}
'''];md=[f'# {title}\n\n{author}. Developed in dialogue with Codex. 4 October 2026.\n']
    for i,p in enumerate(pages):
        if i:out.append(r'\clearpage')
        out.append(r'{\small\color{accent}'+escape(p.get('kind','Research argument'))+r'}\par')
        out.append(r'{\LARGE\bfseries\color{ink}'+escape(p['title'])+r'}\par\vspace{7pt}')
        if i==0:out.append(escape(author)+r'\par Developed in dialogue with Codex | 4 October 2026\par\vspace{8pt}')
        md.append(f'\n## {i+1}. {p["title"]}\n')
        for s in p['body']:out.append(escape(s)+r'\par');md.append(s+'\n')
        for eq in p.get('equations',[]):out.append(r'\['+eq+r'\]');md.append('\n\\[\n'+eq+'\n\\]\n')
        if p.get('table'):
            rows=p['table'];n=len(rows[0]);out.append(r'{\small\begin{tabularx}{\linewidth}{'+('X'+'r'*(n-1))+r'}\toprule')
            for j,row in enumerate(rows):out.append(' & '.join(escape(str(v)) for v in row)+r'\\'+(r'\midrule' if j==0 else ''))
            out.append(r'\bottomrule\end{tabularx}}\par');md.append('\n'+'\n'.join('| '+' | '.join(map(str,row))+' |' for row in rows)+'\n')
        if p.get('figure'):
            out.append(r'\begin{center}\includegraphics[width=.97\linewidth,height=.26\textheight,keepaspectratio]{figures/'+p['figure']+r'.pdf}\end{center}')
            out.append(r'{\footnotesize '+escape(p['caption'])+r'\par}');md.append(f'\nFigure: figures/{p["figure"]}.pdf\n{p["caption"]}\n')
        for ref in p.get('references',[]):
            text,url=ref;out.append(r'{\small '+escape(text)+r'\par\url{'+url+r'}\par}');md.append(text+' '+url+'\n')
    out.append(r'\end{document}');(B/'WHITE-PAPER.tex').write_text('\n'.join(out));(B/'MANUSCRIPT.md').write_text('\n'.join(md));(B/'WHITE-PAPER.txt').write_text('\n'.join(md));(B/'page-ledger.json').write_text(json.dumps(pages,indent=2))
    for _ in range(2):
        r=subprocess.run(['pdflatex','-interaction=nonstopmode','-halt-on-error','WHITE-PAPER.tex'],cwd=B,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,text=True)
        if r.returncode:raise RuntimeError(r.stdout[-4000:])
    info=subprocess.check_output(['pdfinfo',str(B/'WHITE-PAPER.pdf')],text=True);n=int(re.search(r'Pages:\s+(\d+)',info).group(1));assert n==len(pages),(title,n,len(pages))
    assert 'Overfull' not in (B/'WHITE-PAPER.log').read_text(),title
    words=len(re.findall(r"\b[\w'-]+\b",' '.join(md)))
    print(title,':',n,'pages;',words,'words')
    return {'title':title,'author':author,'pages':n,'words':words,'figures':len(list((B/'figures').glob('*.pdf')))}

def package(base,metadata):
    B=Path(base);(B/'document-checks.json').write_text(json.dumps({**metadata,'page_count_verified':True,'overfull_boxes':0},indent=2))
    files=[p for p in sorted(B.rglob('*')) if p.is_file() and p.suffix not in ['.aux','.out','.log'] and '__pycache__' not in str(p) and p.name not in ['SOURCE.zip','MANIFEST.json']]
    m={**metadata,'files':[{'path':str(p.relative_to(B)),'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'bytes':p.stat().st_size} for p in files]};(B/'MANIFEST.json').write_text(json.dumps(m,indent=2))
    with zipfile.ZipFile(B/'SOURCE.zip','w',zipfile.ZIP_DEFLATED) as z:
        for p in files+[B/'MANIFEST.json']:z.write(p,Path(B.name)/p.relative_to(B))
    assert zipfile.ZipFile(B/'SOURCE.zip').testzip() is None
    return m
