"""
Test suite for enhanced transfer workflow models.
Tests the dual approval workflow, state tracking, and business rules.
"""

import pytest
from django.test import TestCase
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.utils import timezone
from datetime import timedelta

from .models import (
    SolicitudTraslado, AprobacionTraslado, ActivoInventario, 
    AlmacenRegional, Empresa, Vicepresidencia, UnidadOrganizacional
)

User = get_user_model()


class TransferWorkflowModelsTestCase(TestCase):
    """Test case for transfer workflow models enhancements"""
    
    def setUp(self):
        """Set up test data"""
        # Create organizational structure
        self.empresa = Empresa.objects.create(
            nombre='Hidroven',
            codigo='HID'
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
            codigo='GA-001',
            tipo='GERENCIA'
        )
        
        # Create users
        self.manager_zul = User.objects.create_user(
            username='manager_zul',
            email='manager.zul@hidroven.com',
            password='testpass123'
        )
        
        self.manager_car = User.objects.create_user(
            username='manager_car',
            email='manager.car@hidroven.com',
            password='testpass123'
        )
        
        self.solicitante = User.objects.create_user(
            username='solicitante',
            email='solicitante@hidroven.com',
            password='testpass123'
        )
        
        # Create warehouses
        self.almacen_zul = AlmacenRegional.objects.create(
            unidad_organizacional=self.unidad_almacenes,
            nombre='Almacén Regional Zulia',
            prefijo='ZUL',
            ubicacion='Maracaibo, Zulia',
            manager=self.manager_zul
        )
        
        self.almacen_car = AlmacenRegional.objects.create(
            unidad_organizacional=self.unidad_almacenes,
            nombre='Almacén Regional Carabobo',
            prefijo='CAR',
            ubicacion='Valencia, Carabobo',
            manager=self.manager_car
        )
        
        # Create a dummy product for the generic foreign key
        from django.contrib.contenttypes.models import ContentType
        from catalogo.models import CategoriaProducto, Marca
        
        # Create category and brand
        categoria = CategoriaProducto.objects.create(
            nombre='Bombas',
            descripcion='Bombas de agua'
        )
        
        marca = Marca.objects.create(
            nombre='TestBrand',
            descripcion='Test brand for testing'
        )
        
        # Create a simple product model for testing
        # We'll use the ContentType model itself as a dummy product
        self.content_type = ContentType.objects.get_for_model(ContentType)
        
        # Create asset
        self.activo = ActivoInventario.objects.create(
            codigo_actual='ZUL-BOMBA-000001-2024',
            codigo_original='ZUL-BOMBA-000001-2024',
            tipo_activo='BOMBA',
            descripcion='Bomba centrífuga 5HP',
            almacen_actual=self.almacen_zul,
            estado='EN_ALMACEN',
            valor_unitario=5000.00,
            producto_inventario_type=self.content_type,
            producto_inventario_id=self.content_type.id,
            creado_por=self.solicitante
        )
    
    def test_solicitud_traslado_creation(self):
        """Test basic transfer request creation"""
        solicitud = SolicitudTraslado.objects.create(
            activo=self.activo,
            almacen_origen=self.almacen_zul,
            almacen_destino=self.almacen_car,
            solicitante=self.solicitante,
            motivo='Reubicación por demanda operativa',
            fecha_limite=timezone.now() + timedelta(days=7),
            prioridad='NORMAL'
        )
        
        # Check that request number was generated
        self.assertIsNotNone(solicitud.numero_solicitud)
        self.assertTrue(solicitud.numero_solicitud.startswith('ST-'))
        
        # Check initial state
        self.assertEqual(solicitud.estado, 'PENDIENTE')
        
        # Check approval status
        approval_status = solicitud.get_approval_status()
        self.assertFalse(approval_status['origen_aprobado'])
        self.assertFalse(approval_status['destino_aprobado'])
        self.assertTrue(approval_status['pendiente_origen'])
        self.assertTrue(approval_status['pendiente_destino'])
    
    def test_dual_approval_workflow(self):
        """Test the dual approval workflow"""
        # Create transfer request
        solicitud = SolicitudTraslado.objects.create(
            activo=self.activo,
            almacen_origen=self.almacen_zul,
            almacen_destino=self.almacen_car,
            solicitante=self.solicitante,
            motivo='Test transfer',
            fecha_limite=timezone.now() + timedelta(days=7),
            prioridad='NORMAL'
        )
        
        # Test origin approval
        aprobacion_origen = AprobacionTraslado.create_approval(
            solicitud=solicitud,
            aprobador=self.manager_zul,
            tipo_aprobacion='ORIGEN',
            decision='APROBADO',
            comentarios='Aprobado para traslado'
        )
        
        # Check that solicitud state was updated
        solicitud.refresh_from_db()
        self.assertEqual(solicitud.estado, 'APROBADA_ORIGEN')
        self.assertEqual(solicitud.aprobacion_origen, aprobacion_origen)
        
        # Test destination approval
        aprobacion_destino = AprobacionTraslado.create_approval(
            solicitud=solicitud,
            aprobador=self.manager_car,
            tipo_aprobacion='DESTINO',
            decision='APROBADO',
            comentarios='Recibido con capacidad disponible'
        )
        
        # Check that solicitud state was updated to fully approved
        solicitud.refresh_from_db()
        self.assertEqual(solicitud.estado, 'APROBADA_COMPLETA')
        self.assertEqual(solicitud.aprobacion_destino, aprobacion_destino)
        
        # Check that transfer can now be executed
        self.assertTrue(solicitud.can_execute())
    
    def test_approval_rejection(self):
        """Test approval rejection workflow"""
        solicitud = SolicitudTraslado.objects.create(
            activo=self.activo,
            almacen_origen=self.almacen_zul,
            almacen_destino=self.almacen_car,
            solicitante=self.solicitante,
            motivo='Test transfer',
            fecha_limite=timezone.now() + timedelta(days=7),
            prioridad='NORMAL'
        )
        
        # Reject from origin
        AprobacionTraslado.create_approval(
            solicitud=solicitud,
            aprobador=self.manager_zul,
            tipo_aprobacion='ORIGEN',
            decision='RECHAZADO',
            comentarios='Asset needed for local operations'
        )
        
        # Check that solicitud state was updated to rejected
        solicitud.refresh_from_db()
        self.assertEqual(solicitud.estado, 'RECHAZADA')
        
        # Check that transfer cannot be executed
        self.assertFalse(solicitud.can_execute())
    
    def test_workflow_validation(self):
        """Test workflow validation rules"""
        # Test same warehouse validation
        with self.assertRaises(ValidationError):
            SolicitudTraslado.objects.create(
                activo=self.activo,
                almacen_origen=self.almacen_zul,
                almacen_destino=self.almacen_zul,  # Same as origin
                solicitante=self.solicitante,
                motivo='Invalid transfer',
                fecha_limite=timezone.now() + timedelta(days=7),
                prioridad='NORMAL'
            )
        
        # Test asset location validation
        activo_wrong_location = ActivoInventario.objects.create(
            codigo_actual='CAR-BOMBA-000002-2024',
            codigo_original='CAR-BOMBA-000002-2024',
            tipo_activo='BOMBA',
            descripcion='Bomba en CAR',
            almacen_actual=self.almacen_car,
            estado='EN_ALMACEN',
            valor_unitario=3000.00,
            producto_inventario_type=self.content_type,
            producto_inventario_id=self.content_type.id,
            creado_por=self.solicitante
        )
        
        with self.assertRaises(ValidationError):
            SolicitudTraslado.objects.create(
                activo=activo_wrong_location,
                almacen_origen=self.almacen_zul,  # Asset is not here
                almacen_destino=self.almacen_car,
                solicitante=self.solicitante,
                motivo='Invalid transfer',
                fecha_limite=timezone.now() + timedelta(days=7),
                prioridad='NORMAL'
            )
    
    def test_approval_authorization(self):
        """Test that only authorized managers can approve"""
        solicitud = SolicitudTraslado.objects.create(
            activo=self.activo,
            almacen_origen=self.almacen_zul,
            almacen_destino=self.almacen_car,
            solicitante=self.solicitante,
            motivo='Test transfer',
            fecha_limite=timezone.now() + timedelta(days=7),
            prioridad='NORMAL'
        )
        
        # Test unauthorized approval
        with self.assertRaises(ValidationError):
            AprobacionTraslado.create_approval(
                solicitud=solicitud,
                aprobador=self.manager_car,  # Wrong manager for origin
                tipo_aprobacion='ORIGEN',
                decision='APROBADO',
                comentarios='Unauthorized approval'
            )
    
    def test_manager_dashboard_queries(self):
        """Test manager dashboard query methods"""
        # Create multiple requests
        solicitud1 = SolicitudTraslado.objects.create(
            activo=self.activo,
            almacen_origen=self.almacen_zul,
            almacen_destino=self.almacen_car,
            solicitante=self.solicitante,
            motivo='Transfer 1',
            fecha_limite=timezone.now() + timedelta(days=7),
            prioridad='NORMAL'
        )
        
        # Create another asset for second request
        activo2 = ActivoInventario.objects.create(
            codigo_actual='ZUL-MOTOR-000001-2024',
            codigo_original='ZUL-MOTOR-000001-2024',
            tipo_activo='MOTOR',
            descripcion='Motor eléctrico 10HP',
            almacen_actual=self.almacen_zul,
            estado='EN_ALMACEN',
            valor_unitario=8000.00,
            producto_inventario_type=self.content_type,
            producto_inventario_id=self.content_type.id,
            creado_por=self.solicitante
        )
        
        solicitud2 = SolicitudTraslado.objects.create(
            activo=activo2,
            almacen_origen=self.almacen_zul,
            almacen_destino=self.almacen_car,
            solicitante=self.solicitante,
            motivo='Transfer 2',
            fecha_limite=timezone.now() + timedelta(days=3),
            prioridad='ALTA'
        )
        
        # Test pending requests for manager
        pending = SolicitudTraslado.get_pending_for_manager(self.manager_zul)
        self.assertEqual(pending.count(), 2)
        
        # Test dashboard stats
        stats = SolicitudTraslado.get_dashboard_stats_for_manager(self.manager_zul)
        self.assertEqual(stats['pending_approvals'], 2)
        self.assertEqual(stats['total_requests'], 2)
        
        # Test high priority requests
        high_priority = SolicitudTraslado.get_high_priority_requests(self.manager_zul)
        self.assertEqual(high_priority.count(), 1)
        self.assertEqual(high_priority.first(), solicitud2)
    
    def test_workflow_timeline(self):
        """Test workflow timeline functionality"""
        solicitud = SolicitudTraslado.objects.create(
            activo=self.activo,
            almacen_origen=self.almacen_zul,
            almacen_destino=self.almacen_car,
            solicitante=self.solicitante,
            motivo='Test transfer',
            fecha_limite=timezone.now() + timedelta(days=7),
            prioridad='NORMAL'
        )
        
        # Add approvals
        AprobacionTraslado.create_approval(
            solicitud=solicitud,
            aprobador=self.manager_zul,
            tipo_aprobacion='ORIGEN',
            decision='APROBADO',
            comentarios='Origin approval'
        )
        
        AprobacionTraslado.create_approval(
            solicitud=solicitud,
            aprobador=self.manager_car,
            tipo_aprobacion='DESTINO',
            decision='APROBADO',
            comentarios='Destination approval'
        )
        
        # Get timeline
        timeline = solicitud.get_workflow_timeline()
        
        # Should have creation + 2 approvals
        self.assertEqual(len(timeline), 3)
        
        # Check timeline events
        events = [event['evento'] for event in timeline]
        self.assertIn('Solicitud Creada', events)
        self.assertIn('Aprobación Origen - Aprobado', events)
        self.assertIn('Aprobación Destino - Aprobado', events)
    
    def test_approval_statistics(self):
        """Test approval statistics functionality"""
        solicitud = SolicitudTraslado.objects.create(
            activo=self.activo,
            almacen_origen=self.almacen_zul,
            almacen_destino=self.almacen_car,
            solicitante=self.solicitante,
            motivo='Test transfer',
            fecha_limite=timezone.now() + timedelta(days=7),
            prioridad='NORMAL'
        )
        
        # Create approvals
        AprobacionTraslado.create_approval(
            solicitud=solicitud,
            aprobador=self.manager_zul,
            tipo_aprobacion='ORIGEN',
            decision='APROBADO',
            comentarios='Approved'
        )
        
        AprobacionTraslado.create_approval(
            solicitud=solicitud,
            aprobador=self.manager_car,
            tipo_aprobacion='DESTINO',
            decision='RECHAZADO',
            comentarios='Rejected'
        )
        
        # Test user statistics
        stats_zul = AprobacionTraslado.get_approval_statistics(user=self.manager_zul)
        self.assertEqual(stats_zul['total_approvals'], 1)
        self.assertEqual(stats_zul['decision_breakdown']['APROBADO'], 1)
        self.assertEqual(stats_zul['approval_rate'], 100.0)
        
        stats_car = AprobacionTraslado.get_approval_statistics(user=self.manager_car)
        self.assertEqual(stats_car['total_approvals'], 1)
        self.assertEqual(stats_car['decision_breakdown']['RECHAZADO'], 1)
        self.assertEqual(stats_car['approval_rate'], 0.0)


if __name__ == '__main__':
    import django
    import os
    import sys
    
    # Setup Django
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'siae.settings')
    django.setup()
    
    # Run tests
    from django.test.utils import get_runner
    from django.conf import settings
    
    TestRunner = get_runner(settings)
    test_runner = TestRunner()
    failures = test_runner.run_tests(['institucion.test_transfer_workflow_models'])
    
    if failures:
        sys.exit(1)