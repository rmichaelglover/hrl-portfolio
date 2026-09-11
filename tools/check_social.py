"""Verify static share metadata, PNG dimensions, and internal navigation targets."""
from pathlib import Path
from html.parser import HTMLParser
from urllib.parse import urlsplit,unquote
import json,struct
ROOT=Path(__file__).resolve().parents[1]
BASE='https://rmichaelglover.github.io/hrl-portfolio/'
class Tags(HTMLParser):
 def __init__(self):super().__init__();self.meta={};self.links=[];self.canonical=[]
 def handle_starttag(self,tag,attrs):
  a=dict(attrs)
  if tag=='meta':self.meta.setdefault(a.get('property',a.get('name')),[]).append(a.get('content'))
  if tag=='a' and 'href' in a:self.links.append(a['href'])
  if tag=='link' and a.get('rel')=='canonical':self.canonical.append(a['href'])
rows=json.loads((ROOT/'tools/social-manifest.json').read_text());errors=[]
for row in rows:
 path=ROOT/row['path'];p=Tags();p.feed(path.read_text())
 for key in ['og:title','og:description','og:url','og:image','og:image:alt','twitter:card']:
  if len(p.meta.get(key,[]))!=1:errors.append((row['path'],'missing/duplicate '+key))
 if len(p.canonical)!=1:errors.append((row['path'],'missing/duplicate canonical'))
 image=ROOT/row['image']
 if not image.exists():errors.append((row['path'],'missing image'));continue
 raw=image.read_bytes()
 if raw[:8]!=b'\x89PNG\r\n\x1a\n' or struct.unpack('>II',raw[16:24])!=(1200,630):errors.append((str(image),'incorrect image format/dimensions'))
 if p.meta.get('og:image')!=[BASE+row['image']]:errors.append((row['path'],'wrong public image URL'))
 for link in p.links:
  u=urlsplit(link)
  if u.scheme or u.netloc or not u.path or '{{' in link:continue
  rawpath=unquote(u.path)
  if rawpath.startswith('/hrl-portfolio/'):target=ROOT/rawpath[len('/hrl-portfolio/'):]
  elif rawpath.startswith('/'):continue
  else:target=path.parent/rawpath
  if target.exists():continue
  if target.suffix=='.html' and target.with_suffix('.md').exists():continue
  errors.append((row['path'],'unresolved local link '+link))
if errors:
 for error in errors:print(*error,sep=': ')
 raise SystemExit(1)
print('PASS:',len(rows),'HTML pages; unique static metadata, public image URLs, 1200x630 PNGs, internal links (including Markdown-generated targets).')
