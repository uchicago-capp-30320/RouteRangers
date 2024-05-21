"""
Purpose: Processing data from db to display survey results
Date: May 21, 2024
Author: Jimena Salinas
"""

import os
import sys
import django
from dotenv import load_dotenv
import pandas as pd
from shapely import wkt
import geopandas as gpd
from geopandas import GeoDataFrame
import json
from shapely.geometry import MultiPolygon
from django.db.models import Avg, Count, Sum


def setup_django() -> None:
    load_dotenv()
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "geodjango.settings")

    # parent directory to find route_rangers_api
    current_dir = os.path.dirname(os.path.abspath(__file__))
    parent_dir = os.path.abspath(os.path.join(current_dir, "../../"))
    sys.path.append(parent_dir)

    django.setup()


setup_django()

from route_rangers_api.models import (
    SurveyUser,
    SurveyResponse,
)
from city_mapping import CITY_CONTEXT


def get_number_of_responses(city: str) -> int:
    """
    Given a city return the number of users who
    filled out our transit survey
    """
    all_responses = (
        SurveyUser.objects.filter(city=CITY_CONTEXT[city]["DB_Name"])
        .distinct("user_id")
        .count()
    )
    return all_responses


def get_transit_use_pct(city: str) -> float:
    """
    Given a city return the number of users who
    use transit regularly
    """

    use_transit = SurveyUser.objects.filter(
        city=CITY_CONTEXT[city]["DB_Name"], frequent_transit=1
    ).aggregate(daily_ridership=(Sum("frequent_transit")))

    percentage = (
        use_transit["daily_ridership"]
        / (
            SurveyUser.objects.filter(city=CITY_CONTEXT[city]["DB_Name"])
            .distinct("user_id")
            .count()
        )
        * 100
    )

    return round(percentage, 1)


def get_rider_satisfaction(city: str) -> float:
    satisfied_responses = (
        SurveyResponse.objects.filter(city=CITY_CONTEXT[city]["DB_Name"])
        .exclude(satisfied=None)
        .count()
    )

    if satisfied_responses != 0:
        average = (
            SurveyResponse.objects.filter(city=CITY_CONTEXT[city]["DB_Name"])
            .exclude(satisfied=None)
            .aggregate((Sum("satisfied")))
        )["satisfied__sum"] / satisfied_responses
    else:
        "No ratings yet!"

    return round(average, 1)


# def get_rider_satisfaction(city: str) -> float:
#     satisfied_responses = SurveyResponse.objects.filter(
#         city=CITY_CONTEXT[city]["DB_Name"], satisfied>0
#     ).count()

#     # else:
# average = (
#     SurveyResponse.objects.filter(
#         city=CITY_CONTEXT[city]["DB_Name"], satisfied=True
#     ).aggregate((Sum("satisfied")))
#     #         / satisfied_responses
#     #     )

#     return satisfied_responses  # Rounded to 1 decimal point


print(get_number_of_responses("NewYork"))

print(get_rider_satisfaction("NewYork"))
print(get_transit_use_pct("NewYork"))
