from typing import Optional
from pydantic import BaseModel, Field
from pydantic.alias_generators import to_camel
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


class RegionSchema(BaseModel):
    name: str = Field(title="Official name of the region")
    bb_min_lat: float = Field(title="Southern latitude of the bounding box")
    bb_min_lon: float = Field(title="Western longitude of the bounding box")
    bb_max_lat: float = Field(title="Northern latitude of the bounding box")
    bb_max_lon: float = Field(title="Eastern longitude of the bounding box")
    img_url: Optional[str] = Field(None, title="URL of cover image for the region")
    num_pls: Optional[int] = Field(None, title="Number of power line segments in the region")

    model_config = {
        "alias_generator": to_camel,
        "populate_by_name": True,
        "from_attributes": True,
        "json_schema_extra": {
            "examples": [
                {
                    "name": "Mesa",
                    "bbMinLat": 33.3132423,
                    "bbMinLon": -111.9348257,
                    "bbMaxLat": 33.5121448,
                    "bbMaxLon": -111.7181466,
                    "imgUrl": "https://commons.wikimedia.org/w/thumb.php?width=320&f=Downtown%20Mesa%20Arizona.jpg",
                    "numPls": 41,
                },
            ]
        },
    }
