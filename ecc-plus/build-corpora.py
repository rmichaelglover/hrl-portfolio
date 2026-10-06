"""Rebuild six attributed source collections from explicitly chosen editions.
Usage: python3 build-corpora.py /path/to/source-cache
Downloads use the recorded URLs; the optional cache makes builds repeatable offline.
Requires beautifulsoup4; all output is text/JSON, never executable source content.
"""
from pathlib import Path
from bs4 import BeautifulSoup
import sys,re,json,hashlib,zipfile,struct,zlib,urllib.request,datetime
ROOT=Path(__file__).resolve().parent
CACHE=Path(sys.argv[1]) if len(sys.argv)>1 else ROOT/'.source-cache'
CACHE.mkdir(parents=True,exist_ok=True)
OUT=ROOT/'corpora';OUT.mkdir(exist_ok=True)
SOURCES={
 'bible':('bible.html','https://www.gutenberg.org/files/10/10-h/10-h.htm'),
 'old':('old-english.html','https://www.gutenberg.org/cache/epub/31543/pg31543-images.html'),
 'middle':('middle-english.html','https://www.gutenberg.org/cache/epub/10625/pg10625-images.html'),
 'quran':('quran.html','https://www.gutenberg.org/cache/epub/2800/pg2800-images.html'),
 'early':('cawdrey.zip','https://www.crosswire.org/ftpmirror/pub/sword/packages/rawzip/Cawdrey.zip')}
raw={}
for k,(file,url) in SOURCES.items():
 p=CACHE/file
 if not p.exists():
  with urllib.request.urlopen(url,timeout=60) as r:p.write_bytes(r.read())
 raw[k]=p.read_bytes()
def soup(k):return BeautifulSoup(raw[k],'html.parser')
def text(e):return re.sub(r'\s+',' ',e.get_text(' ',strip=True)).strip()
def save(name,title,kind,edition,language,source,records,notes):
 obj={'id':name,'title':title,'kind':kind,'edition':edition,'language':language,'source_url':source,'notes':notes,'records':records}
 data=json.dumps(obj,ensure_ascii=False,separators=(',',':')).encode();(OUT/(name+'.json')).write_bytes(data)
 return {k:v for k,v in obj.items() if k!='records'}|{'file':name+'.json','record_count':len(records),'group_count':len(set(r['group'] for r in records)),'sha256':hashlib.sha256(data).hexdigest(),'bytes':len(data)}
manifest=[]
# Split paragraphs containing multiple numbered verses without discarding wording.
s=soup('bible');part=None;book=None;books=[];collections={'ot':[],'nt':[]};booknum=0
for e in s.find_all(['h2','p']):
 t=text(e)
 if e.name=='h2':
  if 'Old Testament' in t:part='ot';book=None
  elif 'New Testament' in t:part='nt';book=None
  elif part and t:
   book=t;booknum+=1;books.append((part,book))
  continue
 if not part or not book or e.find_parent('div',class_='chapter') is None:continue
 hits=list(re.finditer(r'(?<!\d)(\d+):(\d+)\s+',t))
 if collections[part] and (not hits or hits[0].start()>0):
  prefix=t[:hits[0].start()] if hits else t
  collections[part][-1]['text']+=' '+prefix.strip()
 for i,m in enumerate(hits):
  end=hits[i+1].start() if i+1<len(hits) else len(t);ref=f'{m[1]}:{m[2]}'
  collections[part].append({'id':f'{booknum}:{ref}','group':book,'label':f'{book} {ref}','text':t[m.end():end].strip(),'headwords':[]})
assert len(books)==66,(len(books),books[-2:])
assert len(collections['ot'])==23145,len(collections['ot'])
assert len(collections['nt'])==7957,len(collections['nt'])
for key,title in [('ot','Old Testament'),('nt','New Testament')]:
 manifest.append(save(key,title,'scripture','King James Version · Project Gutenberg #10','English translation',SOURCES['bible'][1],collections[key],'This edition has 39 Old Testament and 27 New Testament books, without the Apocrypha. It is an English translation, not the original Hebrew, Aramaic, or Greek. Whitespace is normalized; verse labels are separated from the text.'))
# Keep Rodwell source paragraphs distinct from modern ayah numbering and commentary.
s=soup('quran');records=[];chapter=None;in_notes=False;para=0;surahs=set()
def roman(s):
 values={'I':1,'V':5,'X':10,'L':50,'C':100,'D':500,'M':1000};return sum(-values[c] if i+1<len(s) and values[c]<values[s[i+1]] else values[c] for i,c in enumerate(s))
for e in s.find_all(['h3','h4','h5','p']):
 t=text(e)
 if e.name in ['h3','h4','h5']:
  m=re.match(r'^SURA(?:1)?[\s-]+([IVXLCDM]+)',t)
  if m:chapter=roman(m[1]);surahs.add(chapter);para=0;in_notes=False
  elif chapter:chapter=None
  continue
 if chapter is None:continue
 if re.fullmatch(r'_+',t):in_notes=True;continue
 if in_notes or not t or re.match(r'^(MECCA|MEDINA)[.\s-]',t):continue
 # Stop before the Gutenberg footer; it is outside the chapter's textual container.
 if e.find_parent(id='pg-footer') is not None:continue
 para+=1;anchor=e.get('id',f'surah-{chapter}-p-{para}')
 records.append({'id':anchor,'group':f'Surah {chapter}','label':f'Surah {chapter} · edition paragraph {para}','text':t,'headwords':[],'source_url':SOURCES['quran'][1]+'#'+anchor})
