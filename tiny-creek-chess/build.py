"""Preserve base routes; supply small-country city/garden learning spaces."""
import json,math,hashlib
from pathlib import Path
from shapely.geometry import shape,Point,mapping
root=Path(__file__).resolve().parent
base=root.parent/'worlds-of-kings-fusion/data/atlas.json'
d=json.loads(base.read_text());cozy=json.loads((root.parent/'tiny-creek-world/data/globe.json').read_text());existing={r['id']:r for r in cozy['regions']};country={c['id']:c for c in d['countries']};created=[]
for r in d['regions']:
 r.update({k:v for k,v in existing.get(r['id'],{}).items() if k in ['anchor','shore','continent']});r.setdefault('anchor',r['center']);r.setdefault('continent',country.get(r['country'],{}).get('continent','Ocean'));r['marine']=r['country'] is None
 if r['marine']:r['shore']=r['center']
def bearing(a,b):
 dx=(b[0]-a[0]+180)%360-180;dy=b[1]-a[1];return round(math.atan2(dx*math.cos(math.radians(a[1])),dy)/(math.pi/4))%8
def distance(a,b):return (((b[0]-a[0]+180)%360-180)*math.cos(math.radians(a[1])))**2+(b[1]-a[1])**2
for code,c in country.items():
 land=[r for r in d['regions'] if r['country']==code];need=max(0,16-len(land))
 if not need:continue
 g=shape(c['geometry']);g=max(g.geoms,key=lambda p:p.area) if g.geom_type=='MultiPolygon' else g
 bounds=g.bounds;points=[];kind=[];names=[]
 cities=sorted([x for x in d['cities'] if x['country']==code],key=lambda x:-x['population'])
 occupied=[r['anchor']for r in land]
 for city in cities:
  p=city['center']
  if g.covers(Point(p)) and all(distance(p,q)>1e-12 for q in occupied+points):points.append(p);kind.append('city');names.append(city['name'])
  if len(points)>=need:break
 if len(points)<need:
  # Interior lattice learning plots are explicitly fictional, never claimed as cities.
  candidates=[]
  for iy in range(24):
   for ix in range(24):
    p=[bounds[0]+(ix+.5)*(bounds[2]-bounds[0])/24,bounds[1]+(iy+.5)*(bounds[3]-bounds[1])/24]
    if g.covers(Point(p)):candidates.append(p)
  while len(points)<need:
   if not candidates:raise ValueError('No interior garden plots: '+code)
   p=max(candidates,key=lambda p:min(distance(p,q)for q in occupied+points));candidates.remove(p);points.append(p);kind.append('garden');names.append(c['name']+' · story garden '+str(len(points)))
 for p,k,name in zip(points[:need],kind,names):
  parent=min(land,key=lambda r:distance(p,r['anchor']));radius=max(1e-6,min(bounds[2]-bounds[0],bounds[3]-bounds[1])/90)
  g2=Point(p).buffer(radius,resolution=6).intersection(g)
  r={'id':len(d['regions']),'key':code+'-learning-'+str(len(created)),'country':code,'name':name,'local':name,'kind':k,'center':p,'anchor':p,'continent':c['continent'],'marine':False,'extent':list(g2.bounds),'geometry':mapping(g2),'neighbors':[],'routes':[[]for _ in range(8)],'parent':parent['id']}
  d['regions'].append(r);created.append(r)
 # Connect nearby learning spaces and the mainland gateway using geographic sectors.
 local=[r for r in d['regions']if r['country']==code]
 for r in [x for x in created if x['country']==code]:
  near=sorted([x for x in local if x['id']!=r['id']],key=lambda x:distance(r['anchor'],x['anchor']))[:8]
  gateway=d['regions'][r['parent']];outside=[d['regions'][n]for n in gateway['neighbors']if d['regions'][n]['country']!=code]
  if not outside:outside=sorted([q for q in d['regions']if q['country']!=code],key=lambda q:distance(r['anchor'],q['anchor']))[:3]
  near+=outside[:3]
  for q in near:
   for a,b in [(r,q),(q,r)]:
    if b['id']not in a['neighbors']:a['neighbors'].append(b['id'])
    sector=bearing(a['anchor'],b['anchor']);routes=a['routes'][sector]
    if b['id']not in routes:routes.append(b['id'])
    routes.sort(key=lambda n:distance(a['anchor'],d['regions'][n]['anchor']))
d['marine']=[];d['source']={'base':'../worlds-of-kings-fusion/data/atlas.json','sha256':hashlib.sha256(base.read_bytes()).hexdigest(),'note':'Original provinces and ocean routes preserved. Added city learning spots and explicitly fictional interior garden plots supply a minimum of sixteen spaces per mapped country. City points are Natural Earth populated places; garden plots are not administrative divisions.'}
(root/'data/atlas.json').write_text(json.dumps(d,ensure_ascii=False,separators=(',',':')))
print(len(created),'supplemental city/garden spaces;',len(d['regions']),'total spaces')
