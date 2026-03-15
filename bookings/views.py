from django.shortcuts import render
from .models import Event
from django.shortcuts import  get_object_or_404, redirect, render

# Create your views here.
def home_view(request):
    latest_events = Event.objects.filter(is_published=True).select_related("venue")[:6]
    
    context = {
        "latest_events" : latest_events  
    }
    return render(request, 'booking/index.html', context)


def event_detail_view(request, event_id):
    event = get_object_or_404(
        Event.objects.select_related("venue"),
        pk=event_id,
        is_published = True,
    )
    
    context = {
        "event": event
    }
    
    return render(request, "booking/event_detail.html", context)


def events_view(request):
    events = Event.objects.filter(is_published=True).select_related("venue")
    
    context = {
        "events": events
    }
    
    return render(request, "booking/events.html",context)
    
def venue_view(request):
    return render(request, 'booking/venue.html')