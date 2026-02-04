"""
Management command to test the complete system integration.
"""

from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.contrib.contenttypes.models import ContentType
from decimal import Decimal

from institucion.system_integration import hidroven_system
from institucion.models import AlmacenRegional
from inventario.models import ChemicalProduct, UnitOfMeasure, Supplier
from catalogo.models import CategoriaProducto

User = get_user_model()


class Command(BaseCommand):
    help = 'Test the complete Hidroven system integration'

    def add_arguments(self, parser):
        parser.add_argument(
            '--health-check',
            action='store_true',
            help='Run system health check',
        )
        parser.add_argument(
            '--diagnostics',
            action='store_true',
            help='Run system diagnostics',
        )
        parser.add_argument(
            '--full-test',
            action='store_true',
            help='Run complete integration test',
        )

    def handle(self, *args, **options):
        if options['health_check']:
            self.run_health_check()
        
        if options['diagnostics']:
            self.run_diagnostics()
        
        if options['full_test']:
            self.run_full_integration_test()
        
        if not any([options['health_check'], options['diagnostics'], options['full_test']]):
            self.stdout.write(
                self.style.WARNING('Use --health-check, --diagnostics, or --full-test')
            )

    def run_health_check(self):
        """Run system health check"""
        self.stdout.write(
            self.style.SUCCESS('Running system health check...')
        )
        
        try:
            health_report = hidroven_system.get_system_health()
            
            self.stdout.write(f"Overall Status: {health_report['overall_status']}")
            self.stdout.write(f"Timestamp: {health_report['timestamp']}")
            
            self.stdout.write('\nService Status:')
            for service_name, service_status in health_report['services'].items():
                status_color = self.style.SUCCESS if service_status['status'] == 'healthy' else self.style.ERROR
                self.stdout.write(f"  {service_name}: {status_color(service_status['status'])}")
            
            if health_report.get('statistics'):
                self.stdout.write('\nSystem Statistics:')
                for stat_name, stat_value in health_report['statistics'].items():
                    self.stdout.write(f"  {stat_name}: {stat_value}")
            
            if health_report.get('alerts'):
                self.stdout.write('\nSystem Alerts:')
                for alert in health_report['alerts']:
                    alert_color = self.style.ERROR if alert['severity'] == 'high' else self.style.WARNING
                    self.stdout.write(f"  {alert_color(alert['type'])}: {alert['message']}")
            
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Health check failed: {str(e)}')
            )

    def run_diagnostics(self):
        """Run system diagnostics"""
        self.stdout.write(
            self.style.SUCCESS('Running system diagnostics...')
        )
        
        try:
            diagnostics = hidroven_system.run_system_diagnostics()
            
            self.stdout.write(f"Tests Run: {diagnostics['tests_run']}")
            self.stdout.write(f"Tests Passed: {diagnostics['tests_passed']}")
            self.stdout.write(f"Tests Failed: {diagnostics['tests_failed']}")
            
            self.stdout.write('\nTest Results:')
            for result in diagnostics['results']:
                status_color = self.style.SUCCESS if result['status'] == 'passed' else self.style.ERROR
                self.stdout.write(f"  {result['test']}: {status_color(result['status'])}")
                
                if result['status'] == 'passed' and 'details' in result:
                    self.stdout.write(f"    {result['details']}")
                elif result['status'] == 'failed' and 'error' in result:
                    self.stdout.write(f"    Error: {result['error']}")
            
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Diagnostics failed: {str(e)}')
            )

    def run_full_integration_test(self):
        """Run complete integration test"""
        self.stdout.write(
            self.style.SUCCESS('Running full integration test...')
        )
        
        try:
            # Create test user
            user, created = User.objects.get_or_create(
                username='test_integration_user',
                defaults={
                    'email': 'test@hidroven.gob.ve',
                    'role': 'ADMINISTRADOR'
                }
            )
            
            if created:
                user.set_password('testpass123')
                user.save()
                self.stdout.write('Created test user')
            
            # Get test warehouse
            warehouse = AlmacenRegional.objects.filter(prefijo='ZUL').first()
            if not warehouse:
                self.stdout.write(
                    self.style.ERROR('No test warehouse found. Run setup_hidroven_data first.')
                )
                return
            
            # Create test product if needed
            categoria, _ = CategoriaProducto.objects.get_or_create(
                codigo='TST',
                defaults={'nombre': 'Test Category'}
            )
            
            unidad_medida, _ = UnitOfMeasure.objects.get_or_create(
                nombre='Unidad',
                defaults={'simbolo': 'UN', 'tipo': 'CANTIDAD'}
            )
            
            proveedor, _ = Supplier.objects.get_or_create(
                nombre='Test Supplier',
                defaults={'rif': 'J-12345678-9', 'codigo': 'SUP001'}
            )
            
            producto, _ = ChemicalProduct.objects.get_or_create(
                nombre='Test Chemical Product',
                defaults={
                    'categoria': categoria,
                    'unidad_medida': unidad_medida,
                    'proveedor': proveedor,
                    'precio_unitario': Decimal('1000.00')
                }
            )
            
            # Test complete asset creation
            self.stdout.write('Testing complete asset creation...')
            
            product_content_type = ContentType.objects.get_for_model(ChemicalProduct)
            
            asset_data = {
                'tipo_activo': 'QUIMICO',
                'almacen_actual': warehouse,
                'producto_inventario_type': product_content_type,
                'producto_inventario_id': producto.id,
                'valor_unitario': Decimal('1500.00'),
                'numero_serie': 'TEST-INTEGRATION-001',
                'descripcion': 'Test asset for integration testing'
            }
            
            asset = hidroven_system.create_asset_complete(asset_data, user)
            self.stdout.write(f'✓ Asset created: {asset.codigo_actual}')
            
            # Test system health after asset creation
            self.stdout.write('Testing system health after operations...')
            health_report = hidroven_system.get_system_health()
            self.stdout.write(f'✓ System health: {health_report["overall_status"]}')
            
            # Test asset disposal
            self.stdout.write('Testing complete asset disposal...')
            disposal_data = {
                'motivo': 'Integration test cleanup',
                'observaciones': 'Test disposal for integration testing'
            }
            
            disposal_report = hidroven_system.dispose_asset_complete(
                asset.id, disposal_data, user
            )
            self.stdout.write(f'✓ Asset disposed: {disposal_report["asset_code"]}')
            
            self.stdout.write(
                self.style.SUCCESS('Full integration test completed successfully!')
            )
            
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Integration test failed: {str(e)}')
            )