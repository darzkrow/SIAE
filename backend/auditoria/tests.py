from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from catalogo.models import CategoriaProducto
from auditoria.models import AuditLog

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
