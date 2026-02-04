"""
Simple test for report generation to verify functionality.
"""

from django.test import TestCase
from django.utils import timezone
from datetime import timedelta
from decimal import Decimal
from django.contrib.contenttypes.models import ContentType

from accounts.models import CustomUser
from .models import (
    Empresa, Vicepresidencia, UnidadOrganizacional, AlmacenRegional,
    ActivoInventario
)
from .services import ReportGenerationService, ReportFilters
from inventario.models import ChemicalProduct, UnitOfMeasure, Supplier
from catalogo.models import CategoriaProducto, Marca


class SimpleReportGenerationTestCase(TestCase):
    """Simple test for report generation functionality"""
    
    def setUp(self):
        """Set up test data"""
        # Create test user
        self.user = CustomUser.objects.create_user(
            username='report_test_user',
            email='report@test.com',
            password='testpass123',
            role='OPERADOR'
        )
        
        # Create organizational hierarchy
        self.empresa = Empresa.objects.create(
            nombre='Hidroven Test',
            codigo='HVT'
        )
        
        self.vicepresidencia = Vicepresidencia.objects.create(
            nombre='VP Operaciones Hídricas',
            codigo='VPO',
            empresa=self.empresa,
            tipo='OPERACIONES_HIDRICAS'
        )
        
        self.unidad = UnidadOrganizacional.objects.create(
            nombre='Unidad Test',
            codigo='UT',
            vicepresidencia=self.vicepresidencia
        )
        
        # Create warehouse
        self.warehouse = AlmacenRegional.objects.create(
            nombre='Almacén Zulia Test',
            prefijo='ZUL',
            unidad_organizacional=self.unidad,
            capacidad_maxima=1000,
            ubicacion='Maracaibo'
        )
        
        # Create product categories and products
        self.categoria = CategoriaProducto.objects.create(
            nombre='Test Category',
            codigo='TST'
        )
        
        self.marca = Marca.objects.create(
            nombre='Test Brand'
        )
        
        # Create unit of measure
        self.unidad_medida = UnitOfMeasure.objects.create(
            nombre='Litros',
            simbolo='L',
            tipo='VOLUMEN'
        )
        
        # Create supplier
        self.proveedor = Supplier.objects.create(
            nombre='Test Supplier',
            rif='J-12345678-9',
            codigo='SUP001'
        )
        
        self.producto = ChemicalProduct.objects.create(
            nombre='Test Product',
            categoria=self.categoria,
            unidad_medida=self.unidad_medida,
            proveedor=self.proveedor,
            precio_unitario=Decimal('1000.00'),
            concentracion=Decimal('99.9')
        )
    
    def test_report_generation_basic(self):
        """Test basic report generation functionality"""
        print("Testing basic report generation")
        
        # Create test asset
        product_content_type = ContentType.objects.get_for_model(ChemicalProduct)
        asset = ActivoInventario.objects.create(
            tipo_activo='BOMBA',
            estado='EN_ALMACEN',
            almacen_actual=self.warehouse,
            producto_inventario_type=product_content_type,
            producto_inventario_id=self.producto.id,
            valor_unitario=Decimal('1500.00'),
            numero_serie='TEST001',
            descripcion='Test asset',
            creado_por=self.user
        )
        
        # Create report filters
        filters = ReportFilters(
            fecha_inicio=timezone.now() - timedelta(days=30),
            fecha_fin=timezone.now()
        )
        
        try:
            # Test inventory report generation
            inventory_report = ReportGenerationService.generate_inventory_hierarchy_report(filters)
            self.assertIsNotNone(inventory_report)
            print("✓ Inventory report generated successfully")
            
            # Test movement report generation
            movement_report = ReportGenerationService.generate_asset_movement_report(filters)
            self.assertIsNotNone(movement_report)
            print("✓ Movement report generated successfully")
            
            # Test utilization report generation
            utilization_report = ReportGenerationService.generate_utilization_rate_report(filters)
            self.assertIsNotNone(utilization_report)
            print("✓ Utilization report generated successfully")
            
        except Exception as e:
            self.fail(f"Report generation failed: {str(e)}")