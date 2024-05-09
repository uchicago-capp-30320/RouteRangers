import os
from typing import List, Dict, Tuple
from requests.models import Response
import datetime
import pytz
import pandas as pd
from dotenv import load_dotenv
import itertools
from app.scripts.utils import (
    process_daily_ridership_data,
    #ingest_monthly_data,
    extract_stations,
)

from route_rangers_api.models import (
   BikeRidership,
   BikeStation,
)
from django.contrib.gis.geos import Point


#########################
# Load and define variables
#########################
load_dotenv()

DATA_PORTAL_APP_TOKEN = os.getenv("DATA_PORTAL_APP_TOKEN")
BIKE_DATA_DIR = os.getenv("BIKE_DATA_DIR")

REQUEST_DELAY = 0.2
RESULTS_PER_PAGE = 50000  # Max number of results for API
TIMEOUT = 30

BIKE_STATIONS_ENDPOINT = "https://gbfs.lyft.com/gbfs/2.3/bkn/en/station_information.json"

def extract_bike_stations_files() -> List:
    """
    Extract bike station data from NY
    """

    daily_dfs = []

    for file in os.listdir(f"{BIKE_DATA_DIR}/2023-citibike-tripdata/7_July"):
        file_df = pd.read_csv(f"{BIKE_DATA_DIR}/2023-citibike-tripdata/7_July/{file}")
        daily_dfs.append(file_df)

    daily_df = pd.concat(daily_dfs)
    daily_df = daily_df.sort_values(by="started_at", ascending=True)

    stations = daily_df.groupby("start_station_id").first().reset_index()

    return stations


def ingest_bike_stations_data()-> None:
    stations = extract_stations(BIKE_STATIONS_ENDPOINT)
    for station in stations:
        try:
            obs = BikeStation(
                    city = "NYC",
                    station_id=station["station_id"],
                    station_name=station["name"],
                    short_name = station["short_name"],
                    n_docks=station["capacity"],
                    location=Point(station["lon"],station["lat"]),
                )
            obs.save()
        except:
            print(f"station {station['name']} has already been ingested")

def create_daily_ridership_month(filepath: str) -> pd.DataFrame:
    """
    Create a dataframe with daily information by station with the
    number of trips started and ended for one monthly file
    """
    monthly_dfs = []
    print(f"Directory from where to read csv {filepath}")
    #for file in os.listdir(f"{BIKE_DATA_DIR}/2023-citibike-tripdata/{filepath}"):
    for file in os.listdir(filepath):
        print(f"File to be read to concatenate df: {file}")
        file_df = pd.read_csv(f"{filepath}/{file}")
        monthly_dfs.append(file_df)

    monthly_df = pd.concat(monthly_dfs)

    ridership_df = process_daily_ridership_data(monthly_df)

    return ridership_df


def ingest_monthly_data(monthly_ridership_df:pd.DataFrame)->None:
    """
    Ingest ridership at the daily level into the BikeRidership table
    """
    for row in monthly_ridership_df.itertuples():
        try:
            obs_station = BikeStation.objects.filter(city="NYC",short_name=row.station_id).first().id
            print(f"Observation Station: {obs_station}")
            obs = BikeRidership(station_id=obs_station,date=row.date,
                            n_started = row.n_rides_started,
                            n_ended = row.n_rides_ended)
            obs.save()
            print(f"Observation Station: {obs_station} - {row.date} succesfully ingested")
        except:
            print(f"Observation Station: {obs_station} - {row.date} not ingested")

def ingest_citibike_ridership_data():
    """
    Ingest the citibike ridership data into the BikeRidership table
    """
    for file in os.listdir(f"{BIKE_DATA_DIR}/2023-citibike-tripdata/"):
        print(f"File to be created as df: {file}")
        if file != ".DS_Store":
            print(f"File to be passed into create_daily_ridership_month: {BIKE_DATA_DIR}/2023-citibike-tripdata/{file}")
            monthly_df = create_daily_ridership_month(
                f"{BIKE_DATA_DIR}/2023-citibike-tripdata/{file}"
            )
            ingest_monthly_data(monthly_df)

def run():
    ingest_bike_stations_data()
    ingest_citibike_ridership_data()

