"""
Management command to demonstrate migration support functionality.

This command creates sample data and demonstrates the migration workflow
from old organizational structure to new hierarchical structure.
"""

from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.db import transaction
from django.utils import timezone

from institucion.models import (
    # Old structure
    OrganizacionCentral, Sucursal, Acueducto,
    # New structure
    Empresa, Vicepresidencia, UnidadOrganizacional, AlmacenRegional,
    # Migration support
    MigracionOrganizacional, AcueductoNuevo
)

User = get_user_model()


class Command(BaseCommand):
    help = 'Demonstrate migration support functionality with sample data'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--cleanup',
            action='store_true',
            help='Clean up demo data before creating new data',
        )
        parser.add_argument(
            '--show-status',
            action='store_true',
            help='Show migration status without creating data',
        )
    
    def handle(self, *args, **options):
        if options['show_status']:
            self.show_migration_status()
            return
        
        if options['cleanup']:
            self.cleanup_demo_data()
        
        self.stdout.write(
            self.style.SUCCESS('🚀 Starting Migration Support Demo')
        )
        
        try:
            with transaction.atomic():
                # Create demo data
                user = self.create_demo_user()
                old_structure = self.create_old_structure()
                new_structure = self.create_new_structure(user)
                
                # Demonstrate migration workflow
                self.demonstrate_migration_workflow(
                    old_structure, new_structure, user
                )
                
                # Show results
                self.show_migration_results()
                
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'❌ Error during demo: {str(e)}')
            )
            raise
        
        self.stdout.write(
            self.style.SUCCESS('✅ Migration Support Demo completed successfully!')
        )
    
    def create_demo_user(self):
        """Create or get demo user"""
        user, created = User.objects.get_or_create(
            username='migration_demo',
            defaults={
                'email': 'migration@demo.com',
                'first_name': 'Migration',
                'last_name': 'Demo'
            }
        )
        
        if created:
            user.set_password('demo123')
            user.save()
            self.stdout.write('👤 Created demo user')
        else:
            self.stdout.write('👤 Using existing demo user')
        
        return user
    
    def create_old_structure(self):
        """Create old organizational structure"""
        self.stdout.write('🏢 Creating old organizational structure...')
        
        # Create OrganizacionCentral
        org_central, created = OrganizacionCentral.objects.get_or_create(
            nombre='Hidroven Central Demo',
            defaults={'rif': 'J-12345678-9'}
        )
        
        # Create Sucursal
        sucursal, created = Sucursal.objects.get_or_create(
            nombre='Sucursal Zulia Demo',
            organizacion_central=org_central,
            defaults={
                'codigo': 'SUC-ZUL-DEMO',
                'direccion': 'Maracaibo, Zulia',
                'telefono': '0261-1234567'
            }
        )
        
        # Create Acueductos
        acueductos = []
        acueducto_data = [
            ('Acueducto Maracaibo Norte Demo', 'ACU-MAR-N-DEMO', 'Maracaibo Norte'),
            ('Acueducto Maracaibo Sur Demo', 'ACU-MAR-S-DEMO', 'Maracaibo Sur'),
            ('Sistema Bombeo La Concepción Demo', 'SIS-BOM-LC-DEMO', 'La Concepción'),
        ]
        
        for nombre, codigo, ubicacion in acueducto_data:
            acueducto, created = Acueducto.objects.get_or_create(
                nombre=nombre,
                sucursal=sucursal,
                defaults={
                    'codigo': codigo,
                    'ubicacion': ubicacion
                }
            )
            acueductos.append(acueducto)
        
        self.stdout.write(
            f'  ✓ Created: 1 OrganizacionCentral, 1 Sucursal, {len(acueductos)} Acueductos'
        )
        
        return {
            'organizacion_central': org_central,
            'sucursal': sucursal,
            'acueductos': acueductos
        }
    
    def create_new_structure(self, user):
        """Create new hierarchical structure"""
        self.stdout.write('🏗️ Creating new hierarchical structure...')
        
        # Create Empresa
        empresa, created = Empresa.objects.get_or_create(
            nombre='Hidroven Demo',
            defaults={'codigo': 'HIDROVEN-DEMO'}
        )
        
        # Create Vicepresidencia
        vicepresidencia, created = Vicepresidencia.objects.get_or_create(
            empresa=empresa,
            tipo='OPERACIONES_HIDRICAS',
            defaults={
                'nombre': 'VP Operaciones Hídricas Demo',
                'codigo': 'VP-OPE-DEMO',
                'descripcion': 'Vicepresidencia de Operaciones Hídricas para demo'
            }
        )
        
        # Create UnidadOrganizacional
        unidad_organizacional, created = UnidadOrganizacional.objects.get_or_create(
            vicepresidencia=vicepresidencia,
            codigo='GER-ZUL-DEMO',
            defaults={
                'nombre': 'Gerencia Regional Zulia Demo',
                'tipo': 'GERENCIA',
                'descripcion': 'Gerencia Regional para el estado Zulia - Demo',
                'ubicacion': 'Maracaibo, Zulia'
            }
        )
        
        # Create AlmacenRegional
        almacen_regional, created = AlmacenRegional.objects.get_or_create(
            prefijo='ZUL',
            defaults={
                'unidad_organizacional': unidad_organizacional,
                'nombre': 'Almacén Regional Zulia Demo',
                'ubicacion': 'Maracaibo, Zulia',
                'manager': user,
                'capacidad_maxima': 5000,
                'descripcion': 'Almacén regional para demo de migración'
            }
        )
        
        # Create AcueductoNuevo
        acueductos_nuevos = []
        acueducto_data = [
            ('Acueducto Maracaibo Norte Nuevo', 'ACU-MAR-N-NEW', 'ACUEDUCTO'),
            ('Acueducto Maracaibo Sur Nuevo', 'ACU-MAR-S-NEW', 'ACUEDUCTO'),
            ('Sistema Bombeo La Concepción Nuevo', 'SIS-BOM-LC-NEW', 'SISTEMA_BOMBEO'),
        ]
        
        for nombre, codigo, tipo_sistema in acueducto_data:
            acueducto_nuevo, created = AcueductoNuevo.objects.get_or_create(
                unidad_organizacional=unidad_organizacional,
                codigo=codigo,
                defaults={
                    'nombre': nombre,
                    'tipo_sistema': tipo_sistema,
                    'responsable_operativo': user,
                    'ubicacion': 'Maracaibo, Zulia',
                    'capacidad_produccion': 1000.0,
                    'poblacion_servida': 50000,
                    'creado_por': user
                }
            )
            acueductos_nuevos.append(acueducto_nuevo)
        
        self.stdout.write(
            f'  ✓ Created: 1 Empresa, 1 Vicepresidencia, 1 UnidadOrganizacional, '
            f'1 AlmacenRegional, {len(acueductos_nuevos)} AcueductosNuevos'
        )
        
        return {
            'empresa': empresa,
            'vicepresidencia': vicepresidencia,
            'unidad_organizacional': unidad_organizacional,
            'almacen_regional': almacen_regional,
            'acueductos_nuevos': acueductos_nuevos
        }
    
    def demonstrate_migration_workflow(self, old_structure, new_structure, user):
        """Demonstrate complete migration workflow"""
        self.stdout.write('🔄 Demonstrating migration workflow...')
        
        # 1. Create migration for OrganizacionCentral
        self.stdout.write('  📋 Creating migration for OrganizacionCentral...')
        migracion_org = MigracionOrganizacional.crear_migracion_organizacion(
            organizacion_central=old_structure['organizacion_central'],
            empresa=new_structure['empresa'],
            usuario=user
        )
        self.stdout.write(f'    ✓ Created migration {migracion_org.id}')
        
        # 2. Create migration for Sucursal
        self.stdout.write('  📋 Creating migration for Sucursal...')
        migracion_sucursal = MigracionOrganizacional.crear_migracion_sucursal(
            sucursal=old_structure['sucursal'],
            vicepresidencia=new_structure['vicepresidencia'],
            usuario=user
        )
        self.stdout.write(f'    ✓ Created migration {migracion_sucursal.id}')
        
        # 3. Create migrations for Acueductos
        self.stdout.write('  📋 Creating migrations for Acueductos...')
        migraciones_acueductos = []
        for i, acueducto_old in enumerate(old_structure['acueductos']):
            migracion_acueducto = MigracionOrganizacional.crear_migracion_acueducto(
                acueducto=acueducto_old,
                unidad_organizacional=new_structure['unidad_organizacional'],
                usuario=user
            )
            
            # Link to new acueducto
            if i < len(new_structure['acueductos_nuevos']):
                migracion_acueducto.acueducto_nuevo = new_structure['acueductos_nuevos'][i]
                migracion_acueducto.save()
            
            migraciones_acueductos.append(migracion_acueducto)
            self.stdout.write(f'    ✓ Created migration {migracion_acueducto.id}')
        
        # 4. Complete migrations
        self.stdout.write('  ✅ Completing migrations...')
        all_migrations = [migracion_org, migracion_sucursal] + migraciones_acueductos
        
        for migracion in all_migrations:
            migracion.marcar_como_completada(user)
            self.stdout.write(f'    ✓ Completed migration {migracion.id}')
        
        # 5. Validate migrations
        self.stdout.write('  ✔️ Validating migrations...')
        for migracion in all_migrations:
            migracion.validar_migracion(user)
            self.stdout.write(f'    ✓ Validated migration {migracion.id}')
        
        # 6. Demonstrate error handling
        self.stdout.write('  ⚠️ Demonstrating error handling...')
        migracion_org.agregar_warning('This is a demo warning')
        migracion_sucursal.agregar_error('This is a demo error (non-critical)')
        
        # 7. Demonstrate rollback (on one migration)
        self.stdout.write('  ↩️ Demonstrating rollback...')
        if migraciones_acueductos:
            migracion_to_rollback = migraciones_acueductos[-1]
            migracion_to_rollback.revertir_migracion(
                user, 
                'Demo rollback - testing rollback functionality'
            )
            self.stdout.write(f'    ✓ Rolled back migration {migracion_to_rollback.id}')
        
        self.stdout.write('  🎯 Migration workflow demonstration completed!')
    
    def show_migration_results(self):
        """Show migration results and statistics"""
        self.stdout.write('📊 Migration Results:')
        
        # Get statistics
        resultado = MigracionOrganizacional.validar_integridad_migracion()
        
        self.stdout.write(f'  📈 Total migrations: {resultado["total_migraciones"]}')
        self.stdout.write(f'  ✅ Completed: {resultado["completadas"]}')
        self.stdout.write(f'  ⏳ Pending: {resultado["pendientes"]}')
        self.stdout.write(f'  ❌ Failed: {resultado["fallidas"]}')
        self.stdout.write(f'  ↩️ Reverted: {MigracionOrganizacional.objects.filter(estado_migracion="REVERTIDA").count()}')
        
        if resultado['warnings']:
            self.stdout.write('  ⚠️ Warnings:')
            for warning in resultado['warnings'][:5]:  # Show first 5
                self.stdout.write(f'    - {warning}')
        
        if resultado['errores']:
            self.stdout.write('  🚨 Errors:')
            for error in resultado['errores'][:5]:  # Show first 5
                self.stdout.write(f'    - {error}')
        
        # Show recent migrations
        self.stdout.write('  📋 Recent migrations:')
        recent_migrations = MigracionOrganizacional.objects.order_by('-fecha_migracion')[:5]
        
        for migracion in recent_migrations:
            status_icon = {
                'PENDIENTE': '⏳',
                'EN_PROCESO': '🔄',
                'COMPLETADA': '✅',
                'FALLIDA': '❌',
                'REVERTIDA': '↩️'
            }.get(migracion.estado_migracion, '❓')
            
            self.stdout.write(
                f'    {status_icon} {migracion.id}: {migracion.get_old_reference_display()[:50]}... '
                f'→ {migracion.get_new_reference_display()[:50]}...'
            )
    
    def show_migration_status(self):
        """Show current migration status"""
        self.stdout.write(self.style.SUCCESS('📊 Current Migration Status'))
        
        resultado = MigracionOrganizacional.validar_integridad_migracion()
        
        self.stdout.write(f'Total migrations: {resultado["total_migraciones"]}')
        self.stdout.write(f'Completed: {resultado["completadas"]}')
        self.stdout.write(f'Pending: {resultado["pendientes"]}')
        self.stdout.write(f'Failed: {resultado["fallidas"]}')
        
        # Show migrations by type
        self.stdout.write('\nMigrations by type:')
        
        org_migrations = MigracionOrganizacional.objects.filter(
            organizacion_central_id__isnull=False,
            sucursal_id__isnull=True,
            acueducto_id__isnull=True
        ).count()
        
        sucursal_migrations = MigracionOrganizacional.objects.filter(
            sucursal_id__isnull=False,
            acueducto_id__isnull=True
        ).count()
        
        acueducto_migrations = MigracionOrganizacional.objects.filter(
            acueducto_id__isnull=False
        ).count()
        
        self.stdout.write(f'  OrganizacionCentral → Empresa: {org_migrations}')
        self.stdout.write(f'  Sucursal → Vicepresidencia: {sucursal_migrations}')
        self.stdout.write(f'  Acueducto → UnidadOrganizacional: {acueducto_migrations}')
    
    def cleanup_demo_data(self):
        """Clean up demo data"""
        self.stdout.write('🧹 Cleaning up demo data...')
        
        # Delete migrations first (due to foreign keys)
        deleted_migrations = MigracionOrganizacional.objects.filter(
            migrado_por__username='migration_demo'
        ).delete()
        
        # Delete new structure
        AcueductoNuevo.objects.filter(codigo__contains='DEMO').delete()
        AlmacenRegional.objects.filter(nombre__contains='Demo').delete()
        UnidadOrganizacional.objects.filter(codigo__contains='DEMO').delete()
        Vicepresidencia.objects.filter(codigo__contains='DEMO').delete()
        Empresa.objects.filter(codigo__contains='DEMO').delete()
        
        # Delete old structure
        Acueducto.objects.filter(codigo__contains='DEMO').delete()
        Sucursal.objects.filter(codigo__contains='DEMO').delete()
        OrganizacionCentral.objects.filter(nombre__contains='Demo').delete()
        
        # Delete demo user
        User.objects.filter(username='migration_demo').delete()
        
        self.stdout.write(f'  ✓ Cleaned up {deleted_migrations[0]} migration records and related data')