import numpy as np
import pandas as pd
import geopandas as gpd

import rasterio
from rasterio.windows import from_bounds

## edges of the dataset
# df = pd.read_csv("../data/bears/1_bears_RO.csv")
# gdf = gpd.GeoDataFrame(
    # df, geometry=gpd.points_from_xy(df["X"], df["Y"]), crs="EPSG:3844"
# ).to_crs(epsg=4326)
# 
# minx, miny, maxx, maxy = gdf.total_bounds
# print(f"Bear GPS bounding box: {minx}, {miny}, {maxx}, {maxy}")

## edges of romania for egsp4326 purposes
romania = gpd.read_file("../data/gadm41_ROU_0.json")
romania = romania.to_crs("EPSG:4326")  ## WGS84 (normal gps) for the raster

## bounding box of the Romania outline
minx, miny, maxx, maxy = romania.total_bounds
print(f"Romania boundary bounds: {minx}, {miny}, {maxx}, {maxy}")

with rasterio.open("../data/wc2.1_30s_elev.tif") as src:
    window = from_bounds(minx, miny, maxx, maxy, src.transform)
    out_image = src.read(1, window=window)
    out_transform = src.window_transform(window)
    nodata_value = src.nodata

## convert to float adn mask nodata
elevation_grid = out_image.astype(float)
if nodata_value is not None:
    elevation_grid[elevation_grid == nodata_value] = np.nan

## create meshgrid for lon/lat coordinates
num_rows, num_cols = elevation_grid.shape
xmin, ymax = out_transform[2], out_transform[5]
pixel_size_x, pixel_size_y = out_transform[0], -out_transform[4]
x_coords = xmin + np.arange(num_cols) * pixel_size_x
y_coords = ymax - np.arange(num_rows) * pixel_size_y
lon_grid, lat_grid = np.meshgrid(x_coords, y_coords)

## saveinator 3000
np.savez("../data/bears_elevation_grid.npz", elevation=elevation_grid, lon=lon_grid, lat=lat_grid)

