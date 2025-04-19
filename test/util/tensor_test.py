import pytest
import numpy as np
from src.util.tensor import *


def test_grayscale_to_rgba():
    # Raises errors for incorrect inputs
    with pytest.raises(AssertionError):
        grayscale_to_rgba(np.ndarray((2, 2, 2), dtype=np.uint8), [0.1, 0.2, 0.3, 0.4])
    with pytest.raises(AssertionError):
        grayscale_to_rgba(np.ndarray((2, 2), dtype=np.uint8), [0.1, 0.2, 0.3])
    with pytest.raises(AssertionError):
        grayscale_to_rgba(np.ndarray((2, 2), dtype=np.uint8), [0.1, 0.2, 0.3, 4.0])

    arr = np.ndarray((2, 2), dtype=np.uint8)
    i = 5
    arr[0, 0] = 0
    arr[0, 1] = 32
    arr[1, 0] = 64
    arr[1, 1] = 128
    rgba = [0.25, 0.5, 0.75, 1.0]
    t = grayscale_to_rgba(arr, rgba)
    exp = [
        [
            [0, 0, 0, 0],
            [8, 16, 24, 32],
        ],
        [
            [16, 32, 48, 64],
            [32, 64, 96, 128],
        ],
    ]
    for r in range(0, 2):
        for c in range(0, 2):
            for i in range(0, 4):
                assert t[r][c][i] == exp[r][c][i]
