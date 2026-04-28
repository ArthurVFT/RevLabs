from django.shortcuts import render

# Velocidades médias mais realistas (em km/h) tendo Interlagos como base (fator 1.0).
CARS = {
    'mercedes': {'id': 'mercedes', 'name': "Mercedes-AMG GT Black Series '20", 'image': 'img/mercedes-amg.png', 'base_avg_speed_kmh': 160.0, 'power_hp': 730, 'weight_kg': 1540},
    'porsche':  {'id': 'porsche',  'name': "Porsche 911 GT3 RS (992) '22",    'image': 'img/porsche-911.png',  'base_avg_speed_kmh': 156.0, 'power_hp': 525, 'weight_kg': 1450},
    'ferrari':  {'id': 'ferrari',  'name': "Ferrari 458 Italia '09",           'image': 'img/ferrari-458.png',  'base_avg_speed_kmh': 150.0, 'power_hp': 570, 'weight_kg': 1485},
    'parati':   {'id': 'parati',   'name': "VW Parati",                        'image': 'img/vw-parati.png',    'base_avg_speed_kmh': 110.0, 'power_hp': 90,  'weight_kg': 950},
    'brasilia': {'id': 'brasilia', 'name': "VW Brasilia",                      'image': 'img/vw-brasilia.png',  'base_avg_speed_kmh': 98.0,  'power_hp': 65,  'weight_kg': 890},
    'fusca':    {'id': 'fusca',    'name': "VW Fusca",                         'image': 'img/vw-fusca.png',     'base_avg_speed_kmh': 95.0,  'power_hp': 65,  'weight_kg': 800}
}

# Multiplicadores de pista: Monza é a pista mais rápida (longas retas), Suzuka é muito técnica.
TRACKS = {
    'monza':       {'id': 'monza',       'name': 'Monza - Italy',               'length_km': 5.793, 'speed_multiplier': 1.18, 'image': 'img/monza.png'},
    'spa':         {'id': 'spa',         'name': 'Spa-Francorchamps - Belgium', 'length_km': 7.004, 'speed_multiplier': 1.12, 'image': 'img/spa.png'},
    'silverstone': {'id': 'silverstone', 'name': 'Silverstone - Great Britain', 'length_km': 5.891, 'speed_multiplier': 1.08, 'image': 'img/silverstone.png'},
    'interlagos':  {'id': 'interlagos',  'name': 'Interlagos - Brazil',         'length_km': 4.309, 'speed_multiplier': 1.00, 'image': 'img/interlagos-icon.png'},
    'nurburgring': {'id': 'nurburgring', 'name': 'Nürburgring GP - Germany',    'length_km': 5.148, 'speed_multiplier': 0.96, 'image': 'img/nurburgring.png'},
    'suzuka':      {'id': 'suzuka',      'name': 'Suzuka - Japan',              'length_km': 5.807, 'speed_multiplier': 0.94, 'image': 'img/suzuka.png'},
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
    
    # Aplica o fator da pista na velocidade do carro
    track_multiplier = selected_track.get('speed_multiplier', 1.0)
    base_speed = selected_car['base_avg_speed_kmh'] * track_multiplier
    
    base_seconds = (track_length / base_speed) * 3600
    final_time = seconds_to_time(base_seconds)

    context = {
        'car': selected_car,
        'track': selected_track,
        'final_time': final_time,
        'base_time': final_time,
        'track_length': track_length,
        'base_speed': base_speed,
        'base_power': selected_car['power_hp'],
        'base_weight': selected_car['weight_kg']
    }
    return render(request, 'simulator/dashboard.html', context)