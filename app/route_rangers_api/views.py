from django.db.models import F
from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse, HttpResponseRedirect
from django.template import loader
from django.http import Http404, JsonResponse
from django.urls import reverse
from django.views import generic
from django.utils import timezone
from django.core.serializers import serialize
from django.templatetags.static import static
import uuid
import pdb

from app.route_rangers_api.utils.city_mapping import CITY_CONTEXT, CITIES_CHOICES_SURVEY
from route_rangers_api.models import TransitRoute, TransitStation, SurveyAnswer
from route_rangers_api.forms import (
    RiderSurvey1,
    RiderSurvey2,
    RiderSurvey3,
    RiderSurvey4,
)


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

    city_name = CITY_CONTEXT[city]["CityName"]

    context = {
        "City": CITY_CONTEXT[city]["CityName"],
        "City_NoSpace": city,
        "heatmaplabel": f"{city_name} Population Density",
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
        "geojsonfilepath": static(CITY_CONTEXT[city]["geojsonfilepath"]),
        "routes": routes_json,
    }
    return render(request, "dashboard.html", context)


def survey_p1(request, city):
    url = ""
    #Gen unique user id with uuid
    request.session["uuid"] = str(uuid.uuid4())
    print(request.method)
    if request.method == "POST":
        # # create new object
        city_survey = CITIES_CHOICES_SURVEY[str(city)]
        print(f"City passed to obs:{city_survey}")
        survey_answer = SurveyAnswer(user_id=request.session["uuid"], city=city_survey)
        update_survey = RiderSurvey1(request.POST,instance=survey_answer)
        # update and save
        update_survey.save()
        print("survey answer", survey_answer)
        url = "2"
        return redirect(url)
    else:
        form = RiderSurvey1()

    
    context = get_city_context(city,form,url)

    return render(request, "survey.html", context)


def survey_p2(request, city: str):
    url = "2"
    print(request.method)
    if request.method == "POST":
        form = RiderSurvey2(request.POST)
        if form.is_valid():
            # return survey answer object
            # get
            # update and save
            form.save()
            return redirect(url)
    else:
        form = RiderSurvey2()

    context = get_city_context(city,form,url)

    return render(request, "survey_p2.html", context)


def survey_p3(request, city: str):
    url = "4"
    print(request.method)
    if request.method == "POST":
        form = RiderSurvey3(request.POST)
        if form.is_valid():
            form.save()
            return redirect(url)
    else:
        form = RiderSurvey3()

    context = get_city_context(city,form,url)
    return render(request, "survey_p3.html", context)


def survey_p4(request, city: str):
    url = "thanks"
    print(request.method)
    if request.method == "POST":
        form = RiderSurvey4(request.POST)
        if form.is_valid():
            form.save()
            return redirect(url)
    else:
        form = RiderSurvey4()

    context = get_city_context(city,form,url)
    return render(request, "survey_p4.html", context)


def thanks(request, city: str):
    url = "thanks"

    context = {
        "City": CITY_CONTEXT[city]["CityName"],
        "City_NoSpace": city,
        "cities_class": "cs-li-link",
        "policy_class": "cs-li-link ",
        "survey_class": "cs-li-link cs-active",
        "feedback_class": "cs-li-link",
        "Coordinates": CITY_CONTEXT[city]["Coordinates"],
        "url": url,
    }
    return render(request, "thanks.html", context)


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


def get_city_context(city,form,url):
    context = {
        "City": CITY_CONTEXT[city]["CityName"],
        "City_NoSpace": city,
        "cities_class": "cs-li-link",
        "policy_class": "cs-li-link ",
        "survey_class": "cs-li-link cs-active",
        "feedback_class": "cs-li-link",
        "Coordinates": CITY_CONTEXT[city]["Coordinates"],
        "form": form,
        "url": url,
    }
    return context