import pandas as pd
import geopandas as gpd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.cm as cm

#### data loading shenanigans

## elevation grid (assumed to be already masked and cropped to Romania)
# elev = np.load("../data/romania_elevation_grid.npz") ## JUST ROMANIA
elev = np.load("../data/bears_elevation_grid.npz") ## EXPANDED TO A RECTANGLE
elevation_grid = elev["elevation"]
lon_grid = elev["lon"]
lat_grid = elev["lat"]

## bear GPS data
df = pd.read_csv("../data/bears/1_bears_RO.csv")
gdf = gpd.GeoDataFrame(
    df,
    geometry=gpd.points_from_xy(df["X"], df["Y"]),
    crs="EPSG:3844"
).to_crs(epsg=4326)

## loading and reprojecting the Romania outline from GADM for border purposes
romania_shape = gpd.read_file("../data/gadm41_ROU_0.json").to_crs(epsg=4326)
minx, miny, maxx, maxy = romania_shape.total_bounds
print(f"Romania boundary bounds: {minx}, {miny}, {maxx}, {maxy}")


#### plotting shenanigans
fig, ax = plt.subplots(figsize=(12, 10))

## elevation as background
masked_elev = np.ma.masked_invalid(elevation_grid)
elev_plot = ax.imshow(
    masked_elev,
    extent=[lon_grid.min(), lon_grid.max(), lat_grid.min(), lat_grid.max()],
    origin="upper",
    cmap="terrain",
    alpha=0.5
)
cbar = plt.colorbar(elev_plot, ax=ax, label="Elevation (m)")

## plot Romania's boundary
romania_shape.boundary.plot(ax=ax, color="black", linewidth=1.5, zorder=10)
# romania_shape.boundary.plot(ax=ax, color="black", linewidth=1)

## plotting each bear as a separate color
bear_ids = gdf["Name"].unique()
cmap = cm.get_cmap("tab10", len(bear_ids))
color_dict = {bear: cmap(i) for i, bear in enumerate(bear_ids)}

for bear in bear_ids:
    bear_data = gdf[gdf["Name"] == bear]
    bear_data.plot(ax=ax, markersize=2, color=color_dict[bear], label=bear, alpha=0.8)

## because good graphs need labels
ax.legend(title="Bear ID", fontsize="small", loc="upper right")
ax.set_title("Brown Bear Movement in Romania")
plt.xlabel("Longitude")
plt.ylabel("Latitude")

## set axis limits to match romania
ax.set_xlim(minx, maxx)
ax.set_ylim(miny, maxy)

plt.tight_layout()
plt.savefig("../images/all_bears_height_map.png", dpi=300)
plt.show()

