from django.urls import path
from app.route_rangers_api import views
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin


app_name = "app"

urlpatterns = [
    path("", views.index, name="index"),
    path("about/", views.about, name="about"),
    path("dashboard/<str:city>", views.dashboard, name="dashboard"),
    path("survey/<str:city>", views.survey, name="survey"),
    path("responses/<str:city>", views.responses, name="responses"),
]
