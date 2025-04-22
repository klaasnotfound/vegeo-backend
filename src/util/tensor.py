import numpy as np

from numpy.typing import NDArray
from typing import List


def grayscale_to_rgba(arr: NDArray, rgba: List[float]) -> NDArray:
    """Convert an (m x n) array of grayscale values (0-255) to an RGBA tensor (m x n x 4).

    :param arr:  2-dimensional array with values in [0, 255]
    :param rgba: vector with [r, g, b, a] values in [0, 1]

    The RGBA values are multiplied with the input values, so [1.0, 0.0, 0.0, 0.5] would
    map the grayscale intensities to the red channel with 50% opacity.
    """

    assert len(np.shape(arr)) == 2, "Input array must be a 2-dimensional."
    assert len(rgba) == 4, "RGBA vector must contain exactly 4 values."
    assert all([(v >= 0.0 and v <= 1.0) for v in rgba]), "RGBA vector must contain float values in [0, 1]."

    data = np.zeros((*np.shape(arr), 4), dtype=np.uint8)
    for r in range(0, np.size(arr, 0)):
        for c in range(0, np.size(arr, 1)):
            data[r, c] = [arr[r, c] * v for v in rgba]

    return data
