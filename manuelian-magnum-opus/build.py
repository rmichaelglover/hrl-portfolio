from pathlib import Path
import re,subprocess
R=Path(__file__).resolve().parent
text=(R/'MANUSCRIPT.md').read_text()
def esc(s):
 chunks=re.split(r'(\$[^$]+\$)',s)
 for i in range(0,len(chunks),2):
  chunks[i]=chunks[i].replace('&',r'\&').replace('%',r'\%').replace('_',r'\_').replace('’',"'").replace('“','``').replace('”',"''")
 return re.sub(r'\*\*(.*?)\*\*',r'\\textbf{\1}',''.join(chunks))
header=r'''\documentclass[10pt]{article}
\usepackage[a4paper,margin=.75in,headheight=15pt]{geometry}
\usepackage[T1]{fontenc}\usepackage[utf8]{inputenc}\usepackage{lmodern,microtype,amsmath,amssymb,xcolor,hyperref,fancyhdr,graphicx}
\definecolor{ink}{HTML}{153F50}\definecolor{blue}{HTML}{0072B2}
\hypersetup{colorlinks=true,urlcolor=blue,pdftitle={The Tree, the Proof, and the Light},pdfauthor={Michael Emanuel Glover}}
\urlstyle{same}\setlength{\emergencystretch}{3em}\setlength{\parskip}{8pt}\setlength{\parindent}{0pt}
\pagestyle{fancy}\fancyhf{}\fancyhead[L]{\small MANUELIAN INQUIRY | PROOF AND PERSPECTIVE}\fancyhead[R]{\small Glover | 2026}\fancyfoot[C]{\thepage}
\begin{document}\begin{center}
{\LARGE\bfseries\color{ink}The Tree, the Proof, and the Light}\par\vspace{10pt}
{\large\color{blue}A Manuelian inquiry into knowledge,\\perspective, origins and enough}\par\vspace{10pt}
Michael Emanuel Glover | 3 October 2026
\end{center}
'''
lines=text[text.index('## Prologue'):].splitlines();out=[header];display=False;first=True
for line in lines:
 if line.strip()==r'\[':display=True;out.append(line);continue
 if display:
  out.append(line)
  if line.strip()==r'\]':display=False
 elif line.startswith('## '):
  if not first:out.append(r'\clearpage')
  out.append(r'\section*{'+esc(line[3:])+'}');first=False
 elif line.startswith('### '):out.append(r'\subsection*{'+esc(line[4:])+'}')
 elif line.startswith('[FIGURE '):
  name,caption=line[8:-1].split(' | ',1)
  out.append(r'\begin{minipage}{\linewidth}\begin{center}\includegraphics[width=.97\linewidth,height=.32\textheight,keepaspectratio]{figures/'+name+r'.pdf}\end{center}')
  out.append(r'{\small '+esc(caption)+r'\par}\end{minipage}')
 elif 'https://' in line:
  parts=re.split(r'(https://\S+)',line);out.append(''.join(r'\url{'+s+'}' if s.startswith('https://') else esc(s) for s in parts))
 else:out.append(esc(line))
out.append(r'\end{document}');(R/'MAGNUM-OPUS.tex').write_text('\n'.join(out));(R/'MAGNUM-OPUS.txt').write_text(re.sub(r'\[FIGURE ([^ ]+) \| (.*?)\]',lambda m:m[2]+'\n(Figure: figures/'+m[1]+'.pdf)',text))
for _ in range(2):
 result=subprocess.run(['pdflatex','-interaction=nonstopmode','-halt-on-error','MAGNUM-OPUS.tex'],cwd=R,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,text=True)
 if result.returncode:print(result.stdout[-4000:]);raise SystemExit(result.returncode)
print(subprocess.check_output(['pdfinfo',str(R/'MAGNUM-OPUS.pdf')],text=True))
