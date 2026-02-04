"""
Management command to set up the initial Hidroven organizational hierarchy.

This command creates the basic organizational structure as specified in the design document:
- Hidroven (root company)
- Three Vicepresidencias (Comercialización, Operaciones Hídricas, Administrativa)
- Sample organizational units under each VP

Usage:
    python manage.py setup_hidroven_hierarchy
"""

from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from django.contrib.auth import get_user_model
from institucion.models import Empresa, Vicepresidencia, UnidadOrganizacional, AlmacenRegional

User = get_user_model()


class Command(BaseCommand):
    help = 'Set up the initial Hidroven organizational hierarchy'

    def add_arguments(self, parser):
        parser.add_argument(
            '--reset',
            action='store_true',
            help='Reset existing hierarchy (delete all and recreate)',
        )

    def handle(self, *args, **options):
        """Execute the command"""
        try:
            with transaction.atomic():
                if options['reset']:
                    self.stdout.write(
                        self.style.WARNING('Resetting existing hierarchy...')
                    )
                    self._reset_hierarchy()

                self._create_hierarchy()
                
                self.stdout.write(
                    self.style.SUCCESS(
                        'Successfully set up Hidroven organizational hierarchy!'
                    )
                )
                
        except Exception as e:
            raise CommandError(f'Error setting up hierarchy: {str(e)}')

    def _reset_hierarchy(self):
        """Reset existing hierarchy"""
        # Delete in reverse order to avoid foreign key constraints
        AlmacenRegional.objects.all().delete()
        UnidadOrganizacional.objects.all().delete()
        Vicepresidencia.objects.all().delete()
        Empresa.objects.all().delete()
        
        self.stdout.write('Existing hierarchy deleted.')

    def _create_hierarchy(self):
        """Create the Hidroven organizational hierarchy"""
        
        # 1. Create root company - Hidroven
        hidroven, created = Empresa.objects.get_or_create(
            codigo='HDV',
            defaults={
                'nombre': 'Hidroven',
                'rif': 'G-20000000-0',
                'direccion': 'Caracas, Venezuela',
                'telefono': '+58-212-1234567',
                'email': 'info@hidroven.gob.ve',
                'activo': True
            }
        )
        
        if created:
            self.stdout.write(f'Created empresa: {hidroven.nombre}')
        else:
            self.stdout.write(f'Empresa already exists: {hidroven.nombre}')

        # 2. Create the three Vicepresidencias
        vicepresidencias_data = [
            {
                'codigo': 'VP-COM',
                'nombre': 'Vicepresidencia de Comercialización',
                'tipo': 'COMERCIALIZACION',
                'descripcion': 'Responsable de la comercialización y facturación de servicios de agua'
            },
            {
                'codigo': 'VP-OH',
                'nombre': 'Vicepresidencia de Operaciones Hídricas',
                'tipo': 'OPERACIONES_HIDRICAS',
                'descripcion': 'Responsable de las operaciones técnicas y mantenimiento de infraestructura hídrica'
            },
            {
                'codigo': 'VP-ADM',
                'nombre': 'Vicepresidencia Administrativa',
                'tipo': 'ADMINISTRATIVA',
                'descripcion': 'Responsable de la administración, recursos humanos y finanzas'
            }
        ]

        vicepresidencias = {}
        for vp_data in vicepresidencias_data:
            vp, created = Vicepresidencia.objects.get_or_create(
                empresa=hidroven,
                codigo=vp_data['codigo'],
                defaults={
                    'nombre': vp_data['nombre'],
                    'tipo': vp_data['tipo'],
                    'descripcion': vp_data['descripcion'],
                    'activo': True
                }
            )
            vicepresidencias[vp_data['tipo']] = vp
            
            if created:
                self.stdout.write(f'Created VP: {vp.nombre}')
            else:
                self.stdout.write(f'VP already exists: {vp.nombre}')

        # 3. Create organizational units under each VP
        self._create_comercializacion_units(vicepresidencias['COMERCIALIZACION'])
        self._create_operaciones_units(vicepresidencias['OPERACIONES_HIDRICAS'])
        self._create_administrativa_units(vicepresidencias['ADMINISTRATIVA'])

    def _create_comercializacion_units(self, vp_comercializacion):
        """Create organizational units under VP Comercialización"""
        units_data = [
            {
                'codigo': 'GER-COM-FAC',
                'nombre': 'Gerencia de Facturación',
                'tipo': 'GERENCIA',
                'descripcion': 'Responsable de la facturación de servicios'
            },
            {
                'codigo': 'GER-COM-REC',
                'nombre': 'Gerencia de Recaudación',
                'tipo': 'GERENCIA',
                'descripcion': 'Responsable de la recaudación de pagos'
            },
            {
                'codigo': 'GER-COM-ATC',
                'nombre': 'Gerencia de Atención al Cliente',
                'tipo': 'GERENCIA',
                'descripcion': 'Responsable de la atención y servicio al cliente'
            }
        ]
        
        self._create_units(vp_comercializacion, units_data, 'Comercialización')

    def _create_operaciones_units(self, vp_operaciones):
        """Create organizational units under VP Operaciones Hídricas"""
        units_data = [
            {
                'codigo': 'GER-OP-ALM',
                'nombre': 'Gerencia de Almacenes',
                'tipo': 'GERENCIA',
                'descripcion': 'Responsable de la gestión de almacenes regionales'
            },
            {
                'codigo': 'GER-OP-MAN',
                'nombre': 'Gerencia de Mantenimiento',
                'tipo': 'GERENCIA',
                'descripcion': 'Responsable del mantenimiento de infraestructura'
            },
            {
                'codigo': 'GER-OP-PRO',
                'nombre': 'Gerencia de Producción',
                'tipo': 'GERENCIA',
                'descripcion': 'Responsable de la producción y tratamiento de agua'
            },
            {
                'codigo': 'GER-OP-DIS',
                'nombre': 'Gerencia de Distribución',
                'tipo': 'GERENCIA',
                'descripcion': 'Responsable de la distribución de agua'
            }
        ]
        
        gerencias = self._create_units(vp_operaciones, units_data, 'Operaciones Hídricas')
        
        # Create regional warehouses under Gerencia de Almacenes
        if 'GER-OP-ALM' in gerencias:
            self._create_regional_warehouses(gerencias['GER-OP-ALM'])

    def _create_administrativa_units(self, vp_administrativa):
        """Create organizational units under VP Administrativa"""
        units_data = [
            {
                'codigo': 'GER-ADM-RH',
                'nombre': 'Gerencia de Recursos Humanos',
                'tipo': 'GERENCIA',
                'descripcion': 'Responsable de la gestión del talento humano'
            },
            {
                'codigo': 'GER-ADM-FIN',
                'nombre': 'Gerencia de Finanzas',
                'tipo': 'GERENCIA',
                'descripcion': 'Responsable de la gestión financiera'
            },
            {
                'codigo': 'GER-ADM-TEC',
                'nombre': 'Gerencia de Tecnología',
                'tipo': 'GERENCIA',
                'descripcion': 'Responsable de la infraestructura tecnológica'
            },
            {
                'codigo': 'GER-ADM-JUR',
                'nombre': 'Gerencia Jurídica',
                'tipo': 'GERENCIA',
                'descripcion': 'Responsable de los asuntos legales'
            }
        ]
        
        self._create_units(vp_administrativa, units_data, 'Administrativa')

    def _create_units(self, vicepresidencia, units_data, vp_name):
        """Create organizational units under a vicepresidencia"""
        created_units = {}
        
        for unit_data in units_data:
            unit, created = UnidadOrganizacional.objects.get_or_create(
                vicepresidencia=vicepresidencia,
                codigo=unit_data['codigo'],
                defaults={
                    'nombre': unit_data['nombre'],
                    'tipo': unit_data['tipo'],
                    'descripcion': unit_data['descripcion'],
                    'activo': True
                }
            )
            created_units[unit_data['codigo']] = unit
            
            if created:
                self.stdout.write(f'Created unit under VP {vp_name}: {unit.nombre}')
            else:
                self.stdout.write(f'Unit already exists under VP {vp_name}: {unit.nombre}')
        
        return created_units

    def _create_regional_warehouses(self, gerencia_almacenes):
        """Create the 9 regional warehouses under Gerencia de Almacenes"""
        warehouses_data = [
            {
                'codigo': 'ALM-ZUL', 
                'nombre': 'Almacén Regional Zulia', 
                'ubicacion': 'Maracaibo, Zulia',
                'prefijo': 'ZUL'
            },
            {
                'codigo': 'ALM-CAR', 
                'nombre': 'Almacén Regional Carabobo', 
                'ubicacion': 'Valencia, Carabobo',
                'prefijo': 'CAR'
            },
            {
                'codigo': 'ALM-MIR', 
                'nombre': 'Almacén Regional Miranda', 
                'ubicacion': 'Los Teques, Miranda',
                'prefijo': 'MIR'
            },
            {
                'codigo': 'ALM-ARA', 
                'nombre': 'Almacén Regional Aragua', 
                'ubicacion': 'Maracay, Aragua',
                'prefijo': 'ARA'
            },
            {
                'codigo': 'ALM-LAR', 
                'nombre': 'Almacén Regional Lara', 
                'ubicacion': 'Barquisimeto, Lara',
                'prefijo': 'LAR'
            },
            {
                'codigo': 'ALM-TAC', 
                'nombre': 'Almacén Regional Táchira', 
                'ubicacion': 'San Cristóbal, Táchira',
                'prefijo': 'TAC'
            },
            {
                'codigo': 'ALM-BOL', 
                'nombre': 'Almacén Regional Bolívar', 
                'ubicacion': 'Ciudad Bolívar, Bolívar',
                'prefijo': 'BOL'
            },
            {
                'codigo': 'ALM-ANZ', 
                'nombre': 'Almacén Regional Anzoátegui', 
                'ubicacion': 'Barcelona, Anzoátegui',
                'prefijo': 'ANZ'
            },
            {
                'codigo': 'ALM-MON', 
                'nombre': 'Almacén Regional Monagas', 
                'ubicacion': 'Maturín, Monagas',
                'prefijo': 'MON'
            }
        ]
        
        for warehouse_data in warehouses_data:
            # Create the organizational unit first
            unidad_organizacional, created = UnidadOrganizacional.objects.get_or_create(
                vicepresidencia=gerencia_almacenes.vicepresidencia,
                codigo=warehouse_data['codigo'],
                defaults={
                    'nombre': warehouse_data['nombre'],
                    'tipo': 'ALMACEN',
                    'descripcion': f'Unidad organizacional para {warehouse_data["nombre"]}',
                    'ubicacion': warehouse_data['ubicacion'],
                    'parent': gerencia_almacenes,
                    'activo': True
                }
            )
            
            if created:
                self.stdout.write(f'Created organizational unit: {unidad_organizacional.nombre}')
            else:
                self.stdout.write(f'Organizational unit already exists: {unidad_organizacional.nombre}')
            
            # Create the AlmacenRegional instance
            almacen_regional, created = AlmacenRegional.objects.get_or_create(
                prefijo=warehouse_data['prefijo'],
                defaults={
                    'unidad_organizacional': unidad_organizacional,
                    'nombre': warehouse_data['nombre'],
                    'ubicacion': warehouse_data['ubicacion'],
                    'capacidad_maxima': 10000,  # Default capacity
                    'activo': True,
                    'descripcion': f'Almacén regional para la gestión de inventario en {warehouse_data["ubicacion"]}',
                }
            )
            
            if created:
                self.stdout.write(f'Created regional warehouse: {almacen_regional.nombre} ({almacen_regional.prefijo})')
            else:
                self.stdout.write(f'Regional warehouse already exists: {almacen_regional.nombre} ({almacen_regional.prefijo})')