"""
Tests for inventario models.
Testing critical business logic for stock management and movements.
"""
import pytest
from django.test import TestCase
from django.core.exceptions import ValidationError
from django.contrib.auth import get_user_model

from inventario.models import (
    OrganizacionCentral, Sucursal, Acueducto, Categoria,
    Tuberia, Equipo, StockTuberia, StockEquipo,
    MovimientoInventario, AlertaStock, Notification
)

User = get_user_model()


@pytest.mark.django_db
class TestOrganizacionCentral(TestCase):
    """Test OrganizacionCentral model."""
    
    def test_create_organizacion(self):
        """Test creating an OrganizacionCentral instance."""
        org = OrganizacionCentral.objects.create(
            nombre="Hidroven",
            rif="J-12345678-9"
        )
        assert org.nombre == "Hidroven"
        assert str(org) == "Hidroven"


@pytest.mark.django_db
class TestSucursalAndAcueducto(TestCase):
    """Test Sucursal and Acueducto models."""
    
    def setUp(self):
        self.org = OrganizacionCentral.objects.create(nombre="Test Org")
        self.sucursal = Sucursal.objects.create(
            nombre="Sucursal Centro",
            organizacion_central=self.org
        )
    
    def test_create_sucursal(self):
        """Test creating a Sucursal."""
        assert self.sucursal.nombre == "Sucursal Centro"
        assert self.sucursal.organizacion_central == self.org
    
    def test_create_acueducto(self):
        """Test creating an Acueducto."""
        acueducto = Acueducto.objects.create(
            nombre="Acueducto Norte",
            sucursal=self.sucursal
        )
        assert acueducto.nombre == "Acueducto Norte"
        assert acueducto.sucursal == self.sucursal


@pytest.mark.django_db
class TestTuberiaAndEquipo(TestCase):
    """Test Tuberia and Equipo models."""
    
    def setUp(self):
        self.categoria = Categoria.objects.create(nombre="Tuberías PVC")
    
    def test_create_tuberia(self):
        """Test creating a Tuberia."""
        tuberia = Tuberia.objects.create(
            nombre="Tubería PVC 110mm",
            descripcion="Tubería para agua potable",
            categoria=self.categoria,
            material=Tuberia.MATERIAL_PVC,
            tipo_uso=Tuberia.USO_POTABLE,
            diametro_nominal_mm=110,
            longitud_m=6.0
        )
        assert tuberia.nombre == "Tubería PVC 110mm"
        assert tuberia.material == Tuberia.MATERIAL_PVC
    
    def test_create_equipo(self):
        """Test creating an Equipo."""
        categoria_equipo = Categoria.objects.create(nombre="Bombas")
        equipo = Equipo.objects.create(
            nombre="Bomba Centrífuga",
            categoria=categoria_equipo,
            marca="Pedrollo",
            modelo="CP-200",
            potencia_hp=5.0,
            numero_serie="SER-001"
        )
        assert equipo.nombre == "Bomba Centrífuga"
        assert equipo.marca == "Pedrollo"


@pytest.mark.django_db
class TestStockManagement(TestCase):
    """Test Stock models (StockTuberia and StockEquipo)."""
    
    def setUp(self):
        org = OrganizacionCentral.objects.create(nombre="Test Org")
        sucursal = Sucursal.objects.create(nombre="Sucursal Test", organizacion_central=org)
        self.acueducto = Acueducto.objects.create(nombre="Acueducto Test", sucursal=sucursal)
        
        categoria = Categoria.objects.create(nombre="Test Cat")
        self.tuberia = Tuberia.objects.create(
            nombre="Tubería Test",
            categoria=categoria,
            material=Tuberia.MATERIAL_PVC,
            tipo_uso=Tuberia.USO_POTABLE,
            diametro_nominal_mm=100,
            longitud_m=6.0
        )
    
    def test_create_stock_tuberia(self):
        """Test creating StockTuberia."""
        stock = StockTuberia.objects.create(
            tuberia=self.tuberia,
            acueducto=self.acueducto,
            cantidad=50
        )
        assert stock.cantidad == 50
        assert stock.tuberia == self.tuberia
    
    def test_stock_cannot_be_negative(self):
        """Test that stock quantity cannot be negative."""
        stock = StockTuberia.objects.create(
            tuberia=self.tuberia,
            acueducto=self.acueducto,
            cantidad=10
        )
        stock.cantidad = -5
        with pytest.raises(ValidationError):
            stock.save()


