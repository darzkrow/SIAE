#!/usr/bin/env python
"""
Demonstration script for enhanced inventory models functionality.
Shows the new search vector, tags, and custom fields features.
"""
import os
import sys
import django

# Setup Django environment
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from decimal import Decimal
from inventario.models import (
    Tag, ChemicalProduct, Pipe, PumpAndMotor, Accessory,
    UnitOfMeasure, Supplier
)
from catalogo.models import CategoriaProducto, Marca


def create_demo_data():
    """Create demonstration data to show enhanced functionality."""
    print("🚀 Creating demonstration data for enhanced inventory models...")
    
    # Create required related objects
    categoria, _ = CategoriaProducto.objects.get_or_create(
        codigo='DEMO',
        defaults={'nombre': 'Demo Category'}
    )
    
    bom_categoria, _ = CategoriaProducto.objects.get_or_create(
        codigo='BOM',
        defaults={'nombre': 'Bombas y Motores'}
    )
    
    unidad, _ = UnitOfMeasure.objects.get_or_create(
        simbolo='kg',
        defaults={
            'nombre': 'Kilogramo',
            'tipo': UnitOfMeasure.TipoUnidad.PESO
        }
    )
    
    proveedor, _ = Supplier.objects.get_or_create(
        codigo='DEMO001',
        defaults={'nombre': 'Demo Supplier'}
    )
    
    marca, _ = Marca.objects.get_or_create(
        nombre='Demo Brand'
    )
    
    # Create tags
    print("📋 Creating tags...")
    urgent_tag, _ = Tag.objects.get_or_create(
        name='Urgent',
        defaults={'color': '#ff0000', 'description': 'Items that need urgent attention'}
    )
    
    eco_tag, _ = Tag.objects.get_or_create(
        name='Eco-Friendly',
        defaults={'color': '#00ff00', 'description': 'Environmentally friendly products'}
    )
    
    premium_tag, _ = Tag.objects.get_or_create(
        name='Premium',
        defaults={'color': '#ffd700', 'description': 'High-quality premium products'}
    )
    
    print(f"✅ Created tags: {urgent_tag.name}, {eco_tag.name}, {premium_tag.name}")
    
    # Create chemical product with enhanced features
    print("🧪 Creating chemical product with enhanced features...")
    chemical = ChemicalProduct.objects.create(
        nombre='Chlorine Dioxide Solution',
        descripcion='Water disinfection chemical for potable water treatment',
        categoria=categoria,
        unidad_medida=unidad,
        proveedor=proveedor,
        precio_unitario=Decimal('150.00'),
        notas='Store in cool, dry place. Handle with care.',
        custom_fields={
            'batch_number': 'BATCH-2024-001',
            'expiry_date': '2025-12-31',
            'storage_temperature': -20,
            'safety_level': 'High',
            'certification': 'NSF/ANSI 60'
        },
        concentracion=Decimal('25.00'),
        unidad_concentracion=ChemicalProduct.UnidadConcentracion.PORCENTAJE,
        presentacion=ChemicalProduct.TipoPresentacion.TAMBOR,
        es_peligroso=True,
        nivel_peligrosidad=ChemicalProduct.NivelPeligrosidad.ALTO
    )
    
    # Add tags to chemical
    chemical.tags.add(urgent_tag, eco_tag)
    
    print(f"✅ Created chemical: {chemical.nombre} (SKU: {chemical.sku})")
    print(f"   Custom fields: {chemical.custom_fields}")
    print(f"   Tags: {', '.join(tag.name for tag in chemical.tags.all())}")
    
    # Create pipe with enhanced features
    print("🔧 Creating pipe with enhanced features...")
    pipe = Pipe.objects.create(
        nombre='PVC Pipe 6 inch',
        descripcion='High-quality PVC pipe for water distribution',
        categoria=categoria,
        unidad_medida=unidad,
        proveedor=proveedor,
        precio_unitario=Decimal('45.00'),
        material=Pipe.Material.PVC,
        diametro_nominal=Decimal('6.0'),
        unidad_diametro=Pipe.UnidadDiametro.PULGADAS,
        presion_nominal=Pipe.PresionNominal.PN16,
        tipo_union=Pipe.TipoUnion.SOLDABLE,
        tipo_uso=Pipe.TipoUso.POTABLE,
        custom_fields={
            'installation_guide': 'Use PVC cement for joints',
            'warranty_years': 25,
            'color': 'Blue',
            'standard': 'ASTM D1785'
        }
    )
    
    # Add tags to pipe
    pipe.tags.add(premium_tag, eco_tag)
    
    print(f"✅ Created pipe: {pipe.nombre} (SKU: {pipe.sku})")
    print(f"   Custom fields: {pipe.custom_fields}")
    print(f"   Tags: {', '.join(tag.name for tag in pipe.tags.all())}")
    
    # Create pump with enhanced features
    print("⚡ Creating pump with enhanced features...")
    pump = PumpAndMotor.objects.create(
        nombre='Centrifugal Pump 5HP',
        descripcion='High-efficiency centrifugal pump for water systems',
        categoria=bom_categoria,  # Uses BOM category
        unidad_medida=unidad,
        proveedor=proveedor,
        precio_unitario=Decimal('2500.00'),
        tipo_equipo=PumpAndMotor.TipoEquipo.BOMBA_CENTRIFUGA,
        marca=marca,
        modelo='CP-5000',
        numero_serie='DEMO-PUMP-001',
        potencia_hp=Decimal('5.0'),
        voltaje=220,
        fases=PumpAndMotor.Fases.TRIFASICO,
        caudal_maximo=Decimal('100.0'),
        altura_dinamica=Decimal('50.0'),
        eficiencia=Decimal('85.5'),
        custom_fields={
            'installation_date': '2024-01-15',
            'maintenance_schedule': 'Every 6 months',
            'operating_hours': 0,
            'location': 'Pump Station A',
            'technician': 'John Doe'
        }
    )
    
    # Add tags to pump
    pump.tags.add(premium_tag, urgent_tag)
    
    print(f"✅ Created pump: {pump.nombre} (SKU: {pump.sku})")
    print(f"   Custom fields: {pump.custom_fields}")
    print(f"   Tags: {', '.join(tag.name for tag in pump.tags.all())}")
    
    return chemical, pipe, pump


