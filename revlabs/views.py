from django.shortcuts import render

CARS = {
    'mercedes': {'id': 'mercedes', 'name': "Mercedes-AMG GT Black Series '20", 'image': 'img/mercedes-amg.png', 'time': '1:38.175'},
    'ferrari':  {'id': 'ferrari',  'name': "Ferrari 458 Italia '09",           'image': 'img/ferrari-458.png',  'time': '1:41.200'},
    'porsche':  {'id': 'porsche',  'name': "Porsche 911 GT3 RS (992) '22",    'image': 'img/porsche-911.png',  'time': '1:39.500'},
    'parati':   {'id': 'parati',   'name': "VW Parati",                        'image': 'img/vw-parati.png',    'time': '2:15.300'},
    'fusca':    {'id': 'fusca',    'name': "VW Fusca",                         'image': 'img/vw-fusca.png',     'time': '2:30.000'},
    'brasilia': {'id': 'brasilia', 'name': "VW Brasilia",                      'image': 'img/vw-brasilia.png',  'time': '2:25.500'}
}

TRACKS = {
    'monza':       {'id': 'monza',       'name': 'Monza - Italy',               'multiplier': 0.85, 'image': 'img/monza.png'},
    'suzuka':      {'id': 'suzuka',      'name': 'Suzuka - Japan',              'multiplier': 1.05, 'image': 'img/suzuka.png'},
    'interlagos':  {'id': 'interlagos',  'name': 'Interlagos - Brazil',         'multiplier': 1.00, 'image': 'img/interlagos-icon.png'},
    'nurburgring': {'id': 'nurburgring', 'name': 'Nürburgring GP - Germany',    'multiplier': 1.20, 'image': 'img/nurburgring.png'},
    'spa':         {'id': 'spa',         'name': 'Spa-Francorchamps - Belgium', 'multiplier': 1.40, 'image': 'img/spa.png'},
    'silverstone': {'id': 'silverstone', 'name': 'Silverstone - Great Britain', 'multiplier': 1.10, 'image': 'img/silverstone.png'},
}

def time_to_seconds(time_str):
    m, s = time_str.split(':')
    return int(m) * 60 + float(s)

def seconds_to_time(seconds):
    m = int(seconds // 60)
    s = seconds % 60
    return f"{m}:{s:06.3f}"

def track_selection(request):
    return render(request, 'simulator/track_selection.html', {'tracks': TRACKS.values()})

def car_selection(request):
    track_id = request.GET.get('track', 'interlagos')
    selected_track = TRACKS.get(track_id, TRACKS['interlagos'])
    
    context = {
        'cars': CARS.values(),
        'selected_track': selected_track 
    }
    return render(request, 'simulator/car_selection.html', context)

def dashboard(request):
    car_id = request.GET.get('car', 'mercedes') 
    track_id = request.GET.get('track', 'interlagos')
    
    selected_car = CARS.get(car_id, CARS['mercedes'])
    selected_track = TRACKS.get(track_id, TRACKS['interlagos'])

    base_seconds = time_to_seconds(selected_car['time'])
    adjusted_seconds = base_seconds * selected_track['multiplier']
    final_time = seconds_to_time(adjusted_seconds)
    
    context = {
        'car': selected_car,
        'track': selected_track,
        'final_time': final_time,
        'base_time': selected_car['time']
    }
    return render(request, 'simulator/dashboard.html', context)