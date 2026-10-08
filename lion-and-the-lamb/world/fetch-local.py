from pathlib import Path
import requests,json,hashlib,concurrent.futures
root=Path('/tmp/lamb-world-sources');tasks=[]
for place,bbox in {'atlanta':[-84.47,33.68,-84.29,33.86],'mobile':[-88.16,30.59,-87.96,30.79],'arlington':[-87.80,31.88,-87.38,32.23]}.items():
 for kind,base,layers in [('roads','https://carto.nationalmap.gov/arcgis/rest/services/transportation/MapServer/',[29,30,31,32,35,38]),('water','https://hydro.nationalmap.gov/arcgis/rest/services/nhd/MapServer/',[6,12])]:
  for layer in layers:tasks.append((f'{place}-{kind}-{layer}',base+str(layer)+'/query',dict(where='1=1',geometry=','.join(map(str,bbox)),geometryType='esriGeometryEnvelope',inSR=4326,spatialRel='esriSpatialRelIntersects',outFields='*',outSR=4326,geometryPrecision=5,maxAllowableOffset=.0001,resultRecordCount=10000,f='geojson')))
def get(t):
 name,url,params=t;p=root/(name+'.geojson')
 if p.exists():
  data=p.read_bytes();a=json.loads(data);print(name,len(a.get('features',[])),'cached',flush=True);return name,dict(url=url,query=params,sha256=hashlib.sha256(data).hexdigest(),count=len(a.get('features',[])))
 params={**params,'resultRecordCount':1000,'orderByFields':'OBJECTID'};features=[];offset=0
 while True:
  r=requests.get(url,params={**params,'resultOffset':offset},timeout=120);r.raise_for_status();a=r.json()
  if a.get('error'):raise RuntimeError((name,a['error']))
  batch=a.get('features',[]);features.extend(batch)
  if not a.get('exceededTransferLimit'):break
  if not batch:raise RuntimeError((name,'empty truncated page'))
  offset+=len(batch)
 data=json.dumps({'type':'FeatureCollection','features':features},separators=(',',':')).encode();p.write_bytes(data);print(name,len(features),flush=True);return name,dict(url=url,query=params,sha256=hashlib.sha256(data).hexdigest(),count=len(features))

manifest={}
with concurrent.futures.ThreadPoolExecutor(max_workers=4)as pool:
 for name,info in pool.map(get,tasks):manifest[name]=info
(root/'local-download-manifest.json').write_text(json.dumps(manifest,indent=2))
