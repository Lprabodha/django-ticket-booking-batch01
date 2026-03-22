from django.shortcuts import render, redirect
from .forms import RegisterForm
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from bookings.models import Booking, Event

# Create your views here.

def login_view(request):
    
    error_message = None
    
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")
        
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            login(request, user)
            next_url = request.POST.get('next') or request.GET.get('next') or 'dashboard'
            return redirect(next_url)
        else:
            error_message = "Invalid username or password"    
    
    return render(request, "accounts/login.html", {'error': error_message})

def register_view(request):
    
    if request.method == "POST":
        form = RegisterForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data.get("username")
            password = form.cleaned_data.get("password")
            
            user = User.objects.create_user(username=username, password=password)
            login(request, user)
            return redirect("dashboard")
    else: 
        form = RegisterForm()
    return render(request, "accounts/register.html", {'form': form})

def logout_view(request):
    logout(request)
    return redirect("index")


@login_required
def dashboard_view(request):
    
    bookings = Booking.objects.filter(user=request.user).select_related("event", "event__venue").prefetch_related("tickets").order_by("-id")
    
    total_tickets = sum(b.quantity for b in bookings)
    
    return render(request, "accounts/dashboard.html", {
        "bookings" : bookings,
        "total_tickets" : total_tickets
    })