# EnvironmentalSatelliteMonitoring
Satellite monitoring of environmental changes (gold mining, deforestation, fires) surrounding indigenous communities in Madre de Dios, Peru. The project uses Sentinel-2 imagery from Google Earth Engine to map changes over time, with the goal of training a UNet classifier on Sentinel 1 & 2 images to detect mining activity.

### Goals
- Identify regions of indigenous communities and build areas of interest around each one (territory & buffer)
- Produce cloud-free visible light composite images to track changes year over year
- Retrieve radar images from Sentinel-1 to test change detection even through cloud cover
- Train and validate a classifier to detect mining
- Summarize changes near each community

### Checklist
[*] Create AOIs for 2024 update indigenous communities
[] Pull alerts from GeoBosque
[] Pull sentinel-2 images for each AOI across the years
[] Create map of recent alerts
[] Get mining concessions from the state
[] Pull landsat data for older comparisons

### Study Area
The area of study is the departament of Madre de Dios, Peru. Madre de Dios covers ~84,000 km<sup>2</sup>, which is covered by 22 Sentinel-2 tiles.
//
There are 37 indigenous community territories within this area.

### Resources:
Used [geojson.io](geojson.io) to identify coordinate regions for AOIs (areas of interest)

[Earth Engine Data Catalog](https://developers.google.com/earth-engine/datasets)

[FAO GAUL 2025](https://developers.google.com/earth-engine/datasets/catalog/FAO_GAUL_2025_level1) The Food and Agriculture Organization of the United Nations provides global administrative region data (including for Madre de Dios)

[Landmark](https://landmarkmap.org/data-methods/access-data) Indigenous Peoples’ and Local Community Lands and Territories dataset was used for indigenous region boundaries
Last update: June 2026
CC BY-SA 4.0

[GeoBosques](https://geobosques.minam.gob.pe/geobosque/view/index.php) Deforestation alert data provided by the Peruvian ministry of the environment

[Amazon Mining Watch](https://amazonminingwatch.org/en/about) MAAP's amazon mining watch, complete with data available for download and methodology on how mining is detected

