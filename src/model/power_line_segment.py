import json
from typing import Dict
from sqlalchemy import Integer, Float, String
from sqlalchemy.orm import Mapped, mapped_column
from src.model.base import Base


class PowerLineSegment(Base):
    """Segment of a low-voltage power line, described by an OSM way ID, a bounding box and a collection of lat/lon nodes"""

    __tablename__ = "power_line_segment"

    id: Mapped[int] = mapped_column(primary_key=True)
    bb_min_lat: Mapped[float] = mapped_column(Float)
    bb_min_lon: Mapped[float] = mapped_column(Float)
    bb_max_lat: Mapped[float] = mapped_column(Float)
    bb_max_lon: Mapped[float] = mapped_column(Float)
    num_nodes: Mapped[int] = mapped_column(Integer)
    geometry: Mapped[str] = mapped_column(String)

    def __init__(self, data: Dict[str, object]):
        assert data["type"] == "way", f'Invalid entity type: "{data['type']}"'
        self.id = data["id"]
        self.bb_min_lat = data["bounds"]["minlat"]
        self.bb_min_lon = data["bounds"]["minlon"]
        self.bb_max_lat = data["bounds"]["maxlat"]
        self.bb_max_lon = data["bounds"]["maxlon"]
        self.num_nodes = len(data["nodes"])
        geometry = [[p["lat"], p["lon"]] for p in data["geometry"]]
        self.geometry = json.dumps(geometry)

    def __repr__(self) -> str:
        return f"PowerLineSegment [{self.id}] ({self.bb_min_lat}, {self.bb_min_lon}) - ({self.bb_max_lat}, {self.bb_max_lon}) {self.num_nodes} nodes"
