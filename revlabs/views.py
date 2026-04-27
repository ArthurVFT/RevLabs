from django.shortcuts import render

CARS = {
    'mercedes': {'id': 'mercedes', 'name': "Mercedes-AMG GT Black Series '20", 'image': 'img/mercedes-amg.png', 'base_avg_speed_kmh': 210.0},
    'ferrari':  {'id': 'ferrari',  'name': "Ferrari 458 Italia '09",           'image': 'img/ferrari-458.png',  'base_avg_speed_kmh': 205.0},
    'porsche':  {'id': 'porsche',  'name': "Porsche 911 GT3 RS (992) '22",    'image': 'img/porsche-911.png',  'base_avg_speed_kmh': 208.0},
    'parati':   {'id': 'parati',   'name': "VW Parati",                        'image': 'img/vw-parati.png',    'base_avg_speed_kmh': 115.0},
    'fusca':    {'id': 'fusca',    'name': "VW Fusca",                         'image': 'img/vw-fusca.png',     'base_avg_speed_kmh': 105.0},
    'brasilia': {'id': 'brasilia', 'name': "VW Brasilia",                      'image': 'img/vw-brasilia.png',  'base_avg_speed_kmh': 110.0}
}

TRACKS = {
    'monza':       {'id': 'monza',       'name': 'Monza - Italy',               'length_km': 5.793, 'image': 'img/monza.png'},
    'suzuka':      {'id': 'suzuka',      'name': 'Suzuka - Japan',              'length_km': 5.807, 'image': 'img/suzuka.png'},
    'interlagos':  {'id': 'interlagos',  'name': 'Interlagos - Brazil',         'length_km': 4.309, 'image': 'img/interlagos-icon.png'},
    'nurburgring': {'id': 'nurburgring', 'name': 'Nürburgring GP - Germany',    'length_km': 5.148, 'image': 'img/nurburgring.png'},
    'spa':         {'id': 'spa',         'name': 'Spa-Francorchamps - Belgium', 'length_km': 7.004, 'image': 'img/spa.png'},
    'silverstone': {'id': 'silverstone', 'name': 'Silverstone - Great Britain', 'length_km': 5.891, 'image': 'img/silverstone.png'},
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

    track_length = selected_track['length_km']
    base_speed = selected_car['base_avg_speed_kmh']
    
    base_seconds = (track_length / base_speed) * 3600
    final_time = seconds_to_time(base_seconds)
    
    context = {
        'car': selected_car,
        'track': selected_track,
        'final_time': final_time,
        'track_length': track_length,
        'base_speed': base_speed
    }
    return render(request, 'simulator/dashboard.html', context)