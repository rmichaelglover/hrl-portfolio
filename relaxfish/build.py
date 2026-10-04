#!/usr/bin/env python3
from pathlib import Path
import re,json,subprocess,hashlib,zipfile
R=Path(__file__).resolve().parent;summary=json.loads((R/'data/summary.json').read_text());results=json.loads((R/'data/results.json').read_text())
def escape(s):
 # Preserve inline mathematics and raw display equations.
 parts=re.split(r'(\$[^$]+\$)',s)
 for i in range(0,len(parts),2):
  parts[i]=parts[i].replace('\\','\\textbackslash{}').replace('&','\\&').replace('%','\\%').replace('_','\\_').replace('#','\\#')
  parts[i]=parts[i].replace('`','').replace('≤',r'$\le$').replace('≥',r'$\ge$').replace('−','-').replace('×',r'$\times$').replace('’',"'").replace('“','``').replace('”',"''").replace('–','--').replace('—','---')
 return re.sub(r'\*\*(.*?)\*\*',r'\\textbf{\1}',''.join(parts))
def table(name):
 if name=='summary':
  header=['Model','Agreement','Median gap (cp)','Median time (ms)'];rows=[]
  for m,label in [('static','Static'),('relaxfish','Relaxfish'),('stockfish_2k','Stockfish 14.1 / 2k')]:
   v=summary['models'][m];rows.append([label,str(v['agreement'])+'/24',f"{v['median_gap_cp']:.1f}",f"{v['median_seconds']*1000:.2f}"])
 elif name=='matches':
  header=['Opening','Relaxfish side','Continuation plies','Result'];rows=[[m['opening'],m['relaxfish_color'],str(len(m['moves'])),m['outcome']] for m in results['matches']]
 elif name=='parameters':
  header=['Parameter','Executed value'];rows=[['Role count','7'],['Relaxation iterations','12'],['Unary floor','0.02'],['Pair coefficient','0.18'],['Triple coefficient','0.12'],['Role scale','18 cp'],['Search depth','1 ply'],['Reference / successor nodes','20,000 / 5,000'],['Comparator threads / hash','1 / 16 MiB'],['Seed','20261003']]
 else:
  header=['Claim','Status'];rows=[['Role update is executable','Measured and verified'],['Potential increases on the suite','Measured'],['Reference agreement rises 6 to 10','Measured; exact paired p = 0.125'],['Prototype beats Stockfish','Not established; four losses'],['Habitat small-position outcomes','Certified under variant rules'],['Current Stockfish superiority','Prospective target'],['Standard chess is solved','Not established']]
 cols='l'+'r'*(len(header)-1) if name in ['summary','matches'] else 'p{.43\\linewidth}p{.48\\linewidth}'
 return '\\begin{center}\\small\n\\begin{tabular}{'+cols+'}\\toprule\n'+' & '.join(map(escape,header))+'\\\\\\midrule\n'+'\n'.join(' & '.join(map(escape,row))+'\\\\' for row in rows)+'\n\\bottomrule\\end{tabular}\\end{center}\n'
preamble=r'''\documentclass[10pt]{article}
\usepackage[a4paper,margin=0.75in,headheight=15pt]{geometry}
\usepackage[T1]{fontenc}\usepackage[utf8]{inputenc}
\usepackage{lmodern,microtype,amsmath,amssymb,graphicx,booktabs,xcolor,hyperref,fancyhdr,caption}
\definecolor{ink}{HTML}{152E3C}\definecolor{blue}{HTML}{0072B2}\definecolor{mint}{HTML}{009E73}\definecolor{orange}{HTML}{D55E00}
\hypersetup{colorlinks=true,linkcolor=blue,urlcolor=blue,pdftitle={Better Than Stockfish: Relaxfish},pdfauthor={Michael Emanuel Glover}}
\urlstyle{same}\setlength{\emergencystretch}{3em}
\pagestyle{fancy}\fancyhf{}\fancyhead[L]{\small\textcolor{ink}{RELAXFISH | RESEARCH ARTICLE}}
\fancyhead[R]{\small Glover | 2026}\fancyfoot[C]{\small\thepage}
\renewcommand{\headrulewidth}{0.4pt}\setlength{\parindent}{0pt}\setlength{\parskip}{8pt}
\captionsetup{font=small,labelfont=bf,justification=raggedright,singlelinecheck=false}
\begin{document}
\begin{center}
{\fontsize{29}{33}\selectfont\bfseries\color{ink} Better Than Stockfish:\\Relaxfish}\par\vspace{9pt}
{\large\color{blue}Hierarchical relaxation, adversarial evidence\\and empirical approximate solving}\par\vspace{9pt}
Michael Emanuel Glover\par
{\small Research article and extended methods | 3 October 2026}
\end{center}
'''
s=(R/'manuscript.md').read_text();s=s[s.index('## Abstract'):];out=[preamble];display=False;first=True
for line in s.splitlines():
 if line.strip()==r'\[':display=True;out.append(line);continue
 if display:
  out.append(line)
  if line.strip()==r'\]':display=False
  continue
 if line.startswith('## '):
  if not first:out.append(r'\clearpage')
  out.append(r'\section*{'+escape(line[3:])+'}');first=False
 elif line.startswith('### '):out.append(r'\subsection*{'+escape(line[4:])+'}')
 elif line.startswith('[FIGURE '):
  name,caption=line[8:-1].split(' | ',1)
  out.append(r'\begin{minipage}{\linewidth}\begin{center}\includegraphics[width=.97\linewidth,height=.35\textheight,keepaspectratio]{figures/'+name+r'.pdf}\end{center}')
  out.append(r'{\small\textcolor{ink}{'+escape(caption)+r'}\par}\end{minipage}')
 elif line.startswith('[TABLE '):out.append(table(line[7:-1]))
 elif line.startswith(tuple(str(i)+'. ' for i in range(1,13))) and 'http' in line:
  parts=re.split(r'(https?://\S+)',line);out.append(''.join(r'\url{'+p+'}' if p.startswith('http') else escape(p) for p in parts)+r'\par')
 else:out.append(escape(line))
out.append(r'\end{document}');(R/'RELAXFISH.tex').write_text('\n'.join(out)+'\n')
for _ in range(2):
 p=subprocess.run(['pdflatex','-interaction=nonstopmode','-halt-on-error','RELAXFISH.tex'],cwd=R,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,text=True)
 if p.returncode:print(p.stdout[-5000:]);raise SystemExit(p.returncode)
plain=(R/'manuscript.md').read_text()
for name in ['summary','matches','parameters','claims']:
 tex_table=table(name)
 # Render each LaTeX table as readable plaintext rows.
 body=tex_table.split('\\toprule')[1].split('\\bottomrule')[0]
 body=body.replace('\\midrule','').replace('\\\\','\n').replace('\\&','&').replace('\\_','_')
 plain=plain.replace('[TABLE '+name+']',body.strip())
(R/'RELAXFISH.txt').write_text(plain)
print(subprocess.check_output(['pdfinfo',str(R/'RELAXFISH.pdf')],text=True))
