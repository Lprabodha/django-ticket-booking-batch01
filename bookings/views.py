import uuid
import logging
import json
import requests

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
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import ensure_csrf_cookie
from django.http import JsonResponse

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
    
    
@ensure_csrf_cookie
def assistant_view(request):
    return render(request, "booking/assistant.html")

@require_POST
def ai_chat(request):
    try:
        body = json.loads(request.body.decode() or "{}")
    except json.JSONDecodeError:
        return JsonResponse({"reply": "Could not read your message. Try again."})

    user_message = body.get("message", "")
    if not isinstance(user_message, str):
        user_message = str(user_message)
    user_message = user_message.strip()
    if not user_message:
        return JsonResponse({"reply": "Please type a message first."})

    intent_reply = _basic_intent_reply(user_message)
    if intent_reply is not None:
        return JsonResponse({"reply": intent_reply})

    if not settings.HF_API_TOKEN:
        return JsonResponse({"reply": "Add HF_API_TOKEN to your .env file (Hugging Face token)."})

    lines = []
    for event in Event.objects.filter(is_published=True).select_related("venue")[:25]:
        v = event.venue
        lines.append(
            f"{event.title} | {event.event_date} {event.event_time} | {v.name}, {v.city} | "
            f"${event.price} | {event.available_tickets} tickets left | id: {event.id}"
        )
    catalog = "\n".join(lines) if lines else "(no published events yet)"

    system_prompt = (
        "You are a helpful ticket booking assistant for StarEvents. "
        "Use only the events list below for facts. Do not invent events.\n\n"
        "How to format every reply (important):\n"
        "- Use line breaks so text is easy to scan; never one huge paragraph.\n"
        "- For multiple events: put a blank line between each event.\n"
        "- For each event use this shape (plain text, you may use **Title** for the name):\n"
        "  **Event name**\n"
        "  - Date & time: ...\n"
        "  - Venue: ...\n"
        "  - Price: ...\n"
        "  - Tickets left: ...\n"
        "- Do not use emoji.\n\n"
        "Events:\n"
        f"{catalog}"
    )

    payload = {
        "model": settings.HF_CHAT_MODEL,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_message},
        ],
    }
    headers = {
        "Authorization": f"Bearer {settings.HF_API_TOKEN}",
        "Content-Type": "application/json",
    }

    try:
        response = requests.post(settings.HF_CHAT_URL, headers=headers, json=payload, timeout=90)
        result = response.json()
        reply = result.get("choices", [{}])[0].get("message", {}).get("content")
        # reply = result["choices"][0]["message"]["content"]
    except Exception as ex:
        logger.exception(ex)
        reply = "Sorry, something went wrong."

    return JsonResponse({"reply": reply})


def _basic_intent_reply(message: str):
    """Simple rule-based replies for hello / goodbye (no AI call)."""
    m = message.lower().strip().rstrip("!.?")
    if not m:
        return None

    # Goodbye
    bye_exact = {
        "bye",
        "goodbye",
        "see you",
        "see ya",
        "see you later",
        "bye bye",
        "cya",
        "farewell",
    }
    words = m.split()
    if m in bye_exact or (len(words) <= 4 and (words[0] == "bye" or words[-1] == "bye")):
        return (
            "Goodbye! Thanks for using StarEvents. "
            "Come back anytime to browse events or book tickets."
        )

    hi_exact = {
        "hi",
        "hello",
        "hey",
        "hiya",
        "yo",
        "sup",
        "howdy",
        "good morning",
        "good afternoon",
        "good evening",
    }
    if m in hi_exact:
        return (
            "Hi! I'm here to help with StarEvents.\n\n"
            "You can ask about upcoming events, venues, prices, or how booking works. "
            "What would you like to know?"
        )
    if m.startswith("hello") and len(m) <= 35 and "event" not in m and "ticket" not in m:
        parts = m.split()
        if len(parts) <= 5:
            return (
                "Hello! I'm the StarEvents ticket assistant.\n\n"
                "Ask me about shows, dates, or tickets — for example: “What events do you have?”"
            )

    return None