import os
from typing import List, Dict, Tuple
from requests.models import Response
import datetime
import pytz
import pandas as pd
from dotenv import load_dotenv
from app.scripts.utils import extract_stations

from route_rangers_api.models import (
   BikeRidership,
   BikeStation,
)
from django.contrib.gis.geos import Point

BIKE_STATIONS_URL = "https://gbfs.lyft.com/gbfs/2.3/pdx/en/station_information.json"

def ingest_stations():
    stations = extract_stations(BIKE_STATIONS_URL)
    for station in stations:
        try:
            print(f"Ingesting PDX {station['station_id']}")
            obs = BikeStation(
                    city = "PDX",
                    station_id=station["station_id"],
                    station_name=station["name"],
                    n_docks=station["capacity"],
                    location=Point(station["lon"],station["lat"]),
                )
            obs.save()
        except:
            print(f"station {station['name']} has already been ingested")

def run():
    ingest_stations()

# if __name__ == "__main__":
#     results = extract_bike_stations()
#     print(results[0])