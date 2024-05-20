"""
Processing data from db to simplify for views
"""

from django.db.models import Avg, Count, Sum
import pandas as pd
from route_rangers_api.models import (
    TransitModes,
    TransitRoute,
    RidershipRoute,
    RidershipStation,
    Demographics,
)
from route_rangers_api.utils.city_mapping import CITY_CONTEXT


def dashboard_metrics(city: str):
    dashboard_card_data = {}
    all_ridership, bus_ridership, train_ridership = get_ridership(city)
    all_routes, bus_routes, train_routes = get_routes(city)
    all_commuters, bus_commuters, train_commuters = get_pct_riders(city)
    dashboard_card_data = {
        "All": {
            "TotalRiders": all_ridership,
            "TotalRoutes": all_routes,
            "PercentOfCommuters": f"{all_commuters}%",
        },
        "Bus": {
            "TotalRiders": bus_ridership,
            "TotalRoutes": bus_routes,
            "PercentOfCommuters": f"{bus_commuters}%",
        },
        "Train": {
            "TotalRiders": train_ridership,
            "TotalRoutes": train_routes,
            "PercentOfCommuters": f"{train_commuters}%",
        },
    }

    return dashboard_card_data


def get_ridership(city: str):
    """
    Get ridership for the city and be able to subset by mode of transit average per day
    """

    # all
    routes = RidershipRoute.objects.filter(
        route_id__city=CITY_CONTEXT[city]["DB_Name"], date__year=2023
    ).aggregate(daily_ridership=(Sum("ridership") / 365))
    stations = RidershipStation.objects.filter(
        station_id__city=CITY_CONTEXT[city]["DB_Name"], date__year=2023
    ).aggregate(daily_ridership=(Sum("ridership") / 365))
    if routes["daily_ridership"] is None:
        routes["daily_ridership"] = 0
    if stations["daily_ridership"] is None:
        stations["daily_ridership"] = 0
    all = routes["daily_ridership"] + stations["daily_ridership"]
    bus = get_ridership_by_mode(city, TransitModes.BUS)
    subway = get_ridership_by_mode(city, TransitModes.SUBWAY)
    light_rail = get_ridership_by_mode(city, TransitModes.LIGHT_RAIL)
    rail = get_ridership_by_mode(city, TransitModes.RAIL)
    train = subway + light_rail + rail
    return (all, bus, train)


def get_ridership_by_mode(city: str, mode: TransitModes):
    mode_routes = RidershipRoute.objects.filter(
        route_id__city=CITY_CONTEXT[city]["DB_Name"], route_id__mode=mode
    ).aggregate(daily_ridership=(Sum("ridership") / 365))
    mode_stations = RidershipStation.objects.filter(
        station_id__city=CITY_CONTEXT[city]["DB_Name"],
        station_id__mode=mode,
    ).aggregate(daily_ridership=(Sum("ridership") / 365))
    if mode_routes["daily_ridership"] is None:
        mode_routes["daily_ridership"] = 0
    if mode_stations["daily_ridership"] is None:
        mode_stations["daily_ridership"] = 0
    return mode_routes["daily_ridership"] + mode_stations["daily_ridership"]


def get_routes(city: str):
    """
    Get routes and be able to subset by mode of transit
    """
    # get num routes
    all_routes = TransitRoute.objects.filter(city=CITY_CONTEXT[city]["DB_Name"]).count()
    bus_routes = TransitRoute.objects.filter(
        city=CITY_CONTEXT[city]["DB_Name"], mode=TransitModes.BUS
    ).count()
    train_routes = TransitRoute.objects.filter(
        city=CITY_CONTEXT[city]["DB_Name"],
        mode__in=[TransitModes.LIGHT_RAIL, TransitModes.RAIL, TransitModes.SUBWAY],
    ).count()

    return all_routes, bus_routes, train_routes


