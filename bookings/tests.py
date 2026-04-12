from django.test import TestCase
from decimal import Decimal
from datetime import date, time
from django.contrib.auth import get_user_model

from bookings.models import Booking, Event, Venue, Ticket

# Create your tests here.

class BookingModelTests(TestCase):
    
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            username="testuser",
            password="12345678",
        )
        
        self.venue = Venue.objects.create(
            name = "Main Hall",
            city = "Galle",
            capacity = 500,
            country = "LK"
        )
        
        self.event = Event.objects.create(
            venue = self.venue,
            title = "Music Night",
            description = "Live event",
            event_date = date(2026, 5,1),
            event_time = time(18, 0),
            is_published = True,
            price = Decimal("1500"),
            available_tickets = 1000
        )
        
        
    def test_booking_generates_and_total_price(self):
        booking = Booking.objects.create(
            user = self.user,
            event = self.event,
            quantity = 2,
            status = Booking.Status.CONFIRMED,
            total_price = Decimal("0.00")
        )
        
        self.assertTrue(booking.booking_reference)
        self.assertEqual(len(booking.booking_reference), 12)
        self.assertEqual(booking.total_price, Decimal("3000"))
        
    def test_ticket_generate_ticket_number(self):
        booking = Booking.objects.create(
            user = self.user,
            event = self.event, 
            quantity = 1,
            status = Booking.Status.CONFIRMED, 
            total_price = Decimal("0.00")
        )
        
        ticket = Ticket.objects.create(
            booking = booking,
            event= self.event, 
            user = self.user
        )
        
        self.assertTrue(ticket.ticket_number.startswith("TKT-"))
        
class VenueModelTests(BookingModelTests):
    def test_string_representation_name(self):
        self.assertEqual(str(self.venue), "Main Hall")