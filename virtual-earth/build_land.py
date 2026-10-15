#!/usr/bin/env python3
"""Strip metadata from pinned public-domain physical land geometry.
Usage: python3 build_land.py /path/to/ne_50m_land.geojson
Download: https://raw.githubusercontent.com/nvkelso/natural-earth-vector/v5.1.2/geojson/ne_50m_land.geojson
Expected source SHA256: e874b27a51d146452be360cafb3cc50c86001074a67d534113e6534682f9826b
"""
import hashlib
import json
from pathlib import Path
import sys
ROOT = Path(__file__).resolve().parent
raw = Path(sys.argv[1]).read_bytes()
assert hashlib.sha256(raw).hexdigest() == 'e874b27a51d146452be360cafb3cc50c86001074a67d534113e6534682f9826b', 'Unexpected source revision'
source = json.loads(raw)
polygons = []
for item in source['features']:
    geometry = item['geometry']
    polygons.extend([geometry['coordinates']] if geometry['type'] == 'Polygon' else geometry['coordinates'])
(ROOT / 'data/land.json').write_text(json.dumps({'type':'MultiPolygon','coordinates':polygons},separators=(',',':')))
print('Physical land polygons:',len(polygons))
