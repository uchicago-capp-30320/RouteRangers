import os
from typing import List, Dict, Tuple
from requests.models import Response
from collections.abc import Callable
import requests
import time
import pandas as pd
import datetime
import os
import pytz
from dotenv import load_dotenv
from route_rangers_api.models import (
    TransitRoute,
    RidershipRoute,
    TransitStation,
    RidershipStation,
)

###########################
# Load and define variables
###########################
load_dotenv()

DATA_PORTAL_APP_TOKEN = os.getenv("DATA_PORTAL_APP_TOKEN")

REQUEST_DELAY = 1
RESULTS_PER_PAGE = 50000  # Max number of results for API
TIMEOUT = 30

CHI_TZ = pytz.timezone("America/Chicago")
START_DATE = datetime.datetime(2023, 1, 1, tzinfo=CHI_TZ)
END_DATE = datetime.datetime(2024, 1, 1, tzinfo=CHI_TZ)

DATASETS = {
    "BUS_RIDERSHIP": {
        "URL": "https://data.cityofchicago.org/resource/jyb9-n7fm.json",
        "ORDER_BY": "route",
    },
    "SUBWAY_RIDERSHIP": {
        "URL": "https://data.cityofchicago.org/resource/5neh-572f.json",
        "ORDER_BY": "stationname",
    },
}

###########################
# Data extraction
###########################


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
    url: str,
    date: datetime.datetime,
    app_token=DATA_PORTAL_APP_TOKEN,
    session: Callable = None,
    order_by: str = None,
) -> List:
    """
    Extract daily data from a Chicago Subway or Bus ridership endpoint
    storing it in a list with partial responses subject to the limit parameter.
    One item in the list has up to "limit" items
    """
    # Create datetime objects for date query filter
    start_date, end_date = build_start_end_date_str(date)

    # Define parameters to pass into the request:
    where_clause = f"date >= '{start_date}' AND date < '{end_date}'"

    params = build_parameters(app_token, where_clause=where_clause, order_by=order_by)

    resp = make_request(url, params, session)

    # Status code handling
    if resp.status_code == 200:
        pass
    elif (
        resp.status_code == 202
    ):  # API docs indicate that OK Status Codes are 200 and 202
        print("202 response code")  ##TODO: Add retry functionality
    else:
        print("Not succesful requests")

    resp_list = resp.json()

    return resp_list


def build_parameters(
    app_token: str,
    limit: int = None,
    offset: int = None,
    where_clause: str = None,
    order_by: str = None,
) -> Dict:
    """
    Build parameters to be passsed into the request call
    """
    params = {
        "$$APP_TOKEN": app_token,
        "$limit": limit,
        "$offset": offset,
        "$order": order_by,
        "$where": where_clause,
    }
    return params


def build_start_end_date_str(date: datetime.datetime) -> Tuple[str, str]:
    """
    Creates two strings to pass as filters on the query for
    a request to the Chicago data Portal
    """
    start_date = date.astimezone(CHI_TZ)
    time_delta = datetime.timedelta(days=1)
    end_date = start_date + time_delta
    start_date = start_date.strftime("%Y-%m-%d")
    end_date = end_date.strftime("%Y-%m-%d")

    return start_date, end_date


#####################
# Data Ingestion
#####################


def ingest_bus_ridership(
    start_date: datetime.date = START_DATE, end_date: datetime.date = END_DATE
) -> None:
    """
    Ingest the Chicago bus ridership data to the RouteRidership table
    starting from start_date and ending at end_date (inclusive)
    """
    session = requests.Session()
    url = DATASETS["BUS_RIDERSHIP"]["URL"]
    date = start_date
    time_delta = datetime.timedelta(days=1)
    while date <= end_date:
        print(f"Extracting bus ridership for {date}")
        date_ridership = extract_daily_data(url=url, date=date, order_by="route")
        print(f"Ingesting bus ridership for {date}")
        ingest_daily_bus_ridership(date_ridership, date)
        date += time_delta


def ingest_daily_bus_ridership(daily_bus_json, date: datetime.date) -> None:
    """
    Ingest Chicago bus data into the RouteRidership table. It ingests the data for one
    day of ridership
    """
    for row in daily_bus_json:
        print(row["route"])
        try:
            print(
                f"Ingesting ridership data for stations {str(row['route'])} - {row['date']}"
            )
            obs_route = TransitRoute.objects.filter(
                city="CHI", route_id=row["route"]
            ).first()
            obs_route_id = obs_route.id
            obs = RidershipRoute(
                route_id=obs_route_id, date=date, ridership=row["rides"]
            )
            obs.save()
        except:
            print(f"Ingestion for row {row['route']} - {row['date']} not succesful")


def ingest_subway_ridership(start_date: datetime.date, end_date: datetime.date) -> None:
    """
    Ingest the Chicago subway ridership data to the RouteRidership table
    starting from start_date and ending at end_date (inclusive)
    """
    session = requests.Session()
    url = DATASETS["SUBWAY_RIDERSHIP"]["URL"]
    date = start_date
    time_delta = datetime.timedelta(days=1)
    while date <= end_date:
        print(f"Extracting subway ridership for {date}")
        date_ridership = extract_daily_data(url=url, date=date, order_by="station_id")
        print(f"Starting subway ridership for {date}")
        ingest_daily_subway_ridership(date_ridership, date)
        date += time_delta


def ingest_daily_subway_ridership(daily_subway_json, date: datetime.date) -> None:
    """
    Ingest Chicago subway data into the StationsRidership table. It ingests the data for one
    day of ridership
    """
    for row in daily_subway_json:

        try:
            print(
                f"Ingesting ridership data for station {row['station_id']} - {row['date']}"
            )
            obs_station = TransitStation.objects.filter(
                city="CHI", station_id=row["station_id"]
            ).first()
            obs_station_id = obs_station.id
            obs = RidershipStation(
                station_id=obs_station_id, date=date, ridership=row["rides"]
            )
            obs.save()
        except:
            print(
                f"Ingestion for row {row['station_id']} - {row['date']} not succesful"
            )


def run():
    start = datetime.datetime(2023, 1, 1)
    end = datetime.datetime(2023, 2, 1)
    # ingest_bus_ridership()
    ingest_subway_ridership(start_date=start, end_date=end)


# if __name__ == "__main__":
#     date = datetime.datetime(2023,7,9)
#     resp = extract_daily_data(DATASETS["BUS_RIDERSHIP"]["URL"],date)
#     for r in resp[:10]:
#         print(r)
#         print(r["route"])
