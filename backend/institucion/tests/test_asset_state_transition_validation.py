# ============================================================================
# PROPERTY TEST: ASSET STATE TRANSITION VALIDATION
# ============================================================================

"""
Property-based tests for asset state transition validation.

**Property 10: Asset State Transition Validation**
**Validates: Requirements 5.2, 5.3, 5.4**

This module tests the AssetStateManager's ability to:
- Validate state transitions according to business rules (Requirement 5.2)
- Reject invalid transitions (Requirement 5.3)
- Create audit trails for state changes (Requirement 5.4)
"""

import pytest
from django.test import TestCase, TransactionTestCase
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.utils import timezone
from django.db import transaction
from hypothesis import given, assume, settings, strategies as st
from hypothesis.extra.django import TestCase as HypothesisTestCase
from decimal import Decimal
import logging

from .models import (
    Empresa, Vicepresidencia, UnidadOrganizacional, AlmacenRegional,
    ActivoInventario, HistorialMovimientoActivo, SolicitudTraslado
)
from .state_management import AssetStateManager
from .services import AssetCodeGenerator

User = get_user_model()
logger = logging.getLogger(__name__)


# ============================================================================
# TEST DATA STRATEGIES
# ============================================================================

def valid_asset_state_strategy():
    """Strategy for generating valid asset states"""
    return st.sampled_from(AssetStateManager.ASSET_STATES)


def asset_state_transition_strategy():
    """Strategy for generating asset state transitions"""
    return st.tuples(
        valid_asset_state_strategy(),  # from_state
        valid_asset_state_strategy()   # to_state
    )


def valid_state_transition_strategy():
    """Strategy for generating only valid state transitions based on business rules"""
    valid_transitions = []
    for rule in AssetStateManager.STATE_TRANSITION_RULES:
        if rule.allowed:
            valid_transitions.append((rule.from_state, rule.to_state))
    
    return st.sampled_from(valid_transitions)


def invalid_state_transition_strategy():
    """Strategy for generating invalid state transitions"""
    # Get all possible transitions
    all_states = AssetStateManager.ASSET_STATES
    all_transitions = [(from_state, to_state) for from_state in all_states for to_state in all_states]
    
    # Get valid transitions
    valid_transitions = set()
    for rule in AssetStateManager.STATE_TRANSITION_RULES:
        if rule.allowed:
            valid_transitions.add((rule.from_state, rule.to_state))
    
    # Add same-state transitions (always valid)
    for state in all_states:
        valid_transitions.add((state, state))
    
    # Get invalid transitions
    invalid_transitions = [t for t in all_transitions if t not in valid_transitions]
    
    if not invalid_transitions:
        # If no invalid transitions exist, create some artificial ones
        return st.tuples(
            st.sampled_from(all_states),
            st.text(min_size=1, max_size=20).filter(lambda x: x not in all_states)
        )
    
    return st.sampled_from(invalid_transitions)


@st.composite
def asset_data_strategy(draw):
    """Strategy for generating asset data"""
    return {
        'tipo_activo': draw(st.sampled_from([choice[0] for choice in ActivoInventario.ASSET_TYPES])),
        'descripcion': draw(st.text(min_size=10, max_size=200)),
        'valor_unitario': draw(st.decimals(
            min_value=Decimal('0.01'),
            max_value=Decimal('999999.99'),
            places=2
        )),
        'numero_serie': draw(st.text(min_size=0, max_size=50)),
        'estado': draw(valid_asset_state_strategy())
    }


@st.composite
def user_data_strategy(draw):
    """Strategy for generating user data"""
    return {
        'username': draw(st.text(
            min_size=3, max_size=20,
            alphabet=st.characters(whitelist_categories=('Lu', 'Ll', 'Nd'), whitelist_characters='_')
        ).filter(lambda x: x and x[0].isalpha())),
        'email': draw(st.emails()),
        'first_name': draw(st.text(min_size=1, max_size=30)),
        'last_name': draw(st.text(min_size=1, max_size=30))
    }


