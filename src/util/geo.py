import math
from collections import namedtuple
from typing import List

TileCoords = namedtuple("TileCoords", "x y")
Pixel = namedtuple("Pixel", "x y")
LatLon = namedtuple("LatLon", "lat lon")

# See https://en.wikipedia.org/wiki/Web_Mercator_projection
LAT_MAX = math.degrees(2 * math.atan(math.pow(math.e, math.pi)) - math.pi / 2)


def lat_lon_to_tile_coords(lat: float, lon: float, z: int) -> TileCoords:
    """Convert a lat/long coordinate to web Mercator tile coordinates at a given zoom level"""

    assert lat >= -LAT_MAX and lat <= LAT_MAX, f"Latitude must be within [-{LAT_MAX}, {LAT_MAX}]"
    assert lon >= -180.0 and lon <= 180.0, "Longitude must be within [-180, 180]"
    assert z >= 0 and z <= 17, "Zoom level must be within [0, 17]"

    # See https://en.wikipedia.org/wiki/Web_Mercator_projection
    tx = math.floor((2**z) * (180 + lon) / 360)
    ty = math.floor((2**z) * (180 - math.degrees(math.log(math.tan(math.pi / 4 + math.radians(lat) / 2)))) / 360)

    return TileCoords(tx, ty)


def lat_lon_to_pixel_coords(lat: float, lon: float, z: int, ts=256) -> Pixel:
    """Convert a lat/long coordinate to the global web Mercator pixel coordinate at a given zoom level.

    :param lat: latitude value within [-85.05, 85.05]
    :param lon: longitude value within [-180.0, 180.0]
    :param z:   zoom level / LOD of the tile within [1,17]
    :param ts:  tile size in pixels within [1, 4096]
    """

    assert lat >= -LAT_MAX and lat <= LAT_MAX, f"Latitude must be within [-{LAT_MAX}, {LAT_MAX}]"
    assert lon >= -180.0 and lon <= 180.0, "Longitude must be within [-180, 180]"
    assert z >= 0 and z <= 17, "Zoom level must be within [0, 17]"
    assert ts > 0 and ts <= 4096, "Tile size must within [1, 4096]"

    # See https://en.wikipedia.org/wiki/Web_Mercator_projection
    px = math.floor((2**z) * (180 + lon) / 360 * ts)
    py = math.floor((2**z) * (180 - math.degrees(math.log(math.tan(math.pi / 4 + math.radians(lat) / 2)))) / 360 * ts)

    return Pixel(px, py)


def tile_coords_to_lat_lon(x: int, y: int, z: int, ox=0.5, oy=0.5) -> LatLon:
    """Return the center lat/lon coordinate of an x/y/z web mercator tile.

    :param x: web mercator x coordinate of the tile
    :param y: web mercator y coordinate of the tile
    :param z: zoom level / LOD of the tile
    :param ox: x offset within the tile in [0, 1] (0.5 is at the center)
    :param oy: y offset within the tile in [0, 1] (0.5 is at the center)
    """

    assert x >= 0 and x < (2**z), f"x must be within [0, {(2**z) - 1}]"
    assert y >= 0 and y < (2**z), f"y must be within [0, {(2**z) - 1}]"
    assert z >= 0 and z <= 17, "Zoom level must be within [0, 17]"
    assert ox >= 0 and ox <= 1, "x offset must be within [0, 1]"
    assert oy >= 0 and oy <= 1, "y offset must be within [0, 1]"

    lon = (x + ox) * 360 / (2**z) - 180
    lat = 90 - math.degrees(2 * math.atan(math.pow(math.e, 2 * math.pi / (2**z) * (y + oy) - math.pi)))

    return LatLon(lat, lon)


def pixel_coords_to_lat_lon(px: int, py: int, z: int, ts=256) -> LatLon:
    """Convert a global web Mercator pixel coordinate to a lat/long coordinate.

    :param px: global pixel x coordinate
    :param py: global pixel y coordinate
    :param z: zoom level / LOD of the tile
    :param ts:  tile size in pixels within [1, 4096]
    """

    pMax = (2**z) * ts
    assert px >= 0 and px < pMax, f"px must be within [0, {pMax - 1}]"
    assert py >= 0 and py < pMax, f"py must be within [0, {pMax - 1}]"
    assert z >= 0 and z <= 17, "Zoom level must be within [0, 17]"
    assert ts > 0 and ts <= 4096, "Tile size must within [1, 4096]"

    lon = px / ts * 360 / (2**z) - 180
    lat = 90 - math.degrees(2 * math.atan(math.pow(math.e, 2 * math.pi / (2**z) * py / ts - math.pi)))

    return LatLon(lat, lon)


def pixels_in_circle(r: int, ox=0, oy=0) -> List[Pixel]:
    """Return pixel coordinates that fall into a circle with radius `r`."""

    pixels: List[Pixel] = []

    rs = r * r
    num = 0
    for y in range(-r, r + 1):
        for x in range(-r, r + 1):
            if x * x + y * y < rs:
                pixels.append(Pixel(x + ox, y + oy))

    return pixels
