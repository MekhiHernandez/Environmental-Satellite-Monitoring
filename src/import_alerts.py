"""
Import alert data from GeoBosques, the peruvian government alerts
"""

import requests
import pandas as pd
import geopandas as gpd

# GeoBosques early deforestation alerts (MINAM). Each point is one ~30 m Landsat pixel.
URL = 'https://gis.bosques.gob.pe/server/rest/services/Interoperabilidad/alertas_tempranas_pt_2026/MapServer/0/query'
PAGE_SIZE = 2000    # the server never sends more than this per request

def fetch_alerts(where: str) -> gpd.GeoDataFrame:
    params = {
        'where': where,
        'outFields': '*',
        'orderByFields': 'objectid',    # same order every time, so pages don't overlap
        'resultOffset': 0,
        'resultRecordCount': PAGE_SIZE,
        'f': 'geojson',
    }
    features = []

    while True:
        response = requests.get(URL, params=params)
        response.raise_for_status()     # stop if the server returned an error
        page = response.json()['features']

        features += page
        print(f"got {len(page)} rows at offset {params['resultOffset']}")

        if len(page) < PAGE_SIZE:       # short page = last page
            break
        params['resultOffset'] += PAGE_SIZE

    alerts = gpd.GeoDataFrame.from_features(features, crs=4326)
    alerts['fe_alerta'] = pd.to_datetime(alerts['fe_alerta'], unit='ms')   # ms since 1970 -> date
    return alerts


if __name__ == "__main__":
    gpkg = 'data/mdd_monitoring.gpkg'

    alerts = fetch_alerts("ubigeo LIKE '17%'")    # 17 = Madre de Dios
    print(len(alerts), 'alerts from', alerts['fe_alerta'].min().date(), 'to', alerts['fe_alerta'].max().date())

    alerts.to_file(gpkg, layer='alerts_latest_week', driver='GPKG')
