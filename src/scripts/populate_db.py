import re
import requests

from src import db
from src.model.power_line_segment import PowerLineSegment
from src.model.region import Region
from src.util import log
from src.util.geo import LatLon


def fetch_major_us_cities():
    """Fetch the name, population and location of US cities with at least 500,000 residents from Wikidata."""

    # This SPARQL query returns all US cities with more than 500,000 residents:
    #
    # SELECT ?cityLabel ?population ?gps ?image
    # WHERE {
    #   ?city wdt:P31 wd:Q1093829 .
    #   ?city wdt:P1082 ?population .
    #   ?city wdt:P625 ?gps .
    #   ?city wdt:P18 ?image .
    #   FILTER(?population > 500000)
    #   SERVICE wikibase:label { bd:serviceParam wikibase:language "en" . }
    # }
    url = "https://query.wikidata.org/sparql?query=SELECT%20%3FcityLabel%20%3Fpopulation%20%3Fgps%20%3Fimage%0AWHERE%20%7B%0A%20%20%3Fcity%20wdt%3AP31%20wd%3AQ1093829%20.%0A%20%20%3Fcity%20wdt%3AP1082%20%3Fpopulation%20.%0A%20%20%3Fcity%20wdt%3AP625%20%3Fgps%20.%0A%20%20%3Fcity%20wdt%3AP18%20%3Fimage%20.%0A%20%20FILTER(%3Fpopulation%20%3E%20500000)%0A%20%20SERVICE%20wikibase%3Alabel%20%7B%20bd%3AserviceParam%20wikibase%3Alanguage%20%22en%22%20.%20%7D%0A%7D"
    headers = {"Accept": "application/sparql-results+json"}

    res = requests.get(url, headers=headers)
    data = res.json()
    items = data["results"]["bindings"]
    cities = []
    for item in items:
        loc = [float(v) for v in re.findall(r".*\((.*?) (.*?)\)", item["gps"]["value"])[0]]
        img_file = item["image"]["value"].split("/")[-1]
        img_url = f"https://commons.wikimedia.org/w/thumb.php?width=320&f={img_file}"
        cities.append(
            {
                "name": item["cityLabel"]["value"],
                "population": round(float(item["population"]["value"])),
                "lat": loc[1],
                "lon": loc[0],
                "img_url": img_url,
            }
        )

    return cities


def fetch_minor_power_lines(lat: float, lon: float, bb_size=0.2):
    """Fetch the geometry of minor powerlines in a given area from Overpass."""

    url = "https://overpass-api.de/api/interpreter"
    headers = {"Content-Type": "application/x-www-form-urlencoded"}
    sw = LatLon(lat - bb_size / 2, lon - bb_size / 2)
    ne = LatLon(lat + bb_size / 2, lon + bb_size / 2)
    query = f'[out:json][timeout:25]; nwr["power"="minor_line"]({sw.lat},{sw.lon},{ne.lat},{ne.lon}); out geom;'

    res = requests.post(url, {"data": query}, headers=headers)
    data = res.json()
    if len(data["elements"]) == 0:
        return None, None, None
    min_lat = min([el["bounds"]["minlat"] for el in data["elements"]])
    min_lon = min([el["bounds"]["minlon"] for el in data["elements"]])
    max_lat = max([el["bounds"]["maxlat"] for el in data["elements"]])
    max_lon = max([el["bounds"]["maxlon"] for el in data["elements"]])

    return LatLon(min_lat, min_lon), LatLon(max_lat, max_lon), data


def populate_db():
    """Fetch power line data for major US cities and stores it in the database."""
    log.msg("Fetch power line data for major US cities")

    db.reset()
    with db.get_session() as session:
        cities = fetch_major_us_cities()

        for city in cities:
            sw, ne, data = fetch_minor_power_lines(city["lat"], city["lon"])
            if not data:
                log.error(f"{city['name']}", " (no segments)")
                continue
            num_pls = len(data["elements"])
            log.info(f" {city['name']}", f" ({num_pls} segments)", "  ↓")
            segments = [PowerLineSegment(el) for el in data["elements"]]
            session.add_all(segments)
            if len(segments) > 0:
                region = Region(city["name"], sw, ne, city["img_url"], num_pls)
                session.add(region)

        session.commit()

    log.success("Done")


if __name__ == "__main__":
    populate_db()
