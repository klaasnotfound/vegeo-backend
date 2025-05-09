import os
import sqlalchemy
from dotenv import load_dotenv
from sqlalchemy.orm import Session

# Important: We need to import Base and *all* derived modules.
from src.model.base import Base
import src.model.power_line_segment
import src.model.region
import src.model.img_tile
import src.model.vegetation_alert

load_dotenv()

DB_SESSION = None
CONN = os.getenv("DB_CONN").replace("postgresql://", "postgresql+psycopg2://")
ENGINE = sqlalchemy.create_engine(CONN)


def reset():
    Base.metadata.drop_all(ENGINE)


def reset_table(collection: Base):
    collection.__table__.drop(ENGINE)
    collection.__table__.create(ENGINE)


def get_session():
    global DB_SESSION
    if DB_SESSION:
        return DB_SESSION
    Base.metadata.create_all(ENGINE)
    DB_SESSION = Session(ENGINE)
    return DB_SESSION
