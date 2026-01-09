"""
Database migrations to add indexes for performance optimization.
Run with: python manage.py migrate
"""
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('inventario', '0001_initial'),  # Adjust to your latest migration
    ]

    operations = [
        # Indexes for StockTuberia
        migrations.AddIndex(
            model_name='stocktuberia',
            index=models.Index(fields=['tuberia', 'acueducto'], name='stock_tub_lookup_idx'),
        ),
        migrations.AddIndex(
            model_name='stocktuberia',
            index=models.Index(fields=['cantidad'], name='stock_tub_qty_idx'),
        ),
        
        # Indexes for StockEquipo
        migrations.AddIndex(
            model_name='stockequipo',
            index=models.Index(fields=['equipo', 'acueducto'], name='stock_eq_lookup_idx'),
        ),
        migrations.AddIndex(
            model_name='stockequipo',
            index=models.Index(fields=['cantidad'], name='stock_eq_qty_idx'),
        ),
        
        # Indexes for MovimientoInventario
        migrations.AddIndex(
            model_name='movimientoinventario',
            index=models.Index(fields=['-fecha_movimiento'], name='mov_fecha_idx'),
        ),
        migrations.AddIndex(
            model_name='movimientoinventario',
            index=models.Index(fields=['tipo_movimiento'], name='mov_tipo_idx'),
        ),
        migrations.AddIndex(
            model_name='movimientoinventario',
            index=models.Index(fields=['acueducto_origen'], name='mov_origen_idx'),
        ),
        migrations.AddIndex(
            model_name='movimientoinventario',
            index=models.Index(fields=['acueducto_destino'], name='mov_destino_idx'),
        ),
        
        # Indexes for InventoryAudit
        migrations.AddIndex(
            model_name='inventoryaudit',
            index=models.Index(fields=['-fecha'], name='audit_fecha_idx'),
        ),
        migrations.AddIndex(
            model_name='inventoryaudit',
            index=models.Index(fields=['status'], name='audit_status_idx'),
        ),
        
        # Indexes for AlertaStock
        migrations.AddIndex(
            model_name='alertastock',
            index=models.Index(fields=['activo'], name='alert_active_idx'),
        ),
        migrations.AddIndex(
            model_name='alertastock',
            index=models.Index(fields=['acueducto'], name='alert_acue_idx'),
        ),
        
        # Composite indexes for common queries
        migrations.AddIndex(
            model_name='movimientoinventario',
            index=models.Index(
                fields=['tipo_movimiento', '-fecha_movimiento'], 
                name='mov_tipo_fecha_idx'
            ),
        ),
    ]
