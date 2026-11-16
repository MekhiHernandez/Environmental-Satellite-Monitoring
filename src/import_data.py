"""
Fetch region boundary, community boundaries, and calculate square areas of interest
around each community, and a grid that fully covers the Madre de Dios region for 
classifier training later
"""


import ee
import geemap
import requests
import geopandas as gpd
import math

from shapely.geometry import box

ee.Authenticate()
ee.Initialize(project='mimetic-sweep-337316')

def fetch_region() -> gpd.GeoDataFrame:
    mdd = (ee.FeatureCollection('FAO/GAUL/2025/level1')
           .filter(ee.Filter.eq('GAUL1_NAME', 'Madre De Dios')))
    return geemap.ee_to_gdf(mdd)

def fetch_communities(region: gpd.GeoDataFrame) -> gpd.GeoDataFrame:
    shp = 'data/landmark_data/shp/LandMark_IP_LC_poly_public_v202606.shp'

    peru = gpd.read_file(
        shp,
        where="iso_code LIKE 'PER%'",
        columns=['iso_code', 'landmark_i', 'name', 'ethncty_1', 'doc_status', 'form_rec', 'data_src'],
    )
    peru = peru.rename(columns={'landmark_i':'community_id'})
    rg_adj = region.to_crs(peru.crs)
    communities = peru[peru.intersects(rg_adj.union_all())]
    communities['geometry'] = communities.geometry.force_2d()
    return communities.to_crs(4326)

def build_community_aois(communities: gpd.GeoDataFrame,
                         buffer_m: int = 5000) -> gpd.GeoDataFrame:
    utm = communities.to_crs(32719)
    squares = []

    for geom in utm.geometry:
        minx, miny, maxx, maxy = geom.bounds
        cx, cy = (minx + maxx) / 2, (miny + maxy) / 2
        half = max(maxx - minx, maxy - miny) / 2 + buffer_m
        squares.append(box(cx - half, cy - half, cx + half, cy + half))

    aois = gpd.GeoDataFrame(
        {
            'community_id': utm['community_id'].values,
            'name': utm['name'].values,
            'buffer_m': buffer_m,
        },
        geometry = squares,
        crs = 32719
    )
    return aois.to_crs(4326)

def build_region_grid(region: gpd.GeoDataFrame, size_m: int = 20000) -> gpd.GeoDataFrame:
    utm = region.to_crs(32719)
    area = utm.union_all()
    minx, miny, maxx, maxy = area.bounds

    start_x = math.floor(minx / size_m) * size_m
    start_y = math.floor(miny / size_m) * size_m
    n_cols = math.ceil((maxx - start_x) / size_m)
    n_rows = math.ceil((maxy - start_y) / size_m)

    cells = []
    for row in range(n_rows):
        for col in range(n_cols):
            x, y = start_x + col * size_m, start_y + row * size_m
            cell = box(x, y, x+size_m, y+size_m)

            if cell.intersects(area):
                cells.append({
                    'grid_id': f'r{row:02d}_c{col:02d}',
                    'row': row,
                    'col': col,
                    'size_m': size_m,
                    'frac_in_region': round(cell.intersection(area).area / cell.area, 3),
                    'geometry': cell,
                })
    grid = gpd.GeoDataFrame(cells, crs=32719)
    return grid.to_crs(4326)

def get_image(region, start_date, end_date, collection='COPERNICUS/S2_SR_HARMONIZED'):
    datapoint = (ee.ImageCollection(collection)
        .filterBounds(region)
        .filterDate(start_date, end_date)
        .sort('CLOUDY_PIXEL_PERCENTAGE')
        .first()
        .clip(region.bounds())
    )
    return datapoint

def save_image(image, region, filename, vis_params={'bands': ['B4','B3','B2'], 'min': 0, 'max': 3000}, dimensions=1024):
    url = image.getThumbURL({
        **vis_params,
        'region': region,
        'dimensions': dimensions,
        'format': 'png'
    })

    response = requests.get(url)
    response.raise_for_status()

    with open(f'data/{filename}', 'wb') as f:
        f.write(response.content)


if __name__ == "__main__":
    gpkg = 'data/mdd_monitoring.gpkg'

    region = fetch_region()
    communities = fetch_communities(region)
    community_aois = build_community_aois(communities)
    grid = build_region_grid(region)

    region.to_file(gpkg, layer='region', driver='GPKG')
    communities.to_file(gpkg, layer='communities', driver='GPKG')
    community_aois.to_file(gpkg, layer='community_aois', driver='GPKG')
    grid.to_file(gpkg, layer='region_grid', driver='GPKG')

    print(gpd.list_layers(gpkg))



