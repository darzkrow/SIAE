# ============================================================================
# PROPERTY-BASED TESTS FOR DUAL APPROVAL WORKFLOW
# ============================================================================

"""
Property-based tests for the dual approval workflow system.

This module tests the following properties:
- Property 8: Dual Approval Workflow Enforcement
- Property 9: Transfer Execution Completeness

Requirements validated:
- 4.2: Dual approval workflow enforcement
- 4.4: Transfer execution management
- 4.5: Workflow state management
- 4.6: Business rule enforcement
- 4.7: Transfer completion with asset code evolution
- 7.1: Atomic inventory updates with transfer completion
- 7.2: Discrepancy detection and flagging system
- 7.3: Separate inventory tracking by asset type and warehouse
"""

import pytest
from hypothesis import given, strategies as st, settings, assume, example
from hypothesis.extra.django import TestCase as HypothesisTestCase
from django.test import TransactionTestCase
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.utils import timezone
from datetime import timedelta
import logging

from .models import (
    Empresa, Vicepresidencia, UnidadOrganizacional, AlmacenRegional,
    ActivoInventario, SolicitudTraslado, AprobacionTraslado,
    HistorialMovimientoActivo
)
from .transfer_manager import TransferManager, TransferRequestData
from .services import AssetCodeGenerator
from .state_management import AssetStateManager

User = get_user_model()
logger = logging.getLogger(__name__)


# ============================================================================
# TEST DATA GENERATORS
# ============================================================================

@st.composite
def warehouse_data(draw):
    """Generate valid warehouse data"""
    prefixes = ['ZUL', 'CAR', 'MIR', 'ARA', 'LAR', 'TAC', 'BOL', 'ANZ', 'MON']
    return {
        'prefijo': draw(st.sampled_from(prefixes)),
        'nombre': draw(st.text(min_size=5, max_size=50, alphabet=st.characters(whitelist_categories=('Lu', 'Ll', 'Nd', 'Zs')))),
        'ubicacion': draw(st.text(min_size=5, max_size=100, alphabet=st.characters(whitelist_categories=('Lu', 'Ll', 'Nd', 'Zs')))),
        'capacidad_maxima': draw(st.integers(min_value=100, max_value=10000)),
    }


@st.composite
def asset_data(draw):
    """Generate valid asset data"""
    asset_types = ['BOMBA', 'MOTOR', 'TUBERIA', 'QUIMICO', 'ACCESORIO', 'EQUIPO', 'VALVULA', 'MEDIDOR']
    return {
        'tipo_activo': draw(st.sampled_from(asset_types)),
        'descripcion': draw(st.text(min_size=10, max_size=200, alphabet=st.characters(whitelist_categories=('Lu', 'Ll', 'Nd', 'Zs')))),
        'valor_unitario': draw(st.decimals(min_value=1, max_value=100000, places=2)),
        'numero_serie': draw(st.text(min_size=5, max_size=20, alphabet=st.characters(whitelist_categories=('Lu', 'Nd')))),
    }


@st.composite
def transfer_request_data(draw):
    """Generate valid transfer request data"""
    priorities = ['BAJA', 'NORMAL', 'ALTA', 'URGENTE']
    
    # Generate deadline based on priority
    priority = draw(st.sampled_from(priorities))
    if priority == 'URGENTE':
        hours_ahead = draw(st.integers(min_value=1, max_value=4))
    elif priority == 'ALTA':
        hours_ahead = draw(st.integers(min_value=4, max_value=24))
    else:
        hours_ahead = draw(st.integers(min_value=4, max_value=168))  # Up to 1 week
    
    return {
        'motivo': draw(st.text(min_size=10, max_size=500, alphabet=st.characters(whitelist_categories=('Lu', 'Ll', 'Nd', 'Zs', 'Po')))),
        'prioridad': priority,
        'fecha_limite': timezone.now() + timedelta(hours=hours_ahead),
        'observaciones': draw(st.text(min_size=0, max_size=200, alphabet=st.characters(whitelist_categories=('Lu', 'Ll', 'Nd', 'Zs', 'Po')))),
    }


