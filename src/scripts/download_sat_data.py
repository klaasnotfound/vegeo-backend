import os
import random
import requests
from sqlalchemy import select, desc
from src.model.region import Region
from src.util.geo import lat_lon_to_tile_coords
from src.util import log
from src import db


def download_sampled_naip_data_to_disk(region: Region, n=20):
    """Download n randomly sampled NAIP satellite image tiles for a given region."""

    # Config
    tile_layer_url = "https://gis.apfo.usda.gov/arcgis/rest/services/NAIP/USDA_CONUS_PRIME/ImageServer/tile/"
    data_dir = os.path.normpath(f"{__file__}/../../../data/label")
    if not os.path.exists(data_dir):
        os.makedirs(data_dir)

    # Prepare tile range
    z = 17
    mn = lat_lon_to_tile_coords(region.bb_max_lat, region.bb_min_lon, z)
    mx = lat_lon_to_tile_coords(region.bb_min_lat, region.bb_max_lon, z)
    log.msg(f"Download USDA satellite data for {region.name} ({n} tiles)")

    # Download the tiles
    xs = [random.choice(range(mn.x, mx.x)) for v in range(0, n)]
    ys = [random.choice(range(mn.y, mx.y)) for v in range(0, n)]
    for x, y in zip(xs, ys):
        tpath = f"{z}/{y}/{x}"
        url = f"{tile_layer_url}{tpath}?blankTile=false"
        fpath = f"{data_dir}/naip_{z}_{y}_{x}.jpg"
        if os.path.isfile(fpath):
            log.info(f" {tpath}", "(cached)")
            continue
        res = requests.get(url)
        if res.status_code != 200:
            log.error(f" {tpath}", f" ({res.status_code} {res.reason})")
            continue
        with open(fpath, "wb") as f:
            f.write(res.content)
            log.info(f" {tpath}", " ✓", "  ↓")

    log.success("Done")


def download_training_data(num_regions=5):
    """Download randomly sampled satellite data for labeling/training."""

    with db.get_session() as session:
        regions = session.scalars(
            select(Region).order_by(desc(Region.num_pls)).limit(num_regions)
        )
        for region in regions:
            download_sampled_naip_data_to_disk(region)


if __name__ == "__main__":
    download_training_data()
