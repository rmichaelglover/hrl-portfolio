"""Add static sharing metadata and emit a manifest for screenshot-based cards.
Run after generating pages. Render cards with tools/render_social.py.
"""
from pathlib import Path
from html.parser import HTMLParser
import html,json,re
ROOT=Path(__file__).resolve().parents[1]
BASE='https://rmichaelglover.github.io/hrl-portfolio/'
class Info(HTMLParser):
 def __init__(self):super().__init__();self.title='';self.paragraphs=[];self.desc='';self.images=[];self.t=False;self.p=None
 def handle_starttag(self,t,attrs):
  a=dict(attrs)
  if t=='title':self.t=True
  if t=='p':self.p=[]
  if t=='meta' and a.get('name')=='description':self.desc=a.get('content','')
  if t=='img' and a.get('src'):self.images.append(a['src'])
 def handle_endtag(self,t):
  if t=='title':self.t=False
  if t=='p' and self.p is not None:self.paragraphs.append(' '.join(''.join(self.p).split()));self.p=None
 def handle_data(self,s):
  if self.t:self.title+=s
  if self.p is not None:self.p.append(s)
def parse(s):p=Info();p.feed(s);return p
special={
 'wave-worlds/index.html':('Wave Worlds | Air, Water & Music','Three first-person worlds. Hear the same notes travel through air, water, and their boundary, with independent sources and listening controls.','wave-worlds'),
 'index.html':('Wings Out | Interactive Portfolio','Explore sound, chess, cellular worlds, geometry, and relaxation labeling. Play with the ideas in your browser.','portfolio'),
 'hyperobject/index.html':('Projective Sound Field','Colored sine waves in first-person perspective. Play a musical octave, explore stereo geometry, and try the null conductor.','sound-field'),
 'cellular-complexes/index.html':('Cellular Complexes','Same rule, different neighbors: compare automata on squares, rectangles, triangles, cubes, and tetrahedra.','cellular-complexes'),
 'projective-resolution/index.html':('Conceptual Resolution','Rotate a rod and triangle. Change distance and resolution. See three features become one observed class.','projective-resolution')}
manifest=[]
for path in sorted(ROOT.rglob('*.html')):
 rel=path.relative_to(ROOT).as_posix()
 if any(part.startswith(('_','.')) for part in path.relative_to(ROOT).parts) or 'template' in path.name or 'test' in path.name or path.name=='rasterize_dump.html':continue
 text=path.read_text();info=parse(text)
 if not info.title:continue
 slug=rel.removesuffix('.html').replace('/','--')
 title,desc,key=special.get(rel,(info.title.strip(),info.desc or next((p for p in info.paragraphs if len(p)>45),'Explore '+info.title.strip()+' in the HRL portfolio.'),slug))
 desc=' '.join(desc.split());desc=desc if len(desc)<=185 else desc[:182].rsplit(' ',1)[0]+'...'
 route='' if rel=='index.html' else rel[:-10] if rel.endswith('index.html') else rel
 image='assets/social/'+key+'.png'
 tags={'og:type':'website','og:site_name':'Wings Out | HRL Portfolio','og:title':title,'og:description':desc,'og:url':BASE+route,'og:image':BASE+image,'og:image:width':'1200','og:image:height':'630','og:image:alt':title+' — visual preview'}
 block='<!-- social-preview:start -->\n'+'\n'.join('<meta property="'+k+'" content="'+html.escape(v,quote=True)+'">' for k,v in tags.items())+'\n'
 block+='\n'.join('<meta name="'+k+'" content="'+html.escape(v,quote=True)+'">' for k,v in {'twitter:card':'summary_large_image','twitter:title':title,'twitter:description':desc,'twitter:image':BASE+image}.items())+'\n<link rel="canonical" href="'+BASE+route+'">\n<!-- social-preview:end -->'
 text=re.sub(r'\n?<!-- social-preview:start -->.*?<!-- social-preview:end -->','',text,flags=re.S)
 text=re.sub(r'(<title\b[^>]*>.*?</title>)',lambda m:m[0]+'\n'+block,text,count=1,flags=re.S|re.I)
 path.write_text(text)
 artwork=None
 # Prefer an existing local thumbnail/image from this page; skip tiny controls and remote files.
 for src in info.images:
  if src.startswith(('http','data:','/')):continue
  candidate=(path.parent/src.split('?')[0]).resolve()
  if candidate.is_file() and candidate.suffix.lower() in ['.png','.jpg','.jpeg','.webp','.gif'] and candidate.stat().st_size>15000:
   artwork=str(candidate.relative_to(ROOT));break
 manifest.append({'path':rel,'title':title,'description':desc,'key':key,'image':image,'artwork':artwork})
(ROOT/'assets/social').mkdir(exist_ok=True)
(ROOT/'tools/social-manifest.json').write_text(json.dumps(manifest,indent=2,ensure_ascii=False)+'\n')
# Preserve metadata when rebuilding the musical pages from their source templates.
for source,dest in [('hyperobject/index.html','hyperobject/field-template.html'),('hyperobject/structure.html','hyperobject/template.html')]:
 block=re.search(r'<!-- social-preview:start -->.*?<!-- social-preview:end -->',(ROOT/source).read_text(),re.S)[0]
 p=ROOT/dest;text=p.read_text();text=re.sub(r'\n?<!-- social-preview:start -->.*?<!-- social-preview:end -->','',text,flags=re.S)
 text=re.sub(r'(<title\b[^>]*>.*?</title>)',lambda m:m[0]+'\n'+block,text,count=1,flags=re.S|re.I);p.write_text(text)
print('Static metadata:',len(manifest),'pages')