assert surahs==set(range(1,115)),surahs
records.sort(key=lambda r:(int(r['group'].split()[1]),int(r['label'].split()[-1])))
manifest.append(save('quran','Qur’an','scripture','J. M. Rodwell translation · Project Gutenberg #2800','English translation',SOURCES['quran'][1],records,'Historical translation originally published in 1861. Rodwell rearranges surahs; browsing here uses standard surah numbers. References are edition paragraphs, not modern ayah numbers. Introductions and separated footnotes are excluded from the searchable corpus; inline note numbers remain. The translation and its historical perspective are not a replacement for the Arabic text.'))
# Extract dictionary entry paragraphs with their headword anchors; keep senses unsplit.
for key,name,title,edition in [('old','old-english','Old English dictionary','J. R. Clark Hall · A Concise Anglo-Saxon Dictionary · second edition, 1916'),('middle','middle-english','Middle English dictionary','A. L. Mayhew & Walter W. Skeat · A Concise Dictionary of Middle English, 1888')]:
 s=soup(key);records=[];seen=set()
 for a in s.select('a[id^="word_"]'):
  p=a.find_parent('p')
  if p is None or id(p) in seen:continue
  seen.add(id(p));headwords=[text(b) for b in p.select('b.entry')]
  if not headwords:continue
  anchor=a['id'];records.append({'id':anchor,'group':headwords[0][0].upper(),'label':headwords[0],'text':text(p),'headwords':headwords,'source_url':SOURCES[key][1]+'#'+anchor})
 assert len(records)>10000,(key,len(records))
 manifest.append(save(name,title,'dictionary',edition,'Historical headwords with English glosses',SOURCES[key][1],records,'A later scholarly dictionary of this historical language, not a dictionary compiled during that language period. Entry wording, alternative forms, senses, examples, and abbreviations are kept together; HTML whitespace is normalized. Cross-references and cited material may need consultation of the original.'))
# SWORD zLD: dat points to block/item; each inflated block begins with an item table.
z=zipfile.ZipFile(CACHE/'cawdrey.zip');base='modules/lexdict/zld/cawdrey/cawdrey';idx=z.read(base+'.idx');dat=z.read(base+'.dat');dx=z.read(base+'.zdx');dt=z.read(base+'.zdt');blocks={};records=[]
for n in range(len(idx)//8):
 off,size=struct.unpack_from('<II',idx,n*8);entry=dat[off:off+size];word,pointer=entry.split(b'\r\n',1);block,item=struct.unpack_from('<II',pointer)
 if block not in blocks:
  bo,bs=struct.unpack_from('<II',dx,block*8);blocks[block]=zlib.decompress(dt[bo:bo+bs])
 data=blocks[block];count=struct.unpack_from('<I',data)[0];assert item<count
 eo,es=struct.unpack_from('<II',data,4+item*8);xml=data[eo:eo+es].decode('utf-8').rstrip('\x00');entry_soup=BeautifulSoup(xml,'html.parser');orth=entry_soup.find('orth');head=text(orth) if orth else word.decode('utf-8');definition=text(entry_soup)
 records.append({'id':f'cawdrey-{n+1}','group':head[0].upper(),'label':head,'text':definition,'headwords':[head]})
assert len(records)==len(idx)//8
manifest.append(save('early-modern','Early Modern English dictionary','dictionary','Robert Cawdrey · A Table Alphabeticall, 1604 · SWORD module 1.0','Early Modern English','https://crosswire.org/sword/modules/ModInfo.jsp?modName=Cawdrey',records,'Complete entries in the downloaded SWORD module, not a new transcription of the printed volume. A hard-word dictionary, not a full inventory of English. Alternative explanations remain within entries; one entry is not assumed to mean one sense.'))
license_parts=[]
for k in ['bible','old','middle','quran']:
 s=soup(k);footer=s.find(id='pg-footer')
 if footer:license_parts.append(f'=== {k}: {SOURCES[k][1]} ===\n'+footer.get_text('\n',strip=True))
license_parts.append('=== Cawdrey SWORD module ===\n'+z.read('mods.d/cawdrey.conf').decode())
(OUT/'SOURCE-LICENSES.txt').write_text('\n\n'.join(license_parts))
(OUT/'manifest.json').write_text(json.dumps({'built_at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'collections':manifest,'source_sha256':{k:hashlib.sha256(v).hexdigest() for k,v in raw.items()},'license_file':'SOURCE-LICENSES.txt','tokenization':'Unicode letters and combining marks; internal apostrophes and hyphens retained. Exact spelling and capitalization are preserved. Case-insensitive matching is a separately labeled search option.','coverage':'Full extracted source records for the chosen editions/modules. Source introductions, apparatus and footnotes are not counted as scripture. No theological entailment or word-sense resolution is inferred from a search hit.'},ensure_ascii=False,indent=2))
for c in manifest:print(c['title'],c['record_count'],'records',c['group_count'],'groups')
