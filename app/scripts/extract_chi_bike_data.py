import os
from typing import List, Dict, Tuple
from requests.models import Response
import datetime
import pytz
import pandas as pd
from dotenv import load_dotenv
import itertools

from route_rangers_api.models import (
   BikeRidership,
   BikeStation,
)
from django.contrib.gis.geos import Point

from app.scripts.utils import make_request, process_daily_ridership_data, ingest_monthly_data

#########################
# Load and define variables
#########################
load_dotenv()

DATA_PORTAL_APP_TOKEN = os.getenv("DATA_PORTAL_APP_TOKEN")
BIKE_DATA_DIR = os.getenv("BIKE_DATA_DIR")

REQUEST_DELAY = 0.2
RESULTS_PER_PAGE = 50000  # Max number of results for API
TIMEOUT = 30

CHI_TZ = pytz.timezone("America/Chicago")


def extract_bike_stations(app_token=DATA_PORTAL_APP_TOKEN) -> List:
    """
    Extract bike station data from Chicago API
    """
    params = {"$$APP_TOKEN": app_token}
    resp = make_request(
        url="https://data.cityofchicago.org/resource/bbyy-e7gq.json", params=params
    )
    results = resp.json()
    return results


def ingest_bike_stations() -> None:
    """
    Ingest bike station data into BikeStation table
    """
    bike_stations = extract_bike_stations()
    for station in bike_stations:
        obs = BikeStation(
            city = "CHI",
            station_id=station["id"],
            station_name=station["station_name"],
            n_docks=station["total_docks"],
            location=Point(station["location"]["coordinates"]),
        )
        obs.save()


def create_daily_ridership_month(filepath: str) -> pd.DataFrame:
    """
    Create a dataframe with daily information by station with the 
    number of trips started and ended for one monthly file
    """
    monthly_df = pd.read_csv(filepath)
    ridership_df = process_daily_ridership_data(monthly_df)

    return ridership_df

def ingest_monthly_data(monthly_ridership_df:pd.DataFrame)->None:
    """
    Ingest ridership at the daily level into the BikeRidership table
    """
    for row in monthly_ridership_df.itertuples():
        obs_station = BikeStation.objects.filter(station_id=row.station)
        obs = BikeRidership(station=obs_station,date=row.date,
                            n_started = row.n_rides_started,
                            n_ended = row.n_rides_ended)
        obs.save()

def ingest_divvy_data():
    """
    Ingest the divvy data into the BikeRidership table 
    """
    for file in os.listdir(f"{BIKE_DATA_DIR}/2023-divvy-tripdata/"):
        if file!=".DS_Store":
            monthly_df = create_daily_ridership_month(f"{BIKE_DATA_DIR}/2023-divvy-tripdata/{file}")
            ingest_monthly_data(monthly_df)

def run():
    ingest_bike_stations()

if __name__ == "__main__":

   stations = extract_bike_stations()
   print(stations[0]["location"])

