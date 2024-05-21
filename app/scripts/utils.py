from typing import Dict, Tuple, List
from collections.abc import Callable
import pandas as pd
import requests
from requests.models import Response
import time
import requests
import datetime


REQUEST_DELAY = 0.5
TIMEOUT = 40


def make_request(
    url: str, params: Dict, session: Callable = None, timeout: int = TIMEOUT
) -> Response:
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

        resp = requests.get(url, params, timeout=timeout)
    return resp


def build_start_end_date_str(date: datetime.datetime, timezone) -> Tuple[str, str]:
    """
    Creates two strings to pass as filters on the query for
    a request to the Chicago data Portal
    """
    start_date = date.astimezone(timezone)
    time_delta = datetime.timedelta(days=1)
    end_date = start_date + time_delta
    start_date = start_date.strftime("%Y-%m-%d")
    end_date = end_date.strftime("%Y-%m-%d")

    return start_date, end_date

#######################
## Bike Ridership Utils
#######################

def extract_stations(url: str) -> List:
    """
    Extract bike station data from GTFS
    """
    resp = make_request(url=url, params={})
    results = resp.json()
    stations = results["data"]["stations"]

    return stations


def process_daily_ridership_data(monthly_df) -> pd.DataFrame:
    monthly_df["date"] = pd.to_datetime(monthly_df["started_at"]).dt.date
    monthly_df["start_station_id"] = monthly_df["start_station_id"].str.strip()
    monthly_df["end_station_id"] = monthly_df["end_station_id"].str.strip()

    started_at = (
        monthly_df.groupby(["start_station_id", "date"])
        .size()
        .reset_index(name="n_rides_started")
    )
    started_at = started_at.rename(columns={"start_station_id": "station_id"})

    ended_at = (
        monthly_df.groupby(["end_station_id", "date"])
        .size()
        .reset_index(name="n_rides_ended")
    )
    ended_at = ended_at.rename(columns={"end_station_id": "station_id"})

    ridership_df = started_at.merge(ended_at, how="left", on=["station_id", "date"])
    ridership_df["n_rides_ended"] = ridership_df["n_rides_ended"].fillna(0).astype(int)
    ridership_df["date"] = pd.to_datetime(ridership_df["date"])

    return ridership_df


