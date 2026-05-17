import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'project.settings')
django.setup()

from revlabs.models import PartCategory, CarPart

print("Iniciando a reestruturação completa do catálogo...")

PartCategory.objects.filter(main_category='brakes', name='Brake Kits').delete()
PartCategory.objects.filter(main_category='tyres', name='Compounds').delete()
PartCategory.objects.filter(main_category='engine', name='Pistons').delete()
PartCategory.objects.filter(main_category='suspension').delete()

brakes_discs, _ = PartCategory.objects.get_or_create(main_category='brakes', name='Brake Discs')
brakes_calipers, _ = PartCategory.objects.get_or_create(main_category='brakes', name='Brake Calipers')

susp_coilover, _ = PartCategory.objects.get_or_create(main_category='suspension', name='Coilover')
susp_antiroll, _ = PartCategory.objects.get_or_create(main_category='suspension', name='Anti-roll bar')

aero_diffuser, _ = PartCategory.objects.get_or_create(main_category='aerodynamics', name='Diffuser')
aero_front, _ = PartCategory.objects.get_or_create(main_category='aerodynamics', name='Front Aero')
aero_rear, _ = PartCategory.objects.get_or_create(main_category='aerodynamics', name='Rear Aero')

engine_block, _ = PartCategory.objects.get_or_create(main_category='engine', name='Engine Block')
engine_filters, _ = PartCategory.objects.get_or_create(main_category='engine', name='Air Filters')
engine_ecu, _ = PartCategory.objects.get_or_create(main_category='engine', name='ECU')
engine_turbos, _ = PartCategory.objects.get_or_create(main_category='engine', name='Turbochargers')
engine_super, _ = PartCategory.objects.get_or_create(main_category='engine', name='Superchargers')

tyre_cats = {}
for t_name in ['Touring', 'Performance', 'Semi-Slick', 'High-Performance', 'Slick', 'Weather']:
    tyre_cats[t_name], _ = PartCategory.objects.get_or_create(main_category='tyres', name=t_name)

catalogo_pecas = [
    # Engine Block
    (engine_block, "Forged Aluminum Pistons", 20, -3, "img/pistao.png"),
    (engine_block, "Bore Up", 35, 2, "img/avatar-placeholder.png"),
    (engine_block, "Engine Balance Tuning", 15, -5, "img/avatar-placeholder.png"),
    (engine_block, "High Compression Pistons", 25, -2, "img/avatar-placeholder.png"),
    
    # Engine Complementares
    (engine_filters, "Cold Air Intake", 12, -1, "img/filtro_ar.png"),
    (engine_ecu, "Stage 2 ECU Remap", 55, 0, "img/ecu.png"),
    (engine_turbos, "Twin-Scroll Turbo Kit", 140, 18, "img/turbo-icon.png"),
    (engine_super, "Roots Supercharger", 110, 25, "img/supercompressor.png"),

    # Brakes
    (brakes_discs, "Slotted Steel Rotors", 0, -2, "img/avatar-placeholder.png"),
    (brakes_discs, "Carbon Ceramic Discs", 0, -15, "img/avatar-placeholder.png"),
    (brakes_calipers, "Sport 4-Piston Calipers", 0, -3, "img/avatar-placeholder.png"),
    (brakes_calipers, "6-Piston Big Brake Kit", 0, -8, "img/avatar-placeholder.png"),

    # Suspension
    (susp_coilover, "Street Coilovers", 0, -5, "img/avatar-placeholder.png"),
    (susp_coilover, "Fully Adjustable Race Coilovers", 0, -12, "img/avatar-placeholder.png"),
    (susp_antiroll, "Stiffened Anti-roll Bars", 0, -2, "img/avatar-placeholder.png"),

    # Aerodynamics
    (aero_diffuser, "Carbon Fiber Rear Diffuser", 0, -6, "img/avatar-placeholder.png"),
    (aero_front, "Carbon Fiber Splitter & Canards", 0, 4, "img/avatar-placeholder.png"),
    (aero_rear, "Adjustable GT Wing", 0, 8, "img/avatar-placeholder.png"),

    # Tyres
    (tyre_cats['Touring'], "Touring Tyres", 0, -5, "img/avatar-placeholder.png"),
    (tyre_cats['Performance'], "Performance Tyres", 0, -20, "img/avatar-placeholder.png"),
    (tyre_cats['Semi-Slick'], "Semi-Slick Track Tyres", 0, -35, "img/avatar-placeholder.png"),
    (tyre_cats['High-Performance'], "High-Performance Tyres", 0, -50, "img/avatar-placeholder.png"),
    (tyre_cats['Slick'], "Racing Slicks", 0, -70, "img/avatar-placeholder.png"),
    (tyre_cats['Weather'], "All-Weather Wet Tyres", 0, -10, "img/avatar-placeholder.png"),
]

print("Injetando o novo catálogo...")
for categoria, nome, hp, peso, img in catalogo_pecas:
    CarPart.objects.get_or_create(
        name=nome,
        defaults={
            'category': categoria,
            'added_hp': hp,
            'added_weight_kg': peso,
            'image_path': img
        }
    )

print("Catálogo atualizado com sucesso!")