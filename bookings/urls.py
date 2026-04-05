from django.urls import path
from . import views

urlpatterns = [
    path("", views.home_view, name="index"),
    path("venue", views.venue_view,name="venue"),
    path("events/", views.events_view, name= "event_list"),
    path("events/<uuid:event_id>/", views.event_detail_view, name="event_detail"),
    path("events/<uuid:event_id>/book", views.book_event_view, name="book_event"),
    path("assistant/", views.assistant_view, name="assistant"),
    path("assistant/chat", views.ai_chat, name="ai_chat")
]
