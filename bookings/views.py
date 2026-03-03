from django.shortcuts import render

# Create your views here.
def home_view(request):
    return render(request, 'booking/index.html')
    
def venue_view(request):
    return render(request, 'booking/venue.html')