@st.composite
def state_change_data_strategy(draw):
    """Strategy for generating state change data"""
    return {
        'motivo': draw(st.text(min_size=5, max_size=200)),
        'observaciones': draw(st.text(min_size=0, max_size=500)),
        'auto_triggered': draw(st.booleans()),
        'trigger_condition': draw(st.one_of(
            st.none(),
            st.sampled_from(['transfer_approved', 'transfer_completed', 'maintenance_required'])
        ))
    }


# ============================================================================
# TEST BASE CLASS
# ============================================================================

class AssetStateTransitionTestCase(HypothesisTestCase, TransactionTestCase):
    """
    Base test case for asset state transition property tests.
    Uses TransactionTestCase to handle database transactions properly.
    """
    
    def setUp(self):
        """Set up test data"""
        import uuid
        unique_id = str(uuid.uuid4())[:8]
        
        # Create organizational hierarchy
        self.empresa = Empresa.objects.create(
            nombre=f'Hidroven Test {unique_id}',
            codigo=f'HIDRO_TEST_{unique_id}'
        )
        
        self.vp_operaciones = Vicepresidencia.objects.create(
            empresa=self.empresa,
            nombre=f'VP Operaciones Hídricas Test {unique_id}',
            codigo=f'VP_OP_TEST_{unique_id}',
            tipo='OPERACIONES_HIDRICAS'
        )
        
        self.unidad_almacenes = UnidadOrganizacional.objects.create(
            vicepresidencia=self.vp_operaciones,
            nombre=f'Gerencia de Almacenes Test {unique_id}',
            codigo=f'GA_TEST_{unique_id}',
            tipo='GERENCIA'
        )
        
        # Create test warehouse
        # Use a different prefix for each test to avoid conflicts
        available_prefixes = ['CAR', 'MIR', 'ARA', 'LAR', 'TAC', 'BOL', 'ANZ', 'MON']
        import random
        selected_prefix = random.choice(available_prefixes)
        
        self.almacen = AlmacenRegional.objects.create(
            unidad_organizacional=self.unidad_almacenes,
            nombre=f'Almacén Regional {selected_prefix} Test {unique_id}',
            prefijo=selected_prefix,
            ubicacion=f'Test Location {selected_prefix}',
            capacidad_maxima=1000
        )
        
        # Create test users
        self.test_user = User.objects.create_user(
            username=f'test_user_{unique_id}',
            email=f'test_{unique_id}@example.com',
            password='testpass123'
        )
        
        self.manager_user = User.objects.create_user(
            username=f'manager_user_{unique_id}',
            email=f'manager_{unique_id}@example.com',
            password='managerpass123'
        )
        
        # Set warehouse manager
        self.almacen.manager = self.manager_user
        self.almacen.save()
    
    def create_test_asset(self, estado='EN_ALMACEN', **kwargs):
        """Create a test asset with given state"""
        from django.contrib.contenttypes.models import ContentType
        from inventario.models import ChemicalProduct
        
        # Create a dummy product for the generic foreign key
        try:
            chemical_product = ChemicalProduct.objects.first()
            if not chemical_product:
                chemical_product = ChemicalProduct.objects.create(
                    sku='TEST-CHEM-001',
                    nombre='Test Chemical Product',
                    descripcion='Test chemical for asset testing',
                    stock_actual=100,
                    stock_minimo=10,
                    precio_unitario=Decimal('50.00')
                )
        except Exception:
            # If ChemicalProduct doesn't exist or fails, create a minimal content type reference
            chemical_product = None
        
        defaults = {
            'tipo_activo': 'BOMBA',
            'descripcion': 'Bomba de agua para pruebas',
            'almacen_actual': self.almacen,
            'estado': estado,
            'valor_unitario': Decimal('1000.00'),
            'creado_por': self.test_user,
            'actualizado_por': self.test_user
        }
        
        # Set up generic foreign key fields
        if chemical_product:
            defaults['producto_inventario_type'] = ContentType.objects.get_for_model(ChemicalProduct)
            defaults['producto_inventario_id'] = chemical_product.id
        else:
            # Use User model as a fallback for testing
            defaults['producto_inventario_type'] = ContentType.objects.get_for_model(User)
            defaults['producto_inventario_id'] = self.test_user.id
        
        defaults.update(kwargs)
        
        # Generate unique asset code
        codigo = AssetCodeGenerator.generate_asset_code(
            warehouse_prefix=defaults['almacen_actual'].prefijo,
            asset_type=defaults['tipo_activo']
        )
        defaults['codigo_actual'] = codigo
        defaults['codigo_original'] = codigo
        
        return ActivoInventario.objects.create(**defaults)
    
    def assertDatabaseIntegrity(self, model_class):
        """Assert database integrity for the given model"""
        try:
            # Check that all objects can be retrieved
            count = model_class.objects.count()
            self.assertGreaterEqual(count, 0)
            
            # Check that all objects can be validated
            for obj in model_class.objects.all():
                obj.full_clean()
                
        except Exception as e:
            self.fail(f"Database integrity check failed for {model_class.__name__}: {str(e)}")


