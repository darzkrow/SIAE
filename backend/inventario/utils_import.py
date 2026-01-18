import csv
import io
from decimal import Decimal
from django.db import transaction
from django.contrib.contenttypes.models import ContentType
from inventario.models import (
    ChemicalProduct, Pipe, PumpAndMotor, Accessory,
    UnitOfMeasure, Supplier,
    Sucursal, Acueducto, OrganizacionCentral
)
from catalogo.models import CategoriaProducto

class CSVImportProcessor:
    """Procesador para importar productos y entidades desde CSV."""
    
    MODEL_MAP = {
        'chemical': ChemicalProduct,
        'pipe': Pipe,
        'pump': PumpAndMotor,
        'accessory': Accessory,
        'sucursal': Sucursal,
        'acueducto': Acueducto
    }

    @staticmethod
    def process_csv(file_obj, product_type):
        """Procesa un archivo CSV y crea los productos."""
        model = CSVImportProcessor.MODEL_MAP.get(product_type)
        if not model:
            return {'error': f'Tipo de producto {product_type} no soportado'}

        decoded_file = file_obj.read().decode('utf-8')
        io_string = io.StringIO(decoded_file)
        reader = csv.DictReader(io_string)
        
        results = {
            'success': 0,
            'errors': [],
            'total': 0
        }

        with transaction.atomic():
            for row in reader:
                results['total'] += 1
                try:
                    # 1. Resolver FKs (Hierarchy/Master Data)
                    if 'categoria' in row:
                        row['categoria'], _ = CategoriaProducto.objects.get_or_create(nombre=row['categoria'])
                    if 'unidad_medida' in row:
                        row['unidad_medida'], _ = UnitOfMeasure.objects.get_or_create(nombre=row['unidad_medida'])
                    if 'proveedor' in row:
                        row['proveedor'], _ = Supplier.objects.get_or_create(nombre=row['proveedor'])
                    if 'organizacion_central' in row:
                        row['organizacion_central'], _ = OrganizacionCentral.objects.get_or_create(nombre=row['organizacion_central'])
                    if 'sucursal' in row:
                        row['sucursal'], _ = Sucursal.objects.get_or_create(nombre=row['sucursal'])
                    
                    # 2. Convertir Decimales
                    for field in ['stock_actual', 'stock_minimo', 'precio_unitario', 'diametro_nominal', 'longitud_unitaria', 'potencia_hp', 'caudal_maximo', 'altura_dinamica']:
                        if field in row and row[field]:
                            row[field] = Decimal(row[field].replace(',', '.'))
                        elif field in row:
                            row[field] = Decimal('0.00')

                    # 3. Filtrar campos que existen en el modelo
                    model_fields = [f.name for f in model._meta.get_fields()]
                    clean_row = {k: v for k, v in row.items() if k in model_fields}

                    # 4. Crear instancia
                    model.objects.create(**clean_row)
                    results['success'] += 1
                    
                except Exception as e:
                    results['errors'].append({
                        'row': results['total'],
                        'error': str(e),
                        'data': row
                    })
                    # Si falla uno, ¿abortamos todo? Depende de la política.
                    # Por ahora seguimos pero marcamos el error.
        
        return results
