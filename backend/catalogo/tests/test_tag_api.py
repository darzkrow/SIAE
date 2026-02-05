"""
Tests para la API de Tags
"""
from rest_framework.test import APITestCase
from rest_framework import status
from django.contrib.auth import get_user_model
from catalogo.models import Tag

User = get_user_model()


class TagAPITest(APITestCase):
    """Tests para el endpoint de Tags"""
    
    def setUp(self):
        """Configuración inicial para cada test"""
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123',
            email='test@example.com'
        )
        self.client.force_authenticate(user=self.user)
        self.url = '/api/catalogo/tags/'
    
    def test_list_tags(self):
        """Test listar tags"""
        Tag.objects.create(name='Tag1', color='#FF0000')
        Tag.objects.create(name='Tag2', color='#00FF00')
        
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)
    
    def test_create_tag(self):
        """Test crear tag via API"""
        data = {
            'name': 'Nuevo Tag',
            'color': '#00FF00',
            'description': 'Tag de prueba'
        }
        response = self.client.post(self.url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Tag.objects.count(), 1)
        self.assertEqual(Tag.objects.first().name, 'Nuevo Tag')
    
    def test_create_tag_duplicate_name(self):
        """Test que no se puede crear tag con nombre duplicado"""
        Tag.objects.create(name='Duplicado')
        data = {'name': 'Duplicado', 'color': '#FF0000'}
        response = self.client.post(self.url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    
    def test_retrieve_tag(self):
        """Test obtener un tag específico"""
        tag = Tag.objects.create(name='Test Tag', color='#0000FF')
        response = self.client.get(f'{self.url}{tag.id}/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], 'Test Tag')
    
    def test_update_tag(self):
        """Test actualizar tag"""
        tag = Tag.objects.create(name='Original', color='#FF0000')
        data = {'name': 'Actualizado', 'color': '#00FF00'}
        response = self.client.put(f'{self.url}{tag.id}/', data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        tag.refresh_from_db()
        self.assertEqual(tag.name, 'Actualizado')
        self.assertEqual(tag.color, '#00FF00')
    
    def test_partial_update_tag(self):
        """Test actualización parcial de tag"""
        tag = Tag.objects.create(name='Original', color='#FF0000')
        data = {'color': '#0000FF'}
        response = self.client.patch(f'{self.url}{tag.id}/', data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        tag.refresh_from_db()
        self.assertEqual(tag.name, 'Original')  # No cambió
        self.assertEqual(tag.color, '#0000FF')  # Cambió
    
    def test_delete_tag(self):
        """Test eliminar tag"""
        tag = Tag.objects.create(name='A Eliminar')
        response = self.client.delete(f'{self.url}{tag.id}/')
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Tag.objects.count(), 0)
    
    def test_search_tags(self):
        """Test búsqueda de tags"""
        Tag.objects.create(name='Urgente', description='Productos urgentes')
        Tag.objects.create(name='Normal', description='Productos normales')
        
        response = self.client.get(f'{self.url}?search=Urgente')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['name'], 'Urgente')
    
    def test_ordering_tags(self):
        """Test ordenamiento de tags"""
        Tag.objects.create(name='Zebra')
        Tag.objects.create(name='Alpha')
        
        response = self.client.get(f'{self.url}?ordering=name')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data[0]['name'], 'Alpha')
        self.assertEqual(response.data[1]['name'], 'Zebra')
    
    def test_unauthenticated_access(self):
        """Test que usuarios no autenticados no pueden acceder"""
        self.client.force_authenticate(user=None)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
