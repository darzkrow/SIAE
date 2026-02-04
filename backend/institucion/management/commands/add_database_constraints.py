"""
Management command to add database constraints for data integrity.
"""

from django.core.management.base import BaseCommand
from django.db import connection


class Command(BaseCommand):
    help = 'Add database constraints for data integrity in Hidroven system'

    def handle(self, *args, **options):
        self.stdout.write(
            self.style.SUCCESS('Adding database constraints for data integrity...')
        )
        
        with connection.cursor() as cursor:
            constraints = [
                # Ensure asset codes follow the correct pattern
                {
                    'name': 'chk_asset_code_pattern',
                    'table': 'institucion_activoinventario',
                    'condition': "codigo_actual ~ '^[A-Z]{3}(-[A-Z]{3})*-[A-Z]+-(\\d+)-(\\d{4})$'",
                    'description': 'Asset codes must follow warehouse-type-sequence-year pattern'
                },
                
                # Ensure warehouse prefixes are exactly 3 characters
                {
                    'name': 'chk_warehouse_prefix_length',
                    'table': 'institucion_almacenregional',
                    'condition': "LENGTH(prefijo) = 3",
                    'description': 'Warehouse prefixes must be exactly 3 characters'
                },
                
                # Ensure capacity is positive
                {
                    'name': 'chk_warehouse_capacity_positive',
                    'table': 'institucion_almacenregional',
                    'condition': "capacidad_maxima > 0",
                    'description': 'Warehouse capacity must be positive'
                },
                
                # Ensure asset values are positive
                {
                    'name': 'chk_asset_value_positive',
                    'table': 'institucion_activoinventario',
                    'condition': "valor_unitario >= 0",
                    'description': 'Asset values must be non-negative'
                },
                
                # Ensure movement dates are not in the future
                {
                    'name': 'chk_movement_date_not_future',
                    'table': 'institucion_historialmovimientoactivo',
                    'condition': "fecha_movimiento <= CURRENT_TIMESTAMP",
                    'description': 'Movement dates cannot be in the future'
                },
                
                # Ensure transfer requests have valid date ranges
                {
                    'name': 'chk_transfer_date_range',
                    'table': 'institucion_solicitudtraslado',
                    'condition': "fecha_ejecucion_programada IS NULL OR fecha_ejecucion_programada >= fecha_solicitud",
                    'description': 'Transfer execution date must be after request date'
                },
            ]
            
            for constraint in constraints:
                try:
                    # Check if constraint already exists (PostgreSQL)
                    if 'postgresql' in connection.vendor:
                        cursor.execute("""
                            SELECT 1 FROM information_schema.check_constraints 
                            WHERE constraint_name = %s
                        """, [constraint['name']])
                        
                        if cursor.fetchone():
                            self.stdout.write(f"  Constraint {constraint['name']} already exists")
                            continue
                    
                    # Add the constraint
                    sql = f"""
                        ALTER TABLE {constraint['table']} 
                        ADD CONSTRAINT {constraint['name']} 
                        CHECK ({constraint['condition']})
                    """
                    
                    cursor.execute(sql)
                    self.stdout.write(
                        self.style.SUCCESS(f"  Added: {constraint['name']} - {constraint['description']}")
                    )
                    
                except Exception as e:
                    # Some constraints might not be supported in SQLite or might already exist
                    self.stdout.write(
                        self.style.WARNING(f"  Could not add {constraint['name']}: {str(e)}")
                    )
        
        self.stdout.write(
            self.style.SUCCESS('Database constraints setup completed!')
        )