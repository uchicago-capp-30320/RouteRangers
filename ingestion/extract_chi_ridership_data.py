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

###########################
# Load and define variables
###########################
load_dotenv()

DATA_PORTAL_APP_TOKEN = os.getenv("DATA_PORTAL_APP_TOKEN")

REQUEST_DELAY = 0.2
RESULTS_PER_PAGE = 50000  # Max number of results for API
TIMEOUT = 30

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

CHI_TZ = pytz.timezone("America/Chicago")


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
        pass  ##TODO: Add retry functionality
    else:
        pass

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


if __name__ == "__main__":
    date = datetime.datetime(2023, 2, 28)
    resp = extract_daily_data(
        DATASETS["SUBWAY_RIDERSHIP"]["URL"],
        date,
        order_by=DATASETS["SUBWAY_RIDERSHIP"]["ORDER_BY"],
    )
    print(resp)
    print(len(resp))
