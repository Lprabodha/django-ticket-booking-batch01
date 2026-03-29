import uuid
import logging

from django.shortcuts import render
from .models import Event, Booking, Ticket
from django.shortcuts import  get_object_or_404, redirect, render
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.contrib import messages
from django.urls import reverse
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.core.mail import EmailMultiAlternatives
from django.conf import settings

logger = logging.getLogger(__name__)


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

@login_required
def book_event_view(request, event_id):
    event = get_object_or_404(Event.objects.select_related("venue"), pk=event_id, is_published=True)
    
    if request.method == "GET": 
        
        context = {
            "event" : event,
            "quantity": 1,
            "quantity_options": range(1, min(event.available_tickets, 5) + 1),
            "booking_total" : event.price
        }
        
        return render(request, "booking/book_event.html", context)
    
    
    quantity_raw = request.POST.get("quantity", "1")
    
    try:
        quantity = int(quantity_raw)
    except (TypeError, ValueError):
        quantity = 1    
        
    quantity = max(quantity, 1)
    
    if event.available_tickets < 1:
        return redirect("event_detail", event_id=event_id)
    
    if quantity > event.available_tickets:
        quantity = event.available_tickets
        
    
    with transaction.atomic():
        event = get_object_or_404(Event.objects.select_for_update("venue"), pk=event_id, is_published=True)
        
        if event.available_tickets < quantity:
            quantity = event.available_tickets
            
        if quantity < 1:
            return redirect("event_detail", event_id=event_id)
        
        booking = Booking.objects.create(
            user=request.user,
            event=event,
            quantity=quantity,
            total_price= event.price * quantity,
            status= Booking.Status.CONFIRMED
        )
        
        Ticket.objects.bulk_create([
            Ticket(
                booking=booking, 
                event=event,
                user=request.user,
                ticket_number= f"TKT-{uuid.uuid4().hex[:10].upper()}"
            )
            for _ in range(quantity)
        ])
        
        transaction.on_commit(lambda: _send_booking_confirmation_email(request, booking))
        
        event.available_tickets -= quantity
        event.save(update_fields=["available_tickets"])
        
    messages.success(
        request, f"Your booking for {quantity} ticket(s) to {event.title} is confirmed! Your booking reference is {booking.booking_reference}."
    )
    
    return redirect("dashboard")


def _send_booking_confirmation_email(request, booking):
    if not booking.user.email:
        messages.warning(request, "Booking confirmed, but no email was sent because your account has no email address.")
        return

    user_display_name = booking.user.get_full_name() or booking.user.username
    event = booking.event
    dashboard_url = request.build_absolute_uri(reverse("dashboard"))

    subject = f"Booking Confirmation - {event.title}"
    context = {
        "user_display_name": user_display_name,
        "event": event,
        "booking": booking,
        "dashboard_url": dashboard_url,
    }

    html_message = render_to_string("booking/emails/booking_confirmation.html", context)
    text_message = strip_tags(html_message)

    email = EmailMultiAlternatives(
        subject=subject,
        body=text_message,
        from_email=settings.DEFAULT_FROM_EMAIL,
        to=[booking.user.email],
    )
    email.attach_alternative(html_message, "text/html")
    try:
        email.send(fail_silently=False)
    except Exception:
        logger.exception(
            "Failed to send booking confirmation email",
            extra={"booking_id": booking.id, "event_id": event.id, "user_id": booking.user.id},
        )
        messages.warning(
            request,
            "Booking confirmed, but confirmation email could not be sent. Please contact support.",
        )
    