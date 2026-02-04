"""
Unit tests for the asset state management system.
"""

import pytest
from django.test import TestCase
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.db import transaction

from .models import ActivoInventario, AlmacenRegional, HistorialMovimientoActivo
from .state_management import AssetStateManager, AssetStateAuditLogger
from .services import AssetCodeGenerator

User = get_user_model()


class AssetStateManagerTestCase(TestCase):
    """Test cases for AssetStateManager"""

    def setUp(self):
        """Set up test data"""
        # Create test user
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )

        # Create test warehouse
        from .models import Empresa, Vicepresidencia, UnidadOrganizacional
        from catalogo.models import CategoriaProducto
        from inventario.models import UnitOfMeasure, Supplier, ChemicalProduct
        from django.contrib.contenttypes.models import ContentType
        
        # Create organizational hierarchy
        self.empresa = Empresa.objects.create(
            nombre='Test Empresa',
            codigo='TEST'
        )
        
        self.vp = Vicepresidencia.objects.create(
            empresa=self.empresa,
            nombre='VP Test',
            codigo='VPT',
            tipo='OPERACIONES_HIDRICAS'
        )
        
        self.unidad = UnidadOrganizacional.objects.create(
            vicepresidencia=self.vp,
            nombre='Unidad Test',
            codigo='UT001',
            tipo='ALMACEN'
        )

        self.warehouse = AlmacenRegional.objects.create(
            unidad_organizacional=self.unidad,
            nombre='Almacén Test',
            prefijo='ZUL',
            ubicacion='Test Location',
            manager=self.user
        )

        # Create test product for inventory relationship
        category = CategoriaProducto.objects.create(
            nombre='Test Category',
            codigo='TEST'
        )
        
        unit = UnitOfMeasure.objects.create(
            nombre='Unidad',
            simbolo='UN',
            tipo='UNIDAD'
        )
        
        supplier = Supplier.objects.create(
            nombre='Test Supplier'
        )
        
        self.product = ChemicalProduct.objects.create(
            nombre='Test Chemical',
            categoria=category,
            unidad_medida=unit,
            proveedor=supplier,
            precio_unitario=100.00
        )

        # Create test asset
        asset_code = AssetCodeGenerator.generate_asset_code('ZUL', 'BOMBA')
        self.asset = ActivoInventario.objects.create(
            codigo_actual=asset_code,
            codigo_original=asset_code,
            tipo_activo='BOMBA',
            descripcion='Test asset for state management',
            almacen_actual=self.warehouse,
            estado='EN_ALMACEN',
            valor_unitario=1000.00,
            producto_inventario_type=ContentType.objects.get_for_model(ChemicalProduct),
            producto_inventario_id=self.product.id,
            creado_por=self.user,
            actualizado_por=self.user
        )

    def test_validate_state_transition_valid(self):
        """Test valid state transitions"""
        # Test valid transitions from EN_ALMACEN
        is_valid, message = AssetStateManager.validate_state_transition('EN_ALMACEN', 'EN_TRANSITO')
        self.assertTrue(is_valid)
        self.assertIn('transfer is approved', message)

        is_valid, message = AssetStateManager.validate_state_transition('EN_ALMACEN', 'INSTALADO')
        self.assertTrue(is_valid)

        is_valid, message = AssetStateManager.validate_state_transition('EN_ALMACEN', 'MANTENIMIENTO')
        self.assertTrue(is_valid)

    def test_validate_state_transition_invalid(self):
        """Test invalid state transitions"""
        # Test invalid transition from EN_ALMACEN to EN_USO (must go through INSTALADO)
        is_valid, message = AssetStateManager.validate_state_transition('EN_ALMACEN', 'EN_USO')
        self.assertFalse(is_valid)
        self.assertIn('not allowed', message)

        # Test invalid states
        is_valid, message = AssetStateManager.validate_state_transition('INVALID_STATE', 'EN_ALMACEN')
        self.assertFalse(is_valid)
        self.assertIn('Invalid source state', message)

    def test_validate_state_transition_same_state(self):
        """Test transition to same state"""
        is_valid, message = AssetStateManager.validate_state_transition('EN_ALMACEN', 'EN_ALMACEN')
        self.assertTrue(is_valid)
        self.assertIn('No state change required', message)

    def test_get_allowed_transitions(self):
        """Test getting allowed transitions"""
        transitions = AssetStateManager.get_allowed_transitions('EN_ALMACEN')
        expected_states = ['EN_TRANSITO', 'INSTALADO', 'MANTENIMIENTO']
        
        transition_states = [t[0] for t in transitions]
        for state in expected_states:
            self.assertIn(state, transition_states)

    def test_can_transition_automatically(self):
        """Test automatic transition validation"""
        # Test automatic transition for transfer approval
        can_auto = AssetStateManager.can_transition_automatically(
            'EN_ALMACEN', 'EN_TRANSITO', 'transfer_approved'
        )
        self.assertTrue(can_auto)

        # Test non-automatic transition
        can_auto = AssetStateManager.can_transition_automatically(
            'EN_ALMACEN', 'INSTALADO', 'transfer_approved'
        )
        self.assertFalse(can_auto)

    def test_change_asset_state_valid(self):
        """Test successful asset state change"""
        initial_state = self.asset.estado
        target_state = 'MANTENIMIENTO'

        # Change state
        success = AssetStateManager.change_asset_state(
            activo=self.asset,
            new_state=target_state,
            user=self.user,
            motivo='Test state change',
            observaciones='Unit test'
        )

        self.assertTrue(success)
        
        # Refresh asset from database
        self.asset.refresh_from_db()
        self.assertEqual(self.asset.estado, target_state)

        # Check audit record was created
        audit_records = HistorialMovimientoActivo.objects.filter(
            activo=self.asset,
            tipo_movimiento='CAMBIO_ESTADO'
        )
        self.assertTrue(audit_records.exists())
        
        latest_record = audit_records.latest('fecha_movimiento')
        self.assertEqual(latest_record.estado_anterior, initial_state)
        self.assertEqual(latest_record.estado_nuevo, target_state)
        self.assertEqual(latest_record.usuario_responsable, self.user)

    def test_change_asset_state_invalid(self):
        """Test invalid asset state change"""
        with self.assertRaises(ValidationError):
            AssetStateManager.change_asset_state(
                activo=self.asset,
                new_state='EN_USO',  # Invalid transition from EN_ALMACEN
                user=self.user,
                motivo='Invalid test',
                observaciones='Should fail'
            )

        # Asset state should remain unchanged
        self.asset.refresh_from_db()
        self.assertEqual(self.asset.estado, 'EN_ALMACEN')

    def test_change_asset_state_automatic(self):
        """Test automatic asset state change"""
        success = AssetStateManager.change_asset_state(
            activo=self.asset,
            new_state='EN_TRANSITO',
            user=self.user,
            motivo='Transfer approved',
            auto_triggered=True,
            trigger_condition='transfer_approved'
        )

        self.assertTrue(success)
        self.asset.refresh_from_db()
        self.assertEqual(self.asset.estado, 'EN_TRANSITO')

        # Check audit record has automatic marker
        audit_record = HistorialMovimientoActivo.objects.filter(
            activo=self.asset,
            tipo_movimiento='CAMBIO_ESTADO_AUTO_TRANSFER_APPROVED'
        ).latest('fecha_movimiento')
        
        self.assertIn('[AUTOMÁTICO', audit_record.motivo)

    def test_validate_transfer_request_state(self):
        """Test transfer request state validation"""
        # Asset in warehouse should be transferable
        can_transfer, message = AssetStateManager.validate_transfer_request_state(self.asset)
        self.assertTrue(can_transfer)
        self.assertIn('available for transfer', message)

        # Asset in transit should not be transferable
        self.asset.estado = 'EN_TRANSITO'
        self.asset.save()
        
        can_transfer, message = AssetStateManager.validate_transfer_request_state(self.asset)
        self.assertFalse(can_transfer)
        self.assertIn('in transit cannot be transferred', message)

    def test_get_state_statistics(self):
        """Test state statistics calculation"""
        # Create additional assets in different states
        for i, state in enumerate(['INSTALADO', 'EN_USO', 'MANTENIMIENTO'], 1):
            asset_code = AssetCodeGenerator.generate_asset_code('ZUL', 'BOMBA')
            ActivoInventario.objects.create(
                codigo_actual=asset_code,
                codigo_original=asset_code,
                tipo_activo='BOMBA',
                descripcion=f'Test asset {i}',
                almacen_actual=self.warehouse,
                estado=state,
                valor_unitario=1000.00 * i,
                producto_inventario_type=ContentType.objects.get_for_model(ChemicalProduct),
                producto_inventario_id=self.product.id,
                creado_por=self.user,
                actualizado_por=self.user
            )

        # Get statistics
        all_assets = ActivoInventario.objects.all()
        stats = AssetStateManager.get_state_statistics(all_assets)

        self.assertEqual(stats['total_assets'], 4)
        self.assertEqual(stats['state_counts']['EN_ALMACEN'], 1)
        self.assertEqual(stats['state_counts']['INSTALADO'], 1)
        self.assertEqual(stats['state_counts']['EN_USO'], 1)
        self.assertEqual(stats['state_counts']['MANTENIMIENTO'], 1)
        self.assertEqual(stats['assets_available_for_transfer'], 1)
        self.assertEqual(stats['assets_in_use'], 2)  # INSTALADO + EN_USO

    def test_validate_bulk_state_change(self):
        """Test bulk state change validation"""
        # Create additional assets
        assets = []
        for i in range(3):
            asset_code = AssetCodeGenerator.generate_asset_code('ZUL', 'BOMBA')
            asset = ActivoInventario.objects.create(
                codigo_actual=asset_code,
                codigo_original=asset_code,
                tipo_activo='BOMBA',
                descripcion=f'Bulk test asset {i}',
                almacen_actual=self.warehouse,
                estado='EN_ALMACEN',
                valor_unitario=1000.00,
                producto_inventario_type=ContentType.objects.get_for_model(ChemicalProduct),
                producto_inventario_id=self.product.id,
                creado_por=self.user,
                actualizado_por=self.user
            )
            assets.append(asset)

        # Test bulk validation
        queryset = ActivoInventario.objects.filter(id__in=[a.id for a in assets])
        result = AssetStateManager.validate_bulk_state_change(queryset, 'MANTENIMIENTO')

        self.assertTrue(result['can_proceed'])
        self.assertEqual(result['valid_count'], 3)
        self.assertEqual(result['invalid_count'], 0)

    def test_bulk_change_asset_states(self):
        """Test bulk asset state change"""
        # Create assets for bulk operation
        assets = []
        for i in range(2):
            asset_code = AssetCodeGenerator.generate_asset_code('ZUL', 'BOMBA')
            asset = ActivoInventario.objects.create(
                codigo_actual=asset_code,
                codigo_original=asset_code,
                tipo_activo='BOMBA',
                descripcion=f'Bulk change asset {i}',
                almacen_actual=self.warehouse,
                estado='EN_ALMACEN',
                valor_unitario=1000.00,
                producto_inventario_type=ContentType.objects.get_for_model(ChemicalProduct),
                producto_inventario_id=self.product.id,
                creado_por=self.user,
                actualizado_por=self.user
            )
            assets.append(asset)

        # Perform bulk change
        queryset = ActivoInventario.objects.filter(id__in=[a.id for a in assets])
        result = AssetStateManager.bulk_change_asset_states(
            activos_queryset=queryset,
            new_state='MANTENIMIENTO',
            user=self.user,
            motivo='Bulk maintenance test',
            observaciones='Unit test bulk operation'
        )

        self.assertTrue(result['success'])
        self.assertEqual(result['changed_count'], 2)
        self.assertEqual(result['failed_count'], 0)

        # Verify assets were changed
        for asset in assets:
            asset.refresh_from_db()
            self.assertEqual(asset.estado, 'MANTENIMIENTO')


