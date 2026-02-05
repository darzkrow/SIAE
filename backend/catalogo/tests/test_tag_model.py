"""
Tests para el modelo Tag en catálogo
"""
from django.test import TestCase
from django.core.exceptions import ValidationError
from catalogo.models import Tag


class TagModelTest(TestCase):
    """Tests para el modelo Tag"""
    
    def test_create_tag(self):
        """Test crear tag básico"""
        tag = Tag.objects.create(
            name='Urgente',
            color='#FF0000',
            description='Productos urgentes'
        )
        self.assertEqual(tag.name, 'Urgente')
        self.assertEqual(tag.color, '#FF0000')
        self.assertEqual(tag.description, 'Productos urgentes')
    
    def test_tag_unique_name(self):
        """Test unicidad de nombre"""
        Tag.objects.create(name='Test')
        with self.assertRaises(Exception):
            Tag.objects.create(name='Test')
    
    def test_tag_str(self):
        """Test representación string"""
        tag = Tag.objects.create(name='Nacional')
        self.assertEqual(str(tag), 'Nacional')
    
    def test_tag_default_color(self):
        """Test color por defecto"""
        tag = Tag.objects.create(name='Sin Color')
        self.assertEqual(tag.color, '#007bff')
    
    def test_tag_ordering(self):
        """Test ordenamiento por nombre"""
        Tag.objects.create(name='Zebra')
        Tag.objects.create(name='Alpha')
        Tag.objects.create(name='Beta')
        
        tags = list(Tag.objects.all())
        self.assertEqual(tags[0].name, 'Alpha')
        self.assertEqual(tags[1].name, 'Beta')
        self.assertEqual(tags[2].name, 'Zebra')
    
    def test_tag_timestamps(self):
        """Test que se crean timestamps automáticamente"""
        tag = Tag.objects.create(name='Timestamp Test')
        self.assertIsNotNone(tag.created_at)
        self.assertIsNotNone(tag.updated_at)
    
    def test_tag_blank_description(self):
        """Test que description puede estar vacío"""
        tag = Tag.objects.create(name='Sin Descripción')
        self.assertEqual(tag.description, '')
