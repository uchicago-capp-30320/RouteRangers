import requests
from route_rangers_api.models import Demographics
from django.contrib.gis.geos import Polygon
from typing import Dict
from requests.models import Response
from collections.abc import Callable
import time
from dotenv import load_dotenv

load_dotenv()

TIMEOUT = 15
REQUEST_DELAY = 0.5


CENSUS_GEOM_ENDPOINT = "https://tigerweb.geo.census.gov/arcgis/rest/services/TIGERweb/tigerWMS_Census2020/MapServer/6/query?"


def make_request(url: str, params: Dict = {}, session: Callable = None) -> Response:
    """
    Make a request to `url` and return the raw response.

    This function ensure that the domain matches what is
    expected and that the rate limit is obeyed.
    """
    time.sleep(REQUEST_DELAY)
    print(f"Fetching {url}")
    if session:
        resp = session.get(url, params=params)
    else:
        resp = requests.get(url, params, timeout=TIMEOUT)
    return resp


def get_census_tract_geom(state: str, county: str, tract: str):
    """
    Obtains the geometry of a census tract from the
    'Census TIGERweb GeoServices REST' API
    """
    where_clause = f"STATE = '{state}' AND COUNTY = '{county}' AND TRACT = '{tract}'"

    params = {
        "where": where_clause,
        "timeRelation": "esriTimeRelationOverlaps",
        "geometryType": "esriGeometryEnvelope",
        "spatialRel": "esriSpatialRelIntersects",
        "units": "esriSRUnit_Foot",
        "returnGeometry": "true",
        "returnTrueCurves": "false",
        "returnIdsOnly": "false",
        "returnCountOnly": "false",
        "returnZ": "false",
        "returnM": "false",
        "returnDistinctValues": "false",
        "returnExtentOnly": "false",
        "sqlFormat": "none",
        "featureEncoding": "esriDefault",
        "f": "geojson",
    }

    resp = make_request(CENSUS_GEOM_ENDPOINT, params)
    geom_json = resp.json()

    coordinates = geom_json["features"][0]["geometry"]["coordinates"][0]

    return coordinates


def ingest_city_census_tract_geo(update = True):
    """
    Ingest the geometry of the census tract
    """
    if update:
        obs_to_update = Demographics.objects.filter(geographic_delimitation__isnull=True)
    else:
        obs_to_update = Demographics.objects.all()

    for obs in obs_to_update:
        # Retrieve parameters for query
        state = obs.state
        county = obs.county
        tract = obs.census_tract

        # Obtain and update geometry
        coordinates = get_census_tract_geom(state, county, tract)
        geom = Polygon(coordinates)

        obs.geographic_delimitation = geom
        obs.save()

if __name__ == "__main__":
    coords = get_census_tract_geom("17", "031", "340600")
    print(coords)
