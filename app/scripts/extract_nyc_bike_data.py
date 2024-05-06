import os
from typing import List, Dict, Tuple
from requests.models import Response
import datetime
import pytz
import pandas as pd
from dotenv import load_dotenv
import itertools
from app.scripts.utils import process_daily_ridership_data,ingest_monthly_data

# from route_rangers_api.models import (
#    BikeRidership,
#    BikeStation,
# )
# from django.contrib.gis.geos import Point
from app.scripts.utils import make_request

#########################
# Load and define variables
#########################
load_dotenv()

DATA_PORTAL_APP_TOKEN = os.getenv("DATA_PORTAL_APP_TOKEN")
BIKE_DATA_DIR = os.getenv("BIKE_DATA_DIR")

REQUEST_DELAY = 0.2
RESULTS_PER_PAGE = 50000  # Max number of results for API
TIMEOUT = 30

def extract_bike_stations() -> List:
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

def ingest_bike_stations_data() -> None:
    stations_df = extract_bike_stations()

    for row in stations_df.itertuples():
        loc = Point(row.start_lat,row.start_lng)
        obs = BikeStation(station_id=row.started_at_id,station_name=row.started_at_name,
                          location=loc)
        obs.save()

def create_daily_ridership_month(filepath: str) -> pd.DataFrame:
    """
    Create a dataframe with daily information by station with the 
    number of trips started and ended for one monthly file
    """
    monthly_dfs = []

    for file in os.listdir(f"{BIKE_DATA_DIR}/2023-citibike-tripdata/{filepath}"):
        file_df = pd.read_csv(f"{BIKE_DATA_DIR}/2023-citibike-tripdata/{filepath}/{file}")
        monthly_dfs.append(file_df)

    monthly_df = pd.concat(monthly_dfs)

    ridership_df = process_daily_ridership_data(monthly_df)

    return ridership_df

def ingest_citibike_ridership_data():
    """
    Ingest the citibike ridership data into the BikeRidership table 
    """
    for file in os.listdir(f"{BIKE_DATA_DIR}/2023-citibike-tripdata/"):
        if file!=".DS_Store":
            monthly_df = create_daily_ridership_month(f"{BIKE_DATA_DIR}/2023-divvy-tripdata/{file}")
            ingest_monthly_data(monthly_df)

if __name__ == "__main__":
    ingest_citibike_ridership_data()
    