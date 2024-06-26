from django.urls import path
from app.route_rangers_api import views
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin

app_name = "app"

urlpatterns = [
    path("test", views.test, name="test"),
    path("", views.home, name="home"),
    path("about/", views.about, name="about"),
    path("about/<str:city>", views.about_internal, name="about_int"),
    path("dashboard/<str:city>", views.dashboard, name="dashboard"),
    path("responses/<str:city>", views.responses, name="responses"),
    path("survey/<str:city>/", views.survey_p1, name="survey"),
    path("survey/<str:city>/2", views.survey_p2, name="survey_p2"),
    path("survey/<str:city>/3", views.survey_p3, name="survey_p3"),
    path("survey/<str:city>/4", views.survey_p4, name="survey_p4"),
    path("survey/<str:city>/5", views.survey_p5, name="survey_p5"),
    path("survey/<str:city>/thanks", views.thanks, name="thanks"),
]
