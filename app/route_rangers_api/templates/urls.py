from django.urls import path
from . import views
from route_rangers_api.views import MarkersMapView

app_name = "app"

urlpatterns = [
    path('', views.index, name='index'),
    path('home/', views.home, name='home'),
    path('about/', views.about, name='about'),
    path('policy/', views.Policy, name='policy'),
    path('survey/', views.Survey, name='survey'),
    path('feedback/', views.Feedback, name='feedback'),
    path('map/', views.MarkersMapView.as_view(), name='map'),
]
