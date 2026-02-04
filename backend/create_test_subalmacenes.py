"""
Script para crear datos de prueba de Subalmacenes
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from geography.models import State, Municipality, Parish
from institucion.models import Subalmacen, Sucursal, OrganizacionCentral
from django.contrib.auth import get_user_model

User = get_user_model()

def create_test_data():
    print("🚀 Creando datos de prueba para Subalmacenes...")
    
    # 1. Crear estados si no existen
    print("\n1️⃣ Creando Estados...")
    estados_data = [
        'Zulia',
        'Miranda',
        'Carabobo',
        'Aragua',
        'Lara',
    ]
    
    estados = {}
    for nombre in estados_data:
        estado, created = State.objects.get_or_create(name=nombre)
        estados[nombre] = estado
        if created:
            print(f"   ✅ Estado creado: {nombre}")
        else:
            print(f"   ℹ️  Estado existente: {nombre}")
    
    # 2. Crear municipios
    print("\n2️⃣ Creando Municipios...")
    municipios_data = {
        'Zulia': ['Maracaibo', 'San Francisco', 'Cabimas'],
        'Miranda': ['Baruta', 'Chacao', 'Sucre'],
        'Carabobo': ['Valencia', 'Naguanagua', 'San Diego'],
    }
    
    municipios = {}
    for estado_nombre, munis in municipios_data.items():
        estado = estados[estado_nombre]
        for muni_nombre in munis:
            muni, created = Municipality.objects.get_or_create(
                name=muni_nombre,
                state=estado
            )
            municipios[f"{estado_nombre}-{muni_nombre}"] = muni
            if created:
                print(f"   ✅ Municipio creado: {muni_nombre} ({estado_nombre})")
    
    # 3. Obtener o crear organización y sucursal
    print("\n3️⃣ Creando Organización y Sucursal...")
    org, created = OrganizacionCentral.objects.get_or_create(
        nombre='Hidroven',
        defaults={'rif': 'J-00000000-0'}  # Changed from codigo to rif
    )
    if created:
        print(f"   ✅ Organización creada: {org.nombre}")
    
    sucursal, created = Sucursal.objects.get_or_create(
        nombre='Sucursal Zulia',
        organizacion_central=org,
        defaults={'codigo': 'SUC-ZUL'}
    )
    if created:
        print(f"   ✅ Sucursal creada: {sucursal.nombre}")
    
    # 4. Crear subalmacenes de prueba
    print("\n4️⃣ Creando Subalmacenes...")
    subalmacenes_data = [
        {
            'nombre': 'Subalmacén Maracaibo Norte',
            'codigo': 'SUB-ZUL-001',
            'estado': 'Zulia',
            'municipio': 'Zulia-Maracaibo',
            'direccion': 'Av. 5 de Julio, Sector Norte',
            'coordenadas_gps': '10.6666,-71.6333',
            'capacidad': 1000,
        },
        {
            'nombre': 'Subalmacén San Francisco',
            'codigo': 'SUB-ZUL-002',
            'estado': 'Zulia',
            'municipio': 'Zulia-San Francisco',
            'direccion': 'Zona Industrial San Francisco',
            'coordenadas_gps': '10.5500,-71.6000',
            'capacidad': 1500,
        },
        {
            'nombre': 'Subalmacén Cabimas',
            'codigo': 'SUB-ZUL-003',
            'estado': 'Zulia',
            'municipio': 'Zulia-Cabimas',
            'direccion': 'Costa Oriental del Lago',
            'coordenadas_gps': '10.4000,-71.4500',
            'capacidad': 800,
        },
        {
            'nombre': 'Subalmacén Valencia',
            'codigo': 'SUB-CAR-001',
            'estado': 'Carabobo',
            'municipio': 'Carabobo-Valencia',
            'direccion': 'Zona Industrial Valencia',
            'coordenadas_gps': '10.1800,-67.9900',
            'capacidad': 1200,
        },
    ]
    
    for data in subalmacenes_data:
        estado = estados[data['estado']]
        municipio = municipios.get(data['municipio'])
        
        subalmacen, created = Subalmacen.objects.get_or_create(
            codigo=data['codigo'],
            defaults={
                'nombre': data['nombre'],
                'sucursal': sucursal,
                'estado': estado,
                'municipio': municipio,
                'direccion': data['direccion'],
                'coordenadas_gps': data['coordenadas_gps'],
                'capacidad': data['capacidad'],
                'activo': True,
            }
        )
        
        if created:
            print(f"   ✅ Subalmacén creado: {subalmacen.codigo} - {subalmacen.nombre}")
            print(f"      📍 Ubicación: {subalmacen.get_ubicacion_completa()}")
        else:
            print(f"   ℹ️  Subalmacén existente: {subalmacen.codigo}")
    
    # 5. Resumen
    print("\n" + "="*60)
    print("📊 RESUMEN DE DATOS CREADOS")
    print("="*60)
    print(f"Estados: {State.objects.count()}")
    print(f"Municipios: {Municipality.objects.count()}")
    print(f"Subalmacenes: {Subalmacen.objects.count()}")
    print(f"Subalmacenes activos: {Subalmacen.objects.filter(activo=True).count()}")
    print("="*60)
    
    # 6. Listar subalmacenes por estado
    print("\n📍 SUBALMACENES POR ESTADO:")
    for estado in State.objects.all():
        count = Subalmacen.objects.filter(estado=estado).count()
        if count > 0:
            print(f"\n{estado.name}: {count} subalmacenes")
            for sub in Subalmacen.objects.filter(estado=estado):
                print(f"  • {sub.codigo} - {sub.nombre}")
                print(f"    📍 {sub.get_ubicacion_completa()}")
    
    print("\n✅ Datos de prueba creados exitosamente!")

if __name__ == '__main__':
    create_test_data()
