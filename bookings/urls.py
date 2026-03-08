from django.urls import path
from . import views

urlpatterns = [
    path("", views.home_view, name="index"),
    path("venue", views.venue_view,name="venue")
]
