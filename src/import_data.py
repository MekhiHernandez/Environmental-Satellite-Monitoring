import ee
import geemap
import requests
import geopandas as gpd
from geemap.coreutils import geojson_to_ee

ee.Authenticate()
ee.Initialize(project='mimetic-sweep-337316')

#identify area of interest with geojson.io
geoJSON = {
  "type": "FeatureCollection",
  "features": [
    {
      "type": "Feature",
      "properties": {},
      "geometry": {
        "type": "Polygon",
        "coordinates": [
          [
            [
              -71.71342120862744,
              -11.832282101257931
            ],
            [
              -71.06758357416118,
              -11.691345110150777
            ],
            [
              -70.9563894019771,
              -12.173073910824613
            ],
            [
              -71.59795481733642,
              -12.313251644788807
            ],
            [
              -71.71342120862744,
              -11.832282101257931
            ]
          ]
        ]
      }
    }
  ]
}

def fetch_region() -> gpd.GeoDataFrame:
    mdd = (ee.FeatureCollection('FAO/GAUL/2025/level1')
           .filter(ee.Filter.eq('GAUL1_NAME', 'Madre De Dios')))
    return geemap.ee_to_gdf(mdd)

def fetch_communities(region: gpd.GeoDataFrame) -> gpd.GeoDataFrame:
    shp = 'data/landmark_data/shp/LandMark_IP_LC_poly_public_v202606.shp'

    peru = gpd.read_file(
        shp,
        where="iso_code LIKE 'PER%'",
        columns=['iso_code', 'name', 'ethncty_1', 'doc_status', 'form_rec', 'data_src'],
    )
    rg_adj = region.to_crs(peru.crs)
    communities = peru[peru.intersects(rg_adj.union_all())]
    communities['geometry'] = communities.geometry.force_2d()
    return communities.to_crs(4326)

def build_community_aois(communities, half_width_m=10000):
    pass

def build_region_grid(region, size_m=20000):
    pass

coords = geoJSON['features'][0]['geometry']['coordinates']
aoi = ee.Geometry.Polygon(coords)

datapoint = (
    ee.ImageCollection('COPERNICUS/S2_SR_HARMONIZED')
    .filterBounds(aoi)
    .filterDate('2020-01-01', '2020-03-07')
    .sort('CLOUDY_PIXEL_PERCENTAGE')
    .first()
    .clip(aoi.bounds())
)

vis_params = {'bands': ['B4','B3','B2'], 'min': 0, 'max': 3000}

def get_image(region, start_date, end_date, collection='COPERNICUS/S2_SR_HARMONIZED'):
    datapoint = (ee.ImageCollection(collection)
        .filterBounds(region)
        .filterDate(start_date, end_date)
        .sort('CLOUDY_PIXEL_PERCENTAGE')
        .first()
        .clip(region.bounds())
    )
    return datapoint

def save_image(image, region, filename, vis_params=vis_params, dimensions=1024):
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
    region = fetch_region()
    print('region rows:', len(region), '| crs:', region.crs)

    communities = fetch_communities(region)
    print('communities:', len(communities), '| crs:', communities.crs)
    print('any 3D shapes left:', communities.geometry.has_z.any())
    print(communities[['name', 'ethncty_1']].head())