@pytest.mark.django_db
class TestMovimientoInventario(TestCase):
    """Test MovimientoInventario model and stock updates."""
    
    def setUp(self):
        org = OrganizacionCentral.objects.create(nombre="Test Org")
        sucursal = Sucursal.objects.create(nombre="Sucursal Test", organizacion_central=org)
        self.acueducto_origen = Acueducto.objects.create(nombre="Acueducto Origen", sucursal=sucursal)
        self.acueducto_destino = Acueducto.objects.create(nombre="Acueducto Destino", sucursal=sucursal)
        
        categoria = Categoria.objects.create(nombre="Test Cat")
        self.tuberia = Tuberia.objects.create(
            nombre="Tubería Test",
            categoria=categoria,
            material=Tuberia.MATERIAL_PVC,
            tipo_uso=Tuberia.USO_POTABLE,
            diametro_nominal_mm=100,
            longitud_m=6.0
        )
        
        # Initialize stock in origin
        StockTuberia.objects.create(
            tuberia=self.tuberia,
            acueducto=self.acueducto_origen,
            cantidad=100
        )
    
    def test_movimiento_entrada_increases_stock(self):
        """Test that ENTRADA movement increases stock."""
        initial_stock = StockTuberia.objects.get(
            tuberia=self.tuberia,
            acueducto=self.acueducto_origen
        ).cantidad
        
        MovimientoInventario.objects.create(
            tuberia=self.tuberia,
            tipo_movimiento=MovimientoInventario.T_ENTRADA,
            acueducto_destino=self.acueducto_origen,
            cantidad=20,
            razon="Compra nueva"
        )
        
        final_stock = StockTuberia.objects.get(
            tuberia=self.tuberia,
            acueducto=self.acueducto_origen
        ).cantidad
        
        assert final_stock == initial_stock + 20
    
    def test_movimiento_salida_decreases_stock(self):
        """Test that SALIDA movement decreases stock."""
        initial_stock = 100
        
        MovimientoInventario.objects.create(
            tuberia=self.tuberia,
            tipo_movimiento=MovimientoInventario.T_SALIDA,
            acueducto_origen=self.acueducto_origen,
            cantidad=30,
            razon="Instalación"
        )
        
        final_stock = StockTuberia.objects.get(
            tuberia=self.tuberia,
            acueducto=self.acueducto_origen
        ).cantidad
        
        assert final_stock == initial_stock - 30
    
    def test_movimiento_insufficient_stock_raises_error(self):
        """Test that movement with insufficient stock raises ValidationError."""
        with pytest.raises(ValidationError, match="Stock insuficiente"):
            MovimientoInventario.objects.create(
                tuberia=self.tuberia,
                tipo_movimiento=MovimientoInventario.T_SALIDA,
                acueducto_origen=self.acueducto_origen,
                cantidad=200,  # More than available (100)
                razon="Intento de sobreventa"
            )


@pytest.mark.django_db
class TestAlertaStock(TestCase):
    """Test AlertaStock and Notification models."""
    
    def setUp(self):
        org = OrganizacionCentral.objects.create(nombre="Test Org")
        sucursal = Sucursal.objects.create(nombre="Sucursal Test", organizacion_central=org)
        self.acueducto = Acueducto.objects.create(nombre="Acueducto Test", sucursal=sucursal)
        
        categoria = Categoria.objects.create(nombre="Test Cat")
        self.tuberia = Tuberia.objects.create(
            nombre="Tubería Test",
            categoria=categoria,
            material=Tuberia.MATERIAL_PVC,
            tipo_uso=Tuberia.USO_POTABLE,
            diametro_nominal_mm=100,
            longitud_m=6.0
        )
    
    def test_create_alerta_stock(self):
        """Test creating an AlertaStock."""
        alerta = AlertaStock.objects.create(
            tuberia=self.tuberia,
            acueducto=self.acueducto,
            umbral_minimo=10,
            activo=True
        )
        assert alerta.umbral_minimo == 10
        assert alerta.activo is True
    
    def test_alerta_requires_one_articulo(self):
        """Test that AlertaStock requires exactly one of tuberia or equipo."""
        # Both None should raise error
        alerta = AlertaStock(
            acueducto=self.acueducto,
            umbral_minimo=10
        )
        with pytest.raises(ValidationError):
            alerta.clean()
