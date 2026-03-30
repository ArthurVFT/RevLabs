from django.shortcuts import render

# Create your views here.

def dashboard(request):
    return render(request, 'simulator/dashboard.html')

def car_selection(request):
    return render(request, 'simulator/car_selection.html')