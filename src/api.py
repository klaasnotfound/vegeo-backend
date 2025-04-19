from src import db
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import Response
from sqlalchemy import select
from src.model.power_line_segment import PowerLineSegment
from src.model.region import Region
from src.model.img_tile import ImgTile
from src.model.vegetation_alert import VegetationAlert
from src.util.geo import LatLon

load_dotenv()
origins = ["http://localhost:3000"]

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
session = db.get_session()


@app.get("/")
def read_root():
    return {"app": "Vegeo API", "version": "0.0.1"}


@app.get("/regions")
def get_regions():
    return [region for region in session.scalars(select(Region))]


@app.get("/power-lines")
def get_power_line_segments(sw: str, ne: str):
    mn = LatLon(*[float(v) for v in sw.split(",")])
    mx = LatLon(*[float(v) for v in ne.split(",")])
    segments = session.scalars(
        select(PowerLineSegment)
        .where(PowerLineSegment.bb_max_lat > mn.lat)
        .where(PowerLineSegment.bb_max_lon > mn.lon)
        .where(PowerLineSegment.bb_min_lat < mx.lat)
        .where(PowerLineSegment.bb_min_lon < mx.lon)
    )
    if not segments:
        raise HTTPException(status_code=404, detail="Not found")
    return [segment for segment in segments]


@app.get("/vegetation/tiles/{z}/{y}/{x}")
async def get_veg_tile(z: int, y: int, x: int):
    tile = session.scalar(
        select(ImgTile)
        .where(ImgTile.x == x)
        .where(ImgTile.y == y)
        .where(ImgTile.z == z)
    )
    if not tile:
        raise HTTPException(status_code=404, detail="Not found")
    return Response(content=tile.d, media_type="image/jpeg")


@app.get("/vegetation/alerts")
def get_vegetation_alerts(sw: str, ne: str):
    mn = LatLon(*[float(v) for v in sw.split(",")])
    mx = LatLon(*[float(v) for v in ne.split(",")])
    alerts = session.scalars(
        select(VegetationAlert)
        .where(VegetationAlert.lat >= mn.lat)
        .where(VegetationAlert.lon >= mn.lon)
        .where(VegetationAlert.lat <= mx.lat)
        .where(VegetationAlert.lon <= mx.lon)
    )
    if not alerts:
        raise HTTPException(status_code=404, detail="Not found")
    return [alert for alert in alerts]
