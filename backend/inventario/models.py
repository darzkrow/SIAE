"""
💾 Módulo Inventario - Capa de Compatibilidad
Este archivo ahora solo re-exporta modelos desde sus nuevas ubicaciones modulares.
"""
from institucion.models import (
    Acueducto, Sucursal, OrganizacionCentral, 
    AlmacenRegional, Subalmacen
)
from geography.models import Ubicacion
from catalogo.models import CategoriaProducto, Marca, Tag

from productos.models import (
    UnitOfMeasure, ProductBase, 
    ChemicalProduct, Pipe, PumpAndMotor, Accessory,
)
from proveedores.models import Supplier
from stock.models import (
    Stock, MovimientoInventario, InventoryAudit
)
from activos.models import (
    MaterialEstrategico, ActivoFijo, 
    FichaTecnicaMotor, RegistroMantenimiento
)
from core.models import SystemConfiguration

# Proxies y clases de compatibilidad (opcional, si se siguen usando los nombres en español)
class Categoria(Pipe): # Placeholder for proxy logic if needed
    class Meta: proxy = True

class Tuberia(Pipe):
    class Meta: proxy = True

class Equipo(PumpAndMotor):
    class Meta: proxy = True
