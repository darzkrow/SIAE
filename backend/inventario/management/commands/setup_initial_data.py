"""
Script de management command para crear datos iniciales del sistema refactorizado.
Ejecutar con: python manage.py setup_initial_data
"""
from django.core.management.base import BaseCommand
from django.db import transaction
from inventario.models import Category, UnitOfMeasure, Supplier


class Command(BaseCommand):
    help = 'Crea datos iniciales para el sistema refactorizado (categorías, unidades, proveedores)'

    def handle(self, *args, **kwargs):
        self.stdout.write(self.style.SUCCESS('🚀 Iniciando creación de datos iniciales...\n'))
        
        with transaction.atomic():
            # Crear categorías
            self.create_categories()
            
            # Crear unidades de medida
            self.create_units()
            
            # Crear proveedor genérico
            self.create_default_supplier()
        
        self.stdout.write(self.style.SUCCESS('\n✅ Datos iniciales creados exitosamente!'))
    
    def create_categories(self):
        """Crear categorías de productos."""
        self.stdout.write('📁 Creando categorías...')
        
        categorias = [
            {
                'nombre': 'Productos Químicos',
                'codigo': 'QUI',
                'descripcion': 'Químicos para tratamiento de agua potable',
                'orden': 1
            },
            {
                'nombre': 'Tuberías',
                'codigo': 'TUB',
                'descripcion': 'Tuberías para sistemas de agua potable y saneamiento',
                'orden': 2
            },
            {
                'nombre': 'Bombas y Motores',
                'codigo': 'BOM',
                'descripcion': 'Equipos de bombeo y motores eléctricos',
                'orden': 3
            },
            {
                'nombre': 'Accesorios',
                'codigo': 'ACC',
                'descripcion': 'Válvulas, codos, tees y accesorios para tuberías',
                'orden': 4
            },
            {
                'nombre': 'Medidores',
                'codigo': 'MED',
                'descripcion': 'Medidores de agua y accesorios',
                'orden': 5
            }
        ]
        
        for cat_data in categorias:
            categoria, created = Category.objects.get_or_create(
                codigo=cat_data['codigo'],
                defaults=cat_data
            )
            if created:
                self.stdout.write(f'  ✓ {categoria.nombre} ({categoria.codigo})')
            else:
                self.stdout.write(f'  → {categoria.nombre} (ya existe)')
    
    def create_units(self):
        """Crear unidades de medida."""
        self.stdout.write('\n📏 Creando unidades de medida...')
        
        unidades = [
            # Longitud
            {'nombre': 'Metro', 'simbolo': 'm', 'tipo': 'LONGITUD'},
            {'nombre': 'Centímetro', 'simbolo': 'cm', 'tipo': 'LONGITUD'},
            
            # Volumen
            {'nombre': 'Litro', 'simbolo': 'L', 'tipo': 'VOLUMEN'},
            {'nombre': 'Galón', 'simbolo': 'gal', 'tipo': 'VOLUMEN'},
            {'nombre': 'Metro Cúbico', 'simbolo': 'm³', 'tipo': 'VOLUMEN'},
            
            # Peso
            {'nombre': 'Kilogramo', 'simbolo': 'kg', 'tipo': 'PESO'},
            {'nombre': 'Gramo', 'simbolo': 'g', 'tipo': 'PESO'},
            {'nombre': 'Tonelada', 'simbolo': 't', 'tipo': 'PESO'},
            
            # Unidad
            {'nombre': 'Unidad', 'simbolo': 'un', 'tipo': 'UNIDAD'},
            {'nombre': 'Pieza', 'simbolo': 'pza', 'tipo': 'UNIDAD'},
            {'nombre': 'Saco', 'simbolo': 'saco', 'tipo': 'UNIDAD'},
            {'nombre': 'Tambor', 'simbolo': 'tambor', 'tipo': 'UNIDAD'},
            {'nombre': 'Bidón', 'simbolo': 'bidón', 'tipo': 'UNIDAD'},
            
            # Área
            {'nombre': 'Metro Cuadrado', 'simbolo': 'm²', 'tipo': 'AREA'},
        ]
        
        for unidad_data in unidades:
            unidad, created = UnitOfMeasure.objects.get_or_create(
                simbolo=unidad_data['simbolo'],
                defaults=unidad_data
            )
            if created:
                self.stdout.write(f'  ✓ {unidad.nombre} ({unidad.simbolo})')
            else:
                self.stdout.write(f'  → {unidad.nombre} (ya existe)')
    
    def create_default_supplier(self):
        """Crear proveedor genérico por defecto."""
        self.stdout.write('\n🏢 Creando proveedor genérico...')
        
        proveedor, created = Supplier.objects.get_or_create(
            codigo='GEN',
            defaults={
                'nombre': 'Proveedor General',
                'rif': 'J-00000000-0',
                'contacto_nombre': 'Por Definir',
                'telefono': '0000-0000000',
                'email': 'info@example.com',
                'direccion': 'Por definir',
                'activo': True
            }
        )
        
        if created:
            self.stdout.write(f'  ✓ {proveedor.nombre} ({proveedor.codigo})')
            self.stdout.write(self.style.WARNING(
                '  ⚠️  Recuerda actualizar los proveedores reales después'
            ))
        else:
            self.stdout.write(f'  → {proveedor.nombre} (ya existe)')
