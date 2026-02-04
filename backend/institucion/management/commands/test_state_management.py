"""
Management command to test the asset state management system.
"""

from django.core.management.base import BaseCommand, CommandError
from django.contrib.auth import get_user_model
from django.db import transaction
from institucion.models import ActivoInventario, AlmacenRegional
from institucion.state_management import AssetStateManager, AssetStateAuditLogger
from institucion.services import AssetCodeGenerator

User = get_user_model()


class Command(BaseCommand):
    help = 'Test the asset state management system'

    def add_arguments(self, parser):
        parser.add_argument(
            '--create-test-data',
            action='store_true',
            help='Create test data for demonstration',
        )
        parser.add_argument(
            '--test-transitions',
            action='store_true',
            help='Test state transitions',
        )
        parser.add_argument(
            '--test-bulk-operations',
            action='store_true',
            help='Test bulk state operations',
        )
        parser.add_argument(
            '--show-statistics',
            action='store_true',
            help='Show asset state statistics',
        )

    def handle(self, *args, **options):
        self.stdout.write(
            self.style.SUCCESS('Testing Asset State Management System')
        )

        if options['create_test_data']:
            self.create_test_data()

        if options['test_transitions']:
            self.test_state_transitions()

        if options['test_bulk_operations']:
            self.test_bulk_operations()

        if options['show_statistics']:
            self.show_statistics()

        self.stdout.write(
            self.style.SUCCESS('Asset State Management System test completed')
        )

    def create_test_data(self):
        """Create test data for demonstration"""
        self.stdout.write('Creating test data...')

        try:
            # Get or create test user
            user, created = User.objects.get_or_create(
                username='test_state_manager',
                defaults={
                    'email': 'test@example.com',
                    'first_name': 'Test',
                    'last_name': 'Manager'
                }
            )

            # Get a warehouse
            warehouse = AlmacenRegional.objects.first()
            if not warehouse:
                self.stdout.write(
                    self.style.ERROR('No warehouses found. Please create warehouses first.')
                )
                return

            # Create test product for inventory relationship
            from catalogo.models import CategoriaProducto
            from inventario.models import UnitOfMeasure, Supplier, ChemicalProduct
            from django.contrib.contenttypes.models import ContentType
            
            category, _ = CategoriaProducto.objects.get_or_create(
                codigo='TEST',
                defaults={'nombre': 'Test Category'}
            )
            
            unit, _ = UnitOfMeasure.objects.get_or_create(
                simbolo='UN',
                defaults={'nombre': 'Unidad', 'tipo': 'UNIDAD'}
            )
            
            supplier, _ = Supplier.objects.get_or_create(
                nombre='Test Supplier'
            )
            
            product, _ = ChemicalProduct.objects.get_or_create(
                nombre='Test Chemical for State Management',
                defaults={
                    'categoria': category,
                    'unidad_medida': unit,
                    'proveedor': supplier,
                    'precio_unitario': 100.00
                }
            )

            # Create test assets in different states
            states_to_create = ['EN_ALMACEN', 'INSTALADO', 'EN_USO', 'MANTENIMIENTO']
            
            for i, state in enumerate(states_to_create, 1):
                # Generate asset code
                asset_code = AssetCodeGenerator.generate_asset_code(
                    warehouse_prefix=warehouse.prefijo,
                    asset_type='BOMBA'
                )

                # Create asset
                asset = ActivoInventario.objects.create(
                    codigo_actual=asset_code,
                    codigo_original=asset_code,
                    tipo_activo='BOMBA',
                    descripcion=f'Test asset {i} for state management demo',
                    almacen_actual=warehouse,
                    estado=state,
                    valor_unitario=1000.00 * i,
                    producto_inventario_type=ContentType.objects.get_for_model(ChemicalProduct),
                    producto_inventario_id=product.id,
                    creado_por=user,
                    actualizado_por=user
                )

                self.stdout.write(f'Created asset {asset.codigo_actual} in state {state}')

            self.stdout.write(
                self.style.SUCCESS(f'Created {len(states_to_create)} test assets')
            )

        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Error creating test data: {str(e)}')
            )

    def test_state_transitions(self):
        """Test state transitions with validation"""
        self.stdout.write('Testing state transitions...')

        try:
            # Get test user
            user = User.objects.filter(username='test_state_manager').first()
            if not user:
                user = User.objects.first()
                if not user:
                    self.stdout.write(
                        self.style.ERROR('No users found. Please create a user first.')
                    )
                    return

            # Get test assets
            assets = ActivoInventario.objects.all()[:3]
            if not assets:
                self.stdout.write(
                    self.style.ERROR('No assets found. Run with --create-test-data first.')
                )
                return

            for asset in assets:
                current_state = asset.estado
                self.stdout.write(f'\nTesting transitions for asset {asset.codigo_actual} (current state: {current_state})')

                # Get allowed transitions
                allowed_transitions = asset.get_allowed_state_transitions()
                self.stdout.write(f'Allowed transitions: {[t[0] for t in allowed_transitions]}')

                # Test a valid transition
                if allowed_transitions:
                    target_state, description = allowed_transitions[0]
                    self.stdout.write(f'Testing transition to {target_state}: {description}')

                    try:
                        success = asset.change_state(
                            new_state=target_state,
                            user=user,
                            motivo='Test transition from management command',
                            observaciones='Automated test of state management system'
                        )

                        if success:
                            self.stdout.write(
                                self.style.SUCCESS(f'Successfully changed state to {target_state}')
                            )
                        else:
                            self.stdout.write(
                                self.style.WARNING(f'State change returned False')
                            )

                    except Exception as e:
                        self.stdout.write(
                            self.style.ERROR(f'State change failed: {str(e)}')
                        )

                # Test an invalid transition
                invalid_states = [s for s in AssetStateManager.ASSET_STATES 
                                if s not in [t[0] for t in allowed_transitions] and s != current_state]
                
                if invalid_states:
                    invalid_state = invalid_states[0]
                    self.stdout.write(f'Testing invalid transition to {invalid_state}')

                    try:
                        asset.change_state(
                            new_state=invalid_state,
                            user=user,
                            motivo='Test invalid transition',
                            observaciones='This should fail'
                        )
                        self.stdout.write(
                            self.style.WARNING(f'Invalid transition was allowed (unexpected)')
                        )
                    except Exception as e:
                        self.stdout.write(
                            self.style.SUCCESS(f'Invalid transition correctly rejected: {str(e)}')
                        )

        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Error testing state transitions: {str(e)}')
            )

    def test_bulk_operations(self):
        """Test bulk state operations"""
        self.stdout.write('Testing bulk state operations...')

        try:
            # Get test user
            user = User.objects.filter(username='test_state_manager').first()
            if not user:
                user = User.objects.first()

            # Get assets in warehouse state
            warehouse_assets = ActivoInventario.objects.filter(estado='EN_ALMACEN')[:2]
            
            if not warehouse_assets:
                self.stdout.write(
                    self.style.WARNING('No assets in EN_ALMACEN state for bulk testing')
                )
                return

            self.stdout.write(f'Testing bulk state change for {len(warehouse_assets)} assets')

            # Test bulk validation
            validation_result = AssetStateManager.validate_bulk_state_change(
                warehouse_assets, 'MANTENIMIENTO'
            )

            self.stdout.write(f'Bulk validation result:')
            self.stdout.write(f'  - Valid assets: {validation_result["valid_count"]}')
            self.stdout.write(f'  - Invalid assets: {validation_result["invalid_count"]}')
            self.stdout.write(f'  - Can proceed: {validation_result["can_proceed"]}')

            if validation_result['can_proceed']:
                # Execute bulk change
                result = AssetStateManager.bulk_change_asset_states(
                    activos_queryset=warehouse_assets,
                    new_state='MANTENIMIENTO',
                    user=user,
                    motivo='Bulk maintenance operation test',
                    observaciones='Testing bulk state management'
                )

                self.stdout.write(f'Bulk operation result:')
                self.stdout.write(f'  - Success: {result["success"]}')
                self.stdout.write(f'  - Changed: {result["changed_count"]}')
                self.stdout.write(f'  - Failed: {result["failed_count"]}')
                
                if result['errors']:
                    self.stdout.write(f'  - Errors: {result["errors"]}')

        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Error testing bulk operations: {str(e)}')
            )

    def show_statistics(self):
        """Show asset state statistics"""
        self.stdout.write('Asset State Statistics:')

        try:
            # Get all assets
            all_assets = ActivoInventario.objects.all()
            
            if not all_assets:
                self.stdout.write('No assets found.')
                return

            # Get statistics
            stats = AssetStateManager.get_state_statistics(all_assets)

            self.stdout.write(f'\nTotal Assets: {stats["total_assets"]}')
            self.stdout.write('\nState Distribution:')
            
            for state in AssetStateManager.ASSET_STATES:
                count = stats['state_counts'].get(state, 0)
                percentage = stats['state_percentages'].get(state, 0)
                self.stdout.write(f'  - {state}: {count} ({percentage:.1f}%)')

            self.stdout.write(f'\nOperational Summary:')
            self.stdout.write(f'  - Available for transfer: {stats["assets_available_for_transfer"]}')
            self.stdout.write(f'  - In transit: {stats["assets_in_transit"]}')
            self.stdout.write(f'  - In use: {stats["assets_in_use"]}')
            self.stdout.write(f'  - Under maintenance: {stats["assets_under_maintenance"]}')

            # Show state history for first asset
            if all_assets:
                first_asset = all_assets.first()
                history = first_asset.get_state_history(limit=5)
                
                if history:
                    self.stdout.write(f'\nState History for {first_asset.codigo_actual}:')
                    for record in history:
                        self.stdout.write(
                            f'  - {record["fecha"].strftime("%Y-%m-%d %H:%M")} | '
                            f'{record["estado_anterior"]} → {record["estado_nuevo"]} | '
                            f'{record["usuario"]} | {record["motivo"]}'
                        )

        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Error showing statistics: {str(e)}')
            )