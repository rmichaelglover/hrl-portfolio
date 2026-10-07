#!/usr/bin/env python3
"""Build an attributed, simplified Natural Earth atlas and inspectable route candidates.
Requires shapely. Source inputs are cached outside the repository.
"""
import argparse, hashlib, json, math
from pathlib import Path
from collections import defaultdict
from shapely.geometry import shape, mapping, Polygon, MultiPolygon, box
from shapely.geometry.polygon import orient
from shapely.ops import unary_union
from shapely import make_valid
from shapely.strtree import STRtree

ROOT=Path(__file__).resolve().parent
SOURCES={name:f'https://raw.githubusercontent.com/nvkelso/natural-earth-vector/v5.1.2/geojson/{file}' for name,file in {'countries':'ne_10m_admin_0_countries.geojson','provinces':'ne_10m_admin_1_states_provinces.geojson','cities':'ne_10m_populated_places.geojson'}.items()}

def polygons(g):
 if g.geom_type=='Polygon':return [g]
 if g.geom_type in ['MultiPolygon','GeometryCollection']:return [p for child in g.geoms for p in polygons(child)]
 return []
def tidy(g,tolerance=.012):
 ps=polygons(make_valid(g))
 if not ps:return None
 g=unary_union(ps).simplify(tolerance,preserve_topology=True)
 ps=polygons(g)
 return MultiPolygon([orient(p,sign=-1) for p in ps]) if len(ps)>1 else orient(ps[0],sign=-1)
def rounded(v):
 if isinstance(v,(tuple,list)):return[rounded(x)for x in v]
 return round(v,5)if isinstance(v,float)else v
def geo(g):
 obj=mapping(g);return{'type':obj['type'],'coordinates':rounded(obj['coordinates'])}
def anchor(g):
 p=max(polygons(g),key=lambda p:p.area).representative_point();return[round(p.x,5),round(p.y,5)]
def bearing(a,b):
 l1,l2=math.radians(a[1]),math.radians(b[1]);d=math.radians((b[0]-a[0]+180)%360-180)
 return math.degrees(math.atan2(math.sin(d)*math.cos(l2),math.cos(l1)*math.sin(l2)-math.sin(l1)*math.cos(l2)*math.cos(d)))%360

