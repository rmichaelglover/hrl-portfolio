#!/usr/bin/env python3
"""Render the author manuscript as the journal's complete browser reading edition."""
from pathlib import Path
import html
import re

ROOT=Path(__file__).resolve().parent

def inline(s):
    s=html.escape(s)
    s=re.sub(r'\*\*(.+?)\*\*',r'<strong>\1</strong>',s)
    s=re.sub(r'`([^`]+)`',r'<code>\1</code>',s)
    s=re.sub(r'https://[^\s<>]+',lambda m:f'<a href="{m[0]}">{m[0]}</a>',s)
    s=re.sub(r'\[(R\d+(?:, R\d+)*)\]',lambda m:'['+re.sub(r'R(\d+)',lambda n:f'<a href="#reference-R{n[1]}">R{n[1]}</a>',m[1])+']',s)
    return s

def main():
    text=(ROOT/'WHITE-PAPER.md').read_text();lines=text.splitlines();i=0;body=[];toc=[];section=0
    while not lines[i].startswith('**Authorship'):i+=1
    while i<len(lines):
        line=lines[i].strip()
        if not line:i+=1;continue
        if line.startswith('## '):
            section+=1;title=line[3:];anchor=f'section-{section}';toc.append(f'<li><a href="#{anchor}">{html.escape(title)}</a></li>');body.append(f'<h2 id="{anchor}">{inline(title)}</h2>');i+=1;continue
        if line.startswith('!['):
            m=re.fullmatch(r'!\[(.*?)\]\((.*?)\)',line);body.append(f'<figure><img src="{html.escape(m[2])}" alt="{html.escape(m[1])}" loading="lazy"><figcaption>{inline(m[1])}</figcaption></figure>');i+=1;continue
        if line.startswith('|'):
            rows=[]
            while i<len(lines) and lines[i].strip().startswith('|'):
                cells=[x.strip() for x in lines[i].strip().strip('|').split('|')]
                if not all(re.fullmatch(r'[-: ]+',x) for x in cells):rows.append(cells)
                i+=1
            table='<div class="table-scroll" tabindex="0" aria-label="Argument map"><table><thead><tr>'+''.join(f'<th scope="col">{inline(c)}</th>' for c in rows[0])+'</tr></thead><tbody>'
            table+=''.join('<tr>'+''.join(f'<td>{inline(c)}</td>' for c in row)+'</tr>' for row in rows[1:])+'</tbody></table></div>';body.append(table);continue
        p=[line];i+=1
        while i<len(lines) and lines[i].strip() and not lines[i].startswith(('##','![','|')):p.append(lines[i].strip());i+=1
        para=' '.join(p);ref=re.match(r'\*\*(R\d+)\.',para);attr=f' id="reference-{ref[1]}"' if ref else ''
        body.append(f'<p{attr}>{inline(para)}</p>')
    head='''<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>No Machine Will Be God | Attack on Christendom</title><meta name="description" content="Michael Emanuel Glover argues against the Babel project: machine power mistaken for divine sovereignty. A 26-page Christian apologetics paper on anti-reductionism, computation, creation, and sustaining."><link rel="canonical" href="https://rmichaelglover.github.io/hrl-portfolio/attack-on-christendom/babel-project/"><meta property="og:title" content="No Machine Will Be God"><meta property="og:type" content="article"><meta property="og:description" content="The Babel Project, Anti-Reductionism, and the Difference Between Making and Sustaining · Michael Emanuel Glover"><link rel="stylesheet" href="../journal.css"><style>*{box-sizing:border-box}.essay{max-width:900px}h1{line-height:1.12}.subtitle{text-align:center;font-size:23px}.byline{text-align:center}.downloads{display:flex;justify-content:center;flex-wrap:wrap;gap:12px;font-size:15px}.downloads a{padding:8px 12px;border:1px solid #b5a789;text-decoration:none}details{border-top:3px double #96886c;border-bottom:3px double #96886c;margin:28px 0;padding:14px 0}summary{cursor:pointer;font-weight:bold}details ol{padding-left:26px}details li{margin:5px 0}h2{scroll-margin-top:20px}article a{overflow-wrap:anywhere}figure{margin:26px 0}figure img{display:block;width:100%;height:auto}figcaption{font-size:14px;line-height:1.5;color:#5d513c}.table-scroll{overflow-x:auto;margin:24px 0}table{border-collapse:collapse;width:100%;min-width:560px;font-size:15px}th,td{text-align:left;vertical-align:top;border:1px solid #b5a789;padding:10px}th{background:#e8dcc0}.thesis{font-size:22px;font-style:italic;text-align:center;border-top:1px solid #96886c;border-bottom:1px solid #96886c;padding:18px 0}code{overflow-wrap:anywhere}@media(max-width:720px){.essay{padding:20px 18px}.subtitle{font-size:20px}article{font-size:17px}}@media print{details,.downloads{display:none}}</style></head><body><main class="essay"><nav aria-label="Journal"><a href="../">Attack on Christendom</a> · <a href="../#christian-apologetics">Christian Apologetics</a> · <a href="../../research-synthesis-2026/">Research results</a></nav><header><div class="tag">CHRISTIAN APOLOGETICS · THE BABEL PROJECT</div><h1>No Machine Will Be God</h1><p class="subtitle">The Babel Project, Anti-Reductionism, and the Difference Between Making and Sustaining</p><p class="byline"><strong>Michael Emanuel Glover</strong><br>16 October 2026 · Version 1.0 · 26 pages</p><div class="downloads"><a href="NO-MACHINE-WILL-BE-GOD.pdf">Read / download PDF</a><a href="BABEL-PROJECT-SOURCE.zip" download>Paper and source bundle</a><a href="WHITE-PAPER.md">Editable manuscript</a><a href="NO-MACHINE-WILL-BE-GOD.txt">Plain text</a></div></header><p class="thesis">“Anti-reductionism is theism.”</p>'''
    tail='''</article><footer>Michael Emanuel Glover · Attack on Christendom · Christian Apologetics<br>Cypher’s contributions are acknowledged briefly in the text as requested by the author. Scientific sources, mathematical illustrations, and theological premises retain their distinct roles.<p><a href="source-notes.json">Source and reading notes</a> · <a href="calculations.json">Finite calculations</a> · <a href="document-checks.json">Document checks</a> · <a href="../#christian-apologetics">Return to Christian Apologetics</a></p></footer></main></body></html>'''
    page=head+'<details><summary>Contents · 30 sections, three appendices, and references</summary><ol>'+''.join(toc)+'</ol></details><article>'+''.join(body)+tail
    assert page.count('(Cypher)')==text.count('(Cypher)')
    assert len(toc)==35
    (ROOT/'index.html').write_text(page)
    print('Rendered full journal reading edition; all Cypher markers preserved')

if __name__=='__main__':main()
