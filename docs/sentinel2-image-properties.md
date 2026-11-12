# Sentinel-2 Reference

## Bands

Source: [Earth Engine Data Catalog, COPERNICUS/S2_SR_HARMONIZED](https://developers.google.com/earth-engine/datasets/catalog/COPERNICUS_S2_SR_HARMONIZED#bands)

Pixel size: varies

| Name | Units | Min | Max | Scale | Pixel Size | Wavelength | Description |
|---|---|---|---|---|---|---|---|
| `B1` | | | | 0.0001 | 60 meters | 443.9nm (S2A) / 442.3nm (S2B) | Aerosols |
| `B2` | | | | 0.0001 | 10 meters | 496.6nm (S2A) / 492.1nm (S2B) | Blue |
| `B3` | | | | 0.0001 | 10 meters | 560nm (S2A) / 559nm (S2B) | Green |
| `B4` | | | | 0.0001 | 10 meters | 664.5nm (S2A) / 665nm (S2B) | Red |
| `B5` | | | | 0.0001 | 20 meters | 703.9nm (S2A) / 703.8nm (S2B) | Red Edge 1 |
| `B6` | | | | 0.0001 | 20 meters | 740.2nm (S2A) / 739.1nm (S2B) | Red Edge 2 |
| `B7` | | | | 0.0001 | 20 meters | 782.5nm (S2A) / 779.7nm (S2B) | Red Edge 3 |
| `B8` | | | | 0.0001 | 10 meters | 835.1nm (S2A) / 833nm (S2B) | NIR |
| `B8A` | | | | 0.0001 | 20 meters | 864.8nm (S2A) / 864nm (S2B) | Red Edge 4 |
| `B9` | | | | 0.0001 | 60 meters | 945nm (S2A) / 943.2nm (S2B) | Water vapor |
| `B11` | | | | 0.0001 | 20 meters | 1613.7nm (S2A) / 1610.4nm (S2B) | SWIR 1 |
| `B12` | | | | 0.0001 | 20 meters | 2202.4nm (S2A) / 2185.7nm (S2B) | SWIR 2 |
| `AOT` | | | | 0.001 | 10 meters | None | Aerosol Optical Thickness |
| `WVP` | cm | | | 0.001 | 10 meters | None | Water Vapor Pressure. The height the water would occupy if the vapor were condensed into liquid and spread evenly across the column. |
| `SCL` | | 1 | 11 | | 20 meters | None | Scene Classification Map (The "No Data" value of 0 is masked out) |
| `TCI_R` | | | | | 10 meters | None | True Color Image, Red channel |
| `TCI_G` | | | | | 10 meters | None | True Color Image, Green channel |
| `TCI_B` | | | | | 10 meters | None | True Color Image, Blue channel |
| `MSK_CLDPRB` | | 0 | 100 | | 20 meters | None | Cloud Probability Map (missing in some products) |
| `MSK_SNWPRB` | | 0 | 100 | | 20 meters | None | Snow Probability Map (missing in some products) |
| `QA10` | | | | | 10 meters | None | Always empty |
| `QA20` | | | | | 20 meters | None | Always empty |
| `QA60` | | | | | 60 meters | None | Cloud mask. Masked out between 2022-01-25 to 2024-02-28 inclusive. |
| `MSK_CLASSI_OPAQUE` | | | | | 60 meters | None | Opaque clouds classification band (0=no clouds, 1=clouds). Masked out before February 2024. |
| `MSK_CLASSI_CIRRUS` | | | | | 60 meters | None | Cirrus clouds classification band (0=no clouds, 1=clouds). Masked out before February 2024. |
| `MSK_CLASSI_SNOW_ICE` | | | | | 60 meters | None | Snow/ice classification band (0=no snow/ice, 1=snow/ice). Masked out before February 2024. |

### QA60 bitmask

- Bits 0-9: Unused
- Bit 10: Opaque clouds
  - 0: No opaque clouds
  - 1: Opaque clouds present
- Bit 11: Cirrus clouds
  - 0: No cirrus clouds
  - 1: Cirrus clouds present

### SCL class table

| Value | Color | Description |
|---|---|---|
| 1 | #ff0004 | Saturated or defective |
| 2 | #868686 | Dark Area Pixels |
| 3 | #774b0a | Cloud Shadows |
| 4 | #10d22c | Vegetation |
| 5 | #ffff52 | Bare Soils |
| 6 | #0000ff | Water |
| 7 | #818181 | Clouds Low Probability / Unclassified |
| 8 | #c0c0c0 | Clouds Medium Probability |
| 9 | #f1f1f1 | Clouds High Probability |
| 10 | #bac5eb | Cirrus |
| 11 | #52fff9 | Snow / Ice |
