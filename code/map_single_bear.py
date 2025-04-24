import pandas as pd
import geopandas as gpd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.cm as cm

## for gradient colors
from matplotlib.colors import Normalize
from matplotlib.cm import ScalarMappable

import sys
import os

#### data loading shenanigans

## elevation grid (assumed to be already masked and cropped to Romania)
# elev = np.load("../data/romania_elevation_grid.npz") ## JUST ROMANIA
elev = np.load("../data/bears_elevation_grid.npz") ## EXPANDED TO A RECTANGLE
elevation_grid = elev["elevation"]
lon_grid = elev["lon"]
lat_grid = elev["lat"]

## bear GPS data
df = pd.read_csv("../data/bears/1_bears_RO.csv")
df['timestamp'] = pd.to_datetime(df['timestamp'])
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
bear_ids = gdf["Name"].unique()
df['timestamp'] = pd.to_datetime(df['timestamp'])


os.makedirs("../images/bear_tracks", exist_ok=True)

for bear in bear_ids:
    print(f"Bearing bear {bear}")
    bear_data = gdf[gdf["Name"] == bear].sort_values("timestamp")
    bear_timestamps = bear_data['timestamp'].reset_index(drop=True)

    ## normalizing color map to be [0...1]
    point_order = np.linspace(0, 1, len(bear_data))
    # cmap = plt.get_cmap("copper")
    # cmap = plt.get_cmap("YlOrBr")
    cmap = plt.get_cmap("Oranges")

    fig, ax = plt.subplots(figsize=(12, 10), constrained_layout=True)

    ## elevation as background
    masked_elevation = np.ma.masked_invalid(elevation_grid)
    elevation_plot = ax.imshow(
        masked_elevation,
        extent=[lon_grid.min(), lon_grid.max(), lat_grid.min(), lat_grid.max()],
        origin="upper",
        # cmap="terrain",
        cmap="gray",
        alpha=0.5
    )
    plt.colorbar(elevation_plot, ax=ax, label="Elevation (m)")

    ## romania border
    romania_shape.boundary.plot(ax=ax, color="black", linewidth=1.5, zorder=10)

    ## bear path
    sc = ax.scatter(
        bear_data.geometry.x, bear_data.geometry.y,
        c=point_order, cmap=cmap,
        s=16,  # dot size
        label=bear,
        alpha=0.85
    )

    ## colorbar for progression
    norm = Normalize(vmin=0, vmax=1)
    sm = ScalarMappable(cmap=cmap, norm=norm)
    sm.set_array([])
    cbar = plt.colorbar(sm, ax=ax, orientation="vertical", label="Track progression")

    n_ticks = 4
    tick_locs = np.linspace(0, 1, n_ticks)
    date_indices = np.linspace(0, len(bear_timestamps) - 1, n_ticks).astype(int)
    date_labels = [bear_timestamps.iloc[idx].strftime("%Y-%m-%d") for idx in date_indices]

    cbar.set_ticks(tick_locs)
    cbar.set_ticklabels(date_labels)
    cbar.ax.set_ylabel("Date")


    ## zooming on bear
    maxx = bear_data.geometry.x.max()
    minx = bear_data.geometry.x.min()
    mid_x = (minx + maxx) / 2
    range_x = (maxx - minx) * 1.25

    maxy = bear_data.geometry.y.max()
    miny = bear_data.geometry.y.min()
    mid_y = (miny + maxy) / 2
    range_y = (maxy - miny) * 1.25

    ax.set_xlim(mid_x - range_x / 2, mid_x + range_x / 2)
    ax.set_ylim(mid_y - range_y / 2, mid_y + range_y / 2)

    ## rest of axis shenanigans
    ax.set_title(f"Movement of {bear}")
    ax.set_xlabel("Longitude")
    ax.set_ylabel("Latitude")

    plt.savefig(f"../images/bear_tracks/{bear}_track.png", dpi=300)
    plt.close(fig)
