import rasterio
from rasterio.mask import mask
import geopandas as gpd
import numpy as np
import matplotlib.pyplot as plt

## load Romania boundary as GeoJSON (level-0 (means it's country level))
## (the level 1 is provinces etc, level 2 is further subdivisions and so on)
## data taken from https://gadm.org/maps/ROU.html
romania = gpd.read_file("../data/gadm41_ROU_0.json")
## make sure CRS matches raster
romania = romania.to_crs("EPSG:4326")  

## global elevation raster
## data taken from https://www.worldclim.org/data/worldclim21.html
with rasterio.open("../data/wc2.1_30s_elev.tif") as src:
    nodata_value = src.nodata
    ## cropping to romania's borders
    shapes = [feature["geometry"] for feature in romania.__geo_interface__["features"]]
    out_image, out_transform = mask(src, shapes, crop=True, filled=True, nodata=nodata_value)
    out_meta = src.meta.copy()

## convert to float and mask nodata values as np.nan
## i think the nodatas come from sealevels
elevation_grid = out_image[0].astype(float)
if nodata_value is not None:
    elevation_grid[elevation_grid == nodata_value] = np.nan

## build meshgrid for plotting with correct geolocation
num_rows, num_cols = elevation_grid.shape
xmin, ymax = out_transform[2], out_transform[5]
pixel_size_x, pixel_size_y = out_transform[0], -out_transform[4]
x_coords = xmin + np.arange(num_cols) * pixel_size_x
y_coords = ymax - np.arange(num_rows) * pixel_size_y
lon_grid, lat_grid = np.meshgrid(x_coords, y_coords)

## save the data as an npz
## npzs combine multiple arrays into a single file and is lazy loaded
np.savez("../data/romania_elevation_grid.npz", elevation=elevation_grid, lon=lon_grid, lat=lat_grid)

