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
from django.contrib.gis.geos import GEOSGeometry, MultiLineString, LineString

import uuid

from app.route_rangers_api.utils.city_mapping import (
    CITY_CONTEXT,
    CITIES_CHOICES_SURVEY,
    CARD_DATA,
    MODES_OF_TRANSIT,
)
from route_rangers_api.models import (
    TransitRoute,
    TransitStation,
    SurveyResponse,
    SurveyUser,
)
from route_rangers_api.forms import (
    RiderSurvey1,
    RiderSurvey2,
    RiderSurvey3,
    RiderSurvey4,
    RiderSurvey5,
)

from django.contrib.gis.geos import GEOSGeometry, MultiLineString, LineString

from app.route_rangers_api.utils.city_mapping import CITY_CONTEXT
from route_rangers_api.models import TransitRoute, TransitStation

import json


def test(request):
    return HttpResponse("""This is a test route without any html/JS/static stuff""")


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
    routes = TransitRoute.objects.filter(city=CITY_CONTEXT[city]["DB_Name"])
    # reduce load time and data transfer size by overwriting model attribute
    TOLERANCE = 0.00005
    for route in routes:
        simple_geo_representation = route.geo_representation.simplify(
            tolerance=TOLERANCE, preserve_topology=True
        )
        # simplify() might alter the GEOS type; can't allow that
        if isinstance(simple_geo_representation, LineString):
            simple_geo_representation = MultiLineString(simple_geo_representation)
        route.geo_representation = simple_geo_representation

    routes_json = serialize(
        "geojson",
        routes,
        geometry_field="geo_representation",
        fields=("route_name", "color"),
    )

    # stations
    # TODO: consider passing these in with serialized geoJSON instead of
    # creating lst_coords separately
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
        "citydata": CARD_DATA,
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
        "heatmapscale": [0, 10, 20, 50, 100, 200, 500, 1000],
        "heat_map_variable": "density",
        "routes": routes_json,
    }
    return render(request, "dashboard.html", context)


def survey_p1(request, city: str):
    """
    Survey intro page
    """
    # Gen unique user id with uuid
    request.session["uuid"] = str(uuid.uuid4())
    request.session["route_id"] = 1
    print(f'user_id:{request.session["uuid"]} - page 1')
    if request.method == "POST":
        # create new SurveyUser object
        city_survey = CITIES_CHOICES_SURVEY[city]
        survey_answer = SurveyUser(user_id=request.session["uuid"], city=city_survey)
        update_survey = RiderSurvey1(request.POST, instance=survey_answer)
        # update and save
        update_survey.save()

        print("survey answer", survey_answer)
        return redirect(reverse("app:survey_p2", kwargs={"city": city}))

    else:  # GET
        form = RiderSurvey1()

    context = get_survey_context(city, form)

    return render(request, "survey.html", context)


def survey_p2(request, city: str, user_id: str = None):
    """
    Question about trip
    """
    print(request.method)
    user_id = request.session.get("uuid")
    route_id = request.session.get("route_id")

    print(f"user_id:{user_id} - page 2")
    if request.method == "POST":
        # check if route already exists
        city_survey = CITIES_CHOICES_SURVEY[city]
        survey_answer = SurveyResponse(
            user_id_id=user_id, city=city_survey, route_id=route_id
        )
        update_survey = RiderSurvey2(request.POST, instance=survey_answer)
        # update and save
        update_survey.save()

        # return selected mode of transit from form
        selected_mode_index = update_survey.cleaned_data["modes_of_transit"]
        selected_mode = MODES_OF_TRANSIT[selected_mode_index]
        print("selected mode: ", selected_mode)
        if selected_mode == "Train" or selected_mode == "Bus":
            return redirect(reverse("app:survey_p3", kwargs={"city": city}))
        elif selected_mode == "Car" or selected_mode == "Rideshare":
            return redirect(reverse("app:survey_p4", kwargs={"city": city}))
        else:
            return redirect(reverse("app:survey_p5", kwargs={"city": city}))

    else:  # GET
        form = RiderSurvey2()

    context = get_survey_context(city, form)

    return render(request, "survey_p2.html", context)


def survey_p3(request, city: str):
    """
    Questions for transit riders
    """
    user_id = request.session.get("uuid")
    route_id = request.session.get("route_id")
    print(f"user_id: {user_id} and route id: {route_id} - page 3")
    print(request.method)
    if request.method == "POST":
        survey_answer = SurveyResponse.objects.get(
            user_id_id=user_id, route_id=route_id
        )
        update_survey = RiderSurvey3(request.POST, instance=survey_answer)
        update_survey.save()

        # check if user has another trip to report
        another_trip = update_survey.cleaned_data["another_trip"]

        # Not recognizing T/F as booleans so using string
        if another_trip == "True" and int(route_id) < 3:
            route_id += 1
            request.session["route_id"] = route_id
            return redirect(reverse("app:survey_p2", kwargs={"city": city}))
        else:
            return redirect(reverse("app:thanks", kwargs={"city": city}))

    else:  # GET
        form = RiderSurvey3()

    context = get_survey_context(city, form)

    return render(request, "survey_p3.html", context)


def survey_p4(request, city: str):
    """
    Questions for drivers and rider share
    """
    user_id = request.session.get("uuid")
    route_id = request.session.get("route_id")
    print(request.method)
    if request.method == "POST":
        survey_answer = SurveyResponse.objects.get(
            user_id_id=user_id, route_id=route_id
        )
        update_survey = RiderSurvey4(request.POST, instance=survey_answer)
        update_survey.save()

        # check if user has another trip to report
        another_trip = update_survey.cleaned_data["another_trip"]

        if another_trip == "True" and int(route_id) < 3:
            route_id += 1
            request.session["route_id"] = route_id
            return redirect(reverse("app:survey_p2", kwargs={"city": city}))
        else:
            return redirect(reverse("app:thanks", kwargs={"city": city}))

    else:  # GET
        form = RiderSurvey4()

    context = get_survey_context(city, form)

    return render(request, "survey_p4.html", context)


def survey_p5(request, city: str):
    """
    Check if bikers and walkers have another trip to report.
    """
    route_id = request.session.get("route_id")
    print(request.method)
    if request.method == "POST":
        form = RiderSurvey5(request.POST)
        form.is_valid()

        # check if user has another trip to report
        another_trip = form.cleaned_data["another_trip"]

        if another_trip == "True" and int(route_id) < 3:
            route_id += 1
            request.session["route_id"] = route_id
            return redirect(reverse("app:survey_p2", kwargs={"city": city}))
        else:
            return redirect(reverse("app:thanks", kwargs={"city": city}))

    else:  # GET
        form = RiderSurvey5()

    context = get_survey_context(city, form)

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


def get_survey_context(city, form):
    context = {
        "City": CITY_CONTEXT[city]["CityName"],
        "City_NoSpace": city,
        "cities_class": "cs-li-link",
        "policy_class": "cs-li-link ",
        "survey_class": "cs-li-link cs-active",
        "feedback_class": "cs-li-link",
        "Coordinates": CITY_CONTEXT[city]["Coordinates"],
        "form": form,
    }
    return context
