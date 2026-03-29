import uuid
import logging

from django.db import transaction
from rest_framework import serializers

from .models import Booking, Event, Ticket, Venue

class VenueSerializer(serializers.ModelSerializer):
    class Meta:
        model = Venue
        fields = ["id", "name", "address", "country"]
        
class EventSerializer(serializers.ModelSerializer):
    class Meta:
        model = Event
        fields = ["id", "title", "description", "event_date"]