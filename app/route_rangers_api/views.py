from django.db.models import F
from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse, HttpResponseRedirect
from django.template import loader
from django.http import Http404
from django.urls import reverse
from django.views import generic
from django.utils import timezone


def home(request):
    context = {"cities_class": "cs-li-link cs-active", "about_class": "cs-li-link"}
    return render(request, "Cities.html", context)


def about(request):
    context = {"cities_class": "cs-li-link", "about_class": "cs-li-link cs-active"}
    return render(request, "about.html", context)


def Policy_Chicago(request):
    context = {
        "City": "Chicago",
        "City_NoSpace": "Chicago",
        "TotalRiders": "104,749",
        "TotalRoutes": "203",
        "Commute": "40 Min",
        "cities_class": "cs-li-link",
        "policy_class": "cs-li-link cs-active",
        "survey_class": "cs-li-link",
        "feedback_class": "cs-li-link",
        "Coordinates": [41.8781, -87.6298],
    }
    return render(request, "PolicyMaker_CHI.html", context)


def Policy_NY(request):
    context = {
        "City": "New York",
        "City_NoSpace": "NewYork",
        "TotalRiders": "144",
        "TotalRoutes": "144",
        "cities_class": "cs-li-link",
        "policy_class": "cs-li-link cs-active",
        "survey_class": "cs-li-link",
        "feedback_class": "cs-li-link",
        "Commute": "147 Min",
        "Coordinates": [40.7128, -74.0060],
    }
    return render(request, "PolicyMaker_CHI.html", context)


def Policy_PRT(request):
    context = {
        "City": "Portland",
        "City_NoSpace": "Portland",
        "TotalRiders": "104,749",
        "TotalRoutes": "2",
        "Commute": "147 Min",
        "cities_class": "cs-li-link",
        "policy_class": "cs-li-link cs-active",
        "survey_class": "cs-li-link",
        "feedback_class": "cs-li-link",
        "Coordinates": [45.5051, -122.6750],
    }
    return render(request, "PolicyMaker_CHI.html", context)


def Survey_Chicago(request):
    context = {
        "City": "Chicago",
        "City_NoSpace": "Chicago",
        "cities_class": "cs-li-link",
        "policy_class": "cs-li-link ",
        "survey_class": "cs-li-link cs-active",
        "feedback_class": "cs-li-link",
        "Coordinates": [41.8781, -87.6298],
    }
    return render(request, "Survey.html", context)


def Survey_NY(request):
    context = {
        "City": "New York",
        "City_NoSpace": "NewYork",
        "Response": "246",
        "Riders": "12%",
        "Cars": "25%",
        "cities_class": "cs-li-link",
        "policy_class": "cs-li-link ",
        "survey_class": "cs-li-link cs-active",
        "feedback_class": "cs-li-link",
        "Coordinates": [40.7128, -74.0060],
    }
    return render(request, "Survey.html", context)


def Survey_PRT(request):
    context = {
        "City": "Portland",
        "City_NoSpace": "Portland",
        "Response": "11",
        "Riders": "42%",
        "Cars": "40%",
        "cities_class": "cs-li-link",
        "policy_class": "cs-li-link ",
        "survey_class": "cs-li-link cs-active",
        "feedback_class": "cs-li-link",
        "Coordinates": [45.5051, -122.6750],
    }
    return render(request, "Survey.html", context)


def Feedback_Chicago(request):
    context = {
        "City": "Chicago",
        "Response": "567",
        "City_NoSpace": "Chicago",
        "Riders": "30%",
        "Cars": "270%",
        "cities_class": "cs-li-link",
        "policy_class": "cs-li-link ",
        "survey_class": "cs-li-link",
        "feedback_class": "cs-li-link cs-active",
        "Coordinates": [41.8781, -87.6298],
    }
    return render(request, "Feedback.html", context)


def Feedback_NY(request):
    context = {
        "City": "New York",
        "City_NoSpace": "NewYork",
        "Response": "246",
        "Riders": "12%",
        "Cars": "25%",
        "cities_class": "cs-li-link",
        "policy_class": "cs-li-link ",
        "survey_class": "cs-li-link",
        "feedback_class": "cs-li-link cs-active",
        "Coordinates": [40.7128, -74.0060],
    }
    return render(request, "Feedback.html", context)


def Feedback_PRT(request):
    context = {
        "City": "Portland",
        "City_NoSpace": "Portland",
        "Response": "11",
        "Riders": "42%",
        "Cars": "40%",
        "cities_class": "cs-li-link",
        "policy_class": "cs-li-link ",
        "survey_class": "cs-li-link",
        "feedback_class": "cs-li-link cs-active",
        "Coordinates": [45.5051, -122.6750],
    }
    return render(request, "Feedback.html", context)
