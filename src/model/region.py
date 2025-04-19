from typing import Optional
from sqlalchemy import String, Float, Integer
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.schema import PrimaryKeyConstraint
from src.model.base import Base
from src.util.geo import LatLon


class Region(Base):
    """A geographic region with a name and a bounding box"""

    __tablename__ = "region"

    name: Mapped[str] = mapped_column(String, primary_key=True)
    bb_min_lat: Mapped[float] = mapped_column(Float)
    bb_min_lon: Mapped[float] = mapped_column(Float)
    bb_max_lat: Mapped[float] = mapped_column(Float)
    bb_max_lon: Mapped[float] = mapped_column(Float)
    img_url: Mapped[Optional[str]] = mapped_column(String)
    num_pls: Mapped[Optional[int]] = mapped_column(Integer)

    def __init__(
        self,
        name: str,
        sw: LatLon,
        ne: LatLon,
        img_url: Optional[str] = None,
        num_pls: Optional[int] = None,
    ):
        self.name = name
        self.bb_min_lat = sw.lat
        self.bb_min_lon = sw.lon
        self.bb_max_lat = ne.lat
        self.bb_max_lon = ne.lon
        self.img_url = img_url
        self.num_pls = num_pls

    def __repr__(self) -> str:
        return f'Region "{self.name}" ({self.bb_min_lat}, {self.bb_min_lon}) - ({self.bb_max_lat}, {self.bb_max_lon})'
