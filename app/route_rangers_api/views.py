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

from app.route_rangers_api.utils.city_mapping import CITY_CONTEXT, CITIES_CHOICES_SURVEY
from app.route_rangers_api.utils.metric_processing import dashboard_metrics
from route_rangers_api.models import TransitRoute, TransitStation, SurveyResponse

from route_rangers_api.forms import (
    RiderSurvey1,
    RiderSurvey2,
    RiderSurvey3,
    RiderSurvey4,
)

from django.contrib.gis.geos import GEOSGeometry, MultiLineString, LineString


def test(request):
    return HttpResponse("""This is a test route without any html/JS/static stuff""")


def home(request):
    context = {"cities_class": "cs-li-link cs-active", "about_class": "cs-li-link"}
    return render(request, "cities.html", context)


def about(request):
    context = {"cities_class": "cs-li-link", "about_class": "cs-li-link cs-active"}
    return render(request, "about.html", context)


def dashboard(request, city: str):
    # get metrics for dashboard cards
    dashboard_dict = dashboard_metrics(city)

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
        fields=("route_name", "color", "mode"),
    )

    stations = TransitStation.objects.filter(city=CITY_CONTEXT[city]["DB_Name"])
    stations_json = serialize(
        "geojson", stations, geometry_field="location", fields=("station_name", "mode")
    )

    city_name = CITY_CONTEXT[city]["CityName"]

    context = {
        "City": CITY_CONTEXT[city]["CityName"],
        "City_NoSpace": city,
        "citydata": dashboard_dict,
        "heatmaplabel": f"{city_name} Population Density",
        "Commute": "40 Min",
        "cities_class": "cs-li-link",
        "policy_class": "cs-li-link cs-active",
        "survey_class": "cs-li-link",
        "feedback_class": "cs-li-link",
        "coordinates": CITY_CONTEXT[city]["Coordinates"],
        "stations": stations_json,
        "csv": CITY_CONTEXT[city]["csv"],
        "lineplot": CITY_CONTEXT[city]["lineplot"],
        "geojsonfilepath": static(CITY_CONTEXT[city]["geojsonfilepath"]),
        "heatmapscale": [0, 10, 20, 50, 100, 200, 500, 1000],
        "heat_map_variable": "density",
        "routes": routes_json,
    }
    return render(request, "dashboard.html", context)


def survey_p1(request, city: str):
    # url = ""
    # Gen unique user id with uuid
    request.session["uuid"] = str(uuid.uuid4())
    user_id = request.session["uuid"]
    print(f'user_id:{request.session["uuid"]} - page 1')
    if request.method == "POST":
        # create new object
        city_survey = CITIES_CHOICES_SURVEY[city]
        survey_answer = SurveyAnswer(user_id=request.session["uuid"], city=city_survey)
        update_survey = RiderSurvey1(request.POST, instance=survey_answer)
        # update and save
        survey_answer = form.save(instance=survey_answer)

        update_survey.save()

        print("survey answer", survey_answer)
        return redirect(reverse("app:survey_p2", kwargs={"city": city}))
    else:
        form = RiderSurvey1()

    context = get_survey_context(city, form)

    return render(request, "survey.html", context)


def survey_p2(request, city: str, user_id: str = None):
    print(request.method)
    user_id = request.session.get("uuid")
    print(f'user_id:{request.session["uuid"]} - page 1')
    if request.method == "POST":
        survey_answer = SurveyAnswer.objects.get(user_id=user_id)
        update_survey = RiderSurvey2(request.POST, instance=survey_answer)
        update_survey.save()
        return redirect(reverse("app:survey_p3", kwargs={"city": city}))
    else:
        form = RiderSurvey2()

    context = get_survey_context(city, form)

    return render(request, "survey_p2.html", context)


def survey_p2(request, city: str, user_id: str = None):
    print(request.method)
    user_id = request.session.get("uuid")
    print(f'user_id:{request.session["uuid"]} - page 1')
    if request.method == "POST":
        survey_answer = SurveyAnswer.objects.get(user_id=user_id)
        update_survey = RiderSurvey2(request.POST, instance=survey_answer)
        update_survey.save()
        return redirect(reverse("app:survey_p3", kwargs={"city": city}))
    else:
        form = RiderSurvey2()

    context = get_survey_context(city, form)

    return render(request, "survey_p2.html", context)


def survey_p3(request, city: str):
    user_id = request.session.get("uuid")
    print(request.method)
    if request.method == "POST":
        survey_answer = SurveyAnswer.objects.get(user_id=user_id)
        update_survey = RiderSurvey3(request.POST, instance=survey_answer)
        update_survey.save()
        return redirect(reverse("app:survey_p4", kwargs={"city": city}))
    else:
        form = RiderSurvey3()

    context = get_survey_context(city, form)

    return render(request, "survey_p3.html", context)


def survey_p4(request, city: str):
    user_id = request.session.get("uuid")
    print(request.method)
    if request.method == "POST":
        survey_answer = SurveyAnswer.objects.get(user_id=user_id)
        update_survey = RiderSurvey4(request.POST, instance=survey_answer)
        update_survey.save()
        return redirect(reverse("app:thanks", kwargs={"city": city}))
    else:
        form = RiderSurvey4()

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
