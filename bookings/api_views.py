from rest_framework import generics
from .serializer import VenueSerializer, EventSerializer

from .models import Booking, Event, Venue

class VenueListAPIView(generics.ListAPIView):
    queryset = Venue.objects.all()
    serializer_class = VenueSerializer
    
class EventListAPIView(generics.ListAPIView):
    queryset = Event.objects.filter(is_published=True)
    serializer_class = EventSerializer
