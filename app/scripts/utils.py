from typing import Dict, Tuple
from requests.models import Response
from collections.abc import Callable
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