@st.composite
def approval_decision_data(draw):
    """Generate approval decision data"""
    decisions = ['APROBADO', 'RECHAZADO']
    return {
        'decision': draw(st.sampled_from(decisions)),
        'comentarios': draw(st.text(min_size=0, max_size=500, alphabet=st.characters(whitelist_categories=('Lu', 'Ll', 'Nd', 'Zs', 'Po')))),
    }


# ============================================================================
# PROPERTY-BASED TEST CLASS
# ============================================================================

class TransferWorkflowPropertiesTestCase(HypothesisTestCase):
    """
    Property-based tests for transfer workflow system.
    
    Uses TransactionTestCase to support database transactions and rollbacks
    required for testing atomic operations.
    """
    
    def setUp(self):
        """Set up test data"""
        # Create organizational structure
        self.empresa = Empresa.objects.create(
            nombre='Hidroven Test',
            codigo='HVT',
            rif='J-12345678-9'
        )
        
        self.vp_operaciones = Vicepresidencia.objects.create(
            empresa=self.empresa,
            nombre='VP Operaciones Hídricas',
            codigo='VP-OP',
            tipo='OPERACIONES_HIDRICAS'
        )
        
        self.unidad_almacenes = UnidadOrganizacional.objects.create(
            vicepresidencia=self.vp_operaciones,
            nombre='Gerencia de Almacenes',
            codigo='GER-ALM',
            tipo='GERENCIA'
        )
        
        # Create test users
        self.manager_zul = User.objects.create_user(
            username='manager_zul',
            email='manager.zul@hidroven.test',
            password='testpass123'
        )
        
        self.manager_car = User.objects.create_user(
            username='manager_car',
            email='manager.car@hidroven.test',
            password='testpass123'
        )
        
        self.requester = User.objects.create_user(
            username='requester',
            email='requester@hidroven.test',
            password='testpass123'
        )
        
        self.executor = User.objects.create_user(
            username='executor',
            email='executor@hidroven.test',
            password='testpass123'
        )
        
        # Create test warehouses
        self.warehouse_zul = AlmacenRegional.objects.create(
            unidad_organizacional=self.unidad_almacenes,
            nombre='Almacén Zulia',
            prefijo='ZUL',
            ubicacion='Maracaibo, Zulia',
            manager=self.manager_zul,
            capacidad_maxima=5000
        )
        
        self.warehouse_car = AlmacenRegional.objects.create(
            unidad_organizacional=self.unidad_almacenes,
            nombre='Almacén Carabobo',
            prefijo='CAR',
            ubicacion='Valencia, Carabobo',
            manager=self.manager_car,
            capacidad_maxima=3000
        )
    
    def create_test_asset(self, warehouse, asset_data_dict=None):
        """Create a test asset in the specified warehouse"""
        if asset_data_dict is None:
            asset_data_dict = {
                'tipo_activo': 'BOMBA',
                'descripcion': 'Bomba de agua centrífuga',
                'valor_unitario': 1500.00,
                'numero_serie': 'BCA001'
            }
        
        # Generate asset code
        codigo = AssetCodeGenerator.generate_asset_code(
            warehouse_prefix=warehouse.prefijo,
            asset_type=asset_data_dict['tipo_activo']
        )
        
        # Create a dummy content type for the generic foreign key
        from django.contrib.contenttypes.models import ContentType
        from inventario.models import ChemicalProduct  # Use an existing model
        
        # Get or create a test chemical product
        try:
            test_product = ChemicalProduct.objects.first()
            if not test_product:
                # Create a minimal test product if none exists
                from catalogo.models import CategoriaProducto, Marca
                categoria, _ = CategoriaProducto.objects.get_or_create(
                    nombre='Test Category',
                    defaults={'descripcion': 'Test category for property tests'}
                )
                marca, _ = Marca.objects.get_or_create(
                    nombre='Test Brand',
                    defaults={'descripcion': 'Test brand for property tests'}
                )
                test_product = ChemicalProduct.objects.create(
                    nombre='Test Chemical Product',
                    descripcion='Test product for property tests',
                    categoria=categoria,
                    marca=marca,
                    precio_unitario=100.00,
                    unidad_medida='L',
                    concentracion=50.0,
                    ph_minimo=6.0,
                    ph_maximo=8.0
                )
        except Exception:
            # If we can't create a chemical product, use a simpler approach
            # Just use the ContentType for User as a fallback
            from django.contrib.auth import get_user_model
            User = get_user_model()
            content_type = ContentType.objects.get_for_model(User)
            test_product = self.requester
        else:
            content_type = ContentType.objects.get_for_model(ChemicalProduct)
            test_product = test_product
        
        return ActivoInventario.objects.create(
            codigo_actual=codigo,
            codigo_original=codigo,
            almacen_actual=warehouse,
            creado_por=self.requester,
            producto_inventario_type=content_type,
            producto_inventario_id=test_product.id,
            **asset_data_dict
        )
    
    # ========================================================================
    # PROPERTY 8: DUAL APPROVAL WORKFLOW ENFORCEMENT
    # ========================================================================
    
    @given(
        asset_data=asset_data(),
        request_data=transfer_request_data(),
        origin_approval=approval_decision_data(),
        destination_approval=approval_decision_data()
    )
    @settings(max_examples=100, deadline=30000)
    def test_property_8_dual_approval_workflow_enforcement(
        self, asset_data, request_data, origin_approval, destination_approval
    ):
        """
        **Property 8: Dual Approval Workflow Enforcement**
        **Validates: Requirements 4.2, 4.5, 4.6**
        
        For any asset transfer request, the transfer should never execute without 
        receiving approval from both origin warehouse manager and destination 
        warehouse manager, and any rejection should cancel the entire transfer.
        """
        # Create test asset
        asset = self.create_test_asset(self.warehouse_zul, asset_data)
        
        # Create transfer request
        transfer_request = TransferRequestData(
            activo_id=asset.id,
            almacen_origen_id=self.warehouse_zul.id,
            almacen_destino_id=self.warehouse_car.id,
            solicitante_id=self.requester.id,
            **request_data
        )
        
        success, solicitud = TransferManager.create_transfer_request(transfer_request)
        assume(success)  # Skip if request creation fails due to business rules
        
        # Test that transfer cannot execute without approvals
        self.assertFalse(solicitud.can_execute(), 
                        "Transfer should not be executable without approvals")
        
        # Test single approval scenarios
        if origin_approval['decision'] == 'APROBADO':
            # Approve from origin
            approval_result = TransferManager.approve_transfer(
                solicitud.id, self.manager_zul, 'ORIGEN', origin_approval['comentarios']
            )
            self.assertTrue(approval_result.success, 
                          f"Origin approval should succeed: {approval_result.message}")
            
            solicitud.refresh_from_db()
            
            if destination_approval['decision'] == 'RECHAZADO':
                # Reject from destination - should cancel entire transfer
                rejection_result = TransferManager.reject_transfer(
                    solicitud.id, self.manager_car, destination_approval['comentarios']
                )
                self.assertTrue(rejection_result.success,
                              f"Destination rejection should succeed: {rejection_result.message}")
                
                solicitud.refresh_from_db()
                self.assertEqual(solicitud.estado, 'RECHAZADA',
                               "Transfer should be rejected after any rejection")
                self.assertFalse(solicitud.can_execute(),
                               "Rejected transfer should not be executable")
                
            else:  # destination_approval['decision'] == 'APROBADO'
                # Approve from destination - should enable execution
                approval_result = TransferManager.approve_transfer(
                    solicitud.id, self.manager_car, 'DESTINO', destination_approval['comentarios']
                )
                self.assertTrue(approval_result.success,
                              f"Destination approval should succeed: {approval_result.message}")
                
                solicitud.refresh_from_db()
                self.assertEqual(solicitud.estado, 'APROBADA_COMPLETA',
                               "Transfer should be completely approved after both approvals")
                self.assertTrue(solicitud.can_execute(),
                              "Fully approved transfer should be executable")
                
                # Test that execution works with dual approval
                execution_result = TransferManager.execute_transfer(solicitud.id, self.executor)
                self.assertTrue(execution_result.success,
                              f"Transfer execution should succeed with dual approval: {execution_result.message}")
                
                solicitud.refresh_from_db()
                self.assertEqual(solicitud.estado, 'EN_TRANSITO',
                               "Executed transfer should be in transit")
        
        elif origin_approval['decision'] == 'RECHAZADO':
            # Reject from origin - should cancel entire transfer immediately
            rejection_result = TransferManager.reject_transfer(
                solicitud.id, self.manager_zul, origin_approval['comentarios']
            )
            self.assertTrue(rejection_result.success,
                          f"Origin rejection should succeed: {rejection_result.message}")
            
            solicitud.refresh_from_db()
            self.assertEqual(solicitud.estado, 'RECHAZADA',
                           "Transfer should be rejected after origin rejection")
            self.assertFalse(solicitud.can_execute(),
                           "Rejected transfer should not be executable")
    
    @given(
        asset_data=asset_data(),
        request_data=transfer_request_data()
    )
    @settings(max_examples=50, deadline=20000)
    def test_property_8_approval_authority_validation(self, asset_data, request_data):
        """
        Test that only authorized warehouse managers can approve transfers.
        Part of Property 8: Dual Approval Workflow Enforcement.
        """
        # Create test asset
        asset = self.create_test_asset(self.warehouse_zul, asset_data)
        
        # Create transfer request
        transfer_request = TransferRequestData(
            activo_id=asset.id,
            almacen_origen_id=self.warehouse_zul.id,
            almacen_destino_id=self.warehouse_car.id,
            solicitante_id=self.requester.id,
            **request_data
        )
        
        success, solicitud = TransferManager.create_transfer_request(transfer_request)
        assume(success)
        
        # Test that wrong manager cannot approve
        wrong_approval = TransferManager.approve_transfer(
            solicitud.id, self.manager_car, 'ORIGEN', 'Wrong manager approval'
        )
        self.assertFalse(wrong_approval.success,
                        "Wrong manager should not be able to approve from origin")
        
        wrong_approval = TransferManager.approve_transfer(
            solicitud.id, self.manager_zul, 'DESTINO', 'Wrong manager approval'
        )
        self.assertFalse(wrong_approval.success,
                        "Wrong manager should not be able to approve from destination")
        
        # Test that requester cannot approve
        requester_approval = TransferManager.approve_transfer(
            solicitud.id, self.requester, 'ORIGEN', 'Requester approval'
        )
        self.assertFalse(requester_approval.success,
                        "Requester should not be able to approve")
    
    # ========================================================================
    # PROPERTY 9: TRANSFER EXECUTION COMPLETENESS
    # ========================================================================
    
    @given(
        asset_data=asset_data(),
        request_data=transfer_request_data()
    )
    @settings(max_examples=50, deadline=30000)
    def test_property_9_transfer_execution_completeness(self, asset_data, request_data):
        """
        **Property 9: Transfer Execution Completeness**
        **Validates: Requirements 4.4, 4.7, 7.1, 7.2, 7.3**
        
        For any transfer request that receives dual approval, the system should 
        automatically execute the transfer, update the asset location, evolve 
        the asset code, and update inventory counts atomically.
        """
        # Create test asset
        asset = self.create_test_asset(self.warehouse_zul, asset_data)
        original_code = asset.codigo_actual
        
        # Create and approve transfer request
        transfer_request = TransferRequestData(
            activo_id=asset.id,
            almacen_origen_id=self.warehouse_zul.id,
            almacen_destino_id=self.warehouse_car.id,
            solicitante_id=self.requester.id,
            **request_data
        )
        
        success, solicitud = TransferManager.create_transfer_request(transfer_request)
        assume(success)
        
        # Approve from both managers
        origin_approval = TransferManager.approve_transfer(
            solicitud.id, self.manager_zul, 'ORIGEN', 'Origin approval'
        )
        self.assertTrue(origin_approval.success)
        
        destination_approval = TransferManager.approve_transfer(
            solicitud.id, self.manager_car, 'DESTINO', 'Destination approval'
        )
        self.assertTrue(destination_approval.success)
        
        solicitud.refresh_from_db()
        self.assertTrue(solicitud.can_execute())
        
        # Execute transfer
        execution_result = TransferManager.execute_transfer(solicitud.id, self.executor)
        self.assertTrue(execution_result.success,
                      f"Transfer execution should succeed: {execution_result.message}")
        
        # Verify completeness of execution
        solicitud.refresh_from_db()
        asset.refresh_from_db()
        
        # 1. Verify request state updated
        self.assertEqual(solicitud.estado, 'EN_TRANSITO',
                        "Request should be in transit after execution")
        self.assertIsNotNone(solicitud.fecha_ejecucion,
                           "Execution date should be set")
        self.assertEqual(solicitud.ejecutado_por, self.executor,
                        "Executor should be recorded")
        
        # 2. Verify asset location updated
        self.assertEqual(asset.almacen_actual, self.warehouse_car,
                        "Asset should be moved to destination warehouse")
        
        # 3. Verify asset state updated
        self.assertEqual(asset.estado, 'EN_TRANSITO',
                        "Asset should be in transit state")
        
        # 4. Verify asset code evolved
        self.assertNotEqual(asset.codigo_actual, original_code,
                          "Asset code should have evolved")
        self.assertTrue(asset.codigo_actual.startswith('CAR-'),
                       "New code should start with destination warehouse prefix")
        self.assertTrue(asset.codigo_actual.endswith(original_code),
                       "New code should contain original code")
        
        # 5. Verify audit trail created
        movement_records = HistorialMovimientoActivo.objects.filter(
            activo=asset,
            solicitud_traslado=solicitud,
            tipo_movimiento='TRASLADO_EJECUTADO'
        )
        self.assertTrue(movement_records.exists(),
                       "Execution audit record should be created")
        
        execution_record = movement_records.first()
        self.assertEqual(execution_record.almacen_origen, self.warehouse_zul,
                        "Audit record should have correct origin")
        self.assertEqual(execution_record.almacen_destino, self.warehouse_car,
                        "Audit record should have correct destination")
        self.assertEqual(execution_record.usuario_responsable, self.executor,
                        "Audit record should have correct executor")
        
        # 6. Verify code evolution is parseable
        code_info = AssetCodeGenerator.parse_asset_code(asset.codigo_actual)
        self.assertIsNotNone(code_info, "Evolved code should be parseable")
        self.assertEqual(code_info.current_warehouse, 'CAR',
                        "Parsed code should show correct current warehouse")
        self.assertEqual(code_info.transfer_count, 1,
                        "Parsed code should show one transfer")
        
        # 7. Test transfer completion
        completion_result = TransferManager.complete_transfer(solicitud.id, self.manager_car)
        self.assertTrue(completion_result.success,
                      f"Transfer completion should succeed: {completion_result.message}")
        
        solicitud.refresh_from_db()
        asset.refresh_from_db()
        
        self.assertEqual(solicitud.estado, 'COMPLETADA',
                        "Request should be completed")
        self.assertEqual(asset.estado, 'EN_ALMACEN',
                        "Asset should be back in warehouse state")
        self.assertIsNotNone(solicitud.fecha_completada,
                           "Completion date should be set")
    
    @given(
        asset_data=asset_data(),
        request_data=transfer_request_data()
    )
    @settings(max_examples=30, deadline=25000)
    def test_property_9_execution_atomicity(self, asset_data, request_data):
        """
        Test that transfer execution is atomic - either all changes succeed or all fail.
        Part of Property 9: Transfer Execution Completeness.
        """
        # Create test asset
        asset = self.create_test_asset(self.warehouse_zul, asset_data)
        original_code = asset.codigo_actual
        original_warehouse = asset.almacen_actual
        original_state = asset.estado
        
        # Create and approve transfer request
        transfer_request = TransferRequestData(
            activo_id=asset.id,
            almacen_origen_id=self.warehouse_zul.id,
            almacen_destino_id=self.warehouse_car.id,
            solicitante_id=self.requester.id,
            **request_data
        )
        
        success, solicitud = TransferManager.create_transfer_request(transfer_request)
        assume(success)
        
        # Approve from both managers
        TransferManager.approve_transfer(solicitud.id, self.manager_zul, 'ORIGEN', 'Origin approval')
        TransferManager.approve_transfer(solicitud.id, self.manager_car, 'DESTINO', 'Destination approval')
        
        solicitud.refresh_from_db()
        original_solicitud_state = solicitud.estado
        
        # Execute transfer
        execution_result = TransferManager.execute_transfer(solicitud.id, self.executor)
        
        if execution_result.success:
            # If execution succeeded, verify all changes were made
            solicitud.refresh_from_db()
            asset.refresh_from_db()
            
            # All these should have changed together
            self.assertNotEqual(asset.codigo_actual, original_code)
            self.assertNotEqual(asset.almacen_actual, original_warehouse)
            self.assertNotEqual(asset.estado, original_state)
            self.assertNotEqual(solicitud.estado, original_solicitud_state)
            
        else:
            # If execution failed, verify no changes were made (rollback worked)
            solicitud.refresh_from_db()
            asset.refresh_from_db()
            
            # All these should remain unchanged
            self.assertEqual(asset.codigo_actual, original_code)
            self.assertEqual(asset.almacen_actual, original_warehouse)
            self.assertEqual(asset.estado, original_state)
            self.assertEqual(solicitud.estado, original_solicitud_state)
    
    # ========================================================================
    # ADDITIONAL WORKFLOW PROPERTY TESTS
    # ========================================================================
    
    @given(
        asset_data=asset_data(),
        request_data=transfer_request_data()
    )
    @settings(max_examples=30, deadline=20000)
    def test_workflow_state_consistency(self, asset_data, request_data):
        """
        Test that workflow states remain consistent throughout the process.
        """
        # Create test asset
        asset = self.create_test_asset(self.warehouse_zul, asset_data)
        
        # Create transfer request
        transfer_request = TransferRequestData(
            activo_id=asset.id,
            almacen_origen_id=self.warehouse_zul.id,
            almacen_destino_id=self.warehouse_car.id,
            solicitante_id=self.requester.id,
            **request_data
        )
        
        success, solicitud = TransferManager.create_transfer_request(transfer_request)
        assume(success)
        
        # Initial state should be PENDIENTE
        self.assertEqual(solicitud.estado, 'PENDIENTE')
        
        # After first approval, state should reflect partial approval
        TransferManager.approve_transfer(solicitud.id, self.manager_zul, 'ORIGEN', 'Origin approval')
        solicitud.refresh_from_db()
        self.assertIn(solicitud.estado, ['APROBADA_ORIGEN', 'APROBADA_COMPLETA'])
        
        # After second approval, should be completely approved
        TransferManager.approve_transfer(solicitud.id, self.manager_car, 'DESTINO', 'Destination approval')
        solicitud.refresh_from_db()
        self.assertEqual(solicitud.estado, 'APROBADA_COMPLETA')
        
        # After execution, should be in transit
        TransferManager.execute_transfer(solicitud.id, self.executor)
        solicitud.refresh_from_db()
        self.assertEqual(solicitud.estado, 'EN_TRANSITO')
        
        # After completion, should be completed
        TransferManager.complete_transfer(solicitud.id, self.manager_car)
        solicitud.refresh_from_db()
        self.assertEqual(solicitud.estado, 'COMPLETADA')
    
    @given(
        asset_data=asset_data(),
        request_data=transfer_request_data()
    )
    @settings(max_examples=20, deadline=15000)
    def test_audit_trail_completeness(self, asset_data, request_data):
        """
        Test that complete audit trail is maintained throughout transfer process.
        """
        # Create test asset
        asset = self.create_test_asset(self.warehouse_zul, asset_data)
        
        # Create and execute complete transfer
        transfer_request = TransferRequestData(
            activo_id=asset.id,
            almacen_origen_id=self.warehouse_zul.id,
            almacen_destino_id=self.warehouse_car.id,
            solicitante_id=self.requester.id,
            **request_data
        )
        
        success, solicitud = TransferManager.create_transfer_request(transfer_request)
        assume(success)
        
        # Approve and execute
        TransferManager.approve_transfer(solicitud.id, self.manager_zul, 'ORIGEN', 'Origin approval')
        TransferManager.approve_transfer(solicitud.id, self.manager_car, 'DESTINO', 'Destination approval')
        TransferManager.execute_transfer(solicitud.id, self.executor)
        TransferManager.complete_transfer(solicitud.id, self.manager_car)
        
        # Verify audit trail exists
        movement_records = HistorialMovimientoActivo.objects.filter(
            activo=asset,
            solicitud_traslado=solicitud
        ).order_by('fecha_movimiento')
        
        self.assertGreaterEqual(movement_records.count(), 1,
                              "At least one audit record should exist")
        
        # Verify audit records have required information
        for record in movement_records:
            self.assertIsNotNone(record.usuario_responsable,
                               "Audit record should have responsible user")
            self.assertIsNotNone(record.motivo,
                               "Audit record should have reason")
            self.assertIsNotNone(record.fecha_movimiento,
                               "Audit record should have timestamp")
    
    # ========================================================================
    # ERROR CONDITION TESTS
    # ========================================================================
    
    def test_invalid_approval_scenarios(self):
        """Test various invalid approval scenarios"""
        # Create test data
        asset = self.create_test_asset(self.warehouse_zul)
        
        transfer_request = TransferRequestData(
            activo_id=asset.id,
            almacen_origen_id=self.warehouse_zul.id,
            almacen_destino_id=self.warehouse_car.id,
            solicitante_id=self.requester.id,
            motivo='Test transfer for invalid scenarios',
            prioridad='NORMAL',
            fecha_limite=timezone.now() + timedelta(hours=24)
        )
        
        success, solicitud = TransferManager.create_transfer_request(transfer_request)
        self.assertTrue(success)
        
        # Test double approval from same manager
        TransferManager.approve_transfer(solicitud.id, self.manager_zul, 'ORIGEN', 'First approval')
        
        # Second approval from same manager should fail
        second_approval = TransferManager.approve_transfer(
            solicitud.id, self.manager_zul, 'ORIGEN', 'Second approval'
        )
        self.assertFalse(second_approval.success,
                        "Double approval from same manager should fail")
        
        # Test approval after rejection
        TransferManager.reject_transfer(solicitud.id, self.manager_car, 'Rejection reason')
        solicitud.refresh_from_db()
        
        # Approval after rejection should fail
        post_rejection_approval = TransferManager.approve_transfer(
            solicitud.id, self.manager_zul, 'ORIGEN', 'Post rejection approval'
        )
        self.assertFalse(post_rejection_approval.success,
                        "Approval after rejection should fail")
    
    def test_execution_without_approval(self):
        """Test that execution fails without proper approvals"""
        # Create test data
        asset = self.create_test_asset(self.warehouse_zul)
        
        transfer_request = TransferRequestData(
            activo_id=asset.id,
            almacen_origen_id=self.warehouse_zul.id,
            almacen_destino_id=self.warehouse_car.id,
            solicitante_id=self.requester.id,
            motivo='Test transfer for execution without approval',
            prioridad='NORMAL',
            fecha_limite=timezone.now() + timedelta(hours=24)
        )
        
        success, solicitud = TransferManager.create_transfer_request(transfer_request)
        self.assertTrue(success)
        
        # Try to execute without any approvals
        execution_result = TransferManager.execute_transfer(solicitud.id, self.executor)
        self.assertFalse(execution_result.success,
                        "Execution should fail without approvals")
        
        # Try to execute with only one approval
        TransferManager.approve_transfer(solicitud.id, self.manager_zul, 'ORIGEN', 'Single approval')
        
        execution_result = TransferManager.execute_transfer(solicitud.id, self.executor)
        self.assertFalse(execution_result.success,
                        "Execution should fail with only one approval")


