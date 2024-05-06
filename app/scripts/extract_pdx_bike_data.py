import os
from typing import List, Dict, Tuple
from requests.models import Response
import datetime
import pytz
import pandas as pd
from dotenv import load_dotenv
from app.scripts.utils import extract_stations

# from route_rangers_api.models import (
#    BikeRidership,
#    BikeStation,
# )
# from django.contrib.gis.geos import Point
from app.scripts.utils import make_request

BIKE_STATIONS_URL = "https://gbfs.lyft.com/gbfs/2.3/pdx/en/station_information.json"

def ingest_stations():
    station = extract_stations(BIKE_STATIONS_URL)

if __name__ == "__main__":
    results = extract_bike_stations()
    print(results[0])