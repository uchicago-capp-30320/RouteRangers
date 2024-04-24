from django.urls import path

from . import views
from route_rangers_api.views import MarkersMapView

app_name = "app"

urlpatterns = [
    path("", views.index, name="index"),
    path("map/", MarkersMapView.as_view()),
]
