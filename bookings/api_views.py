from rest_framework import generics
from .serializer import VenueSerializer, EventSerializer

from .models import Booking, Event, Venue

class VenueListAPIView(generics.ListAPIView):
    queryset = Venue.objects.all()
    serializer_class = VenueSerializer
    
class EventListAPIView(generics.ListAPIView):
    # queryset = Event.objects.filter(is_published=True)
    serializer_class = EventSerializer
    
    def get_queryset(self):
        queryset = Event.objects.filter(is_published=True)
        
        title = self.request.query_params.get('title')
        event_date = self.request.query_params.get('event_date')
        
        if title:
            queryset = queryset.filter(title__icontains=title)
            
        if event_date:
            queryset = queryset.filter(event_date=event_date)
            
        return queryset
