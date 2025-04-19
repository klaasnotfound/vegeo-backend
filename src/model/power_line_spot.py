from typing import Optional
from src.util.geo import LatLon, Pixel


class PowerLineSpot:
    segment_id: int
    pix_loc: Pixel

    def __init__(self, segment_id, pix_loc: Pixel):
        self.segment_id = segment_id
        self.pix_loc = pix_loc

    def __repr__(self):
        str = f"PowerLineSpot {self.segment_id}"
        if self.pix_loc:
            str = f"{str}: P{[*self.pix_loc]}"

        return str
