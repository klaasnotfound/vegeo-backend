import os
from src.model.img_tile import *


def test_init():
    mt = ImgTile(1, 2, 3, os.urandom(100))
    assert mt.x == 1
    assert mt.y == 2
    assert mt.z == 3
    assert len(mt.d) == 100


def test_repr():
    mt = ImgTile(1, 2, 3, os.urandom(100))
    assert f"{mt!r}" == "ImgTile 3/1/2 (256x256 PNG 100 bytes)"
