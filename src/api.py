from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, Path, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.openapi.docs import get_redoc_html
from fastapi.responses import Response
from sqlalchemy import select
from src import db
from src.model.img_tile import ImgTile
from src.model.power_line_segment import PowerLineSegment, PowerLineSegmentSchema
from src.model.region import Region, RegionSchema
from src.model.root_response import RootResponseSchema
from src.model.vegetation_alert import VegetationAlert, VegetationAlertSchema
from src.util.geo import LatLon

load_dotenv()

API_NAME = "Vegeo API"
API_VERSION = "0.1.0"


app = FastAPI(
    title=API_NAME,
    version=API_VERSION,
    description="The Vegeo API provides read access to power line and vegetation detection data in major US cities.",
    docs_url=None,
    redoc_url=None,
)

origins = ["http://localhost:3000"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
session = db.get_session()


@app.get("/")
def get_root() -> RootResponseSchema:
    """Returns the name and version of the running API server. Can be used to ping server availability."""

    return {"name": API_NAME, "version": API_VERSION}


@app.get("/regions")
async def get_regions() -> list[RegionSchema]:
    """Returns a list of available regions (major US cities for now)."""

    return [region for region in session.scalars(select(Region))]


@app.get("/power-lines")
async def get_power_lines(
    sw: str = Query(description="Southwest bounding box corner", example="34.9760601,-106.7440806"),
    ne: str = Query(description="Northeast bounding box corner", example="35.5360249,-106.5489647"),
) -> list[PowerLineSegmentSchema]:
    """Returns a list of power line segments within the query bounding box."""

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


@app.get("/vegetation/tiles/{z}/{y}/{x}", response_class=Response(media_type="image/png"))
def get_vegetation_tiles(
    z: int = Path(description="Zoom level of the tile (only z=17 is available for now)"),
    y: int = Path(description="Web Mercator x coordinate of the tile"),
    x: int = Path(description="Web Mercator y coordinate of the tile"),
):
    """Returns transparent 256x256 PNG image tiles with magenta pixels showing where vegetation has been detected. These can be overlayed on a satellite imagery tile layer."""

    tile = session.scalar(select(ImgTile).where(ImgTile.x == x).where(ImgTile.y == y).where(ImgTile.z == z))
    if not tile:
        raise HTTPException(status_code=404, detail="Not found")
    return Response(content=tile.d, media_type="image/png")


@app.get("/vegetation/alerts")
def get_vegetation_alerts(
    sw: str = Query(description="Southwest bounding box corner", example="40.6098699,-74.1189911"),
    ne: str = Query(description="Northeast bounding box corner", example="40.8352671,-73.9077914"),
) -> list[VegetationAlertSchema]:
    """Returns a list of geo-referenced alerts for spots where vegetation is estimated to overlap with power line segments."""

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


@app.get("/docs", include_in_schema=False)
def expose_redoc():
    return get_redoc_html(
        openapi_url="/openapi.json", title="Vegeo API Documentation", redoc_favicon_url="https://github.com/klaasnotfound/vegeo-backend/raw/refs/heads/main/data/assets/favicon.png"
    )
