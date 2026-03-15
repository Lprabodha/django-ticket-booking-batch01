from django.db import models
from django.conf import settings
from django.core.validators import MinValueValidator
from django.utils import timezone
import uuid

# Create your models here.
class Venue(models.Model):
    name = models.CharField(max_length=255)
    address = models.TextField(blank=True)
    city = models.CharField(max_length=100)
    country = models.CharField(max_length=100, blank=True)
    capacity = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True) 
    
    class Meta:
        ordering = ["name"]
    
    def __str__(self):
        return self.name
    
class Event(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    venue = models.ForeignKey(Venue, on_delete=models.PROTECT, related_name="events")
    title = models.CharField(max_length=255)
    description = models.TextField()
    event_date = models.DateField()
    event_time = models.TimeField()
    image = models.ImageField(upload_to="events/", blank=True, null=True)
    is_published = models.BooleanField(default=False)
    
    price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(0)]
    )
    
    available_tickets = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True) 
    updated_at = models.DateTimeField(auto_now_add=True) 
    
    class Meta:
            ordering = ["event_date", "event_time"]
            indexes = [
                models.Index(fields=["event_date", "is_published"]),
        ]
        
    def __str__(self):
        return self.title
    
    
class Booking(models.Model):
    class Status(models.TextChoices):
        PENDING = "Pending",  "Pending"
        CONFIRMED = "Confirmed",  "Confirmed"
        CANCELLED = "Cancelled", "Cancelled"
    
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="bookings")
    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name="bookings")
    booking_reference = models.CharField(max_length=50, unique=True, editable=False)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.PENDING)
    quantity = models.PositiveIntegerField(validators=[MinValueValidator(1)])
    total_price = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True) 
    
    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["booking_reference"]),
            models.Index(fields=["status"]),
        ]
        
    def save(self, *args, **kwargs):
        if not self.booking_reference:
            self.booking_reference = uuid.uuid4().hex[:12].upper()
        
        if self.event_id and self.quantity:
            self.total_price = self.event.price * self.quantity
        
        super().save(*args, **kwargs)
        
    def __str__(self):
        return f"{self.booking_reference} - {self.user}"
    
class Ticket(models.Model):
    ticket_number = models.CharField(max_length=50, unique=True, editable=False)
    booking = models.ForeignKey(Booking, on_delete=models.CASCADE, related_name= "tickets")
    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name= "tickets")
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name= "tickets")
    
    purchase_date = models.DateTimeField(default=timezone.now)
    qr_code = models.CharField(max_length=255, blank=True)
    
    class Meta:
        ordering = ["-purchase_date"]
        indexes = [
            models.Index(fields=["ticket_number"])
        ]
        
    def save(self, *args, **kwargs):
        if not self.ticket_number:
            self.ticket_number = f"TKT-{uuid.uuid4().hex[:10].upper()}" # TKT-87EW1W1W1W
        
        super().save(*args, **kwargs)
        
    def __str__(self):
        return self.ticket_number