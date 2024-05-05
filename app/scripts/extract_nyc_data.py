import os
from typing import List, Dict, Tuple
from requests.models import Response
from collections.abc import Callable
import requests
import time
import datetime
import pytz
from dotenv import load_dotenv
from app.route_rangers_api.models import (
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

REQUEST_DELAY = 0.2
RESULTS_PER_PAGE = 50000  # Max number of results for API
TIMEOUT = 30

COLS_TO_KEEP = {"BUS_RIDERSHIP": [], "SUBWAY_RIDERSHIP": []}

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


# This function should be moved to a utils.py file
def make_request(url: str, params: Dict, session: Callable = None) -> Response:
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


def extract_daily_data(
    dataset: str, date: datetime.datetime, app_token=DATA_PORTAL_APP_TOKEN
) -> List:

    # 1. Extract parameters
    url = DATASETS[dataset]["URL"]
    obs_level = DATASETS[dataset]["OBS_LEVEL"]

    # 2. Create SQL query clauses
    select_clause = f"""{obs_level}, date_trunc_ymd(transit_timestamp) AS date,
      SUM(ridership) AS total_ridership"""
    group_clause = f"{obs_level}, date"

    # Create datetime objects for date query filter
    start_date, end_date = build_start_end_date_str(date)
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
        pass  ##TODO: Add retry functionality
    else:
        pass

    results = resp.json()
    return results


def build_start_end_date_str(date: datetime.datetime) -> Tuple[str, str]:
    """
    Creates two strings to pass as filters on the query for
    a request to the NYC Portal
    """
    start_date = date.astimezone(NY_TZ)
    time_delta = datetime.timedelta(days=1)
    end_date = start_date + time_delta
    start_date = start_date.strftime("%Y-%m-%d")
    end_date = end_date.strftime("%Y-%m-%d")

    return start_date, end_date


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
        date_ridership = extract_daily_data(dataset="BUS_RIDERSHIP", date=date)
        ingest_daily_bus_ridership(date_ridership)
        date += time_delta


def ingest_daily_bus_ridership(daily_bus_json, date: datetime.date) -> None:
    """
    Ingest NYC bus data into the RouteRidership table. It ingests the data for one
    day of ridership
    """
    for row in daily_bus_json:
        print(
            f"Ingesting ridership data for stations {row['bus_route']} - {row['date']}"
        )
        obs_route = TransitRoute.objects.filter(city="NYC", route_id=row["bus_route"])[
            0
        ]
        ridership = int(float(row["total_ridership"]))
        obs = RidershipRoute(route=obs_route, date=date, ridership=ridership)
        obs.save()


def ingest_subway_ridership(start_date: datetime.date, end_date: datetime.date) -> None:
    """
    Ingest the NYC subway ridership data to the RouteRidership table
    starting from start_date and ending at end_date (inclusive)
    """
    session = requests.Session()
    date = start_date
    time_delta = datetime.timedelta(days=1)
    while date <= end_date:
        date_ridership = extract_daily_data(dataset="SUBWAY_RIDERSHIP", date=date)
        ingest_daily_subway_ridership(date_ridership, date)
        date += time_delta


def ingest_daily_subway_ridership(daily_subway_json, date: datetime.date) -> None:
    """
    Ingest NYC subway data into the StationsRidership table. It ingests the data for one
    day of ridership
    """
    for row in daily_subway_json:
        print(
            f"Ingesting ridership data for stations {row['stationname']} - {row['date']}"
        )
        obs_route = TransitStation.objects.filter(
            city="NYC", station_id=row["station_complex_id"]
        )[0]
        ridership = int(float(row["total_ridership"]))
        obs = RidershipStation(route=obs_route, date=date, ridership=ridership)
        obs.save()


def run():

    print("Ingesting bus ridership data into RidershipRoute")
    ingest_bus_ridership()
    print("Ingesting subway ridership data into RidershipStation")
    ingest_subway_ridership()


if __name__ == "__main__":
    date = datetime.datetime(2023, 9, 7)
    results = extract_daily_data("SUBWAY_RIDERSHIP", date)
    print(results)
