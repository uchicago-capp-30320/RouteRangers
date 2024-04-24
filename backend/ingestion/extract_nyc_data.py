import os
from typing import List, Dict, Tuple
from requests.models import Response
from collections.abc import Callable
import requests
import time
import pandas as pd
import datetime
import os
from dotenv import load_dotenv

#########################
# Load and define variables
#########################
load_dotenv()

NYC_DATA_PORTAL_APP_TOKEN = os.getenv("NYC_DATA_PORTAL_APP_TOKEN")
TEST_DATA_DIR = os.getenv("TEST_DATA_DIR")

REQUEST_DELAY = 0.2
RESULTS_PER_PAGE = 50000  # Max number of results for API
TIMEOUT = 30

COLS_TO_KEEP = {"BUS_RIDERSHIP": [], "SUBWAY_RIDERSHIP": []}

DATASETS = {
    "BUS_RIDERSHIP": {
        "URL": "https://data.ny.gov/resource/kv7t-n8in.json?",
        "COLS_TO_KEEP": ["date", "bus_route", "ridership", "transfers"],
        "GROUP_BY": ["date", "bus_route"],
    },
    "SUBWAY_RIDERSHIP": {
        "URL": "https://data.ny.gov/resource/wujg-7c2s.json?",
        "COLS_TO_KEEP": ["date", "station_complex_id", "ridership", "transfers"],
        "GROUP_BY": ["date", "station_complex_id"],
    },
}


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
    url: str,
    date: datetime.datetime,
    results_limit=None,
    app_token=NYC_DATA_PORTAL_APP_TOKEN,
    limit=RESULTS_PER_PAGE,
    session: Callable = None,
) -> List:
    """
    Extract daily data from a NYC Subway or Subway ridership endpoint
    storing it in a list with partial responses subject to the limit parameter.
    One item in the list has up to "limit" items
    """
    # Create datetime objects for date query filter
    start_date, end_date = build_start_end_date_str(date)

    # Define parameters to pass into the request:
    where_clause = (
        f"transit_timestamp >= '{start_date}' AND transit_timestamp < '{end_date}'"
    )

    # Make requests
    offset = 0
    n_results = 1
    responses = []

    while n_results > 0:
        # Build parameters and make request
        params = build_parameters(app_token, limit, offset, where_clause)
        resp = make_request(url, params, session)

        # Status code handling
        if resp.status_code == 200:
            pass
        elif (
            resp.status_code == 202
        ):  # API docs indicate that OK Status Codes are 200 and 202
            break  ##TO DO: Add retry functionality
        else:
            break

        resp_list = resp.json()  # Returns a list of dictionaries
        offset += limit
        n_results = len(resp_list)

        if n_results != 0:
            responses.append(resp_list)

    return responses


def create_daily_df(
    responses: List, date: datetime.datetime, dataset: str
) -> pd.DataFrame:
    """
    Create dataframe for one daily response
    """
    # Append dataframes
    daily_df = pd.DataFrame.from_dict(responses[0])

    for resp in responses[1:]:
        aux_df = pd.DataFrame.from_dict(resp)
        daily_df = pd.concat([daily_df, aux_df])

    # Filter columns
    start_date, _ = build_start_end_date_str(date)
    daily_df["date"] = start_date

    daily_df["ridership"] = daily_df["ridership"].astype(float)
    daily_df["transfers"] = daily_df["transfers"].astype(float)

    # Group by to obtain ridership per station/route
    ridership = (
        daily_df.loc[:, DATASETS[dataset]["COLS_TO_KEEP"]]
        .groupby(DATASETS[dataset]["GROUP_BY"],as_index=False)
        .agg("sum")
    )

    if date.weekday() < 5:
        ridership["weekday"] = 1
    else:
        ridership["weekday"] = 0

    return ridership


def build_parameters(
    app_token: str, limit: int, offset: int, where_clause: str
) -> Dict:
    """
    Build parameters to be passsed into the request call
    """
    params = {
        "$$APP_TOKEN": app_token,
        "$limit": limit,
        "$offset": offset,
        "$order": "transit_timestamp",
        "$where": where_clause,
    }
    return params


def build_start_end_date_str(date: datetime.datetime) -> Tuple[str, str]:
    """
    Creates two strings to pass as filters on the query for
    a request to the NYC Portal
    """
    time_delta = datetime.timedelta(days=1)
    end_date = date + time_delta
    start_date = date.strftime("%Y-%m-%d")
    end_date = end_date.strftime("%Y-%m-%d")

    return start_date, end_date


def crawl(start_date: datetime.date, end_date: datetime.date, dataset: str) -> None:
    """
    Crawl to obtain all the information from either the BUS_RIDERSHIP or
    SUBWAY_RIDERSHIP data
    """
    session = requests.Session()
    url = DATASETS[dataset]["URL"]
    date = start_date
    time_delta = datetime.timedelta(days=1)

    while date <= end_date:
        print(f"Obtaining information for {date.strftime('%Y-%m-%d')} for {dataset}")
        responses = extract_daily_data(url=url, date=date, session=session)
        date_df = create_daily_df(responses, date, dataset)
        # TO DO: INGEST INTO DATABASE
        date += time_delta

    return date_df


if __name__ == "__main__":
    date = datetime.datetime(2023,12,2)
    resp = extract_daily_data(DATASETS["BUS_RIDERSHIP"]["URL"],date)
    df = create_daily_df(resp,date,"BUS_RIDERSHIP")
    for row in df.itertuples():
        print(row.bus_route)
