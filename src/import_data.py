import ee
import geemap.core as geemap
import requests

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

def save_image(image, region, filename, vis_params=vis_params, dimensions = 1024):
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
    print(datapoint.bandNames().getInfo())
    save_image(datapoint, aoi, 'test.png')
    print(datapoint.propertyNames().getInfo())
    print(f'Saved data/test.png from date {datapoint.date().format('YYYY-MM-dd').getInfo()}')



