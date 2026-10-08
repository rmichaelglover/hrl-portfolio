from pathlib import Path
import requests,json,concurrent.futures,time,hashlib
root=Path('/tmp/lamb-world-sources');root.mkdir(exist_ok=True)
NE='https://raw.githubusercontent.com/nvkelso/natural-earth-vector/v5.1.2/geojson/'
T='https://tigerweb.geo.census.gov/arcgis/rest/services/Census2020/tigerWMS_Census2020/MapServer/'
tasks=[]
for name,file in {'urban':'ne_10m_urban_areas','roads':'ne_10m_roads','rails':'ne_10m_railroads','rivers':'ne_10m_rivers_lake_centerlines','lakes':'ne_10m_lakes','mountains':'ne_10m_geography_regions_polys'}.items():tasks.append((name,NE+file+'.geojson',None))
fields='GEOID,NAME,STATE,COUNTY,POP100,AREALAND,AREAWATER,INTPTLAT,INTPTLON'
for name,layer in [('tracts',6),('blockgroups',8)]:tasks.append((name,T+str(layer)+'/query',dict(where="STATE IN ('01','13')",outFields=fields,outSR=4326,maxAllowableOffset=.001 if layer==6 else .0003,f='geojson')))
for name,bbox in {'atlanta-core':[-84.47,33.68,-84.29,33.86],'mobile-core':[-88.16,30.59,-87.96,30.79],'arlington-core':[-87.80,31.88,-87.38,32.23]}.items():tasks.append((name,T+'10/query',dict(where='1=1',geometry=','.join(map(str,bbox)),geometryType='esriGeometryEnvelope',inSR=4326,spatialRel='esriSpatialRelIntersects',outFields=fields,outSR=4326,maxAllowableOffset=.00008,f='geojson')))
tasks.append(('beltline','https://gis.beltline.org/server/rest/services/ABI_Trails_public/FeatureServer/0/query',dict(where='1=1',outFields='*',outSR=4326,f='geojson')))
manifest={}
def get(task):
 name,url,params=task;p=root/(name+'.geojson');r=requests.get(url,params=params,timeout=120);r.raise_for_status();a=r.json();
 if a.get('error'):raise RuntimeError((name,a['error']))
 if a.get('exceededTransferLimit'):raise RuntimeError((name,'Transfer limit exceeded'))
 p.write_bytes(r.content);print(name,len(a.get('features',[])),len(r.content),flush=True)
 return name,dict(url=r.url,bytes=len(r.content),sha256=hashlib.sha256(r.content).hexdigest(),count=len(a.get('features',[])))
with concurrent.futures.ThreadPoolExecutor(max_workers=4)as pool:
 for name,info in pool.map(get,tasks):manifest[name]=info
(root/'download-manifest.json').write_text(json.dumps(manifest,indent=2))
