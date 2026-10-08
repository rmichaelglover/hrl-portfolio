"""Derive artistic flag palettes from a pinned SVG reference; no flag artwork is shipped."""
from pathlib import Path
from collections import Counter
import json,re,colorsys,hashlib
root=Path(__file__).resolve().parent
flags=Path('/tmp/emoji-world-flags/svg')
atlas=json.loads((root.parent/'worlds-of-kings-fusion/data/atlas.json').read_text())
colors={'red':'#c73e46','blue':'#275a9e','green':'#398458','yellow':'#e0b929','white':'#ffffff','black':'#293439','orange':'#df8a35','purple':'#86518a','brown':'#9c7154'}
symbols={'red':['🌹','🍎','🍒','❤️','🌶️','🍓'],'blue':['🌊','💎','🌀','💙','🧊','🫐'],'green':['🌿','🍀','🌱','💚','🥝','🌳'],'yellow':['⭐','🌻','☀️','💛','🍋','⚡'],'white':['☁️','❄️','🤍','🕊️','🌼','🥚'],'black':['🌑','♟️','🖤','🎱','🎩','🕶️'],'orange':['🍊','🍁','🧡','🥕','🔥','🏵️'],'purple':['🍇','💜','🔮','🪻'],'brown':['🍂','🪵','🌰','🥔']}
overrides={'USA':['red','white','blue'],'FRA':['blue','white','red'],'KOR':['white','red','blue','black'],'GBR':['blue','white','red'],'AUS':['blue','white','red'],'NZL':['blue','white','red'],'CAN':['red','white'],'CHN':['red','yellow'],'BRA':['green','yellow','blue','white'],'IND':['orange','white','green','blue'],'KEN':['black','red','green','white'],'ZAF':['green','red','blue','yellow','white','black'],'DEU':['black','red','yellow'],'JPN':['white','red'],'ITA':['green','white','red'],'UKR':['blue','yellow'],'RUS':['white','blue','red'],'ISR':['white','blue'],'PSX':['black','white','green','red'],'ATA':['white','blue']}
def group(s):
 if len(s)==3:s=''.join(c*2 for c in s)
 if len(s)!=6:return None
 rgb=[int(s[i:i+2],16)/255 for i in [0,2,4]];h,s,v=colorsys.rgb_to_hsv(*rgb);h*=360
 if v<.25:return'black'
 if s<.15:return'white'if v>.55 else'black'
 return 'red'if h<20 or h>=335 else'orange'if h<42 else'yellow'if h<68 else'green'if h<170 else'blue'if h<265 else'purple'
records={};sources={}
for c in atlas['countries']:
 iso={'FRA':'FR','NOR':'NO','TWN':'TW','KOS':'XK'}.get(c['id'],c['iso2']);p=flags/(iso.lower()+'.svg');names=[]
 if p.exists():
  text=p.read_text();counts=Counter(group(v)for v in re.findall(r'(?:fill|stroke)(?:=|:)\s*[\"\']?\s*#([0-9a-fA-F]{3,8})\b',text));counts.pop(None,None);names=[n for n,k in counts.most_common(6)];sources[c['id']]=hashlib.sha256(p.read_bytes()).hexdigest()
 names=overrides.get(c['id'],names)
 if not names:names=['blue','white'];basis='neutral fallback'
 else:basis='curated flag palette'if c['id']in overrides else'approximate palette from SVG colors'
 flag=''.join(chr(127397+ord(v))for v in iso)if len(iso)==2 and iso.isalpha()else'🌐'
 records[c['id']]={'flag':flag,'names':names,'colors':[colors[n]for n in names],'symbols':list(dict.fromkeys(e for n in names for e in symbols[n])),'basis':basis}
(root/'data/themes.json').write_text(json.dumps({'countries':records,'source':{'url':'https://github.com/hampusborgos/country-flags','commit':'c09927e63705529bbf59ca6684cd9b23225dddad','note':'Artistic palettes; not official color specifications. Only derived color facts, no SVG flag artwork, are shipped.','sha256':sources}},ensure_ascii=False,separators=(',',':')))
print('Built',len(records),'country/territory themes')
