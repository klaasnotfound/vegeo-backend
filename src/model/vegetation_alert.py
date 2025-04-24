from typing import Optional
from pydantic import BaseModel, Field
from pydantic.alias_generators import to_camel
from sqlalchemy import ForeignKey, Integer, Float, PrimaryKeyConstraint, String
from sqlalchemy.orm import Mapped, mapped_column
from src.model.base import Base


class VegetationAlert(Base):
    """Geo-referenced alert informing about a vegetation risk, e.g. to power infrastructure.

    :param lat:    latitude of the alert location
    :param lon:    longitude of the alert location
    :param desc:   short description of the alert risk
    :param risk:   risk level in [1, 10]
    :param pls_id: optional reference to a power line segment
    """

    __tablename__ = "vegetation_alert"

    lat: Mapped[float] = mapped_column(Float)
    lon: Mapped[float] = mapped_column(Float)
    desc: Mapped[str] = mapped_column(String)
    risk: Mapped[int] = mapped_column(Integer)
    pls_id: Mapped[Optional[int]] = mapped_column(ForeignKey("power_line_segment.id"))

    Primary__table_args__ = (PrimaryKeyConstraint(lat, lon),)

    def __init__(self, lat: float, lon: float, desc: str, risk: int, pls_id: int = None):
        assert risk > 0 and risk < 11, "Risk level must be in [1, 10]"

        self.lat = lat
        self.lon = lon
        self.desc = desc
        self.risk = risk
        self.pls_id = pls_id

    def __repr__(self):
        return f"VegetationAlert {self.lat, self.lon} [{self.risk}]: {self.desc}"


class VegetationAlertSchema(BaseModel):
    lat: float = Field(title="Latitude of the alert location")
    lon: float = Field(title="Longitude of the alert location")
    desc: str = Field(title="Short description of the alert")
    risk: int = Field(title="Risk level in [1, 10]")
    pls_id: Optional[int] = Field(None, title="ID of the power line segment this alert belongs to")

    model_config = {
        "alias_generator": to_camel,
        "populate_by_name": True,
        "from_attributes": True,
        "json_schema_extra": {
            "examples": [
                {
                    "lat": 40.7398274408644,
                    "lon": -74.0427875518799,
                    "desc": "Power line overlap",
                    "risk": 2,
                    "plsId": 203432097,
                },
            ]
        },
    }
