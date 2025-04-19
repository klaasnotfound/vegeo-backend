import os
from src.model.power_line_spot import *


def test_init():
    pls = PowerLineSpot(123, Pixel(4, 5))
    assert pls.segment_id == 123
    assert pls.pix_loc == Pixel(4, 5)


def test_repr():
    pls = PowerLineSpot(456, Pixel(7, 8))
    assert f"{pls!r}" == "PowerLineSpot 456: P[7, 8]"
