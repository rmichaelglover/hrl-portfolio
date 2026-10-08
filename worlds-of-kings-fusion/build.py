#!/usr/bin/env python3
"""Topology-preserving cartography in Python, native C++ indexing/coloring."""
from pathlib import Path
import json,subprocess,tempfile
from shapely.geometry import shape,mapping
root=Path(__file__).resolve().parent
source=root.parent/'worlds-of-kings-earth/data/atlas.json'
data=json.loads(source.read_text())
# Antarctica is one shared destination, including all mapped Antarctic land.
antarctic=[r['id'] for r in data['regions'] if r['country']=='ATA']
keep=antarctic[0]; removed=set(antarctic[1:]); old=data['regions']
ant=old[keep]; country=next(c for c in data['countries'] if c['id']=='ATA')
ant.update(geometry=country['geometry'],name='Antarctica',local='Antarctica',center=[0,-90],extent=[-180,-90,180,-60],promotion='antarctica')
ant['neighbors']=list(dict.fromkeys(n for i in antarctic for n in old[i]['neighbors'] if n not in antarctic))
ant['routes']=[list(dict.fromkeys(n for i in antarctic for n in old[i]['routes'][d] if n not in antarctic)) for d in range(8)]
ids={r['id']:i for i,r in enumerate(r for r in old if r['id'] not in removed)}
for n in removed:ids[n]=ids[keep]
data['regions']=[r for r in old if r['id'] not in removed]
for region in data['regions']:
 original=region['id'];region['id']=ids[original]
 region['neighbors']=list(dict.fromkeys(ids[n] for n in region['neighbors'] if ids[n]!=region['id']))
 region['routes']=[list(dict.fromkeys(ids[n] for n in route if ids[n]!=region['id'])) for route in region['routes']]
 if region['country'] is None and region['extent'][3]>=89.999:region['promotion']='north-pole'
for country in data['countries']:country['spaces']=list(dict.fromkeys(ids[n] for n in country['spaces']))
for key in ['polar_links','date_line_links']:data[key]=list({tuple(sorted((ids[a],ids[b]))) for a,b in data[key] if ids[a]!=ids[b]})
data['boardVersion']=2
for region in data['regions']+data['countries']:
 geometry=shape(region['geometry'])
 region['geometry']=mapping(geometry if geometry.area<.15 else geometry.simplify(.10,preserve_topology=True))
with tempfile.TemporaryDirectory(prefix='fusion-build-')as directory:
 temporary=Path(directory);raw=temporary/'atlas.json';binary=temporary/'prepare-atlas'
 raw.write_text(json.dumps(data,separators=(',',':')))
 subprocess.run(['g++','-O3','-std=c++17',str(root/'native/prepare-atlas.cpp'),'-ljsoncpp','-o',str(binary)],check=True)
 subprocess.run([str(binary),str(raw),str(root/'data/atlas.json')],check=True)
