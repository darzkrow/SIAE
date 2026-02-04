"""
Property-based tests for enhanced inventory models functionality.
Tests universal properties that should hold for all enhanced inventory models.

Feature: system-modernization, Property 7: Advanced Search Functionality
**Validates: Requirements 7.1, 7.3**
"""
import pytest
from hypothesis import given, strategies as st, assume, settings
from hypothesis.extra.django import TestCase
from django.db import connection
from decimal import Decimal
from inventario.models import (
    Tag, ChemicalProduct, Pipe, PumpAndMotor, Accessory,
    UnitOfMeasure, Supplier
)
from catalogo.models import CategoriaProducto, Marca


class EnhancedModelPropertyTests(TestCase):
    """Property-based tests for enhanced inventory model functionality."""
    
    def setUp(self):
        """Set up test data."""
        # Create required related objects
        self.categoria, _ = CategoriaProducto.objects.get_or_create(
            codigo='TEST',
            defaults={'nombre': 'Test Category'}
        )
        
        # Create BOM category for pump tests
        self.bom_categoria, _ = CategoriaProducto.objects.get_or_create(
            codigo='BOM',
            defaults={'nombre': 'Bombas y Motores'}
        )
        
        self.unidad, _ = UnitOfMeasure.objects.get_or_create(
            simbolo='kg',
            defaults={
                'nombre': 'Kilogramo',
                'tipo': UnitOfMeasure.TipoUnidad.PESO
            }
        )
        
        self.proveedor, _ = Supplier.objects.get_or_create(
            codigo='SUP001',
            defaults={'nombre': 'Test Supplier'}
        )
        
        self.marca, _ = Marca.objects.get_or_create(
            nombre='Test Brand'
        )

    @given(
        tag_name=st.text(min_size=1, max_size=50).filter(lambda x: x.strip()),
        color=st.sampled_from(['#ff0000', '#00ff00', '#0000ff', '#ffff00', '#ff00ff', '#00ffff']),
        description=st.text(max_size=200)
    )
    @settings(max_examples=50)
    def test_tag_creation_property(self, tag_name, color, description):
        """
        Property: For any valid tag data, tag creation should succeed and preserve all data.
        Feature: system-modernization, Property 7: Advanced Search Functionality
        **Validates: Requirements 7.1, 7.3**
        """
        # Clean the tag name to ensure uniqueness
        unique_tag_name = f"{tag_name.strip()}_{hash(tag_name) % 10000}"
        
        tag = Tag.objects.create(
            name=unique_tag_name,
            color=color,
            description=description
        )
        
        # Property: Created tag should preserve all input data
        assert tag.name == unique_tag_name
        assert tag.color == color
        assert tag.description == description
        assert str(tag) == unique_tag_name

    @given(
        field_name=st.text(min_size=1, max_size=50).filter(lambda x: x.strip() and x.isidentifier()),
        field_value=st.one_of(
            st.text(max_size=100),
            st.integers(min_value=-1000, max_value=1000),
            st.floats(min_value=-1000.0, max_value=1000.0, allow_nan=False, allow_infinity=False),
            st.booleans()
        )
    )
    @settings(max_examples=50)
    def test_custom_fields_property(self, field_name, field_value):
        """
        Property: For any custom field name and value, the system should store and retrieve it correctly.
        Feature: system-modernization, Property 7: Advanced Search Functionality
        **Validates: Requirements 7.1, 7.3**
        """
        chemical = ChemicalProduct.objects.create(
            nombre='Test Chemical',
            categoria=self.categoria,
            unidad_medida=self.unidad,
            proveedor=self.proveedor,
            precio_unitario=Decimal('100.00')
        )
        
        # Set custom field
        chemical.set_custom_field(field_name, field_value)
        
        # Property: Custom field should be stored and retrievable
        assert chemical.get_custom_field(field_name) == field_value
        
        # Property: Custom field should persist after save
        chemical.save()
        chemical.refresh_from_db()
        assert chemical.get_custom_field(field_name) == field_value
        
        # Property: Removing custom field should make it unavailable
        chemical.remove_custom_field(field_name)
        assert chemical.get_custom_field(field_name) is None

    @given(
        num_tags=st.integers(min_value=0, max_value=5)
    )
    @settings(max_examples=30)
    def test_tags_relationship_property(self, num_tags):
        """
        Property: For any number of tags, the many-to-many relationship should work correctly.
        Feature: system-modernization, Property 7: Advanced Search Functionality
        **Validates: Requirements 7.1, 7.3**
        """
        # Create tags
        tags = []
        for i in range(num_tags):
            tag = Tag.objects.create(
                name=f'Tag_{i}_{hash(str(i)) % 10000}',
                color='#ff0000'
            )
            tags.append(tag)
        
        # Create a pipe product
        pipe = Pipe.objects.create(
            nombre='Test Pipe',
            categoria=self.categoria,
            unidad_medida=self.unidad,
            proveedor=self.proveedor,
            precio_unitario=Decimal('50.00'),
            material=Pipe.Material.PVC,
            diametro_nominal=Decimal('100.00'),
            presion_nominal=Pipe.PresionNominal.PN10,
            tipo_union=Pipe.TipoUnion.SOLDABLE,
            tipo_uso=Pipe.TipoUso.POTABLE
        )
        
        # Add all tags
        pipe.tags.set(tags)
        
        # Property: Number of associated tags should match input
        assert pipe.tags.count() == num_tags
        
        # Property: All tags should be associated with the product
        for tag in tags:
            assert tag in pipe.tags.all()
            assert pipe in tag.pipe_products.all()

    @given(
        nombre=st.text(min_size=1, max_size=100).filter(lambda x: x.strip()),
        descripcion=st.text(max_size=200),
        notas=st.text(max_size=200),
        precio=st.decimals(min_value=0, max_value=10000, places=2)
    )
    @settings(max_examples=30)
    def test_search_vector_content_property(self, nombre, descripcion, notas, precio):
        """
        Property: For any product data, search vector update should complete without error.
        Feature: system-modernization, Property 7: Advanced Search Functionality
        **Validates: Requirements 7.1, 7.3**
        """
        assume(precio >= 0)  # Ensure price is non-negative
        
        chemical = ChemicalProduct.objects.create(
            nombre=nombre.strip(),
            descripcion=descripcion,
            notas=notas,
            categoria=self.categoria,
            unidad_medida=self.unidad,
            proveedor=self.proveedor,
            precio_unitario=precio
        )
        
        # Property: Search vector update should not raise an exception
        try:
            chemical.update_search_vector()
            success = True
        except Exception:
            success = False
        
        assert success, "Search vector update should not fail for valid product data"

    @given(
        custom_fields_data=st.dictionaries(
            keys=st.text(min_size=1, max_size=20).filter(lambda x: x.strip() and x.isidentifier()),
            values=st.one_of(
                st.text(max_size=50),
                st.integers(min_value=-100, max_value=100),
                st.booleans()
            ),
            min_size=0,
            max_size=5
        )
    )
    @settings(max_examples=30)
    def test_custom_fields_json_property(self, custom_fields_data):
        """
        Property: For any dictionary of custom fields, JSON storage should preserve data integrity.
        Feature: system-modernization, Property 7: Advanced Search Functionality
        **Validates: Requirements 7.1, 7.3**
        """
        accessory = Accessory.objects.create(
            nombre='Test Valve',
            categoria=self.categoria,
            unidad_medida=self.unidad,
            proveedor=self.proveedor,
            precio_unitario=Decimal('25.00'),
            tipo_accesorio=Accessory.TipoAccesorio.VALVULA,
            diametro_entrada=Decimal('2.0'),
            tipo_conexion=Accessory.TipoConexion.ROSCADA,
            presion_trabajo='PN10',
            material=Accessory.Material.PVC,
            custom_fields=custom_fields_data
        )
        
        # Property: All custom fields should be preserved
        for key, value in custom_fields_data.items():
            assert accessory.get_custom_field(key) == value
        
        # Property: Custom fields should persist after database round-trip
        accessory.save()
        accessory.refresh_from_db()
        
        for key, value in custom_fields_data.items():
            assert accessory.get_custom_field(key) == value

    @given(
        model_choice=st.sampled_from(['chemical', 'pipe', 'pump', 'accessory'])
    )
    @settings(max_examples=20)
    def test_enhanced_functionality_inheritance_property(self, model_choice):
        """
        Property: All product models should inherit enhanced functionality consistently.
        Feature: system-modernization, Property 7: Advanced Search Functionality
        **Validates: Requirements 7.1, 7.3**
        """
        # Create product based on model choice
        if model_choice == 'chemical':
            product = ChemicalProduct.objects.create(
                nombre='Test Chemical',
                categoria=self.categoria,
                unidad_medida=self.unidad,
                proveedor=self.proveedor,
                precio_unitario=Decimal('100.00')
            )
        elif model_choice == 'pipe':
            product = Pipe.objects.create(
                nombre='Test Pipe',
                categoria=self.categoria,
                unidad_medida=self.unidad,
                proveedor=self.proveedor,
                precio_unitario=Decimal('50.00'),
                material=Pipe.Material.PVC,
                diametro_nominal=Decimal('100.00'),
                presion_nominal=Pipe.PresionNominal.PN10,
                tipo_union=Pipe.TipoUnion.SOLDABLE,
                tipo_uso=Pipe.TipoUso.POTABLE
            )
        elif model_choice == 'pump':
            product = PumpAndMotor.objects.create(
                nombre='Test Pump',
                categoria=self.categoria,
                unidad_medida=self.unidad,
                proveedor=self.proveedor,
                precio_unitario=Decimal('1000.00'),
                tipo_equipo=PumpAndMotor.TipoEquipo.BOMBA_CENTRIFUGA,
                marca=self.marca,
                modelo='MODEL123',
                numero_serie=f'SERIAL_{hash(model_choice) % 10000}',
                potencia_hp=Decimal('5.0'),
                voltaje=220,
                fases=PumpAndMotor.Fases.TRIFASICO
            )
        else:  # accessory
            product = Accessory.objects.create(
                nombre='Test Valve',
                categoria=self.categoria,
                unidad_medida=self.unidad,
                proveedor=self.proveedor,
                precio_unitario=Decimal('25.00'),
                tipo_accesorio=Accessory.TipoAccesorio.VALVULA,
                diametro_entrada=Decimal('2.0'),
                tipo_conexion=Accessory.TipoConexion.ROSCADA,
                presion_trabajo='PN10',
                material=Accessory.Material.PVC
            )
        
        # Property: All models should have enhanced functionality
        assert hasattr(product, 'custom_fields')
        assert hasattr(product, 'tags')
        assert hasattr(product, 'search_vector')
        assert hasattr(product, 'get_custom_field')
        assert hasattr(product, 'set_custom_field')
        assert hasattr(product, 'remove_custom_field')
        assert hasattr(product, 'update_search_vector')
        
        # Property: Custom fields should be initialized as empty dict
        assert product.custom_fields == {}
        
        # Property: Tags should be initialized as empty
        assert product.tags.count() == 0

    @given(
        search_terms=st.lists(
            st.text(min_size=1, max_size=20).filter(lambda x: x.strip()),
            min_size=1,
            max_size=5
        )
    )
    @settings(max_examples=20)
    def test_search_content_aggregation_property(self, search_terms):
        """
        Property: Search vector should aggregate content from all relevant fields without error.
        Feature: system-modernization, Property 7: Advanced Search Functionality
        **Validates: Requirements 7.1, 7.3**
        """
        # Create tags with search terms
        tags = []
        for i, term in enumerate(search_terms):
            tag = Tag.objects.create(
                name=f'{term.strip()}_{i}_{hash(term) % 10000}',
                color='#ff0000'
            )
            tags.append(tag)
        
        # Create product with search terms in various fields
        chemical = ChemicalProduct.objects.create(
            nombre=f'Product {search_terms[0]}' if search_terms else 'Product',
            descripcion=' '.join(search_terms[:2]) if len(search_terms) >= 2 else '',
            notas=' '.join(search_terms[2:]) if len(search_terms) > 2 else '',
            categoria=self.categoria,
            unidad_medida=self.unidad,
            proveedor=self.proveedor,
            precio_unitario=Decimal('100.00'),
            custom_fields={
                'search_field': ' '.join(search_terms) if search_terms else ''
            }
        )
        
        # Add tags
        chemical.tags.set(tags)
        
        # Property: Search vector update should complete successfully
        try:
            chemical.update_search_vector()
            success = True
        except Exception:
            success = False
        
        assert success, "Search vector update should handle all content types without error"