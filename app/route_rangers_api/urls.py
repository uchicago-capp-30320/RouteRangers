from django.urls import path
from app.route_rangers_api import views
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin


app_name = "app"

urlpatterns = [
    path("", views.home, name="home"),
    path("about/", views.about, name="about"),
    path("dashboard/Chicago", views.Policy_Chicago, name="policychi"),
    path("dashboard/NewYork", views.Policy_NY, name="policyny"),
    path("dashboard/Portland", views.Policy_PRT, name="policyprt"),
    path("survey/Chicago", views.Survey_Chicago, name="surveyCHI"),
    path("survey/NewYork", views.Survey_NY, name="surveyNY"),
    path("survey/Portland", views.Survey_PRT, name="surveyPRT"),
    path("responses/Chicago", views.Feedback_Chicago, name="responses_CHI"),
    path("responses/NewYork", views.Feedback_NY, name="responses_NY"),
    path("responses/Portland", views.Feedback_PRT, name="responses_NY"),
]
