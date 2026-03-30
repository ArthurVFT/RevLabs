from django.shortcuts import render

CARS = {
    'mercedes': {'id': 'mercedes', 'name': "Mercedes-AMG GT Black Series '20", 'image': 'img/mercedes-amg.png', 'time': '1:38.175'},
    'ferrari':  {'id': 'ferrari',  'name': "Ferrari 458 Italia '09",           'image': 'img/ferrari-458.png',  'time': '1:41.200'},
    'porsche':  {'id': 'porsche',  'name': "Porsche 911 GT3 RS (992) '22",    'image': 'img/porsche-911.png',  'time': '1:39.500'},
    'parati':   {'id': 'parati',   'name': "VW Parati",                        'image': 'img/vw-parati.png',    'time': '2:15.300'},
    'fusca':    {'id': 'fusca',    'name': "VW Fusca",                         'image': 'img/vw-fusca.png',     'time': '2:30.000'},
    'brasilia': {'id': 'brasilia', 'name': "VW Brasilia",                      'image': 'img/vw-brasilia.png',  'time': '2:25.500'}
}

def car_selection(request):
    return render(request, 'simulator/car_selection.html', {'cars': CARS.values()})

def dashboard(request):
    car_id = request.GET.get('car', 'mercedes') 
    selected_car = CARS.get(car_id, CARS['mercedes'])
    
    return render(request, 'simulator/dashboard.html', {'car': selected_car})