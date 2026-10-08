#!/usr/bin/env python3
"""Reuse the preserved simplified globe; derive coarse shore anchors, not species GIS ranges."""
from pathlib import Path
import json,hashlib
from shapely.geometry import shape,Point
from shapely.ops import nearest_points
root=Path(__file__).resolve().parent;source=root.parent/'worlds-of-kings-fusion/data/atlas.json';atlas=json.loads(source.read_text());regions=atlas['regions'];countries={c['id']:c for c in atlas['countries']};population={f['id']:f for f in json.loads((root.parent/'lion-and-the-lamb/world/data/world.json').read_text())['features']}
land=[]
for r in regions:
 if not r['country']:continue
 water=[regions[n]for n in r['neighbors']if regions[n]['country']is None];shore=None
 if water:
  g=shape(r['geometry']);sea=min(water,key=lambda w:abs(w['center'][1]-r['center'][1])+abs((w['center'][0]-r['center'][0]+180)%360-180));q=nearest_points(g.boundary,Point(sea['center']))[0];shore=[round(q.x,5),round(q.y,5)]
 anchor=list(r['center'])
 if r['country']=='ATA' and shore:anchor=shore
 land.append({k:r[k]for k in ['id','country','name','center','extent','geometry']}|{'anchor':anchor,'shore':shore,'continent':countries[r['country']]['continent']})
result={'countries':[{k:c[k]for k in ['id','iso2','name','continent','center','geometry']}|{'density':population.get(c['id'],{}).get('density')}for c in atlas['countries']],'regions':land,'marine':[{'id':r['id'],'country':None,'name':'Ocean cove · '+str(r['row']+1)+':'+str(r['col']+1),'center':r['center'],'anchor':r['center'],'shore':r['center'],'continent':'Ocean','marine':True}for i,r in enumerate(reg for reg in regions if reg['country']is None)if i%9==0], 'capitals':[c for c in atlas['cities']if c['capital']],'source':{'globe':'../worlds-of-kings-fusion/data/atlas.json','sha256':hashlib.sha256(source.read_bytes()).hexdigest(),'naturalEarth':'v5.1.2','note':'Coast anchors derived from globe water-neighbor conventions. Habitat hints are illustrative, not land-cover observations.'}}
(root/'data/globe.json').write_text(json.dumps(result,separators=(',',':')));print('Built',len(land),'land spaces; bytes',(root/'data/globe.json').stat().st_size)
