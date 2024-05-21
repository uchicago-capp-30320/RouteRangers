"""
Processing data from db to simplify for views
"""

from django.db.models import Avg, Count, Sum, Q
import pandas as pd
from route_rangers_api.models import (
    TransitModes,
    TransitRoute,
    RidershipRoute,
    RidershipStation,
    Demographics,
)
from route_rangers_api.utils.city_mapping import CITY_CONTEXT
import json
from django.core.serializers.json import DjangoJSONEncoder


def dashboard_metrics(city: str):
    dashboard_card_data = {}
    all_ridership, bus_ridership, train_ridership = get_ridership(city)
    all_routes, bus_routes, train_routes = get_routes(city)
    all_commuters, bus_commuters, train_commuters = get_pct_riders(city)
    dashboard_card_data = {
        "All": {
            "TotalRiders": f'{format(all_ridership, ",")}',
            "TotalRoutes": all_routes,
            "PercentOfCommuters": f"{all_commuters}%",
        },
        "Bus": {
            "TotalRiders": f'{format(bus_ridership, ",")}',
            "TotalRoutes": bus_routes,
            "PercentOfCommuters": f"{bus_commuters}%",
        },
        "Train": {
            "TotalRiders": f'{format(train_ridership, ",")}',
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


def extract_top_ten(
    city: str, mode: int, transit_unit: str = "stations", weekday: bool = True
):
    """
    Extract ridership for top 10 stations or top 10 routes
    """
    top_ten_units = []
    if transit_unit == "stations":
        stations = RidershipStation.objects.filter(
            station_id__city=CITY_CONTEXT[city]["DB_Name"],
            date__year=2023,
            station_id__mode=mode,
        )
        if weekday:
            stations = stations.exclude(Q(date__week_day=1) | Q(date__week_day=7))
        else:
            stations = stations.exclude(Q(date__week_day=1) | Q(date__week_day=7))
        top_ten_stations = (
            stations.values("station_id__station_name")
            .annotate(avg_ridership=Sum("ridership") / Count("ridership"))
            .order_by("-avg_ridership")[:10]
        )
        for station in top_ten_stations:
            station_value = {
                "name": station["station_id__station_name"],
                "avg_ridership": station["avg_ridership"],
            }
            top_ten_units.append(station_value)
    else:
        routes = RidershipRoute.objects.filter(
            route_id__city=CITY_CONTEXT[city]["DB_Name"],
            date__year=2023,
            route_id__mode=mode,
        )
        print(f"routes: {routes}")
        if weekday:
            routes = routes.exclude(Q(date__week_day=1) | Q(date__week_day=7))
        else:
            routes = routes.exclude(Q(date__week_day=1) | Q(date__week_day=7))
        top_ten_routes = (
            routes.values("route_id__route_name")
            .annotate(avg_ridership=Sum("ridership") / Count("ridership"))
            .order_by("-avg_ridership")[:10]
        )
        for route in top_ten_routes:
            route_value = {
                "name": route["route_id__route_name"],
                "avg_ridership": route["avg_ridership"],
            }
            top_ten_units.append(route_value)

    return json.dumps(list(top_ten_units), cls=DjangoJSONEncoder)


def get_daily_ridership(city: str, mode: int = None):
    """
    Extract daily ridership to be graphed
    """
    if mode:
        route_daily_ridership = (
            RidershipRoute.objects.filter(
                route_id__mode=mode, route_id__city=CITY_CONTEXT[city]["DB_Name"]
            )
            .values("date")
            .annotate(total_ridership=Sum("ridership"))
            .order_by("date")
        )
        station_daily_ridership = (
            RidershipStation.objects.filter(
                station_id__mode=mode, station_id__city=CITY_CONTEXT[city]["DB_Name"]
            )
            .values("date")
            .annotate(total_ridership=Sum("ridership"))
            .order_by("date")
        )

    else:
        route_daily_ridership = (
            RidershipRoute.objects.filter(route_id__city=CITY_CONTEXT[city]["DB_Name"])
            .values("date")
            .annotate(total_ridership=Sum("ridership"))
            .order_by("date")
        )
        station_daily_ridership = (
            RidershipStation.objects.filter(
                station_id__city=CITY_CONTEXT[city]["DB_Name"]
            )
            .values("date")
            .annotate(total_ridership=Sum("ridership"))
            .order_by("date")
        )
    daily_ridership = {}
    for route in route_daily_ridership:
        daily_ridership[route["date"]] = route["total_ridership"]
    for station in station_daily_ridership:
        daily_ridership[station["date"]] = (
            daily_ridership.get(station["date"], 0) + station["total_ridership"]
        )

    ridership_list = []
    for date, ridership in daily_ridership.items():
        date_ridership = {"date": date, "ridership": ridership}
        ridership_list.append(date_ridership)

    return json.dumps(list(ridership_list), cls=DjangoJSONEncoder)