# ============================================================================
# PROPERTY TESTS
# ============================================================================

class AssetStateTransitionValidationPropertyTests(AssetStateTransitionTestCase):
    """
    **Property 10: Asset State Transition Validation**
    **Validates: Requirements 5.2, 5.3, 5.4**
    
    Property-based tests for asset state transition validation system.
    Tests that state transitions follow business rules, invalid transitions
    are rejected, and state changes are properly audited.
    """
    
    @given(valid_state_transition_strategy())
    @settings(max_examples=100, deadline=None)
    def test_valid_state_transitions_are_allowed(self, transition_data):
        """
        Property: All valid state transitions defined in business rules
        should be allowed by the validation system.
        
        **Validates: Requirements 5.2**
        """
        from_state, to_state = transition_data
        
        # Test the validation method
        is_valid, message = AssetStateManager.validate_state_transition(from_state, to_state)
        
        # Valid transitions should always be allowed
        self.assertTrue(
            is_valid,
            f"Valid transition {from_state} → {to_state} was rejected: {message}"
        )
        
        # Message should contain business rule description
        self.assertIsInstance(message, str)
        self.assertGreater(len(message), 0)
    
    @given(invalid_state_transition_strategy())
    @settings(max_examples=100, deadline=None)
    def test_invalid_state_transitions_are_rejected(self, transition_data):
        """
        Property: All invalid state transitions not defined in business rules
        should be rejected by the validation system.
        
        **Validates: Requirements 5.3**
        """
        from_state, to_state = transition_data
        
        # Skip if either state is invalid (not in ASSET_STATES)
        assume(from_state in AssetStateManager.ASSET_STATES)
        assume(to_state in AssetStateManager.ASSET_STATES)
        
        # Test the validation method
        is_valid, message = AssetStateManager.validate_state_transition(from_state, to_state)
        
        # Invalid transitions should always be rejected
        self.assertFalse(
            is_valid,
            f"Invalid transition {from_state} → {to_state} was allowed: {message}"
        )
        
        # Error message should explain why transition is not allowed
        self.assertIsInstance(message, str)
        self.assertGreater(len(message), 0)
        self.assertIn("not allowed", message.lower())
    
    @given(
        valid_state_transition_strategy(),
        state_change_data_strategy()
    )
    @settings(max_examples=100, deadline=None)
    def test_valid_state_changes_create_audit_trail(self, transition_data, change_data):
        """
        Property: All valid state changes should create proper audit trail
        records with complete information.
        
        **Validates: Requirements 5.4**
        """
        from_state, to_state = transition_data
        
        # Skip same-state transitions for this test
        assume(from_state != to_state)
        
        # Skip automatic triggers that don't match the transition
        if change_data['auto_triggered'] and change_data['trigger_condition']:
            # Only allow valid automatic trigger combinations
            valid_auto_transitions = {
                ('EN_ALMACEN', 'EN_TRANSITO'): 'transfer_approved',
                ('EN_TRANSITO', 'EN_ALMACEN'): 'transfer_completed'
            }
            expected_trigger = valid_auto_transitions.get((from_state, to_state))
            if expected_trigger != change_data['trigger_condition']:
                # Skip this combination as it's not a valid automatic transition
                assume(False)
        
        # Create asset in initial state
        asset = self.create_test_asset(estado=from_state)
        
        # Get initial history count after asset creation (asset creation may create audit records)
        initial_history_count = HistorialMovimientoActivo.objects.filter(
            activo=asset,
            tipo_movimiento__startswith='CAMBIO_ESTADO'
        ).count()
        
        # Perform state change
        success = AssetStateManager.change_asset_state(
            activo=asset,
            new_state=to_state,
            user=self.test_user,
            motivo=change_data['motivo'],
            observaciones=change_data['observaciones'],
            auto_triggered=change_data['auto_triggered'],
            trigger_condition=change_data['trigger_condition']
        )
        
        # Verify state change was successful
        self.assertTrue(success, f"Valid state change {from_state} → {to_state} failed")
        
        # Refresh asset from database
        asset.refresh_from_db()
        self.assertEqual(asset.estado, to_state)
        
        # Verify audit trail was created
        new_history_count = HistorialMovimientoActivo.objects.filter(
            activo=asset,
            tipo_movimiento__startswith='CAMBIO_ESTADO'
        ).count()
        self.assertEqual(
            new_history_count,
            initial_history_count + 1,
            "Audit trail record was not created for state change"
        )
        
        # Get the latest audit record
        latest_record = HistorialMovimientoActivo.objects.filter(
            activo=asset,
            tipo_movimiento__startswith='CAMBIO_ESTADO'
        ).latest('fecha_movimiento')
        
        # Verify audit record contains correct information
        self.assertEqual(latest_record.estado_anterior, from_state)
        self.assertEqual(latest_record.estado_nuevo, to_state)
        self.assertEqual(latest_record.usuario_responsable, self.test_user)
        self.assertIn(change_data['motivo'], latest_record.motivo)
        self.assertEqual(latest_record.observaciones, change_data['observaciones'])
        
        # Verify automatic trigger information is recorded
        if change_data['auto_triggered'] and change_data['trigger_condition']:
            self.assertIn('AUTOMÁTICO', latest_record.motivo)
            self.assertIn(change_data['trigger_condition'], latest_record.motivo)
            self.assertIn('CAMBIO_ESTADO_AUTO', latest_record.tipo_movimiento)
        else:
            self.assertEqual(latest_record.tipo_movimiento, 'CAMBIO_ESTADO')
        
        # Verify database integrity
        self.assertDatabaseIntegrity(HistorialMovimientoActivo)
    
    @given(
        invalid_state_transition_strategy(),
        state_change_data_strategy()
    )
    @settings(max_examples=100, deadline=None)
    def test_invalid_state_changes_raise_validation_error(self, transition_data, change_data):
        """
        Property: All invalid state changes should raise ValidationError
        and not modify the asset state or create audit records.
        
        **Validates: Requirements 5.3**
        """
        from_state, to_state = transition_data
        
        # Skip if either state is invalid (not in ASSET_STATES)
        assume(from_state in AssetStateManager.ASSET_STATES)
        assume(to_state in AssetStateManager.ASSET_STATES)
        
        # Skip same-state transitions (always valid)
        assume(from_state != to_state)
        
        # Create asset in initial state
        asset = self.create_test_asset(estado=from_state)
        initial_history_count = HistorialMovimientoActivo.objects.filter(activo=asset).count()
        
        # Attempt invalid state change
        with self.assertRaises(ValidationError) as cm:
            AssetStateManager.change_asset_state(
                activo=asset,
                new_state=to_state,
                user=self.test_user,
                motivo=change_data['motivo'],
                observaciones=change_data['observaciones']
            )
        
        # Verify error message mentions state transition
        error_message = str(cm.exception)
        self.assertIn("State transition not allowed", error_message)
        
        # Verify asset state was not changed
        asset.refresh_from_db()
        self.assertEqual(asset.estado, from_state)
        
        # Verify no audit record was created
        final_history_count = HistorialMovimientoActivo.objects.filter(activo=asset).count()
        self.assertEqual(
            final_history_count,
            initial_history_count,
            "Audit record was created for failed state change"
        )
        
        # Verify database integrity
        self.assertDatabaseIntegrity(ActivoInventario)
        self.assertDatabaseIntegrity(HistorialMovimientoActivo)
    
    @given(
        asset_data_strategy(),
        st.lists(valid_state_transition_strategy(), min_size=1, max_size=5)
    )
    @settings(max_examples=100, deadline=None)
    def test_state_transition_sequence_maintains_consistency(self, asset_data, transition_sequence):
        """
        Property: A sequence of valid state transitions should maintain
        system consistency and create complete audit trail.
        
        **Validates: Requirements 5.2, 5.4**
        """
        # Create asset with initial state
        initial_state = transition_sequence[0][0]  # from_state of first transition
        asset = self.create_test_asset(
            estado=initial_state,
            tipo_activo=asset_data['tipo_activo'],
            descripcion=asset_data['descripcion'],
            valor_unitario=asset_data['valor_unitario'],
            numero_serie=asset_data['numero_serie']
        )
        
        current_state = initial_state
        expected_audit_count = 0
        
        # Apply each transition in sequence
        for i, (from_state, to_state) in enumerate(transition_sequence):
            # Only apply transition if it starts from current state
            if from_state == current_state:
                # Perform state change
                success = AssetStateManager.change_asset_state(
                    activo=asset,
                    new_state=to_state,
                    user=self.test_user,
                    motivo=f'Transition {i+1}: {from_state} → {to_state}',
                    observaciones=f'Step {i+1} in transition sequence'
                )
                
                self.assertTrue(success, f"Valid transition {from_state} → {to_state} failed")
                
                # Update current state and expected audit count
                if from_state != to_state:
                    current_state = to_state
                    expected_audit_count += 1
        
        # Verify final asset state
        asset.refresh_from_db()
        self.assertEqual(asset.estado, current_state)
        
        # Verify complete audit trail
        audit_records = HistorialMovimientoActivo.objects.filter(
            activo=asset,
            tipo_movimiento__startswith='CAMBIO_ESTADO'
        ).order_by('fecha_movimiento')
        
        self.assertEqual(
            audit_records.count(),
            expected_audit_count,
            f"Expected {expected_audit_count} audit records, got {audit_records.count()}"
        )
        
        # Verify audit trail sequence is correct
        previous_state = initial_state
        for record in audit_records:
            self.assertEqual(record.estado_anterior, previous_state)
            previous_state = record.estado_nuevo
        
        # Final state in audit should match asset state
        if audit_records.exists():
            final_record = audit_records.last()
            self.assertEqual(final_record.estado_nuevo, current_state)
        
        # Verify database integrity
        self.assertDatabaseIntegrity(ActivoInventario)
        self.assertDatabaseIntegrity(HistorialMovimientoActivo)
    
    @given(
        asset_data_strategy(),
        st.sampled_from(['transfer_approved', 'transfer_completed'])
    )
    @settings(max_examples=100, deadline=None)
    def test_automatic_state_transitions_follow_business_rules(self, asset_data, trigger_condition):
        """
        Property: Automatic state transitions triggered by system events
        should follow the same business rules as manual transitions.
        
        **Validates: Requirements 5.2, 5.4**
        """
        # Determine appropriate initial state for trigger condition
        if trigger_condition == 'transfer_approved':
            initial_state = 'EN_ALMACEN'
            expected_new_state = 'EN_TRANSITO'
        elif trigger_condition == 'transfer_completed':
            initial_state = 'EN_TRANSITO'
            expected_new_state = 'EN_ALMACEN'
        else:
            assume(False)  # Skip unsupported trigger conditions
        
        # Create asset in appropriate initial state
        asset = self.create_test_asset(
            estado=initial_state,
            tipo_activo=asset_data['tipo_activo'],
            descripcion=asset_data['descripcion'],
            valor_unitario=asset_data['valor_unitario']
        )
        
        # Verify automatic transition is allowed
        can_auto_transition = AssetStateManager.can_transition_automatically(
            initial_state, expected_new_state, trigger_condition
        )
        self.assertTrue(
            can_auto_transition,
            f"Automatic transition {initial_state} → {expected_new_state} "
            f"for trigger {trigger_condition} should be allowed"
        )
        
        # Perform automatic state change
        success = AssetStateManager.change_asset_state(
            activo=asset,
            new_state=expected_new_state,
            user=self.test_user,
            motivo=f'Automatic transition triggered by {trigger_condition}',
            auto_triggered=True,
            trigger_condition=trigger_condition
        )
        
        self.assertTrue(success, "Automatic state transition failed")
        
        # Verify asset state was changed
        asset.refresh_from_db()
        self.assertEqual(asset.estado, expected_new_state)
        
        # Verify audit trail includes automatic trigger information
        latest_record = HistorialMovimientoActivo.objects.filter(activo=asset).latest('fecha_movimiento')
        self.assertEqual(latest_record.estado_anterior, initial_state)
        self.assertEqual(latest_record.estado_nuevo, expected_new_state)
        self.assertIn('AUTOMÁTICO', latest_record.motivo)
        self.assertIn(trigger_condition, latest_record.motivo)
        self.assertIn('CAMBIO_ESTADO_AUTO', latest_record.tipo_movimiento)
        
        # Verify database integrity
        self.assertDatabaseIntegrity(ActivoInventario)
        self.assertDatabaseIntegrity(HistorialMovimientoActivo)
    
    @given(
        asset_data_strategy(),
        st.lists(user_data_strategy(), min_size=1, max_size=3)
    )
    @settings(max_examples=100, deadline=None)
    def test_state_changes_by_different_users_maintain_audit_integrity(self, asset_data, users_data):
        """
        Property: State changes performed by different users should maintain
        audit trail integrity and properly track responsible users.
        
        **Validates: Requirements 5.4**
        """
        # Create test users
        test_users = []
        for i, user_data in enumerate(users_data):
            user = User.objects.create_user(
                username=f"{user_data['username']}_{i}",
                email=f"{i}_{user_data['email']}",
                first_name=user_data['first_name'],
                last_name=user_data['last_name'],
                password='testpass123'
            )
            test_users.append(user)
        
        # Create asset
        asset = self.create_test_asset(
            estado='EN_ALMACEN',
            tipo_activo=asset_data['tipo_activo'],
            descripcion=asset_data['descripcion'],
            valor_unitario=asset_data['valor_unitario']
        )
        
        # Perform state changes with different users
        valid_transitions = [
            ('EN_ALMACEN', 'MANTENIMIENTO'),
            ('MANTENIMIENTO', 'EN_ALMACEN'),
            ('EN_ALMACEN', 'INSTALADO'),
            ('INSTALADO', 'EN_USO')
        ]
        
        current_state = 'EN_ALMACEN'
        audit_count = 0
        
        for i, user in enumerate(test_users):
            # Find a valid transition from current state
            possible_transitions = [t for t in valid_transitions if t[0] == current_state]
            if not possible_transitions:
                break
            
            from_state, to_state = possible_transitions[0]
            
            # Perform state change
            success = AssetStateManager.change_asset_state(
                activo=asset,
                new_state=to_state,
                user=user,
                motivo=f'State change by user {user.username}',
                observaciones=f'Change performed by {user.get_full_name()}'
            )
            
            if success and from_state != to_state:
                current_state = to_state
                audit_count += 1
        
        # Verify audit trail integrity
        audit_records = HistorialMovimientoActivo.objects.filter(
            activo=asset,
            tipo_movimiento__startswith='CAMBIO_ESTADO'
        ).order_by('fecha_movimiento')
        
        self.assertEqual(audit_records.count(), audit_count)
        
        # Verify each audit record has correct user information
        for record in audit_records:
            self.assertIn(record.usuario_responsable, test_users)
            self.assertIn(record.usuario_responsable.username, record.motivo)
            self.assertIsNotNone(record.fecha_movimiento)
            self.assertIsNotNone(record.usuario_responsable)
        
        # Verify database integrity
        self.assertDatabaseIntegrity(ActivoInventario)
        self.assertDatabaseIntegrity(HistorialMovimientoActivo)


