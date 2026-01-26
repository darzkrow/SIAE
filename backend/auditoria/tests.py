from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from catalogo.models import CategoriaProducto
from auditoria.models import AuditLog
from auditoria.utils import (
    log_action, log_authentication_action, log_permission_action,
    log_configuration_change, log_data_operation, log_access_denied
)
from accounts.models import Role, Permission
from django.contrib.contenttypes.models import ContentType

User = get_user_model()

class AuditoriaTests(APITestCase):
    def setUp(self):
        self.admin_user = User.objects.create_superuser(
            username='admin_test',
            password='password123',
            email='admin@test.com'
        )
        self.client.force_authenticate(user=self.admin_user)

    def test_tc_aud_01_creacion_log_categoria(self):
        """TC-AUD-01: Verificar que al crear una categoría se genere un AuditLog"""
        url = '/api/catalog/categorias/'
        data = {
            'nombre': 'Químicos de Prueba',
            'codigo': 'QUI-P',
            'descripcion': 'Test description'
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
        # Verificar log
        aud_log = AuditLog.objects.filter(action='CREATE', object_repr='Químicos de Prueba').first()
        self.assertIsNotNone(aud_log, "No se encontró el log de creación")
        # Por ahora solo validamos que exista el log, el usuario depende del middleware/login real

    def test_tc_soft_01_soft_delete(self):
        """TC-SOFT-01: Verificar Soft Delete en Categorías"""
        cat = CategoriaProducto.objects.create(nombre='Borrable', codigo='BOR')
        url = f'/api/catalog/categorias/{cat.id}/'
        
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        
        # Verificar log de eliminación
        log_del = AuditLog.objects.filter(action='DELETE', object_repr='Borrable').first()
        self.assertIsNotNone(log_del, "No se encontró el log de eliminación")
        
        # Verificar que sigue en DB pero marcado
        cat.refresh_from_db()
        self.assertIsNotNone(cat.deleted_at)
        
        # Verificar que no aparece en el listado normal
        list_response = self.client.get('/api/catalog/categorias/')
        self.assertEqual(len(list_response.data['results']), 0)

    def test_tc_soft_02_restaurar(self):
        """TC-SOFT-02: Verificar restauración desde papelera"""
        cat = CategoriaProducto.objects.create(nombre='Restaurable', codigo='RES')
        cat.delete() # Soft delete
        
        url = f'/api/catalog/categorias/{cat.id}/restaurar/'
        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        cat.refresh_from_db()
        self.assertIsNone(cat.deleted_at)


class EnhancedAuditLogTests(TestCase):
    """Tests for the enhanced AuditLog functionality"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123',
            email='test@example.com'
        )
        self.admin_user = User.objects.create_superuser(
            username='admin',
            password='adminpass123',
            email='admin@example.com'
        )
    
    def test_audit_log_creation_with_enhanced_fields(self):
        """Test creating audit log with all enhanced fields"""
        test_object = CategoriaProducto.objects.create(
            nombre='Test Category',
            codigo='TEST'
        )
        
        changes = {
            'old_values': {'nombre': 'Old Name'},
            'new_values': {'nombre': 'Test Category'}
        }
        
        extra_data = {
            'source': 'api',
            'batch_id': '12345'
        }
        
        audit_log = AuditLog.log_action(
            user=self.user,
            action='CREATE',
            content_object=test_object,
            changes=changes,
            ip_address='192.168.1.100',
            user_agent='Mozilla/5.0 Test Browser',
            session_key='test_session_key',
            extra_data=extra_data,
            risk_level='MEDIUM'
        )
        
        self.assertEqual(audit_log.user, self.user)
        self.assertEqual(audit_log.action, 'CREATE')
        self.assertEqual(audit_log.object_repr, 'Test Category')
        self.assertEqual(audit_log.changes, changes)
        self.assertEqual(audit_log.ip_address, '192.168.1.100')
        self.assertEqual(audit_log.user_agent, 'Mozilla/5.0 Test Browser')
        self.assertEqual(audit_log.session_key, 'test_session_key')
        self.assertEqual(audit_log.extra_data, extra_data)
        self.assertEqual(audit_log.risk_level, 'MEDIUM')
    
    def test_get_changes_summary(self):
        """Test the get_changes_summary method"""
        # Test with fields_changed format
        audit_log = AuditLog.objects.create(
            user=self.user,
            action='UPDATE',
            object_repr='Test Object',
            changes={'fields_changed': ['name', 'description', 'status']}
        )
        
        summary = audit_log.get_changes_summary()
        self.assertEqual(summary, "Campos modificados: name, description, status")
        
        # Test with old_values/new_values format
        audit_log2 = AuditLog.objects.create(
            user=self.user,
            action='UPDATE',
            object_repr='Test Object 2',
            changes={
                'old_values': {'name': 'Old Name', 'status': 'inactive'},
                'new_values': {'name': 'New Name', 'status': 'active'}
            }
        )
        
        summary2 = audit_log2.get_changes_summary()
        self.assertIn('name: Old Name → New Name', summary2)
        self.assertIn('status: inactive → active', summary2)
    
    def test_log_authentication_action(self):
        """Test logging authentication actions"""
        # Test successful login
        audit_log = log_authentication_action(
            user=self.user,
            action='LOGIN',
            success=True,
            ip_address='192.168.1.100',
            user_agent='Test Browser'
        )
        
        self.assertEqual(audit_log.action, 'LOGIN')
        self.assertEqual(audit_log.user, self.user)
        self.assertEqual(audit_log.risk_level, 'LOW')
        self.assertTrue(audit_log.changes['success'])
        
        # Test failed login
        audit_log2 = log_authentication_action(
            user=None,
            action='LOGIN_FAILED',
            success=False,
            ip_address='192.168.1.100',
            extra_data={'username': 'attempted_user'}
        )
        
        self.assertEqual(audit_log2.action, 'LOGIN_FAILED')
        self.assertIsNone(audit_log2.user)
        self.assertEqual(audit_log2.risk_level, 'MEDIUM')
        self.assertFalse(audit_log2.changes['success'])
        self.assertEqual(audit_log2.extra_data['attempted_username'], 'attempted_user')
    
    def test_log_permission_action(self):
        """Test logging permission-related actions"""
        # Create a role and permission for testing
        content_type = ContentType.objects.get_for_model(CategoriaProducto)
        permission = Permission.objects.create(
            name='Can view categories',
            codename='view_categoria',
            content_type=content_type
        )
        role = Role.objects.create(name='Test Role')
        
        # Test role assignment
        audit_log = log_permission_action(
            user=self.admin_user,
            action='ROLE_ASSIGN',
            target_user=self.user,
            role=role,
            granted=True,
            ip_address='192.168.1.100'
        )
        
        self.assertEqual(audit_log.action, 'ROLE_ASSIGN')
        self.assertEqual(audit_log.user, self.admin_user)
        self.assertEqual(audit_log.content_object, self.user)
        self.assertEqual(audit_log.risk_level, 'HIGH')
        self.assertTrue(audit_log.changes['granted'])
        self.assertEqual(audit_log.changes['role'], str(role))
        self.assertEqual(audit_log.extra_data['role_id'], role.id)
    
    def test_log_configuration_change(self):
        """Test logging configuration changes"""
        audit_log = log_configuration_change(
            user=self.admin_user,
            config_key='max_login_attempts',
            old_value=3,
            new_value=5,
            ip_address='192.168.1.100'
        )
        
        self.assertEqual(audit_log.action, 'CONFIG_CHANGE')
        self.assertEqual(audit_log.user, self.admin_user)
        self.assertEqual(audit_log.risk_level, 'MEDIUM')
        self.assertEqual(audit_log.changes['config_key'], 'max_login_attempts')
        self.assertEqual(audit_log.changes['old_value'], 3)
        self.assertEqual(audit_log.changes['new_value'], 5)
        self.assertEqual(audit_log.extra_data['config_key'], 'max_login_attempts')
    
    def test_log_data_operation(self):
        """Test logging data operations"""
        # Test bulk operation with high risk
        audit_log = log_data_operation(
            user=self.admin_user,
            action='BULK_DELETE',
            affected_count=1500,
            operation_type='category_cleanup',
            ip_address='192.168.1.100'
        )
        
        self.assertEqual(audit_log.action, 'BULK_DELETE')
        self.assertEqual(audit_log.user, self.admin_user)
        self.assertEqual(audit_log.risk_level, 'HIGH')  # > 1000 records
        self.assertEqual(audit_log.changes['affected_count'], 1500)
        self.assertEqual(audit_log.changes['operation_type'], 'category_cleanup')
        
        # Test smaller operation with lower risk
        audit_log2 = log_data_operation(
            user=self.user,
            action='EXPORT',
            affected_count=50,
            operation_type='monthly_report'
        )
        
        self.assertEqual(audit_log2.risk_level, 'LOW')  # < 100 records
    
    def test_log_access_denied(self):
        """Test logging access denied events"""
        audit_log = log_access_denied(
            user=self.user,
            resource='admin_panel',
            reason='Insufficient permissions',
            ip_address='192.168.1.100'
        )
        
        self.assertEqual(audit_log.action, 'ACCESS_DENIED')
        self.assertEqual(audit_log.user, self.user)
        self.assertEqual(audit_log.risk_level, 'MEDIUM')
        self.assertEqual(audit_log.changes['resource'], 'admin_panel')
        self.assertEqual(audit_log.changes['reason'], 'Insufficient permissions')
        self.assertEqual(audit_log.extra_data['resource'], 'admin_panel')
    
    def test_audit_log_indexes(self):
        """Test that database indexes are created properly"""
        # This test ensures the model migration created the expected indexes
        from django.db import connection
        
        with connection.cursor() as cursor:
            # Get table info to verify indexes exist
            cursor.execute("""
                SELECT name FROM sqlite_master 
                WHERE type='index' AND tbl_name='auditoria_auditlog'
                AND name LIKE 'auditoria_a_%'
            """)
            indexes = [row[0] for row in cursor.fetchall()]
            
            # Verify key indexes exist
            expected_indexes = [
                'auditoria_a_timesta_3349e8_idx',  # timestamp
                'auditoria_a_user_id_c02936_idx',  # user, timestamp
                'auditoria_a_action_046c23_idx',   # action, timestamp
                'auditoria_a_content_2f8c97_idx',  # content_type, object_id
                'auditoria_a_ip_addr_cb7357_idx',  # ip_address, timestamp
                'auditoria_a_risk_le_d7587b_idx',  # risk_level, timestamp
            ]
            
            for expected_index in expected_indexes:
                self.assertIn(expected_index, indexes, 
                            f"Expected index {expected_index} not found")
    
    def test_audit_log_string_representation(self):
        """Test the string representation of audit log entries"""
        audit_log = AuditLog.objects.create(
            user=self.user,
            action='CREATE',
            object_repr='Test Object'
        )
        
        str_repr = str(audit_log)
        self.assertIn('testuser', str_repr)
        self.assertIn('Creación', str_repr)  # Spanish display name
        self.assertIn('Test Object', str_repr)
        
        # Test system action (no user)
        system_log = AuditLog.objects.create(
            user=None,
            action='SYSTEM_MAINTENANCE',
            object_repr='System Backup'
        )
        
        str_repr2 = str(system_log)
        self.assertIn('Sistema', str_repr2)
