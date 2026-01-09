"""
Comando para generar datos de prueba realistas para una hidroeléctrica.
Incluye plantas, sistemas, tuberías, equipos y stock inicial.

Uso: python manage.py seed_test_data
"""
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from decimal import Decimal
from inventario.models import (
    OrganizacionCentral, Sucursal, Acueducto, Categoria,
    Tuberia, Equipo, StockTuberia, StockEquipo, AlertaStock
)

User = get_user_model()


class Command(BaseCommand):
    help = 'Genera datos de prueba realistas para una hidroeléctrica'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('🌊 Iniciando generación de datos de prueba...'))
        
        # Crear organización
        org, created = OrganizacionCentral.objects.get_or_create(
            nombre='Hidroeléctrica Central Caroní',
            defaults={'rif': 'J-12345678-9'}
        )
        self.stdout.write(f"{'✓' if created else '→'} Organización: {org.nombre}")
        
        # Crear sucursales (plantas)
        sucursales_data = [
            {'nombre': 'Planta Caroní - Sector A', 'desc': 'Planta principal de generación'},
            {'nombre': 'Planta Orinoco - Sector B', 'desc': 'Planta secundaria de distribución'},
            {'nombre': 'Planta Apure - Sector C', 'desc': 'Planta de bombeo auxiliar'},
        ]
        
        sucursales = {}
        for data in sucursales_data:
            sucursal, created = Sucursal.objects.get_or_create(
                nombre=data['nombre'],
                organizacion_central=org
            )
            sucursales[data['nombre']] = sucursal
            self.stdout.write(f"{'✓' if created else '→'} Sucursal: {sucursal.nombre}")
        
        # Crear acueductos (sistemas dentro de cada planta)
        acueductos_data = {
            'Planta Caroní - Sector A': [
                'Sistema de Bombeo Principal',
                'Sistema de Distribución Secundario',
                'Sistema de Emergencia',
            ],
            'Planta Orinoco - Sector B': [
                'Sistema de Bombeo Orinoco',
                'Sistema de Tratamiento',
            ],
            'Planta Apure - Sector C': [
                'Sistema Auxiliar de Bombeo',
            ],
        }
        
        acueductos = {}
        for sucursal_nombre, sistemas in acueductos_data.items():
            for sistema in sistemas:
                acueducto, created = Acueducto.objects.get_or_create(
                    nombre=sistema,
                    sucursal=sucursales[sucursal_nombre]
                )
                acueductos[sistema] = acueducto
                self.stdout.write(f"{'✓' if created else '→'} Acueducto: {acueducto.nombre}")
        
        # Crear categorías
        categorias_data = [
            'Tuberías',
            'Motores de Bombeo',
            'Bombas Centrífugas',
            'Válvulas',
            'Compresores',
            'Generadores',
            'Transformadores',
            'Filtros',
        ]
        
        categorias = {}
        for cat_nombre in categorias_data:
            categoria, created = Categoria.objects.get_or_create(nombre=cat_nombre)
            categorias[cat_nombre] = categoria
            self.stdout.write(f"{'✓' if created else '→'} Categoría: {categoria.nombre}")
        
        # Crear tuberías (artículos operativos)
        tuberias_data = [
            {
                'nombre': 'Tubería PVC 100mm - Agua Potable',
                'categoria': 'Tuberías',
                'material': 'PVC',
                'tipo_uso': 'POTABLE',
                'diametro': 100,
                'longitud': Decimal('50.00'),
                'desc': 'Tubería de PVC para sistemas de agua potable'
            },
            {
                'nombre': 'Tubería PVC 75mm - Agua Potable',
                'categoria': 'Tuberías',
                'material': 'PVC',
                'tipo_uso': 'POTABLE',
                'diametro': 75,
                'longitud': Decimal('50.00'),
                'desc': 'Tubería de PVC de menor diámetro'
            },
            {
                'nombre': 'Tubería Hierro Dúctil 150mm - Aguas Servidas',
                'categoria': 'Tuberías',
                'material': 'HIERRO',
                'tipo_uso': 'SERVIDAS',
                'diametro': 150,
                'longitud': Decimal('100.00'),
                'desc': 'Tubería de hierro dúctil para aguas servidas'
            },
            {
                'nombre': 'Tubería Hierro Dúctil 200mm - Aguas Servidas',
                'categoria': 'Tuberías',
                'material': 'HIERRO',
                'tipo_uso': 'SERVIDAS',
                'diametro': 200,
                'longitud': Decimal('100.00'),
                'desc': 'Tubería de hierro dúctil de mayor diámetro'
            },
            {
                'nombre': 'Tubería Cemento 200mm - Riego',
                'categoria': 'Tuberías',
                'material': 'CEMENTO',
                'tipo_uso': 'RIEGO',
                'diametro': 200,
                'longitud': Decimal('75.00'),
                'desc': 'Tubería de cemento para sistemas de riego'
            },
            {
                'nombre': 'Tubería Cemento 250mm - Riego',
                'categoria': 'Tuberías',
                'material': 'CEMENTO',
                'tipo_uso': 'RIEGO',
                'diametro': 250,
                'longitud': Decimal('75.00'),
                'desc': 'Tubería de cemento de mayor capacidad'
            },
        ]
        
        tuberias = {}
        for tub_data in tuberias_data:
            tuberia, created = Tuberia.objects.get_or_create(
                nombre=tub_data['nombre'],
                defaults={
                    'descripcion': tub_data['desc'],
                    'categoria': categorias[tub_data['categoria']],
                    'material': tub_data['material'],
                    'tipo_uso': tub_data['tipo_uso'],
                    'diametro_nominal_mm': tub_data['diametro'],
                    'longitud_m': tub_data['longitud'],
                }
            )
            tuberias[tub_data['nombre']] = tuberia
            self.stdout.write(f"{'✓' if created else '→'} Tubería: {tuberia.nombre}")
        
        # Crear equipos (motores de bombeo y otros equipos operativos)
        equipos_data = [
            {
                'nombre': 'Motor de Bombeo Centrífugo 50 HP',
                'categoria': 'Motores de Bombeo',
                'marca': 'Siemens',
                'modelo': 'IE3-100L-4',
                'potencia': Decimal('50.00'),
                'serie': 'SIE-2024-001',
                'desc': 'Motor trifásico para bombeo de agua'
            },
            {
                'nombre': 'Motor de Bombeo Centrífugo 75 HP',
                'categoria': 'Motores de Bombeo',
                'marca': 'ABB',
                'modelo': 'M3BP-225M-4',
                'potencia': Decimal('75.00'),
                'serie': 'ABB-2024-001',
                'desc': 'Motor trifásico de alta potencia'
            },
            {
                'nombre': 'Motor de Bombeo Centrífugo 100 HP',
                'categoria': 'Motores de Bombeo',
                'marca': 'WEG',
                'modelo': 'W22-100L-4',
                'potencia': Decimal('100.00'),
                'serie': 'WEG-2024-001',
                'desc': 'Motor de bombeo de máxima potencia'
            },
            {
                'nombre': 'Bomba Centrífuga 100m³/h',
                'categoria': 'Bombas Centrífugas',
                'marca': 'Grundfos',
                'modelo': 'CR-100-2-2',
                'potencia': Decimal('30.00'),
                'serie': 'GRU-2024-001',
                'desc': 'Bomba para sistemas de distribución'
            },
            {
                'nombre': 'Bomba Centrífuga 150m³/h',
                'categoria': 'Bombas Centrífugas',
                'marca': 'Grundfos',
                'modelo': 'CR-150-2-2',
                'potencia': Decimal('45.00'),
                'serie': 'GRU-2024-002',
                'desc': 'Bomba de mayor capacidad'
            },
            {
                'nombre': 'Válvula de Compuerta 150mm',
                'categoria': 'Válvulas',
                'marca': 'Watts',
                'modelo': 'WC-150',
                'serie': 'WAT-2024-001',
                'desc': 'Válvula de control de flujo'
            },
            {
                'nombre': 'Válvula de Compuerta 200mm',
                'categoria': 'Válvulas',
                'marca': 'Watts',
                'modelo': 'WC-200',
                'serie': 'WAT-2024-002',
                'desc': 'Válvula de mayor diámetro'
            },
            {
                'nombre': 'Compresor de Aire 10 HP',
                'categoria': 'Compresores',
                'marca': 'Atlas Copco',
                'modelo': 'GA-10',
                'potencia': Decimal('10.00'),
                'serie': 'ATC-2024-001',
                'desc': 'Compresor para sistemas neumáticos'
            },
            {
                'nombre': 'Generador Diesel 50 kW',
                'categoria': 'Generadores',
                'marca': 'Caterpillar',
                'modelo': 'C50',
                'potencia': Decimal('50.00'),
                'serie': 'CAT-2024-001',
                'desc': 'Generador de emergencia'
            },
            {
                'nombre': 'Transformador 100 kVA',
                'categoria': 'Transformadores',
                'marca': 'Siemens',
                'modelo': 'SIEMENS-100',
                'serie': 'SIE-TRANS-001',
                'desc': 'Transformador de distribución'
            },
            {
                'nombre': 'Filtro de Arena 50 micras',
                'categoria': 'Filtros',
                'marca': 'Pentair',
                'modelo': 'FIL-50',
                'serie': 'PEN-2024-001',
                'desc': 'Filtro para tratamiento de agua'
            },
        ]
        
        equipos = {}
        for eq_data in equipos_data:
            equipo, created = Equipo.objects.get_or_create(
                numero_serie=eq_data['serie'],
                defaults={
                    'nombre': eq_data['nombre'],
                    'descripcion': eq_data['desc'],
                    'categoria': categorias[eq_data['categoria']],
                    'marca': eq_data['marca'],
                    'modelo': eq_data['modelo'],
                    'potencia_hp': eq_data.get('potencia'),
                }
            )
            equipos[eq_data['nombre']] = equipo
            self.stdout.write(f"{'✓' if created else '→'} Equipo: {equipo.nombre}")
        
        # Crear stock inicial
        self.stdout.write(self.style.SUCCESS('\n📦 Creando stock inicial...'))
        
        stock_tuberias_data = [
            ('Tubería PVC 100mm - Agua Potable', 'Sistema de Bombeo Principal', 50),
            ('Tubería PVC 100mm - Agua Potable', 'Sistema de Distribución Secundario', 30),
            ('Tubería PVC 75mm - Agua Potable', 'Sistema de Bombeo Principal', 40),
            ('Tubería Hierro Dúctil 150mm - Aguas Servidas', 'Sistema de Bombeo Principal', 25),
            ('Tubería Hierro Dúctil 200mm - Aguas Servidas', 'Sistema de Tratamiento', 20),
            ('Tubería Cemento 200mm - Riego', 'Sistema Auxiliar de Bombeo', 35),
            ('Tubería Cemento 250mm - Riego', 'Sistema Auxiliar de Bombeo', 15),
        ]
        
        for tub_nombre, acueducto_nombre, cantidad in stock_tuberias_data:
            stock, created = StockTuberia.objects.get_or_create(
                tuberia=tuberias[tub_nombre],
                acueducto=acueductos[acueducto_nombre],
                defaults={'cantidad': cantidad}
            )
            if created:
                self.stdout.write(f"✓ Stock Tubería: {tub_nombre} @ {acueducto_nombre} = {cantidad}")
        
        stock_equipos_data = [
            ('Motor de Bombeo Centrífugo 50 HP', 'Sistema de Bombeo Principal', 3),
            ('Motor de Bombeo Centrífugo 75 HP', 'Sistema de Bombeo Principal', 2),
            ('Motor de Bombeo Centrífugo 100 HP', 'Sistema de Bombeo Orinoco', 1),
            ('Bomba Centrífuga 100m³/h', 'Sistema de Bombeo Principal', 5),
            ('Bomba Centrífuga 150m³/h', 'Sistema de Tratamiento', 3),
            ('Válvula de Compuerta 150mm', 'Sistema de Bombeo Principal', 8),
            ('Válvula de Compuerta 200mm', 'Sistema de Distribución Secundario', 6),
            ('Compresor de Aire 10 HP', 'Sistema de Emergencia', 2),
            ('Generador Diesel 50 kW', 'Sistema de Emergencia', 1),
            ('Transformador 100 kVA', 'Sistema de Bombeo Principal', 2),
            ('Filtro de Arena 50 micras', 'Sistema de Tratamiento', 10),
        ]
        
        for eq_nombre, acueducto_nombre, cantidad in stock_equipos_data:
            stock, created = StockEquipo.objects.get_or_create(
                equipo=equipos[eq_nombre],
                acueducto=acueductos[acueducto_nombre],
                defaults={'cantidad': cantidad}
            )
            if created:
                self.stdout.write(f"✓ Stock Equipo: {eq_nombre} @ {acueducto_nombre} = {cantidad}")
        
        # Crear alertas de stock bajo
        self.stdout.write(self.style.SUCCESS('\n🚨 Creando alertas de stock bajo...'))
        
        alertas_data = [
            ('Tubería PVC 100mm - Agua Potable', 'Sistema de Bombeo Principal', 20, True),
            ('Motor de Bombeo Centrífugo 50 HP', 'Sistema de Bombeo Principal', 1, True),
            ('Bomba Centrífuga 100m³/h', 'Sistema de Bombeo Principal', 2, True),
            ('Válvula de Compuerta 150mm', 'Sistema de Bombeo Principal', 3, True),
        ]
        
        for item_nombre, acueducto_nombre, umbral, activo in alertas_data:
            if item_nombre in tuberias:
                alerta, created = AlertaStock.objects.get_or_create(
                    tuberia=tuberias[item_nombre],
                    acueducto=acueductos[acueducto_nombre],
                    defaults={'umbral_minimo': umbral, 'activo': activo}
                )
                if created:
                    self.stdout.write(f"✓ Alerta: {item_nombre} <= {umbral}")
            elif item_nombre in equipos:
                alerta, created = AlertaStock.objects.get_or_create(
                    equipo=equipos[item_nombre],
                    acueducto=acueductos[acueducto_nombre],
                    defaults={'umbral_minimo': umbral, 'activo': activo}
                )
                if created:
                    self.stdout.write(f"✓ Alerta: {item_nombre} <= {umbral}")
        
        # Crear usuarios de prueba
        self.stdout.write(self.style.SUCCESS('\n👥 Creando usuarios de prueba...'))
        
        usuarios_data = [
            {'username': 'admin_test', 'email': 'admin@test.com', 'role': 'ADMIN'},
            {'username': 'operador_test', 'email': 'operador@test.com', 'role': 'OPERADOR'},
            {'username': 'supervisor_test', 'email': 'supervisor@test.com', 'role': 'OPERADOR'},
        ]
        
        for user_data in usuarios_data:
            user, created = User.objects.get_or_create(
                username=user_data['username'],
                defaults={
                    'email': user_data['email'],
                    'role': user_data['role'],
                }
            )
            if created:
                user.set_password('testpass123')
                user.save()
                self.stdout.write(f"✓ Usuario: {user.username} ({user.role})")
        
        self.stdout.write(self.style.SUCCESS('\n✅ ¡Datos de prueba generados exitosamente!'))
        self.stdout.write(self.style.WARNING('\n📝 Credenciales de prueba:'))
        self.stdout.write('   Admin: admin_test / testpass123')
        self.stdout.write('   Operador: operador_test / testpass123')
