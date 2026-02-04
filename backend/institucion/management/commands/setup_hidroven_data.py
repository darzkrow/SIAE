"""
Management command to set up initial Hidroven organizational structure and warehouses.
"""

from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group
from django.db import transaction

from institucion.models import Empresa, Vicepresidencia, UnidadOrganizacional, AlmacenRegional


class Command(BaseCommand):
    help = 'Set up initial Hidroven organizational structure and regional warehouses'

    def add_arguments(self, parser):
        parser.add_argument(
            '--force',
            action='store_true',
            help='Force recreation of data (will delete existing data)',
        )

    def handle(self, *args, **options):
        force = options['force']
        
        if force:
            self.stdout.write(
                self.style.WARNING('Deleting existing organizational data...')
            )
            AlmacenRegional.objects.all().delete()
            UnidadOrganizacional.objects.all().delete()
            Vicepresidencia.objects.all().delete()
            Empresa.objects.all().delete()

        with transaction.atomic():
            # Create Hidroven company
            empresa, created = Empresa.objects.get_or_create(
                codigo='HV',
                defaults={
                    'nombre': 'Hidroven',
                    'rif': 'G-20000001-0',
                    'direccion': 'Caracas, Venezuela',
                    'telefono': '+58-212-555-0000',
                    'email': 'info@hidroven.gob.ve',
                    'activo': True
                }
            )
            
            if created:
                self.stdout.write(
                    self.style.SUCCESS(f'Created company: {empresa.nombre}')
                )
            else:
                self.stdout.write(f'Company already exists: {empresa.nombre}')

            # Create Vicepresidencias
            vicepresidencias_data = [
                {
                    'codigo': 'VOH',
                    'nombre': 'Vicepresidencia de Operaciones Hídricas',
                    'tipo': 'OPERACIONES_HIDRICAS'
                },
                {
                    'codigo': 'VCO',
                    'nombre': 'Vicepresidencia de Comercialización',
                    'tipo': 'COMERCIALIZACION'
                },
                {
                    'codigo': 'VAD',
                    'nombre': 'Vicepresidencia Administrativa',
                    'tipo': 'ADMINISTRATIVA'
                }
            ]
            
            vicepresidencias = {}
            for vp_data in vicepresidencias_data:
                vp, created = Vicepresidencia.objects.get_or_create(
                    codigo=vp_data['codigo'],
                    defaults={
                        'nombre': vp_data['nombre'],
                        'tipo': vp_data['tipo'],
                        'empresa': empresa,
                        'activo': True
                    }
                )
                vicepresidencias[vp_data['codigo']] = vp
                
                if created:
                    self.stdout.write(
                        self.style.SUCCESS(f'Created VP: {vp.nombre}')
                    )
                else:
                    self.stdout.write(f'VP already exists: {vp.nombre}')

            # Create Unidades Organizacionales under VP Operaciones Hídricas
            vp_operaciones = vicepresidencias['VOH']
            
            unidades_data = [
                {
                    'codigo': 'UORO',
                    'nombre': 'Unidad de Operaciones Región Occidental'
                },
                {
                    'codigo': 'UORC',
                    'nombre': 'Unidad de Operaciones Región Central'
                },
                {
                    'codigo': 'UORI',
                    'nombre': 'Unidad de Operaciones Región Oriental'
                }
            ]
            
            unidades = {}
            for unidad_data in unidades_data:
                unidad, created = UnidadOrganizacional.objects.get_or_create(
                    codigo=unidad_data['codigo'],
                    defaults={
                        'nombre': unidad_data['nombre'],
                        'vicepresidencia': vp_operaciones,
                        'activo': True
                    }
                )
                unidades[unidad_data['codigo']] = unidad
                
                if created:
                    self.stdout.write(
                        self.style.SUCCESS(f'Created Unit: {unidad.nombre}')
                    )
                else:
                    self.stdout.write(f'Unit already exists: {unidad.nombre}')

            # Create 9 Regional Warehouses
            almacenes_data = [
                {
                    'prefijo': 'ZUL',
                    'nombre': 'Almacén Regional Zulia',
                    'unidad': 'UORO',
                    'capacidad': 5000,
                    'ubicacion': 'Maracaibo, Estado Zulia'
                },
                {
                    'prefijo': 'CAR',
                    'nombre': 'Almacén Regional Caracas',
                    'unidad': 'UORC',
                    'capacidad': 8000,
                    'ubicacion': 'Caracas, Distrito Capital'
                },
                {
                    'prefijo': 'MIR',
                    'nombre': 'Almacén Regional Miranda',
                    'unidad': 'UORC',
                    'capacidad': 4500,
                    'ubicacion': 'Los Teques, Estado Miranda'
                },
                {
                    'prefijo': 'ARA',
                    'nombre': 'Almacén Regional Aragua',
                    'unidad': 'UORC',
                    'capacidad': 3500,
                    'ubicacion': 'Maracay, Estado Aragua'
                },
                {
                    'prefijo': 'LAR',
                    'nombre': 'Almacén Regional Lara',
                    'unidad': 'UORO',
                    'capacidad': 3000,
                    'ubicacion': 'Barquisimeto, Estado Lara'
                },
                {
                    'prefijo': 'TAC',
                    'nombre': 'Almacén Regional Táchira',
                    'unidad': 'UORO',
                    'capacidad': 2500,
                    'ubicacion': 'San Cristóbal, Estado Táchira'
                },
                {
                    'prefijo': 'BOL',
                    'nombre': 'Almacén Regional Bolívar',
                    'unidad': 'UORI',
                    'capacidad': 4000,
                    'ubicacion': 'Ciudad Bolívar, Estado Bolívar'
                },
                {
                    'prefijo': 'ANZ',
                    'nombre': 'Almacén Regional Anzoátegui',
                    'unidad': 'UORI',
                    'capacidad': 3500,
                    'ubicacion': 'Barcelona, Estado Anzoátegui'
                },
                {
                    'prefijo': 'MON',
                    'nombre': 'Almacén Regional Monagas',
                    'unidad': 'UORI',
                    'capacidad': 2800,
                    'ubicacion': 'Maturín, Estado Monagas'
                }
            ]
            
            for almacen_data in almacenes_data:
                almacen, created = AlmacenRegional.objects.get_or_create(
                    prefijo=almacen_data['prefijo'],
                    defaults={
                        'nombre': almacen_data['nombre'],
                        'unidad_organizacional': unidades[almacen_data['unidad']],
                        'capacidad_maxima': almacen_data['capacidad'],
                        'ubicacion': almacen_data['ubicacion'],
                        'activo': True
                    }
                )
                
                if created:
                    self.stdout.write(
                        self.style.SUCCESS(f'Created Warehouse: {almacen.nombre} ({almacen.prefijo})')
                    )
                else:
                    self.stdout.write(f'Warehouse already exists: {almacen.nombre} ({almacen.prefijo})')

            # Create permission groups
            groups_data = [
                'Administradores Hidroven',
                'Gerentes Regionales',
                'Supervisores de Almacén',
                'Operadores de Inventario',
                'Auditores',
                'Aprobadores de Transferencias'
            ]
            
            for group_name in groups_data:
                group, created = Group.objects.get_or_create(name=group_name)
                
                if created:
                    self.stdout.write(
                        self.style.SUCCESS(f'Created group: {group.name}')
                    )
                else:
                    self.stdout.write(f'Group already exists: {group.name}')

        self.stdout.write(
            self.style.SUCCESS('Successfully set up Hidroven organizational structure!')
        )
        
        # Display summary
        self.stdout.write('\n' + '='*50)
        self.stdout.write('SUMMARY:')
        self.stdout.write(f'Companies: {Empresa.objects.count()}')
        self.stdout.write(f'Vicepresidencias: {Vicepresidencia.objects.count()}')
        self.stdout.write(f'Organizational Units: {UnidadOrganizacional.objects.count()}')
        self.stdout.write(f'Regional Warehouses: {AlmacenRegional.objects.count()}')
        self.stdout.write(f'Permission Groups: {Group.objects.count()}')
        self.stdout.write('='*50)