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
from typing import Dict


from route_rangers_api.models import (
    SurveyUser,
    SurveyResponse,
)
from route_rangers_api.utils.city_mapping import CITY_CONTEXT


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

    if use_transit != 0:
        percentage = (
            use_transit["daily_ridership"]
            / (
                SurveyUser.objects.filter(city=CITY_CONTEXT[city]["DB_Name"])
                .distinct("user_id")
                .count()
            )
            * 100
        )
    else:
        return "No answers yet!"

    return round(percentage, 1)


def get_rider_satisfaction(city: str) -> float:
    """
    Given a city return the avg transit satisfaction
    rating for reponses that include an answer to that
    question (e.g. exclude null responses)
    """
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
        "No satisfaction ratings yet!"

    return round(average, 1)


def get_transit_mode_dict(city: str) -> Dict:
    """
    Given a city, return a dictionary with a count
    of responses by transit mode. Legend for transit modes:
    """
    MODES_OF_TRANSIT = {
        1: "Bus",
        2: "Train",
        3: "Car",
        4: "Bike",
        5: "Walking",
        6: "Rideshare",
    }

    mode_count_dict = {}
    for mode_id, mode_name in MODES_OF_TRANSIT.items():
        count_by_mode = SurveyResponse.objects.filter(
            city=CITY_CONTEXT[city]["DB_Name"], modes_of_transit=mode_id
        ).count()
        mode_count_dict[mode_name] = count_by_mode

    return mode_count_dict


def get_trip_top_dict(city: str) -> Dict:
    """
    Given a city, return a dictionary with a count
    of responses by time of day
    """
    TIME_OF_DAY = {1: "Peak commute hours", 2: "Daytime", 3: "Nighttime"}
    tod_count_dict = {}
    for tod_id, tod_name in TIME_OF_DAY.items():
        count_by_tod = SurveyResponse.objects.filter(
            city=CITY_CONTEXT[city]["DB_Name"], trip_tod=tod_id
        ).count()
        tod_count_dict[tod_name] = count_by_tod

    return tod_count_dict


def get_transit_improv_drivers_dict(city: str) -> Dict:
    """
    Given a city, return a dictionary with a count
    of responses by suggested improvement
    """
    TRANSIT_IMPROVEMENT = {
        1: "More frequent service",
        2: "More accurate schedule times",
        3: "Fewer transfers or a more direct route",
        4: "It feels safe at the station and onboard",
        5: "No improvement needed",
    }
    improv_count_dict = {}
    for improv_id, improv_name in TRANSIT_IMPROVEMENT.items():
        count_by_improv = SurveyResponse.objects.filter(
            city=CITY_CONTEXT[city]["DB_Name"],
            transit_improvement=improv_id,
            user_id_id__car_owner=1,  # Filter by car_owner
        ).count()
        improv_count_dict[improv_name] = count_by_improv

    return improv_count_dict


def get_transit_improv_riders_dict(city: str) -> Dict:
    """
    Given a city, return a dictionary with a count
    of responses by suggested improvement
    """
    TRANSIT_IMPROVEMENT = {
        1: "More frequent service",
        2: "More accurate schedule times",
        3: "Fewer transfers or a more direct route",
        4: "It feels safe at the station and onboard",
        5: "No improvement needed",
    }
    improv_count_dict = {}
    for improv_id, improv_name in TRANSIT_IMPROVEMENT.items():
        count_by_improv = SurveyResponse.objects.filter(
            city=CITY_CONTEXT[city]["DB_Name"],
            transit_improvement=improv_id,
            user_id_id__car_owner=2,  # Filter by Non car_owner
        ).count()
        improv_count_dict[improv_name] = count_by_improv

    return improv_count_dict