class AssetModelStateIntegrationTestCase(TestCase):
    """Test integration of state management with ActivoInventario model"""

    def setUp(self):
        """Set up test data"""
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )

        # Create organizational hierarchy
        from .models import Empresa, Vicepresidencia, UnidadOrganizacional
        from catalogo.models import CategoriaProducto
        from inventario.models import UnitOfMeasure, Supplier, ChemicalProduct
        from django.contrib.contenttypes.models import ContentType
        
        self.empresa = Empresa.objects.create(
            nombre='Test Empresa',
            codigo='TEST'
        )
        
        self.vp = Vicepresidencia.objects.create(
            empresa=self.empresa,
            nombre='VP Test',
            codigo='VPT',
            tipo='OPERACIONES_HIDRICAS'
        )
        
        self.unidad = UnidadOrganizacional.objects.create(
            vicepresidencia=self.vp,
            nombre='Unidad Test',
            codigo='UT001',
            tipo='ALMACEN'
        )

        self.warehouse = AlmacenRegional.objects.create(
            unidad_organizacional=self.unidad,
            nombre='Almacén Test',
            prefijo='ZUL',
            ubicacion='Test Location',
            manager=self.user
        )

        # Create test product for inventory relationship
        category = CategoriaProducto.objects.create(
            nombre='Test Category',
            codigo='TEST'
        )
        
        unit = UnitOfMeasure.objects.create(
            nombre='Unidad',
            simbolo='UN',
            tipo='UNIDAD'
        )
        
        supplier = Supplier.objects.create(
            nombre='Test Supplier'
        )
        
        self.product = ChemicalProduct.objects.create(
            nombre='Test Chemical',
            categoria=category,
            unidad_medida=unit,
            proveedor=supplier,
            precio_unitario=100.00
        )

        # Create test asset
        asset_code = AssetCodeGenerator.generate_asset_code('ZUL', 'BOMBA')
        self.asset = ActivoInventario.objects.create(
            codigo_actual=asset_code,
            codigo_original=asset_code,
            tipo_activo='BOMBA',
            descripcion='Test asset for integration',
            almacen_actual=self.warehouse,
            estado='EN_ALMACEN',
            valor_unitario=1000.00,
            producto_inventario_type=ContentType.objects.get_for_model(ChemicalProduct),
            producto_inventario_id=self.product.id,
            creado_por=self.user,
            actualizado_por=self.user
        )

    def test_asset_change_state_method(self):
        """Test asset's change_state method"""
        success = self.asset.change_state(
            new_state='MANTENIMIENTO',
            user=self.user,
            motivo='Integration test',
            observaciones='Testing model integration'
        )

        self.assertTrue(success)
        self.asset.refresh_from_db()
        self.assertEqual(self.asset.estado, 'MANTENIMIENTO')

    def test_asset_get_allowed_transitions(self):
        """Test asset's get_allowed_state_transitions method"""
        transitions = self.asset.get_allowed_state_transitions()
        
        self.assertIsInstance(transitions, list)
        self.assertTrue(len(transitions) > 0)
        
        # Should include valid transitions from EN_ALMACEN
        transition_states = [t[0] for t in transitions]
        self.assertIn('EN_TRANSITO', transition_states)
        self.assertIn('INSTALADO', transition_states)
        self.assertIn('MANTENIMIENTO', transition_states)

    def test_asset_can_be_transferred(self):
        """Test asset's can_be_transferred method"""
        can_transfer, message = self.asset.can_be_transferred()
        self.assertTrue(can_transfer)
        self.assertIn('available for transfer', message)

        # Change to transit state
        self.asset.estado = 'EN_TRANSITO'
        self.asset.save()

        can_transfer, message = self.asset.can_be_transferred()
        self.assertFalse(can_transfer)
        self.assertIn('in transit cannot be transferred', message)

    def test_asset_get_state_history(self):
        """Test asset's get_state_history method"""
        # Make some state changes
        self.asset.change_state('MANTENIMIENTO', self.user, 'First change')
        self.asset.change_state('EN_ALMACEN', self.user, 'Second change')

        history = self.asset.get_state_history(limit=5)
        
        self.assertIsInstance(history, list)
        self.assertTrue(len(history) >= 2)
        
        # Check history structure
        for record in history:
            self.assertIn('fecha', record)
            self.assertIn('estado_anterior', record)
            self.assertIn('estado_nuevo', record)
            self.assertIn('usuario', record)
            self.assertIn('motivo', record)

    def test_state_validation_in_model_clean(self):
        """Test that model validation uses state management system"""
        # This should work - valid transition
        self.asset.estado = 'MANTENIMIENTO'
        self.asset.clean()  # Should not raise

        # This should fail - invalid transition
        self.asset.estado = 'EN_USO'  # Invalid from EN_ALMACEN
        with self.assertRaises(ValidationError):
            self.asset.clean()


if __name__ == '__main__':
    pytest.main([__file__])