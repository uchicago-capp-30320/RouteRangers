from django.db.models import F
from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse, HttpResponseRedirect
from django.template import loader
from django.http import Http404
from django.urls import reverse
from django.views import generic
from django.utils import timezone
from django.core.serializers import serialize

from app.route_rangers_api.utils.city_mapping import CITY_CONTEXT
from route_rangers_api.models import TransitRoute, TransitStation


def home(request):
    context = {"cities_class": "cs-li-link cs-active", "about_class": "cs-li-link"}
    return render(request, "cities.html", context)


def about(request):
    context = {"cities_class": "cs-li-link", "about_class": "cs-li-link cs-active"}
    return render(request, "about.html", context)


def dashboard(request, city: str):
    # get num riders

    # get num routes
    num_routes = TransitRoute.objects.filter(city=CITY_CONTEXT[city]["DB_Name"]).count()

    # get commute

    # get paths
    routes = TransitRoute.objects.filter(city="CHI").values(
        "geo_representation", "route_name", "color"
    )

    # stations
    stations = TransitStation.objects.values().filter(
        city=CITY_CONTEXT[city]["DB_Name"]
    )
    lst_coords = [[point["location"].x, point["location"].y] for point in stations]

    context = {
        "City": CITY_CONTEXT[city]["CityName"],
        "City_NoSpace": city,
        "TotalRiders": "104,749",
        "TotalRoutes": num_routes,
        "Commute": "40 Min",
        "cities_class": "cs-li-link",
        "policy_class": "cs-li-link cs-active",
        "survey_class": "cs-li-link",
        "feedback_class": "cs-li-link",
        "Coordinates": CITY_CONTEXT[city]["Coordinates"],
        "stations": lst_coords[:10],
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
        "Coordinates": CITY_CONTEXT[city]["Coordinates"],
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
        "Coordinates": CITY_CONTEXT[city]["Coordinates"],
    }
    return render(request, "responses.html", context)
