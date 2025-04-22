import pytest
import json
from src.model.power_line_segment import *


def test_init(segment_data):
    pls = PowerLineSegment(segment_data)
    assert pls.id == 808267289
    assert pls.bb_min_lat == 35.1192121
    assert pls.bb_min_lon == -89.9336470
    assert pls.bb_max_lat == 35.1197699
    assert pls.bb_max_lon == -89.9321114
    assert pls.num_nodes == 5
    assert pls.geometry == json.dumps(
        [
            [35.1192247, -89.9336470],
            [35.1192121, -89.9329791],
            [35.1197699, -89.9329583],
            [35.1197578, -89.9325044],
            [35.1197408, -89.9321114],
        ]
    )


def test_repr(segment_data):
    pls = PowerLineSegment(segment_data)
    assert f"{pls!r}" == "PowerLineSegment [808267289] (35.1192121, -89.933647) - (35.1197699, -89.9321114) 5 nodes"


@pytest.fixture
def segment_data():
    return {
        "type": "way",
        "id": 808267289,
        "bounds": {
            "minlat": 35.1192121,
            "minlon": -89.9336470,
            "maxlat": 35.1197699,
            "maxlon": -89.9321114,
        },
        "nodes": [7558087174, 7558087173, 7558087175, 7558087176, 7558087177],
        "geometry": [
            {"lat": 35.1192247, "lon": -89.9336470},
            {"lat": 35.1192121, "lon": -89.9329791},
            {"lat": 35.1197699, "lon": -89.9329583},
            {"lat": 35.1197578, "lon": -89.9325044},
            {"lat": 35.1197408, "lon": -89.9321114},
        ],
        "tags": {"power": "minor_line"},
    }
