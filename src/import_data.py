"""
Fetch region boundary, community boundaries, and calculate square areas of interest
around each community, and a grid that fully covers the Madre de Dios region for 
classifier training later
"""


import ee
import geemap
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

def fetch_communities_2024(unify_by_name = True) -> gpd.GeoDataFrame:
    shp = 'data/Comunidades_Nativas_2024/Comunidades_Nativas_2024.shp'

    keep_columns=(['OBJECTID', 'PROVINCIA', 'DISTRITO', 'COMUNIDAD', 'FAMILIA', 'GRUPO_ETNI',
                   'RIO', 'RESOL_ADJU', 'FECHA_ADJU', 'NRO_TITULO', 'FECHA_TITU', 'AREA_SIG_h',
                   'SITUACION', 'OTRAS_OBSE', 'geometry'])
    g = gpd.read_file(shp, columns = keep_columns)

    g = g[g.geometry.notna()]
    g['COMUNIDAD'] = g['COMUNIDAD'].str.replace(' (a)', '', regex=False) # to merge expansions
    g['geometry'] = g.geometry.make_valid()
    g = g.rename(columns={'COMUNIDAD': 'name', 'AREA_SIG_h': 'area_ha'})

    if unify_by_name:
        g=g.dissolve(by='name', aggfunc={
            'GRUPO_ETNI': 'first',
            'PROVINCIA': 'first',
            'DISTRITO': 'first',
            'RIO': 'first',
            'SITUACION': 'first',
            'area_ha': 'sum',
        }).reset_index()

    g['community_id'] = [f'CN{i:03d}' for i in range(len(g))]
    g['folder'] = g['name'].str.lower().str.replace(' ','_')

    return g

def build_community_aois(communities: gpd.GeoDataFrame,
                         buffer_m: int = 500) -> gpd.GeoDataFrame:
    utm = communities.to_crs(32719)
    squares = []

    for geom in utm.geometry:
        minx, miny, maxx, maxy = geom.bounds
        cx, cy = (minx + maxx) / 2, (miny + maxy) / 2
        half = max(maxx - minx, maxy - miny) / 2 + buffer_m
        squares.append(box(cx - half, cy - half, cx + half, cy + half))

    aois = gpd.GeoDataFrame(
        utm.drop(columns='geometry'),
        geometry = squares,
        crs = 32719
    )
    aois['buffer_m'] = buffer_m
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

if __name__ == "__main__":
    gpkg = 'data/mdd_monitoring.gpkg'

    region = fetch_region()
    communities = fetch_communities(region)
    community_aois = build_community_aois(communities)
    grid = build_region_grid(region)
    communities_24 = fetch_communities_2024()
    community_aois_24 = build_community_aois(communities_24)

    region.to_file(gpkg, layer='region', driver='GPKG')
    communities.to_file(gpkg, layer='communities', driver='GPKG')
    communities_24.to_file(gpkg, layer='communities_24', driver='GPKG')
    community_aois.to_file(gpkg, layer='community_aois', driver='GPKG')
    community_aois_24.to_file(gpkg, layer='community_aois_24', driver='GPKG')
    grid.to_file(gpkg, layer='region_grid', driver='GPKG')

    print(gpd.list_layers(gpkg))