def get_pct_riders(city: str):
    """
    Get percent of users that use this mode of transit
    """
    ridership = Demographics.objects.filter(
        county__in=CITY_CONTEXT[city]["fips_county"]
    ).aggregate(
        total_commute=(Sum("transportation_to_work")),
        transit_commute=(Sum("transportation_to_work_public")),
        bus_commute=(Sum("transportation_to_work_bus")),
        train_commute=(Sum("transportation_to_work_subway")),
    )
    all = round(((ridership["transit_commute"] / ridership["total_commute"]) * 100), 1)
    bus = round(((ridership["bus_commute"] / ridership["total_commute"]) * 100), 1)
    train = round(((ridership["train_commute"] / ridership["total_commute"]) * 100), 1)

    return all, bus, train


# Data Model from hardcoded mocked data
# CARD_DATA = {
#     "Bus": {
#         "Fall": {
#             "Weekdays": {
#                 "TotalRiders": 5000,
#                 "TotalRoutes": 30,
#                 "AverageCommuteTime": "45 minutes",
#             },
#             "Weekends": {
#                 "TotalRiders": 6000,
#                 "TotalRoutes": 35,
#                 "AverageCommuteTime": "50 minutes",
#             },
#         },
#         "Winter": {
#             "Weekdays": {
#                 "TotalRiders": 5500,
#                 "TotalRoutes": 32,
#                 "AverageCommuteTime": "48 minutes",
#             },
#             "Weekends": {
#                 "TotalRiders": 5800,
#                 "TotalRoutes": 33,
#                 "AverageCommuteTime": "47 minutes",
#             },
#         },
#         "Spring": {
#             "Weekdays": {
#                 "TotalRiders": 6200,
#                 "TotalRoutes": 37,
#                 "AverageCommuteTime": "52 minutes",
#             },
#             "Weekends": {
#                 "TotalRiders": 1,
#                 "TotalRoutes": 2,
#                 "AverageCommuteTime": "3 minutes",
#             },
#         },
#         "Summer": {
#             "Weekdays": {
#                 "TotalRiders": 4,
#                 "TotalRoutes": 5,
#                 "AverageCommuteTime": "6 minutes",
#             },
#             "Weekends": {
#                 "TotalRiders": 7,
#                 "TotalRoutes": 8,
#                 "AverageCommuteTime": "9 minutes",
#             },
#         },
#     },
#     "Train": {
#         "Fall": {
#             "Weekdays": {
#                 "TotalRiders": 50020,
#                 "TotalRoutes": 320,
#                 "AverageCommuteTime": "415 minutes",
#             },
#             "Weekends": {
#                 "TotalRiders": 60100,
#                 "TotalRoutes": 315,
#                 "AverageCommuteTime": "510 minutes",
#             },
#         },
#         "Winter": {
#             "Weekdays": {
#                 "TotalRiders": 51500,
#                 "TotalRoutes": 312,
#                 "AverageCommuteTime": "418 minutes",
#             },
#             "Weekends": {
#                 "TotalRiders": 5100,
#                 "TotalRoutes": 33,
#                 "AverageCommuteTime": "417 minutes",
#             },
#         },
#         "Spring": {
#             "Weekdays": {
#                 "TotalRiders": 62010,
#                 "TotalRoutes": 317,
#                 "AverageCommuteTime": "512 minutes",
#             },
#             "Weekends": {
#                 "TotalRiders": 11,
#                 "TotalRoutes": 21,
#                 "AverageCommuteTime": "31 minutes",
#             },
#         },
#         "Summer": {
#             "Weekdays": {
#                 "TotalRiders": 41,
#                 "TotalRoutes": 51,
#                 "AverageCommuteTime": "6 minutes",
#             },
#             "Weekends": {
#                 "TotalRiders": 71,
#                 "TotalRoutes": 81,
#                 "AverageCommuteTime": "91 minutes",
#             },
#         },
#     },
#     "all": {
#         "all": {
#             "all": {
#                 "TotalRiders": 71,
#                 "TotalRoutes": 81,
#                 "AverageCommuteTime": "91 minutes",
#             }
#         }
#     },
# }
