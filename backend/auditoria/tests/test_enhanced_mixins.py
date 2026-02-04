"""
Tests for enhanced audit mixins functionality.
"""
from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase
from rest_framework import status
from catalogo.models import CategoriaProducto
from auditoria.models import AuditLog

User = get_user_model()

class EnhancedMixinsTests(APITestCase):
    """Tests for enhanced audit mixins"""
    
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
        self.client.force_authenticate(user=self.admin_user)
    
    def test_enhanced_create_audit(self):
        """Test enhanced audit logging for create operations"""
        initial_count = AuditLog.objects.count()
        
        data = {
            'nombre': 'Test Category',
            'codigo': 'TEST001',
            'descripcion': 'Test description'
        }
        
        response = self.client.post('/api/catalog/categorias/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
        # Check audit log was created
        new_logs = AuditLog.objects.filter(action='CREATE').order_by('-timestamp')
        self.assertTrue(new_logs.exists())
        
        audit_log = new_logs.first()
        self.assertEqual(audit_log.action, 'CREATE')
        self.assertEqual(audit_log.object_repr, 'Test Category')
        self.assertEqual(audit_log.risk_level, 'LOW')
        
        # Check extra data
        self.assertIn('model', audit_log.extra_data)
        self.assertIn('action_source', audit_log.extra_data)
        self.assertEqual(audit_log.extra_data['action_source'], 'api')
    
    def test_enhanced_update_audit_with_changes(self):
        """Test enhanced audit logging for update operations with change tracking"""
        # Create a category first
        category = CategoriaProducto.objects.create(
            nombre='Original Name',
            codigo='ORIG001',
            descripcion='Original description'
        )
        
        # Update the category
        update_data = {
            'nombre': 'Updated Name',
            'descripcion': 'Updated description'
        }
        
        response = self.client.patch(
            f'/api/catalog/categorias/{category.id}/', 
            update_data, 
            format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Check audit log
        audit_log = AuditLog.objects.filter(
            action='UPDATE',
            object_id=category.id
        ).order_by('-timestamp').first()
        
        self.assertIsNotNone(audit_log)
        self.assertEqual(audit_log.risk_level, 'LOW')  # No sensitive fields modified
        
        # Check changes tracking
        self.assertIn('old_values', audit_log.changes)
        self.assertIn('new_values', audit_log.changes)
        self.assertIn('fields_changed', audit_log.changes)
        
        self.assertEqual(audit_log.changes['old_values']['nombre'], 'Original Name')
        self.assertEqual(audit_log.changes['new_values']['nombre'], 'Updated Name')
        self.assertIn('nombre', audit_log.changes['fields_changed'])
        self.assertIn('descripcion', audit_log.changes['fields_changed'])
    
    def test_delete_audit_medium_risk(self):
        """Test that delete operations have MEDIUM risk level"""
        category = CategoriaProducto.objects.create(
            nombre='To Delete',
            codigo='DEL001'
        )
        
        response = self.client.delete(f'/api/catalog/categorias/{category.id}/')
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        
        # Check audit log
        audit_log = AuditLog.objects.filter(
            action='DELETE',
            object_id=category.id
        ).order_by('-timestamp').first()
        
        self.assertIsNotNone(audit_log)
        self.assertEqual(audit_log.risk_level, 'MEDIUM')
    
    def test_restore_operation_audit(self):
        """Test audit logging for restore operations"""
        # Create and soft delete a category
        category = CategoriaProducto.objects.create(
            nombre='To Restore',
            codigo='REST001'
        )
        category.delete()  # Soft delete
        
        # Restore the category
        response = self.client.post(f'/api/catalog/categorias/{category.id}/restaurar/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Check restore audit log
        audit_log = AuditLog.objects.filter(
            action='RESTORE',
            object_id=category.id
        ).order_by('-timestamp').first()
        
        self.assertIsNotNone(audit_log)
        self.assertEqual(audit_log.risk_level, 'MEDIUM')
        self.assertTrue(audit_log.extra_data.get('restored_from_trash', False))
    
    def test_risk_level_assessment_based_on_count(self):
        """Test that risk level is assessed based on affected count in bulk operations"""
        # Test the log_data_operation function directly
        from auditoria.utils import log_data_operation
        
        # Test LOW risk (< 100 records)
        low_risk_log = log_data_operation(
            user=self.admin_user,
            action='BULK_UPDATE',
            affected_count=50,
            operation_type='test_operation'
        )
        self.assertEqual(low_risk_log.risk_level, 'LOW')
        
        # Test MEDIUM risk (100-1000 records)
        medium_risk_log = log_data_operation(
            user=self.admin_user,
            action='BULK_UPDATE',
            affected_count=500,
            operation_type='test_operation'
        )
        self.assertEqual(medium_risk_log.risk_level, 'MEDIUM')
        
        # Test HIGH risk (> 1000 records)
        high_risk_log = log_data_operation(
            user=self.admin_user,
            action='BULK_UPDATE',
            affected_count=1500,
            operation_type='test_operation'
        )
        self.assertEqual(high_risk_log.risk_level, 'HIGH')
    
    def test_papelera_endpoint(self):
        """Test the trash bin (papelera) endpoint"""
        # Create and delete some categories
        for i in range(3):
            category = CategoriaProducto.objects.create(
                nombre=f'Deleted Category {i}',
                codigo=f'DEL{i:03d}'
            )
            category.delete()  # Soft delete
        
        # Test papelera endpoint
        response = self.client.get('/api/catalog/categorias/papelera/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 3)
        
        # Verify all returned items are soft-deleted
        for item in response.data['results']:
            category = CategoriaProducto.all_objects.get(id=item['id'])
            self.assertIsNotNone(category.deleted_at)
    
    def test_audit_log_extra_data_fields(self):
        """Test that extra data contains expected fields"""
        data = {
            'nombre': 'Extra Data Test',
            'codigo': 'EXTRA001',
            'descripcion': 'Testing extra data'
        }
        
        response = self.client.post('/api/catalog/categorias/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
        # Check audit log extra data
        audit_log = AuditLog.objects.filter(action='CREATE').order_by('-timestamp').first()
        
        # Verify extra data contains expected fields
        self.assertIn('model', audit_log.extra_data)
        self.assertIn('action_source', audit_log.extra_data)
        self.assertIn('endpoint', audit_log.extra_data)
        self.assertIn('method', audit_log.extra_data)
        self.assertIn('fields_modified', audit_log.extra_data)
        
        self.assertEqual(audit_log.extra_data['action_source'], 'api')
        self.assertEqual(audit_log.extra_data['method'], 'POST')
        self.assertIn('/api/catalog/categorias/', audit_log.extra_data['endpoint'])
    
    def test_changes_summary_method(self):
        """Test the get_changes_summary method works correctly"""
        # Create and update a category to generate changes
        category = CategoriaProducto.objects.create(
            nombre='Summary Test',
            codigo='SUM001'
        )
        
        update_data = {'descripcion': 'Added description'}
        response = self.client.patch(
            f'/api/catalog/categorias/{category.id}/', 
            update_data, 
            format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Get the audit log and test the summary
        audit_log = AuditLog.objects.filter(
            action='UPDATE',
            object_id=category.id
        ).order_by('-timestamp').first()
        
        summary = audit_log.get_changes_summary()
        # The summary should show the fields that were modified
        self.assertIn('descripcion', summary)
        # It should use the "fields_changed" format since that's what our mixin creates
        self.assertIn('Campos modificados', summary)
    
    def test_system_action_logging(self):
        """Test logging system actions (no user)"""
        # Test the log_action class method directly for system actions
        test_category = CategoriaProducto.objects.create(
            nombre='System Test',
            codigo='SYS001'
        )
        
        audit_log = AuditLog.log_action(
            user=None,  # System action
            action='SYSTEM_MAINTENANCE',
            content_object=test_category,
            changes={'maintenance_type': 'backup'},
            risk_level='MEDIUM',
            extra_data={'automated': True}
        )
        
        self.assertIsNone(audit_log.user)
        self.assertEqual(audit_log.action, 'SYSTEM_MAINTENANCE')
        self.assertEqual(audit_log.risk_level, 'MEDIUM')
        self.assertTrue(audit_log.extra_data['automated'])
        
        # Test string representation for system actions
        str_repr = str(audit_log)
        self.assertIn('Sistema', str_repr)