def demonstrate_search_functionality():
    """Demonstrate search vector functionality."""
    print("\n🔍 Demonstrating search functionality...")
    
    # Update search vectors for all products
    print("📝 Updating search vectors...")
    for model in [ChemicalProduct, Pipe, PumpAndMotor, Accessory]:
        for product in model.objects.all():
            product.update_search_vector()
    
    print("✅ Search vectors updated!")
    
    # Show search content aggregation
    chemical = ChemicalProduct.objects.filter(nombre__icontains='Chlorine').first()
    if chemical:
        print(f"\n📋 Search content for {chemical.nombre}:")
        print(f"   - SKU: {chemical.sku}")
        print(f"   - Name: {chemical.nombre}")
        print(f"   - Description: {chemical.descripcion}")
        print(f"   - Notes: {chemical.notas}")
        print(f"   - Category: {chemical.categoria.nombre}")
        print(f"   - Supplier: {chemical.proveedor.nombre}")
        print(f"   - Tags: {', '.join(tag.name for tag in chemical.tags.all())}")
        print(f"   - Custom fields: {list(chemical.custom_fields.keys())}")


def demonstrate_custom_fields():
    """Demonstrate custom fields functionality."""
    print("\n🎛️ Demonstrating custom fields functionality...")
    
    chemical = ChemicalProduct.objects.filter(nombre__icontains='Chlorine').first()
    if chemical:
        print(f"\n🧪 Custom fields for {chemical.nombre}:")
        
        # Get existing custom fields
        for key, value in chemical.custom_fields.items():
            print(f"   - {key}: {value}")
        
        # Add a new custom field
        chemical.set_custom_field('last_inspection', '2024-01-10')
        chemical.save()
        print(f"   - Added: last_inspection: {chemical.get_custom_field('last_inspection')}")
        
        # Modify an existing custom field
        chemical.set_custom_field('storage_temperature', -25)
        chemical.save()
        print(f"   - Updated: storage_temperature: {chemical.get_custom_field('storage_temperature')}")
        
        # Remove a custom field
        chemical.remove_custom_field('certification')
        chemical.save()
        print(f"   - Removed: certification (now returns: {chemical.get_custom_field('certification')})")


def demonstrate_tags():
    """Demonstrate tags functionality."""
    print("\n🏷️ Demonstrating tags functionality...")
    
    # Show all tags
    print("📋 All available tags:")
    for tag in Tag.objects.all():
        print(f"   - {tag.name} ({tag.color}): {tag.description}")
    
    # Show products by tag
    urgent_tag = Tag.objects.filter(name='Urgent').first()
    if urgent_tag:
        print(f"\n🚨 Products tagged as '{urgent_tag.name}':")
        
        # Check all product types
        for model_name, model_class in [
            ('Chemicals', ChemicalProduct),
            ('Pipes', Pipe),
            ('Pumps', PumpAndMotor),
            ('Accessories', Accessory)
        ]:
            products = model_class.objects.filter(tags=urgent_tag)
            if products.exists():
                print(f"   {model_name}:")
                for product in products:
                    print(f"     - {product.nombre} (SKU: {product.sku})")


def main():
    """Main demonstration function."""
    print("🎯 Enhanced Inventory Models Demonstration")
    print("=" * 50)
    
    # Create demo data
    chemical, pipe, pump = create_demo_data()
    
    # Demonstrate functionality
    demonstrate_search_functionality()
    demonstrate_custom_fields()
    demonstrate_tags()
    
    print("\n✨ Demonstration completed successfully!")
    print("\nEnhanced features implemented:")
    print("✅ Search vector fields for full-text search")
    print("✅ Tag model and many-to-many relationships")
    print("✅ Custom fields JSON support")
    print("✅ Automatic search vector updates")
    print("✅ Cross-database compatibility (PostgreSQL/SQLite)")


if __name__ == '__main__':
    main()