# ============================================================================
# INTEGRATION TESTS
# ============================================================================

class AssetStateTransitionIntegrationTests(AssetStateTransitionTestCase):
    """
    Integration tests for asset state transition validation with transfer workflow.
    """
    
    def test_transfer_workflow_state_transitions(self):
        """
        Test that transfer workflow properly triggers state transitions.
        """
        # Create asset in warehouse
        asset = self.create_test_asset(estado='EN_ALMACEN')
        
        # Create destination warehouse
        almacen_destino = AlmacenRegional.objects.create(
            unidad_organizacional=self.unidad_almacenes,
            nombre='Almacén Regional Carabobo Test',
            prefijo='CAR',
            ubicacion='Valencia, Carabobo',
            capacidad_maxima=1000,
            manager=self.manager_user
        )
        
        # Create transfer request
        solicitud = SolicitudTraslado.objects.create(
            activo=asset,
            almacen_origen=self.almacen,
            almacen_destino=almacen_destino,
            solicitante=self.test_user,
            motivo='Transfer for testing state transitions',
            fecha_limite=timezone.now() + timezone.timedelta(days=7),
            prioridad='NORMAL'
        )
        
        # Test transfer approval triggers state change
        AssetStateManager.handle_transfer_state_changes(
            solicitud_traslado=solicitud,
            stage='approved',
            user=self.manager_user
        )
        
        # Verify asset state changed to EN_TRANSITO
        asset.refresh_from_db()
        self.assertEqual(asset.estado, 'EN_TRANSITO')
        
        # Test transfer completion triggers state change
        AssetStateManager.handle_transfer_state_changes(
            solicitud_traslado=solicitud,
            stage='completed',
            user=self.manager_user
        )
        
        # Verify asset state changed back to EN_ALMACEN
        asset.refresh_from_db()
        self.assertEqual(asset.estado, 'EN_ALMACEN')
        
        # Verify audit trail was created
        audit_records = HistorialMovimientoActivo.objects.filter(
            activo=asset,
            tipo_movimiento__startswith='CAMBIO_ESTADO_AUTO'
        )
        self.assertEqual(audit_records.count(), 2)
    
    def test_asset_state_prevents_invalid_transfers(self):
        """
        Test that assets in certain states cannot be transferred.
        """
        # Create asset in EN_TRANSITO state
        asset = self.create_test_asset(estado='EN_TRANSITO')
        
        # Verify asset cannot be transferred
        can_transfer, message = AssetStateManager.validate_transfer_request_state(asset)
        self.assertFalse(can_transfer)
        self.assertIn("transit", message.lower())


if __name__ == '__main__':
    pytest.main([__file__])