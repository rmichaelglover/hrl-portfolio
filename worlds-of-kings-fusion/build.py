#!/usr/bin/env python3
"""Topology-preserving cartography in Python, native C++ indexing/coloring."""
from pathlib import Path
import json,subprocess,tempfile
from shapely.geometry import shape,mapping
root=Path(__file__).resolve().parent
source=root.parent/'worlds-of-kings-earth/data/atlas.json'
data=json.loads(source.read_text())
for region in data['regions']+data['countries']:
 geometry=shape(region['geometry'])
 region['geometry']=mapping(geometry if geometry.area<.15 else geometry.simplify(.10,preserve_topology=True))
with tempfile.TemporaryDirectory(prefix='fusion-build-')as directory:
 temporary=Path(directory);raw=temporary/'atlas.json';binary=temporary/'prepare-atlas'
 raw.write_text(json.dumps(data,separators=(',',':')))
 subprocess.run(['g++','-O3','-std=c++17',str(root/'native/prepare-atlas.cpp'),'-ljsoncpp','-o',str(binary)],check=True)
 subprocess.run([str(binary),str(raw),str(root/'data/atlas.json')],check=True)
