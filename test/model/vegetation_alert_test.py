import os

import pytest
from src.model.vegetation_alert import *


def test_init():
    # Raises errors for invalid params
    with pytest.raises(AssertionError):
        va = VegetationAlert(45, -90, "Power line overlap", 11, 123)

    va = VegetationAlert(45, -90, "Power line overlap", 4, 123)
    assert va.lat == 45
    assert va.lon == -90
    assert va.desc == "Power line overlap"
    assert va.risk == 4
    assert va.pls_id == 123


def test_repr():
    va = VegetationAlert(45, -90, "Power line overlap", 7, 123)
    assert f"{va!r}" == "VegetationAlert (45, -90) [7]: Power line overlap"
