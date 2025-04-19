from io import BytesIO
import json
import math
import numpy as np

from typing import List
from PIL import Image
from sqlalchemy import select
from sqlalchemy.dialects.postgresql import insert
from tqdm import tqdm
from src import db
from src.model.img_tile import ImgTile
from src.model.power_line_segment import PowerLineSegment
from src.model.power_line_spot import PowerLineSpot
from src.model.region import Region
from src.model.vegetation_alert import VegetationAlert
from src.util import log
from src.util.geo import (
    Pixel,
    lat_lon_to_pixel_coords,
    pixel_coords_to_lat_lon,
    pixels_in_circle,
)
from numpy.typing import NDArray

PIXEL_RADIUS = 8
RISK_THRESH = 0.5


def get_spots_to_check(region: Region, z=17) -> List[PowerLineSpot]:
    """Return pixel coordinates of spots to check along the power lines in a given region."""

    spots: List[PowerLineSpot] = []

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
        p0 = lat_lon_to_pixel_coords(*geom[0], z)
        spots.append(PowerLineSpot(seg.id, pix_loc=p0))
        for g1 in geom[1:]:
            p1 = lat_lon_to_pixel_coords(*g1, z)
            dx, dy = p1.x - p0.x, p1.y - p0.y
            l = math.sqrt((dx * dx) + (dy * dy))
            num_steps = math.ceil(l / (2 * PIXEL_RADIUS))
            for s in range(0, num_steps):
                p0 = Pixel(
                    math.floor(p0[0] + dx / num_steps),
                    math.floor(p0[1] + dy / num_steps),
                )
                spots.append(PowerLineSpot(seg.id, pix_loc=p0))

    return spots


def get_opaque_pixel_percentage(arr: NDArray, p: Pixel, r=PIXEL_RADIUS) -> float:
    """Return the percentage of opaque pixels in a circle with radius r around a reference pixel."""

    w, h, _ = np.shape(arr)
    # If we cannot analyze the full circle, just return 0
    if p.x < r or p.x > w - r or p.y < r or p.y > h - r:
        return 0

    pxls = pixels_in_circle(r, p.x, p.y)
    num_opaque = 0
    for x, y in pxls:
        if arr[y][x][3] > 0:
            num_opaque += 1

    return num_opaque / len(pxls)


def check_spot(spot: PowerLineSpot) -> float:
    """Check a power line spot and generate an alert if there is vegetation overlap."""

    z = 17
    ts = 256
    tx, ty = math.floor(spot.pix_loc.x / ts), math.floor(spot.pix_loc.y / ts)
    px, py = spot.pix_loc.x - tx * ts, spot.pix_loc.y - ty * ts

    session = db.get_session()
    tile = session.scalar(
        select(ImgTile)
        .where(ImgTile.x == tx)
        .where(ImgTile.y == ty)
        .where(ImgTile.z == z)
    )
    if not tile:
        return 0
    im = Image.open(BytesIO(tile.d))
    data = np.array(im)
    return get_opaque_pixel_percentage(data, Pixel(px, py))


def compute_alerts():
    log.msg("Check power lines in major US cities for vegetation overlap")

    db.reset_table(VegetationAlert)

    session = db.get_session()
    regions = session.scalars(select(Region))
    for region in regions:
        spots = get_spots_to_check(region)
        log.info(
            f"Retrieve spots to check along power line segments in {region.name}",
            f" ({len(spots)} spots)",
        )
        alerts: List[VegetationAlert] = []
        spts = tqdm(spots, leave=False, desc="    ↳ Check spots", unit="spots")
        num_alerts = 0
        for spot in spts:
            perc = check_spot(spot)
            if perc < RISK_THRESH:
                continue
            risk = 1 + round((perc - RISK_THRESH) / (1 - RISK_THRESH) * 9)
            loc = pixel_coords_to_lat_lon(*spot.pix_loc, 17)
            alert = {
                "lat": loc.lat,
                "lon": loc.lon,
                "desc": "Power line overlap",
                "risk": risk,
                "pls_id": spot.segment_id,
            }
            stmt = insert(VegetationAlert).values(alert).on_conflict_do_nothing()
            session.execute(stmt)
            num_alerts += 1
        session.commit()
        log.info(f"{num_alerts} alerts in {region.name}", " ✓")

    log.success("Done")


if __name__ == "__main__":
    compute_alerts()
