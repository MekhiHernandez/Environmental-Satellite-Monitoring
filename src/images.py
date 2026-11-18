"""
Build cloud-free Sentinel-2 composites and save them as PNGs, including a
yearly image series for each community with its boundary drawn on top.
Reads the AOI and community layers that import_data.py writes to the GeoPackage.
"""

import ee
import geemap
import requests
import geopandas as gpd

from pathlib import Path

ee.Authenticate()
ee.Initialize(project='mimetic-sweep-337316')


def get_image(region, start_date, end_date, collection='COPERNICUS/S2_SR_HARMONIZED'):
    datapoint = (ee.ImageCollection(collection)
        .filterBounds(region)
        .filterDate(start_date, end_date)
        .sort('CLOUDY_PIXEL_PERCENTAGE')
        .first()
        .clip(region.bounds())
    )
    return datapoint

def mask_clouds(image: ee.Image) -> ee.Image:
    """
    Helper function for get_composite
    """
    scl = image.select('SCL')
    clear = (scl.neq(3)
             .And(scl.neq(8))
             .And(scl.neq(9))
             .And(scl.neq(10)))
    return image.updateMask(clear)

def get_composite(aoi: ee.Geometry, year: int,
                  collection: str ='COPERNICUS/S2_SR_HARMONIZED') -> ee.Image:
    """
    Create composite image of the dry season ground images for a year
    to get unclouded view
    """
    collection = (ee.ImageCollection(collection)
                  .filterBounds(aoi)
                  .filterDate(f'{year}-06-01', f'{year}-10-01')
                  .filter(ee.Filter.lt('CLOUDY_PIXEL_PERCENTAGE',60)))
    collection = collection.map(mask_clouds)
    composite = collection.median()
    return composite


def save_image(image, region, path, vis_params={'bands': ['B4','B3','B2'], 'min': 0, 'max': 3000}, dimensions=1024):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)

    url = image.getThumbURL({
        **vis_params,
        'region': region,
        'dimensions': dimensions,
        'format': 'png'
    })

    response = requests.get(url)
    response.raise_for_status()

    with open(path, 'wb') as f:
        f.write(response.content)


def save_community_timeseries(aois: gpd.GeoDataFrame, communities: gpd.GeoDataFrame,
                              years: range, out_dir: str = 'data/images',
                              dimensions: int = 1024) -> list[str]:
    """
    Save one dry-season composite per community per year, with the community
    boundary drawn on top. Skips images that already exist. Returns the paths
    that failed so they can be retried.
    """
    failed = []

    for i in range(len(aois)):
        one = aois.iloc[[i]]
        cid = one['community_id'].iloc[0]
        folder = one['folder'].iloc[0]

        aoi = geemap.gdf_to_ee(one).geometry()
        boundary = geemap.gdf_to_ee(communities[communities['community_id'] == cid])
        outline = boundary.style(color='yellow', fillColor='00000000', width=2)

        for year in years:
            path = Path(out_dir) / folder / f'bound_comm_{year}.png'
            if path.exists():
                continue

            print(f'{cid} {folder} {year}...')
            try:
                img = get_composite(aoi, year)
                rgb = img.visualize(bands=['B4', 'B3', 'B2'], min=0, max=3000)
                save_image(rgb.blend(outline), aoi, path, vis_params={}, dimensions=dimensions)
            except Exception as e:
                print(f'  failed: {e}')
                failed.append(str(path))

    return failed


if __name__ == "__main__":
    gpkg = 'data/mdd_monitoring.gpkg'

    aois = gpd.read_file(gpkg, layer='community_aois_24')
    communities = gpd.read_file(gpkg, layer='communities_24')

    failed = save_community_timeseries(aois, communities, years=range(2019, 2027))
    print(f'{len(failed)} failed:', failed)
