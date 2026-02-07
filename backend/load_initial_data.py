import os
import django
import subprocess
import sys

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from catalogo.models import Marca, CategoriaProducto
from productos.models import UnitOfMeasure
from flota.models import TipoVehiculo
from tareas.models import CategoriaTarea

def load_fixture(fixture_path, description):
    print(f'Loading {description}...')
    try:
        subprocess.run(['python', 'manage.py', 'loaddata', fixture_path], check=True)
        print(f'Successfully loaded {description}.')
    except subprocess.CalledProcessError as e:
        print(f"Error loading {description}: {e}")

def main():
    print("Checking initial data...")

    # 1. Brands
    if Marca.objects.count() == 0:
        load_fixture('catalogo/fixtures/marcas_populares.json', 'popular brands')
    
    # 2. Categories and Tags
    if CategoriaProducto.objects.count() == 0:
        load_fixture('catalogo/fixtures/initial_data.json', 'catalog categories and tags')

    # 3. Unit of Measures
    if UnitOfMeasure.objects.count() == 0:
        load_fixture('productos/fixtures/unidades_medida.json', 'unit of measures')

    # 4. Vehicle Types
    if TipoVehiculo.objects.count() == 0:
        load_fixture('flota/fixtures/tipos_vehiculos.json', 'vehicle types')

    # 5. Task Categories
    if CategoriaTarea.objects.count() == 0:
        load_fixture('tareas/fixtures/initial_setup.json', 'task categories')

if __name__ == '__main__':
    main()
