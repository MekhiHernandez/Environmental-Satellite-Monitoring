"""
Import mining concessions (catastro minero) from INGEMMET's GEOCATMIN service.
Each feature is one mining right (polygon) with its holder, status and mineral type.
"""

import time
from pathlib import Path

import certifi
import requests
import geopandas as gpd

URL = 'https://geocatmin.ingemmet.gob.pe/arcgis/rest/services/SERV_CATASTRO_MINERO/MapServer/0/query'
# Madre de Dios small-scale/artisanal mining zone ("mining corridor"), set by decree D.L. 1100
CORRIDOR_URL = 'https://geocatmin.ingemmet.gob.pe/arcgis/rest/services/SERV_CATASTRO_MADRE_DIOS/MapServer/1/query'
PAGE_SIZE = 1000    # the server never sends more than this per request
RETRIES = 4         # INGEMMET's server is sometimes slow, so retry before giving up

# INGEMMET's server doesn't send its intermediate certificate, so Python can't verify it.
# Add that certificate (saved in certs/) to the normal trusted list and use the combined file.
CA_BUNDLE = Path('data/ingemmet_ca_bundle.pem')
if not CA_BUNDLE.exists():
    CA_BUNDLE.write_text(Path(certifi.where()).read_text()
                         + Path('certs/sectigo_ov_r36.pem').read_text())


def query(params: dict) -> dict:
    # try the request a few times, waiting 2, 4, 8... seconds between attempts
    for attempt in range(RETRIES):
        try:
            response = requests.get(URL, params=params, timeout=120, verify=CA_BUNDLE)
            response.raise_for_status()
            break
        except requests.RequestException as e:
            if attempt == RETRIES - 1:
                raise
            wait = 2 ** (attempt + 1)
            print(f'  request failed ({e}), retrying in {wait}s')
            time.sleep(wait)

    data = response.json()
    if 'error' in data:     # the server answered, but rejected the query
        raise RuntimeError(data['error'])
    return data


def fetch_concessions(depa: str = 'MADRE DE DIOS', status: str | None = None,
                      bbox: list[float] | None = None) -> gpd.GeoDataFrame:
    # build the filter, e.g. "DEPA = 'MADRE DE DIOS' AND LEYENDA = 'TITULADO'"
    conditions = []
    if depa:
        conditions.append(f"DEPA = '{depa}'")
    if status:
        conditions.append(f"LEYENDA = '{status}'")
    where = ' AND '.join(conditions) or '1=1'

    params = {'where': where, 'f': 'json'}
    if bbox:
        params['geometry'] = ','.join(str(v) for v in bbox)   # xmin,ymin,xmax,ymax
        params['geometryType'] = 'esriGeometryEnvelope'
        params['inSR'] = 4326
        params['spatialRel'] = 'esriSpatialRelIntersects'

    # This server doesn't support resultOffset paging. Instead, first ask for the
    # IDs of every matching row (that list isn't capped), then fetch the rows
    # 1000 IDs at a time using an ID range.
    ids = sorted(query({**params, 'returnIdsOnly': 'true'})['objectIds'] or [])
    print(f'{len(ids)} matching concessions')

    features = []
    for start in range(0, len(ids), PAGE_SIZE):
        chunk = ids[start:start + PAGE_SIZE]
        page = query({
            **params,
            'where': f'({where}) AND OBJECTID >= {chunk[0]} AND OBJECTID <= {chunk[-1]}',
            'outFields': '*',
            'outSR': 4326,
            'f': 'geojson',
        })['features']
        features += page
        print(f'got {len(page)} rows (total {len(features)} of {len(ids)})')

    if not features:
        return gpd.GeoDataFrame(geometry=[], crs=4326)
    return gpd.GeoDataFrame.from_features(features, crs=4326)


def fetch_mining_corridor() -> gpd.GeoDataFrame:
    # the layer is a single polygon, so one request is enough (no paging)
    response = requests.get(CORRIDOR_URL, params={
        'where': '1=1',
        'outFields': 'CODIGO,NOMBRE,HAS,FEC_ING',
        'outSR': 4326,
        'f': 'geojson',
    }, timeout=120, verify=CA_BUNDLE)
    response.raise_for_status()

    corridor = gpd.GeoDataFrame.from_features(response.json()['features'], crs=4326)
    return corridor.rename(columns={'CODIGO': 'code', 'NOMBRE': 'name',
                                    'HAS': 'area_ha', 'FEC_ING': 'date_entered'})


if __name__ == "__main__":
    gpkg = 'data/mdd_monitoring.gpkg'

    concessions = fetch_concessions()    # defaults to MADRE DE DIOS, all statuses
    # e.g. fetch_concessions(status='TITULADO') or fetch_concessions(bbox=[-70.5, -13.2, -69.5, -12.5])
    concessions.to_file('data/concessions.geojson', driver='GeoJSON')
    print('saved data/concessions.geojson')

    corridor = fetch_mining_corridor()
    corridor.to_file(gpkg, layer='mining_corridor', driver='GPKG')
    print(gpd.list_layers(gpkg))
