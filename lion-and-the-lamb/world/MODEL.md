# The Lion and the Lamb: spatial scenario atlas

An imaginative three-zone world, anchored to public population and geographic data. The map explores ordinary human areas, a managed buffer, and a wild-wild zone. Its colors are population-derived scenario candidates, not established habitat, legal designations, animal safety assessments, or a plan for keeping wildlife.

## Classification

For each displayed population unit, density = source population / source land area in square kilometres. Default thresholds are 10 and 300 people/km²: below 10 is a low-population candidate; 10–299.999 is a buffer candidate; 300 or more is a human-pressure candidate. Missing population or usable area is unknown. Users may change thresholds. These thresholds are illustrative choices, not fitted ecological estimates.

At global scale, Natural Earth country population estimates are divided by approximate WGS84 polygon area; estimates have varying source years. This treats each country uniformly. At regional scale, 2020 Census counts and land areas replace those averages. Changing resolution can therefore change colors without representing a change over time. Empty roads, industrial land, and low-population land are not necessarily wilderness. Density alone cannot establish habitat suitability.

## Detail and coverage

Georgia and Alabama use counties and then census tracts. Atlanta and Mobile metropolitan boundaries select census block groups by representative point; full units remain intact, so edge units can extend beyond the metropolitan boundary. Arlington is the unincorporated Alabama community in Wilcox County, with surrounding county block groups; it is not presented as a formal metropolitan area.

Highest detail uses 2020 census blocks in these focus windows, not full metropolitan coverage:

| Focus | West | South | East | North |
|---|---:|---:|---:|---:|
| Atlanta | −84.47 | 33.68 | −84.29 | 33.86 |
| Mobile | −88.16 | 30.59 | −87.96 | 30.79 |
| Arlington, Alabama | −87.80 | 31.88 | −87.38 | 32.23 |

Display geometry is simplified; original census population and land-area denominators are retained. The atlas loads finer datasets as the camera approaches these regions. Optional layers show generalized global rivers, lakes, transport routes, urban areas, and mountain/range/plateau polygons. Mountain polygons are not an elevation raster. USGS transportation provides finer roads and rail in the focus windows. Local USGS hydrography is supplied for Atlanta and Mobile; Arlington currently falls back to regional/global water coverage. Coverage is not a claim that every creek or road is included.

Geographic corridors are drawn as context. The current model does not calculate species-specific movement, connectivity, permeability, carrying capacity, domestication, or injury probabilities. The companion garden model is a separate synthetic demonstration, not a calibrated ecological prediction.

## BeltLine wildlife lane

The purple route follows public BeltLine trail alignment geometry. A separate wildlife lane, tiny pond and creek concepts, and day/night animal symbols are imagined additions—not existing or approved infrastructure. The symbols illustrate familiar native wildlife groups and do not describe measured wildlife occupancy. Axolotls are omitted.

## Data provenance

- [Natural Earth](https://www.naturalearthdata.com/), pinned to [v5.1.2](https://github.com/nvkelso/natural-earth-vector/tree/v5.1.2): countries, population estimates, rivers, lakes, roads, rails, urban areas, and geographic regions. Natural Earth data is public domain.
- [U.S. Census Bureau Census2020 TIGERweb service](https://tigerweb.geo.census.gov/arcgis/rest/services/Census2020/tigerWMS_Census2020/MapServer): counties (82), tracts (6), block groups (8), blocks (10), and metropolitan areas (76); population field POP100 and land area AREALAND.
- [USGS transportation service](https://carto.nationalmap.gov/arcgis/rest/services/transportation/MapServer): road classes 29, 30, 31, 32, 35 and rail 38.
- [USGS hydrography service](https://hydro.nationalmap.gov/arcgis/rest/services/nhd/MapServer): flowlines 6 and water bodies 12.
- [Atlanta BeltLine public trail GIS](https://gis.beltline.org/server/rest/services/ABI_Trails_public/FeatureServer/0): public trail alignments, attributed to Atlanta BeltLine. Public availability is not a blanket license claim for all BeltLine website content.

[The manifest](data/manifest.json) records source hashes, available query metadata, generated dataset sizes and hashes, and focus coordinates. Federal data sources are attributed independently of the scenario.

## Building and responsiveness

`build.py` uses Python, Shapely, and pyproj. Raw GeoJSON inputs are expected in `/tmp/lamb-world-sources`, with pinned Natural Earth country input at `/tmp/world-kings-natural-earth/countries.geojson`. The output includes only simplified model data, not the large raw cache. The source service links above and manifest describe retrieval; rebuilding requires obtaining those inputs first.

Canvas drawing uses viewport filtering, cached Path2D geometry, animation-frame scheduling, and progressive loading. Geographic path precision is retained to avoid collapsing neighborhood roads and blocks. Detail downloads are larger than the initial country layer; responsiveness depends on device and connection. Desktop/mobile checks cover loading, region selection, day/night symbols, controls, and overflow.

Validation: `node test-data.cjs`; companion garden validation: `node ../test-model.cjs`.
