"""
Management command to apply database performance optimizations for Hidroven system.
"""

from django.core.management.base import BaseCommand
from django.db import connection
from django.conf import settings


class Command(BaseCommand):
    help = 'Apply database performance optimizations for Hidroven organizational restructuring'

    def add_arguments(self, parser):
        parser.add_argument(
            '--analyze',
            action='store_true',
            help='Analyze current database performance',
        )
        parser.add_argument(
            '--apply',
            action='store_true',
            help='Apply performance optimizations',
        )

    def handle(self, *args, **options):
        if options['analyze']:
            self.analyze_performance()
        
        if options['apply']:
            self.apply_optimizations()
        
        if not options['analyze'] and not options['apply']:
            self.stdout.write(
                self.style.WARNING('Use --analyze or --apply to perform operations')
            )

    def analyze_performance(self):
        """Analyze current database performance"""
        self.stdout.write(
            self.style.SUCCESS('Analyzing database performance...')
        )
        
        with connection.cursor() as cursor:
            # Check table sizes
            if 'sqlite' in settings.DATABASES['default']['ENGINE']:
                self.analyze_sqlite_performance(cursor)
            elif 'postgresql' in settings.DATABASES['default']['ENGINE']:
                self.analyze_postgresql_performance(cursor)
            else:
                self.stdout.write(
                    self.style.WARNING('Performance analysis not implemented for this database engine')
                )

    def analyze_sqlite_performance(self, cursor):
        """Analyze SQLite performance"""
        self.stdout.write('SQLite Performance Analysis:')
        
        # Get table information
        cursor.execute("""
            SELECT name, sql FROM sqlite_master 
            WHERE type='table' AND name LIKE 'institucion_%'
            ORDER BY name
        """)
        
        tables = cursor.fetchall()
        self.stdout.write(f'Found {len(tables)} institucion tables')
        
        # Check indexes
        cursor.execute("""
            SELECT name, tbl_name, sql FROM sqlite_master 
            WHERE type='index' AND tbl_name LIKE 'institucion_%'
            ORDER BY tbl_name, name
        """)
        
        indexes = cursor.fetchall()
        self.stdout.write(f'Found {len(indexes)} indexes on institucion tables')
        
        # Display index information
        for index_name, table_name, sql in indexes:
            if sql:  # Skip auto-generated indexes
                self.stdout.write(f'  {table_name}: {index_name}')

    def analyze_postgresql_performance(self, cursor):
        """Analyze PostgreSQL performance"""
        self.stdout.write('PostgreSQL Performance Analysis:')
        
        # Get table sizes
        cursor.execute("""
            SELECT 
                schemaname,
                tablename,
                attname,
                n_distinct,
                correlation
            FROM pg_stats 
            WHERE schemaname = 'public' 
            AND tablename LIKE 'institucion_%'
            ORDER BY tablename, attname
        """)
        
        stats = cursor.fetchall()
        self.stdout.write(f'Found statistics for {len(stats)} columns')
        
        # Check index usage
        cursor.execute("""
            SELECT 
                schemaname,
                tablename,
                indexname,
                idx_scan,
                idx_tup_read,
                idx_tup_fetch
            FROM pg_stat_user_indexes 
            WHERE schemaname = 'public' 
            AND tablename LIKE 'institucion_%'
            ORDER BY tablename, indexname
        """)
        
        index_stats = cursor.fetchall()
        self.stdout.write(f'Found usage statistics for {len(index_stats)} indexes')

    def apply_optimizations(self):
        """Apply database optimizations"""
        self.stdout.write(
            self.style.SUCCESS('Applying database optimizations...')
        )
        
        with connection.cursor() as cursor:
            if 'sqlite' in settings.DATABASES['default']['ENGINE']:
                self.apply_sqlite_optimizations(cursor)
            elif 'postgresql' in settings.DATABASES['default']['ENGINE']:
                self.apply_postgresql_optimizations(cursor)
            else:
                self.stdout.write(
                    self.style.WARNING('Optimizations not implemented for this database engine')
                )

    def apply_sqlite_optimizations(self, cursor):
        """Apply SQLite-specific optimizations"""
        self.stdout.write('Applying SQLite optimizations...')
        
        optimizations = [
            # Enable WAL mode for better concurrency
            "PRAGMA journal_mode=WAL;",
            
            # Optimize cache size (10MB)
            "PRAGMA cache_size=10000;",
            
            # Enable foreign key constraints
            "PRAGMA foreign_keys=ON;",
            
            # Optimize synchronous mode for performance
            "PRAGMA synchronous=NORMAL;",
            
            # Set temp store to memory
            "PRAGMA temp_store=MEMORY;",
            
            # Optimize page size
            "PRAGMA page_size=4096;",
        ]
        
        for optimization in optimizations:
            try:
                cursor.execute(optimization)
                self.stdout.write(f'  Applied: {optimization}')
            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(f'  Failed: {optimization} - {str(e)}')
                )
        
        # Analyze tables for query optimization
        tables_to_analyze = [
            'institucion_empresa',
            'institucion_vicepresidencia', 
            'institucion_unidadorganizacional',
            'institucion_almacenregional',
            'institucion_activoinventario',
            'institucion_historialmovimientoactivo',
            'institucion_solicitudtraslado',
            'institucion_aprobaciontraslado',
        ]
        
        for table in tables_to_analyze:
            try:
                cursor.execute(f"ANALYZE {table};")
                self.stdout.write(f'  Analyzed: {table}')
            except Exception as e:
                self.stdout.write(
                    self.style.WARNING(f'  Could not analyze {table}: {str(e)}')
                )

    def apply_postgresql_optimizations(self, cursor):
        """Apply PostgreSQL-specific optimizations"""
        self.stdout.write('Applying PostgreSQL optimizations...')
        
        # Update table statistics
        tables_to_analyze = [
            'institucion_empresa',
            'institucion_vicepresidencia', 
            'institucion_unidadorganizacional',
            'institucion_almacenregional',
            'institucion_activoinventario',
            'institucion_historialmovimientoactivo',
            'institucion_solicitudtraslado',
            'institucion_aprobaciontraslado',
        ]
        
        for table in tables_to_analyze:
            try:
                cursor.execute(f"ANALYZE {table};")
                self.stdout.write(f'  Analyzed: {table}')
            except Exception as e:
                self.stdout.write(
                    self.style.WARNING(f'  Could not analyze {table}: {str(e)}')
                )
        
        # Create additional partial indexes for common queries
        additional_indexes = [
            # Index for active warehouses only
            """
            CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_almacen_activo_partial 
            ON institucion_almacenregional (prefijo, unidad_organizacional_id) 
            WHERE activo = true;
            """,
            
            # Index for assets in specific states
            """
            CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_activo_estado_almacen 
            ON institucion_activoinventario (estado, almacen_actual_id) 
            WHERE estado IN ('EN_ALMACEN', 'EN_TRANSITO');
            """,
            
            # Index for recent movements
            """
            CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_movimiento_reciente 
            ON institucion_historialmovimientoactivo (activo_id, fecha_movimiento DESC) 
            WHERE fecha_movimiento >= CURRENT_DATE - INTERVAL '30 days';
            """,
            
            # Index for pending transfer requests
            """
            CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_solicitud_pendiente 
            ON institucion_solicitudtraslado (almacen_origen_id, fecha_solicitud DESC) 
            WHERE estado IN ('PENDIENTE', 'APROBADA_PARCIAL');
            """,
        ]
        
        for index_sql in additional_indexes:
            try:
                cursor.execute(index_sql)
                self.stdout.write('  Created additional index')
            except Exception as e:
                self.stdout.write(
                    self.style.WARNING(f'  Could not create index: {str(e)}')
                )

        self.stdout.write(
            self.style.SUCCESS('Database optimizations applied successfully!')
        )