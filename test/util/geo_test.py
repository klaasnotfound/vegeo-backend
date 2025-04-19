import pytest
import random
from src.util.geo import *


def test_lat_lon_to_tile_coords():
    # Raises errors for invalid coordinates
    with pytest.raises(AssertionError):
        lat_lon_to_tile_coords(-90, -180, 0)
    with pytest.raises(AssertionError):
        lat_lon_to_tile_coords(-85, -190, 0)
    with pytest.raises(AssertionError):
        lat_lon_to_tile_coords(-85, -180, 20)

    # Works worldwide across different LOD
    assert lat_lon_to_tile_coords(0, 0, 0) == (0, 0)
    assert lat_lon_to_tile_coords(45, 90, 1) == (1, 0)
    assert lat_lon_to_tile_coords(22.5, -45, 2) == (1, 1)
    assert lat_lon_to_tile_coords(44.045768, -82.6746129, 4) == (4, 5)
    assert lat_lon_to_tile_coords(33.253465, -112.144976, 4) == (3, 6)
    assert lat_lon_to_tile_coords(42.284396, -83.736422, 17) == (35048, 48516)
    assert lat_lon_to_tile_coords(52.516541, 13.377698, 17) == (70406, 42987)
    assert lat_lon_to_tile_coords(-33.901526, 18.398813, 17) == (72234, 78669)
    assert lat_lon_to_tile_coords(-51.612495, -69.218215, 17) == (40334, 87548)


def test_lat_lon_to_pixel_coords():
    # Raises errors for invalid coordinates
    with pytest.raises(AssertionError):
        lat_lon_to_pixel_coords(-90, -180, 0)
    with pytest.raises(AssertionError):
        lat_lon_to_pixel_coords(-85, -190, 0)
    with pytest.raises(AssertionError):
        lat_lon_to_pixel_coords(-85, -180, 20)
    with pytest.raises(AssertionError):
        lat_lon_to_pixel_coords(-85, -180, 17, 0)

    # Works for different LODs and tiles worldwide
    assert lat_lon_to_pixel_coords(-85.05, -180.0, 0) == Pixel(0, 255)
    assert lat_lon_to_pixel_coords(-85.05, 179.99, 3) == Pixel(2047, 2047)
    assert lat_lon_to_pixel_coords(42.284422, -83.736420, 17) == Pixel(
        35048 * 256 + 127,
        48516 * 256 + 127,
    )


def test_tile_coords_to_lat_lon():
    # Raises errors for invalid coordinates
    with pytest.raises(AssertionError):
        tile_coords_to_lat_lon(1, 0, 0)
    with pytest.raises(AssertionError):
        tile_coords_to_lat_lon(0, 8, 3)
    with pytest.raises(AssertionError):
        tile_coords_to_lat_lon(0, 0, 18)
    with pytest.raises(AssertionError):
        tile_coords_to_lat_lon(0, 0, 17, ox=-0.1)
    with pytest.raises(AssertionError):
        tile_coords_to_lat_lon(0, 0, 17, ox=0.2, oy=1.2)

    # Works worldwide across different LOD
    assert tile_coords_to_lat_lon(0, 0, 0) == (0, 0)
    assert round(tile_coords_to_lat_lon(1, 0, 1).lat) == 67
    # fmt: off
    assert [round(v, 6) for v in tile_coords_to_lat_lon(35048, 48516, 17)] == [42.284421, -83.736420]
    assert [round(v, 2) for v in tile_coords_to_lat_lon(70406, 42987, 17)] == [52.52, 13.38]
    assert [round(v, 2) for v in tile_coords_to_lat_lon(72234, 78669, 17)] == [-33.9, 18.40]
    assert [round(v, 2) for v in tile_coords_to_lat_lon(40334, 87548, 17)] == [-51.61, -69.22]
    # fmt: on

    # Works at all corners of a tile
    assert tile_coords_to_lat_lon(1, 2, 3, 0, 0) == (66.51326044311185, -135)
    assert tile_coords_to_lat_lon(1, 2, 3, 1, 0) == (66.51326044311185, -90)
    assert tile_coords_to_lat_lon(1, 2, 3, 0, 1) == (40.97989806962012, -135)
    assert tile_coords_to_lat_lon(1, 2, 3, 1, 1) == (40.97989806962012, -90)


def test_pixel_coords_to_lat_lon():
    # Raises errors for invalid coordinates
    with pytest.raises(AssertionError):
        pixel_coords_to_lat_lon(256, 0, 0)
    with pytest.raises(AssertionError):
        pixel_coords_to_lat_lon(0, 2049, 3)
    with pytest.raises(AssertionError):
        pixel_coords_to_lat_lon(0, 0, 18)
    with pytest.raises(AssertionError):
        pixel_coords_to_lat_lon(0, 0, 17, 4097)

    # Works worldwide across different LOD
    assert pixel_coords_to_lat_lon(256, 256, 1) == (0, 0)
    assert pixel_coords_to_lat_lon(512, 512, 2) == (0, 0)
    assert [round(v, 2) for v in pixel_coords_to_lat_lon(2047, 2047, 3)] == [
        -85.04,
        179.82,
    ]


def test_round_trip_conversion():
    # Works with a bunch of pseudorandom points and LODs
    random.seed(0)
    for i in range(10):
        z = random.randint(0, 17)
        x = random.randint(0, z**2 - 1)
        y = random.randint(0, z**2 - 1)
        lat, lon = tile_coords_to_lat_lon(x, y, z)
        tx, ty = lat_lon_to_tile_coords(lat, lon, z)
        assert tx == x and ty == y


def test_pixels_in_circle():
    # Generates the correct number of pixels
    assert len(pixels_in_circle(1)) == 1
    assert len(pixels_in_circle(2)) == 9
    assert len(pixels_in_circle(3)) == 25
    assert len(pixels_in_circle(4)) == 45
    assert len(pixels_in_circle(5)) == 69

    # Generates the correct pixels
    assert pixels_in_circle(1) == [Pixel(0, 0)]
    p5 = set(pixels_in_circle(5))
    assert Pixel(-4, 2) in p5
    assert Pixel(-4, 3) not in p5
    assert Pixel(-3, 3) in p5
    assert Pixel(-3, 4) not in p5
    assert Pixel(-2, 4) in p5

    # Uses offset correctly
    assert len(pixels_in_circle(1, 4, 18)) == 1
    assert len(pixels_in_circle(2, -27, 3)) == 9
    assert len(pixels_in_circle(3, 5, 5)) == 25
    assert pixels_in_circle(1, 27, 113) == [Pixel(27, 113)]
    p4 = set(pixels_in_circle(4, 103, 78))
    assert Pixel(100, 80) in p4
    assert Pixel(100, 81) not in p4
    assert Pixel(105, 81) in p4
    assert Pixel(106, 81) not in p4
