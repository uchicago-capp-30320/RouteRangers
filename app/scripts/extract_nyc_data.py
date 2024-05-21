import os
from typing import List
import requests
import datetime
import pytz
import logging
from dotenv import load_dotenv
from django.db import IntegrityError
from app.scripts.utils import make_request, build_start_end_date_str
from route_rangers_api.models import (
    TransitRoute,
    RidershipRoute,
    TransitStation,
    RidershipStation,
)

#########################
# Load and define variables
#########################
load_dotenv()

DATA_PORTAL_APP_TOKEN = os.getenv("DATA_PORTAL_APP_TOKEN")
TEST_DATA_DIR = os.getenv("TEST_DATA_DIR")

DATASETS = {
    "BUS_RIDERSHIP": {
        "URL": "https://data.ny.gov/resource/kv7t-n8in.json?",
        "GROUP_BY": "date, bus_route",
        "OBS_LEVEL": "bus_route",
    },
    "SUBWAY_RIDERSHIP": {
        "URL": "https://data.ny.gov/resource/wujg-7c2s.json?",
        "COLS_TO_KEEP": ["date", "station_complex_id", "ridership", "transfers"],
        "GROUP_BY": "date, station_complex_id",
        "OBS_LEVEL": "station_complex_id",
    },
}

NY_TZ = pytz.timezone("America/New_York")
START_DATE = datetime.datetime(2023, 1, 1, tzinfo=NY_TZ)
END_DATE = datetime.datetime(2024, 1, 1, tzinfo=NY_TZ)

# Logging configuration
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)


############################
# Data extraction
###########################


def extract_daily_data(
    dataset: str, date: datetime.datetime, app_token=DATA_PORTAL_APP_TOKEN
) -> List:
    """
    Extract daily data from a NY Subway or Bus ridership endpoint
    storing it in a list with dictionaries
    """
    # 1. Extract parameters
    url = DATASETS[dataset]["URL"]
    obs_level = DATASETS[dataset]["OBS_LEVEL"]

    # 2. Create SQL query clauses
    select_clause = f"""{obs_level}, date_trunc_ymd(transit_timestamp) AS date,
      SUM(ridership) AS total_ridership"""
    group_clause = f"{obs_level}, date"

    # Create datetime objects for date query filter
    start_date, end_date = build_start_end_date_str(date, NY_TZ)
    order_clause = f"{obs_level}"

    # 3. Define parameters to pass into the request:
    where_clause = (
        f"transit_timestamp >= '{start_date}' AND transit_timestamp < '{end_date}'"
    )
    params = {
        "$$APP_TOKEN": app_token,
        "$select": select_clause,
        "$group": group_clause,
        "$where": where_clause,
        "$order": order_clause,
    }
    # 4. Obtain results
    resp = make_request(url, params)
    if resp.status_code == 200:
        pass
    elif (
        resp.status_code == 202
    ):  # API docs indicate that OK Status Codes are 200 and 202
        print("Code status 200")  ##TODO: Add retry functionality
    else:
        print("Unsuccesful request")

    results = resp.json()
    return results


#####################
# Data Ingestion
#####################


def ingest_bus_ridership(
    start_date: datetime.date = START_DATE, end_date: datetime.date = END_DATE
) -> None:
    """
    Ingest the NYC bus ridership data to the RouteRidership table
    starting from start_date and ending at end_date (inclusive)
    """
    session = requests.Session()
    date = start_date
    time_delta = datetime.timedelta(days=1)
    while date <= end_date:
        print(f"Extracting bus ridership for {date}")
        date_ridership = extract_daily_data(dataset="BUS_RIDERSHIP", date=date)
        print(f"Ingesting bus ridership for {date}")
        ingest_daily_bus_ridership(date_ridership, date=date)
        date += time_delta


def ingest_daily_bus_ridership(daily_bus_json, date: datetime.date) -> None:
    """
    Ingest NYC bus data into the RouteRidership table. It ingests the data for one
    day of ridership
    """
    for row in daily_bus_json:
        try:
            print(
                f"Ingesting ridership data for stop {row['bus_route']} - {row['date']}"
            )
            obs_route = TransitRoute.objects.get(city="NYC", route_id=row["bus_route"])
            obs_route_id = obs_route.id
            ridership = int(float(row["total_ridership"]))
            obs = RidershipRoute(route_id=obs_route_id, date=date, ridership=ridership)
            obs.save()
        except IntegrityError:
            print(f"{row['bus_route']} - {row['date']} already ingested")
        except Exception as e:
            logging.info(
                f"Ingesting {row['bus_route']} - {row['date']} unsuccesful: {e}"
            )


def ingest_subway_ridership(
    start_date: datetime.date = START_DATE, end_date: datetime.date = END_DATE
) -> None:
    """
    Ingest the NYC subway ridership data to the RouteRidership table
    starting from start_date and ending at end_date (inclusive)
    """
    session = requests.Session()  # TODO: Incorporate session into ingestion
    date = start_date
    time_delta = datetime.timedelta(days=1)
    while date <= end_date:
        print(f"Extracting subway ridership for {date}")
        date_ridership = extract_daily_data(dataset="SUBWAY_RIDERSHIP", date=date)
        print(f"Ingesting subway ridership for {date}")
        ingest_daily_subway_ridership(date_ridership, date)
        date += time_delta


def ingest_daily_subway_ridership(daily_subway_json, date: datetime.date) -> None:
    """
    Ingest NYC subway data into the StationsRidership table. It ingests the data for one
    day of ridership
    """
    for row in daily_subway_json:
        try:
            print(
                f"Ingesting ridership data for station {row['station_complex_id']} - {row['date']}"
            )
            obs_station = TransitStation.objects.get(
                city="NYC", station_id=row["station_complex_id"].strip()
            )
            obs_station_id = obs_station.id
            ridership = int(float(row["total_ridership"]))
            obs = RidershipStation(
                station_id=obs_station_id, date=date, ridership=ridership
            )
            obs.save()
        except IntegrityError:
            print(f"{row['station_complex_id']} - {row['date']} already ingested")
        except Exception as e:
            logging.info(
                f"Ingesting {row['station_complex_id']} - {row['date']} unsuccesful: {e}"
            )


def run(
    start_date_str: str = "2023-01-01",
    end_date_str: str = "2024-01-02",
    transit_type: str = "both",
):
    """
    Run script ingesting ridership data for NY
    """
    # Convert arguments to datetime objects
    start_date = datetime.datetime.strptime(start_date_str, "%Y-%m-%d").replace(
        tzinfo=NY_TZ
    )
    end_date = datetime.datetime.strptime(end_date_str, "%Y-%m-%d").replace(
        tzinfo=NY_TZ
    )

    if transit_type in ["subway", "both"]:
        print("Ingesting subway ridership data into RidershipStation")
        ingest_subway_ridership(start_date=start_date, end_date=end_date)

    if transit_type in ["bus", "both"]:
        print("Ingesting bus ridership data into RouteRidership")
        ingest_bus_ridership(start_date=start_date, end_date=end_date)
