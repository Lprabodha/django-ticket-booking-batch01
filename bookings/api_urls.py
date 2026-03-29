from django.urls import path
from .api_views import VenueListAPIView, EventListAPIView

urlpatterns = [
    path("venues/", VenueListAPIView.as_view(), name="venue-list"),
    path("events/", EventListAPIView.as_view(), name="event-list")
]