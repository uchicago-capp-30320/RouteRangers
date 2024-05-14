from django.db.models import F
from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse, HttpResponseRedirect
from django.template import loader
from django.http import Http404, JsonResponse
from django.urls import reverse
from django.views import generic
from django.utils import timezone
from django.core.serializers import serialize
from django.templatetags.static import static



from app.route_rangers_api.utils.city_mapping import CITY_CONTEXT
from route_rangers_api.models import TransitRoute, TransitStation

import json


def home(request):
    context = {"cities_class": "cs-li-link cs-active", "about_class": "cs-li-link"}
    return render(request, "cities.html", context)


def about(request):
    context = {"cities_class": "cs-li-link", "about_class": "cs-li-link cs-active"}
    return render(request, "about.html", context)


def dashboard(request, city: str):
    # get num riders
    print(city)
    # get num routes
    num_routes = TransitRoute.objects.filter(city=CITY_CONTEXT[city]["DB_Name"]).count()

    # get commute

    # get paths
    routes = TransitRoute.objects.filter(city=CITY_CONTEXT[city]["DB_Name"])  # .values(
    # MultiLineString needs to be serialized into a GeoJson object for Leaflet to
    # work with it.
    # to serialize into GeoJson, need to get out entire Django model object, not just
    # the .values("geo_representation", "route_name", "color")
    # with .values() you get "AttributeError: 'dict' has no component 'meta'"
    routes_json = serialize(
        "geojson",
        routes,
        geometry_field="geo_representation",
        fields=("route_name", "color"),
    )

    # stations
    stations = TransitStation.objects.values().filter(
        city=CITY_CONTEXT[city]["DB_Name"]
    )

    lst_coords = [
        [point["location"].x, point["location"].y, point["station_name"]]
        for point in stations
    ]

    context = {
        "City": CITY_CONTEXT[city]["CityName"],
        "City_NoSpace": city,
        "heatmaplabel": f"{CITY_CONTEXT[city]["CityName"]} Population Density",
        "TotalRiders": "104,749",
        "TotalRoutes": num_routes,
        "Commute": "40 Min",
        "cities_class": "cs-li-link",
        "policy_class": "cs-li-link cs-active",
        "survey_class": "cs-li-link",
        "feedback_class": "cs-li-link",
        "coordinates": CITY_CONTEXT[city]["Coordinates"],
        "stations": lst_coords,
        "csv": CITY_CONTEXT[city]["csv"],
        "lineplot": CITY_CONTEXT[city]["lineplot"],
        'geojsonfilepath': static(CITY_CONTEXT[city]['geojsonfilepath']),
        "routes": routes_json
    }
    return render(request, "dashboard.html", context)


def survey(request, city: str):
    context = {
        "City": CITY_CONTEXT[city]["CityName"],
        "City_NoSpace": city,
        "cities_class": "cs-li-link",
        "policy_class": "cs-li-link ",
        "survey_class": "cs-li-link cs-active",
        "feedback_class": "cs-li-link",
        "coordinates": CITY_CONTEXT[city]["Coordinates"],
    }
    return render(request, "survey.html", context)


def responses(request, city: str):
    context = {
        "City": CITY_CONTEXT[city]["CityName"],
        "Response": "567",
        "City_NoSpace": city,
        "Riders": "30%",
        "Cars": "270%",
        "cities_class": "cs-li-link",
        "policy_class": "cs-li-link ",
        "survey_class": "cs-li-link",
        "feedback_class": "cs-li-link cs-active",
        "coordinates": CITY_CONTEXT[city]["Coordinates"],
    }
    return render(request, "responses.html", context)
