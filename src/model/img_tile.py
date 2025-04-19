from typing import BinaryIO
from sqlalchemy import Integer, LargeBinary
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.schema import PrimaryKeyConstraint
from src.model.base import Base


class ImgTile(Base):
    """A square image tile to be overlayed on map data (usually a 256x256 PNG)"""

    __IMG_FORMAT__ = "PNG"
    __IMG_SIZE__ = 256
    __tablename__ = "img_tile"

    x: Mapped[int] = mapped_column(Integer)
    y: Mapped[int] = mapped_column(Integer)
    z: Mapped[int] = mapped_column(Integer)
    d: Mapped[BinaryIO] = mapped_column(LargeBinary)

    Primary__table_args__ = (PrimaryKeyConstraint(x, y, z),)

    def __init__(self, x: int, y: int, z: int, d: BinaryIO):
        self.x = x
        self.y = y
        self.z = z
        self.d = d

    def __repr__(self) -> str:
        return f"ImgTile {self.z}/{self.x}/{self.y} ({self.__IMG_SIZE__}x{self.__IMG_SIZE__} {self.__IMG_FORMAT__} {len(self.d)} bytes)"
