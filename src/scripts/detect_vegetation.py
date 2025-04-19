import detectree as dtr
import json
import math
import os
import requests
import warnings

from io import BytesIO
from PIL import Image, ImageOps
from sqlalchemy import select
from sqlalchemy.dialects.postgresql import insert
from tqdm import tqdm
from typing import List, Set
from src import db
from src.model.img_tile import ImgTile
from src.model.power_line_segment import PowerLineSegment
from src.model.region import Region
from src.util import log
from src.util.geo import TileCoords, lat_lon_to_tile_coords
from src.util.tensor import grayscale_to_rgba

tile_layer_url = "https://gis.apfo.usda.gov/arcgis/rest/services/NAIP/USDA_CONUS_PRIME/ImageServer/tile/"
temp_dir = os.path.normpath(f"{__file__}/../../../data/temp")


def get_power_line_tile_coords(region: Region, z=17) -> Set[TileCoords]:
    """Get the power line segments in a given region and return the coordinates of all level-17 tiles they intersect with."""

    tile_width = 360 / (2**z)
    tile_coords: Set[TileCoords] = set()

    session = db.get_session()
    segments = session.scalars(
        select(PowerLineSegment)
        .where(PowerLineSegment.bb_max_lat > region.bb_min_lat)
        .where(PowerLineSegment.bb_max_lon > region.bb_min_lon)
        .where(PowerLineSegment.bb_min_lat < region.bb_max_lat)
        .where(PowerLineSegment.bb_min_lon < region.bb_max_lon)
    )
    for seg in segments:
        geom: List[List[float]] = json.loads(seg.geometry)
        p0 = geom[0]
        tile_coords.add(lat_lon_to_tile_coords(*p0, z))
        for p in geom[1:]:
            dlat, dlon = p[0] - p0[0], p[1] - p0[1]
            diff = max(dlat, dlon)
            # This ignores the web Mercator distortion but should overestimate the needed steps
            num_steps = math.ceil(diff / tile_width)
            for s in range(0, num_steps):
                p0 = [p0[0] + dlat / num_steps, p0[1] + dlon / num_steps]
                tile_coords.add(lat_lon_to_tile_coords(*p0, z))

    return tile_coords


def download_and_classify_tiles(region_name: str, tile_coords: Set[TileCoords], z=17):
    """Download NAIP satellite tile images, run tree detection and save the image masks in the DB."""

    session = db.get_session()
    dir_name = region_name.replace(" ", "")
    data_dir = f"{temp_dir}/{dir_name}"
    if not os.path.exists(data_dir):
        os.makedirs(data_dir)

    # Suppress irrelevant warnings from rasterio and the classifier lib
    warnings.filterwarnings("ignore")
    coords = tqdm(
        tile_coords, leave=False, desc="    ↳ Detect vegetation", unit="tiles"
    )
    for x, y in coords:
        tpath = f"{z}/{y}/{x}"
        url = f"{tile_layer_url}{tpath}?blankTile=false"
        fpath = f"{data_dir}/naip_{z}_{y}_{x}.jpg"
        if not os.path.isfile(fpath):
            res = requests.get(url)
            if res.status_code != 200:
                continue
            im = Image.open(BytesIO(res.content))
            im = ImageOps.autocontrast(im)
            im.save(fpath)
        # Check if raster tile exists
        if session.scalar(
            select(ImgTile.x)
            .where(ImgTile.x == x)
            .where(ImgTile.y == y)
            .where(ImgTile.z == z)
        ):
            continue
        pred = dtr.Classifier().predict_img(fpath)
        pred_rgba = grayscale_to_rgba(pred, [1, 0, 1, 0.5])
        det_img = Image.fromarray(pred_rgba)
        blob = BytesIO()
        det_img.save(blob, format="PNG")
        tile_data = {"x": x, "y": y, "z": z, "d": blob.getvalue()}
        stmt = insert(ImgTile).values(tile_data).on_conflict_do_nothing()
        session.execute(stmt)
        session.commit()


def detect_trees():
    """Go through all regions in the DB and detect trees in tiles that intersect with power line segments."""

    log.msg("Detect trees along power lines in major US cities")

    session = db.get_session()
    regions = session.scalars(select(Region))
    # ['Mesa', 'New York City', 'San Francisco', 'Los Angeles', 'Boston', 'San Antonio', 'Seattle', 'Indianapolis', 'Detroit', 'San Diego', 'Denver', 'Houston', 'Phoenix', 'Dallas', 'Fort Worth', 'Austin', 'El Paso', 'Memphis', 'Charlotte', 'Columbus', 'Jacksonville', 'Sacramento', 'Tucson', 'Nashville', 'Las Vegas', 'Albuquerque', 'Oklahoma City', 'Kansas City', 'Fresno']
    for region in regions:
        coords = get_power_line_tile_coords(region)
        log.info(
            f"Process tiles covered by power line segments in {region.name}",
            f" ({len(coords)} tiles)",
        )
        download_and_classify_tiles(region.name, coords)

    log.success("Done")


if __name__ == "__main__":
    detect_trees()