# ============================================================================
# INTEGRATION TESTS WITH HYPOTHESIS EXAMPLES
# ============================================================================

class TransferWorkflowIntegrationTestCase(TransactionTestCase):
    """
    Integration tests with specific examples to complement property-based tests.
    """
    
    def setUp(self):
        """Set up test data - same as property test class"""
        # Create organizational structure
        self.empresa = Empresa.objects.create(
            nombre='Hidroven Test',
            codigo='HVT',
            rif='J-12345678-9'
        )
        
        self.vp_operaciones = Vicepresidencia.objects.create(
            empresa=self.empresa,
            nombre='VP Operaciones Hídricas',
            codigo='VP-OP',
            tipo='OPERACIONES_HIDRICAS'
        )
        
        self.unidad_almacenes = UnidadOrganizacional.objects.create(
            vicepresidencia=self.vp_operaciones,
            nombre='Gerencia de Almacenes',
            codigo='GER-ALM',
            tipo='GERENCIA'
        )
        
        # Create test users
        self.manager_zul = User.objects.create_user(
            username='manager_zul',
            email='manager.zul@hidroven.test',
            password='testpass123'
        )
        
        self.manager_car = User.objects.create_user(
            username='manager_car',
            email='manager.car@hidroven.test',
            password='testpass123'
        )
        
        self.requester = User.objects.create_user(
            username='requester',
            email='requester@hidroven.test',
            password='testpass123'
        )
        
        self.executor = User.objects.create_user(
            username='executor',
            email='executor@hidroven.test',
            password='testpass123'
        )
        
        # Create test warehouses
        self.warehouse_zul = AlmacenRegional.objects.create(
            unidad_organizacional=self.unidad_almacenes,
            nombre='Almacén Zulia',
            prefijo='ZUL',
            ubicacion='Maracaibo, Zulia',
            manager=self.manager_zul,
            capacidad_maxima=5000
        )
        
        self.warehouse_car = AlmacenRegional.objects.create(
            unidad_organizacional=self.unidad_almacenes,
            nombre='Almacén Carabobo',
            prefijo='CAR',
            ubicacion='Valencia, Carabobo',
            manager=self.manager_car,
            capacidad_maxima=3000
        )
    
    def test_complete_workflow_example(self):
        """Test complete workflow with specific example data"""
        # Create test asset
        asset = ActivoInventario.objects.create(
            codigo_actual='ZUL-BOMBA-000001-2024',
            codigo_original='ZUL-BOMBA-000001-2024',
            tipo_activo='BOMBA',
            descripcion='Bomba centrífuga de alta presión',
            almacen_actual=self.warehouse_zul,
            valor_unitario=2500.00,
            numero_serie='BC-HP-001',
            creado_por=self.requester
        )
        
        # Create transfer request
        transfer_request = TransferRequestData(
            activo_id=asset.id,
            almacen_origen_id=self.warehouse_zul.id,
            almacen_destino_id=self.warehouse_car.id,
            solicitante_id=self.requester.id,
            motivo='Transferencia para mantenimiento especializado en Valencia',
            prioridad='ALTA',
            fecha_limite=timezone.now() + timedelta(hours=12),
            observaciones='Requiere manejo especial debido al peso'
        )
        
        # Execute complete workflow
        success, solicitud = TransferManager.create_transfer_request(transfer_request)
        self.assertTrue(success)
        
        # Dual approval
        origin_approval = TransferManager.approve_transfer(
            solicitud.id, self.manager_zul, 'ORIGEN', 
            'Aprobado para mantenimiento. Coordinar transporte especial.'
        )
        self.assertTrue(origin_approval.success)
        
        destination_approval = TransferManager.approve_transfer(
            solicitud.id, self.manager_car, 'DESTINO',
            'Confirmado espacio disponible en taller de mantenimiento.'
        )
        self.assertTrue(destination_approval.success)
        
        # Execute transfer
        execution_result = TransferManager.execute_transfer(solicitud.id, self.executor)
        self.assertTrue(execution_result.success)
        
        # Verify asset code evolution
        asset.refresh_from_db()
        self.assertEqual(asset.codigo_actual, 'CAR-ZUL-BOMBA-000001-2024')
        self.assertEqual(asset.almacen_actual, self.warehouse_car)
        self.assertEqual(asset.estado, 'EN_TRANSITO')
        
        # Complete transfer
        completion_result = TransferManager.complete_transfer(solicitud.id, self.manager_car)
        self.assertTrue(completion_result.success)
        
        # Final verification
        solicitud.refresh_from_db()
        asset.refresh_from_db()
        
        self.assertEqual(solicitud.estado, 'COMPLETADA')
        self.assertEqual(asset.estado, 'EN_ALMACEN')
        self.assertIsNotNone(solicitud.fecha_completada)
        
        # Verify audit trail
        audit_records = HistorialMovimientoActivo.objects.filter(
            activo=asset,
            solicitud_traslado=solicitud
        ).count()
        self.assertGreaterEqual(audit_records, 1)