#!/usr/bin/env python3
from pathlib import Path
import json,math,hashlib
from shapely.geometry import shape,mapping,box,Point
from shapely.geometry.polygon import orient
from shapely import make_valid
from pyproj import Geod
root=Path(__file__).resolve().parent;cache=Path('/tmp/lamb-world-sources');out=root/'data';out.mkdir(exist_ok=True);geod=Geod(ellps='WGS84');manifest={'sources':{},'files':{}}
def load(name):
 p=cache/(name+'.geojson');a=json.loads(p.read_text());assert not a.get('error'),name;assert a.get('type')=='FeatureCollection',name;manifest['sources'][name]={'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'features':len(a['features'])};return a['features']
def polygons(g):
 if g.geom_type=='Polygon':return[orient(g,sign=-1)]
 if hasattr(g,'geoms'):return[p for c in g.geoms for p in polygons(c)]
 return[]
def clean(g,tolerance):
 g=make_valid(g).simplify(tolerance,preserve_topology=True)
 if g.geom_type in ['Polygon','MultiPolygon','GeometryCollection']:
  ps=polygons(g)
  if not ps:return g.buffer(0)
  from shapely.geometry import MultiPolygon
  g=ps[0]if len(ps)==1 else MultiPolygon(ps)
 return g
def rounded(v):
 if isinstance(v,(list,tuple)):return[rounded(x)for x in v]
 return round(v,5)if isinstance(v,float)else v
def entry(feature,kind,tol,pop=False):
 p=feature['properties'];g=shape(feature['geometry']);g=clean(g,tol)
 if g.is_empty:return None
 q=g.representative_point();r={'geometry':{'type':g.geom_type,'coordinates':rounded(mapping(g)['coordinates'])},'bounds':rounded(g.bounds),'center':[round(q.x,5),round(q.y,5)],'kind':kind,'name':p.get('NAME')or p.get('name')or p.get('NAME_EN')or p.get('gnis_name')or p.get('GNIS_NAME')or kind}
 if pop:
  people=p.get('POP100');area=p.get('AREALAND');r.update(id=p['GEOID'],people=int(people)if people is not None else None,areaKm2=float(area)/1e6 if area else None,state=p.get('STATE'),county=p.get('COUNTY'));r['density']=round(r['people']/r['areaKm2'],3)if r['people']is not None and r['areaKm2']else None
 return r
def write(name,features,**extra):
 a={'features':[f for f in features if f],**extra};p=out/(name+'.json');p.write_text(json.dumps(a,separators=(',',':')));manifest['files'][name]={'features':len(a['features']),'bytes':p.stat().st_size,'sha256':hashlib.sha256(p.read_bytes()).hexdigest()};print(name,manifest['files'][name],flush=True)
# Pinned Natural Earth countries: population estimates and polygon-area averages.
a=json.load(open('/tmp/world-kings-natural-earth/countries.geojson'));countries=[]
for f in a['features']:
 r=entry(f,'country',.12);p=f['properties'];g=shape(f['geometry']);area=abs(geod.geometry_area_perimeter(g)[0])/1e6;people=p.get('POP_EST');r.update(id=p['ADM0_A3'],name=p.get('NAME_EN')or p['NAME'],people=people if people is not None and people>=0 else None,popYear=p.get('POP_YEAR'),areaKm2=round(area,2));r['density']=round(r['people']/area,3)if r['people']is not None and area else None;countries.append(r)
write('world',countries,resolution='Country population averages; varying Natural Earth estimate years',vintage='Natural Earth v5.1.2')
counties=load('counties');tracts=load('tracts');groups=load('blockgroups');metros=load('metros');metroshape={f['properties']['CBSA']:shape(f['geometry'])for f in metros}
write('states',[entry(f,'county',.002,True)for f in counties],resolution='2020 Census county averages')
write('tracts',[entry(f,'tract',.0008,True)for f in tracts],resolution='2020 Census tract averages')
for key,cbsa in [('atlanta','12060'),('mobile','33660')]:
 g=metroshape[cbsa];rows=[entry(f,'blockgroup',.00015,True)for f in groups if g.covers(shape(f['geometry']).representative_point())];write(key,rows,resolution='2020 Census block-group averages',metro=entry(next(f for f in metros if f['properties']['CBSA']==cbsa),'metro',.002,True))
write('arlington',[entry(f,'blockgroup',.00015,True)for f in groups if f['properties']['STATE']=='01'and f['properties']['COUNTY']=='131'],resolution='2020 Census block-group averages around Arlington, Wilcox County')
for key in ['atlanta','mobile','arlington']:write(key+'-core',[entry(f,'block',.00004,True)for f in load(key+'-core')],resolution='2020 Census blocks in a focus window; not a full metro coverage claim')
# Geographic corridors are separate from population-derived classifications.
worldgeo=[];regionalgeo=[];region=box(-88.6,30.0,-80.7,35.1)
for name,kind,tol in [('rivers','river',.015),('lakes','lake',.015),('mountains','mountain',.03),('roads','road',.01),('rails','rail',.01),('urban','urban',.005)]:
 rows=load(name)
 for f in rows:
  p=f['properties'];g=shape(f['geometry'])
  if name=='mountains'and not any(k in (p.get('FEATURECLA')or '').lower()for k in ['mountain','range','plateau']):continue
  if name in ['roads','rails']and (p.get('scalerank',99)>6)and not g.intersects(region):continue
  r=entry(f,kind,tol)
  if r:worldgeo.append(r)
  if g.intersects(region):regionalgeo.append(entry(f,kind,.0005))
for key,kinds in [('world-water',{'river','lake'}),('world-relief',{'mountain'}),('world-transport',{'road','rail'}),('world-urban',{'urban'})]:write(key,[f for f in worldgeo if f['kind']in kinds],resolution='Generalized global Natural Earth geography; not complete local infrastructure')
write('regional-geography',regionalgeo,resolution='Natural Earth geography retained more finely for Georgia and Alabama')
for place in ['atlanta','mobile','arlington']:
 features=[]
 for kind,layers in [('roads',[29,30,31,32,35,38]),('water',[6,12])]:
  for layer in layers:
   p=cache/f'{place}-{kind}-{layer}.geojson'
   if not p.exists():continue
   subtype=('rail'if layer==38 else 'dirtroad'if layer==35 else 'road')if kind=='roads'else 'river'if layer==6 else 'lake'
   for f in load(p.stem):features.append(entry(f,subtype,.00008))
 write(place+'-geography',features,resolution='USGS transportation and hydrography in the core focus window')
beltline=[entry(f,'beltline',.000025)for f in load('beltline')];write('beltline',beltline,resolution='Atlanta BeltLine public trail alignments; wildlife lane overlay is imagined')
for name in ['download-manifest','local-download-manifest']:
 p=cache/(name+'.json')
 if p.exists():manifest[name]=json.loads(p.read_text())
manifest['census_base']='https://tigerweb.geo.census.gov/arcgis/rest/services/Census2020/tigerWMS_Census2020/MapServer'
manifest['focus']={'arlington':{'center':[-87.5886139,32.0570917],'label':'Arlington, Alabama · Wilcox County · local focus, not a metro','coordinate_reference':'https://en.wikipedia.org/wiki/Arlington,_Alabama'},'atlanta':{'center':[-84.388,33.749],'cbsa':'12060'},'mobile':{'center':[-88.0399,30.6954],'cbsa':'33660'}}
(out/'manifest.json').write_text(json.dumps(manifest,indent=2))