def main():
 args=argparse.ArgumentParser();args.add_argument('--source-dir',type=Path,default=Path('/tmp/world-kings-natural-earth'));opt=args.parse_args()
 raw={name:json.loads((opt.source_dir/f'{name}.geojson').read_text())['features']for name in SOURCES}
 countries=[];country_shapes={};country_ids={}
 for f in raw['countries']:
  p=f['properties'];g=tidy(shape(f['geometry']));code=p['ADM0_A3'];country_ids[code]=len(countries);country_shapes[code]=g
  countries.append({'id':code,'name':p.get('NAME_EN')or p['NAME'],'formal':p.get('FORMAL_EN')or p['ADMIN'],'iso2':p.get('ISO_A2'),'iso3':p.get('ISO_A3'),'continent':p.get('CONTINENT'),'center':anchor(g),'geometry':geo(g),'spaces':[]})
 regions=[];shapes=[]
 for f in raw['provinces']:
  p=f['properties'];code=p['adm0_a3'];g=tidy(shape(f['geometry']));
  if not g:continue
  name=p.get('name_en')or p.get('name')or f"{countries[country_ids[code]]['name']} · unnamed administrative area"
  n=len(regions);countries[country_ids[code]]['spaces'].append(n)
  regions.append({'id':n,'key':p['adm1_code'],'name':name,'local':p.get('name')or name,'country':code,'kind':'province','center':anchor(g),'geometry':geo(g),'extent':rounded(g.bounds),'neighbors':[],'routes':[[]for _ in range(8)]});shapes.append(g)
 for c in countries:
  if not c['spaces']:
   g=country_shapes[c['id']];n=len(regions);c['spaces'].append(n);regions.append({'id':n,'key':'country-'+c['id'],'name':c['name'],'local':c['name'],'country':c['id'],'kind':'country fallback','center':anchor(g),'geometry':geo(g),'extent':rounded(g.bounds),'neighbors':[],'routes':[[]for _ in range(8)]});shapes.append(g)
 print('Land spaces:',len(regions),flush=True)
 land=unary_union(list(country_shapes.values()));land_count=len(regions)
 # Ocean spaces are actual water portions of 12-degree graticule cells; coastlines remain land borders.
 ocean_grid=defaultdict(list)
 for row in range(15):
  north=90-row*12;south=north-12
  for col in range(30):
   west=-180+col*12;g=box(west,south,west+12,north).difference(land)
   for part in polygons(g):
    if part.area<.00005:continue
    gpart=tidy(part,.012)
    if not gpart:continue
    n=len(regions);ocean_grid[(col,row)].append(n)
    regions.append({'id':n,'key':f'ocean-{col}-{row}-{len(ocean_grid[(col,row)])}','name':f'Ocean space {row+1}:{col+1}'+(f" · coastal part {len(ocean_grid[(col,row)])}"if len(ocean_grid[(col,row)])>1 else ''),'local':'','country':None,'kind':'ocean','center':anchor(gpart),'geometry':geo(gpart),'extent':rounded(gpart.bounds),'row':row,'col':col,'neighbors':[],'routes':[[]for _ in range(8)]});shapes.append(gpart)
 print('Ocean spaces:',len(regions)-land_count,flush=True)
 tree=STRtree(shapes);adj=[set()for _ in regions];corner=[set()for _ in regions];boundary=[g.boundary for g in shapes]
 # Candidate graph, not a final legal-move atlas. Tolerance bridges cartographic simplification seams.
 for i,g in enumerate(shapes):
  for j in tree.query(g.buffer(.02)):
   j=int(j)
   if j<=i:continue
   if boundary[i].distance(boundary[j])>.02:continue
   intersection=boundary[i].intersection(boundary[j])
   if intersection.length>.00001 or not g.intersects(shapes[j]):adj[i].add(j);adj[j].add(i)
   else:corner[i].add(j);corner[j].add(i)
  if i%1000==0:print('Connections:',i,flush=True)
 # Geographic seams are explicit. Connect matching ocean components across the date line and poles.
 polar=set();wrap=set()
 for row in range(15):
  for a in ocean_grid.get((0,row),[]):
   for b in ocean_grid.get((29,row),[]):
    # Both components must actually meet their respective date-line boundaries.
    if shapes[a].bounds[0]<-179.99 and shapes[b].bounds[2]>179.99:adj[a].add(b);adj[b].add(a);wrap.add(tuple(sorted((a,b))))
 for row in [0,14]:
  for col in range(15):
   for a in ocean_grid.get((col,row),[]):
    for b in ocean_grid.get((col+15,row),[]):
     pole=90 if row==0 else -90
     if abs(shapes[a].bounds[3 if row==0 else 1]-pole)<.01 and abs(shapes[b].bounds[3 if row==0 else 1]-pole)<.01:adj[a].add(b);adj[b].add(a);polar.add(tuple(sorted((a,b))))
 for i,r in enumerate(regions):
  r['neighbors']=sorted(adj[i]);diagonal=set(corner[i])
  for j in adj[i]:diagonal.update(adj[j])
  diagonal.discard(i);diagonal.difference_update(adj[i])
  # Cardinal candidates use edge contacts; diagonal candidates are corners or two edge steps.
  for d in range(8):
   target=d*45;candidates=adj[i] if d%2==0 else diagonal
   ranked=[]
   for j in candidates:
    angle=bearing(r['center'],regions[j]['center']);delta=abs((angle-target+180)%360-180)
    if delta<=50:ranked.append((delta,j))
   r['routes'][d]=[j for _,j in sorted(ranked)[:3 if d%2==0 else 1]]
  for j in adj[i]:
   if tuple(sorted((i,j)))in polar:r['routes'][0 if r.get('row')==0 else 4]=[j]
 cities=[]
 for f in raw['cities']:
  p=f['properties'];lon,lat=f['geometry']['coordinates'];cities.append({'name':p.get('NAME_EN')or p['NAME'],'local':p.get('NAME')or '', 'country':p['ADM0_A3'],'population':p.get('POP_MAX')or 0,'capital':bool(p.get('ADM0CAP')),'center':[round(lon,5),round(lat,5)],'key':str(p['NE_ID'])})
 cities.sort(key=lambda c:-c['population'])
 manifest={'source':'Natural Earth','release':'v5.1.2','rights':'Public domain map data; source notices remain distinct from portfolio code licensing.','source_urls':SOURCES,'source_sha256':{name:hashlib.sha256((opt.source_dir/f'{name}.geojson').read_bytes()).hexdigest()for name in SOURCES},'mapped_countries_and_territories':len(countries),'source_province_features':len(raw['provinces']),'land_spaces':land_count,'ocean_spaces':len(regions)-land_count,'cities':len(cities),'simplification_degrees':.012,'connection_tolerance_degrees':.02,'notes':['Natural Earth uses de facto boundaries and includes territories and disputed areas. This pinned snapshot is not a statement of recognition or a live authoritative border service.','Province features are heterogeneous administrative levels, not an assertion that every region is legally equivalent to a US state.','Countries lacking a province feature receive a labeled country fallback, not an invented province.','Routes are candidates for inspection, not a validated full-match movement ruleset. Some cardinal sectors may be empty. Diagonal candidates can skip two edge steps.','Population values are source estimates of differing vintages, not current census rankings.','Ocean components separated by land within a grid cell are distinct spaces. The ocean mask follows the country-layer land union; residual inland water may remain.']}
 data={'manifest':manifest,'countries':countries,'regions':regions,'cities':cities,'polar_links':[list(x)for x in sorted(polar)],'date_line_links':[list(x)for x in sorted(wrap)]}
 out=ROOT/'data'/'atlas.json';out.write_text(json.dumps(data,ensure_ascii=False,separators=(',',':')));(ROOT/'data'/'manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n')
 print('Atlas:',out.stat().st_size,'bytes',flush=True)
if __name__=='__main__':main()
