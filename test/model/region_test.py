from src.model.region import *
from src.util.geo import LatLon


def test_init():
    pls = Region(
        "Memphis",
        LatLon(35.089094, -90.054296),
        LatLon(35.203296, -89.860064),
        "https://example.com/img/memphis.jpg",
        1234,
    )
    assert pls.name == "Memphis"
    assert pls.bb_min_lat == 35.089094
    assert pls.bb_min_lon == -90.054296
    assert pls.bb_max_lat == 35.203296
    assert pls.bb_max_lon == -89.860064
    assert pls.img_url == "https://example.com/img/memphis.jpg"
    assert pls.num_pls == 1234


def test_repr():
    pls = Region(
        "Memphis", LatLon(35.089094, -90.054296), LatLon(35.203296, -89.860064)
    )
    assert (
        f"{pls!r}"
        == 'Region "Memphis" (35.089094, -90.054296) - (35.203296, -89.860064)'
    )
