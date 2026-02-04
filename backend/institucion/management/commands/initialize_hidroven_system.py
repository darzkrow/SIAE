"""
Management command to initialize the complete Hidroven system.
"""

import json
from django.core.management.base import BaseCommand
from django.core.management import call_command
from django.db import transaction
from django.contrib.auth import get_user_model

from institucion.system_config import system_config
from institucion.system_integration import hidroven_system

User = get_user_model()


class Command(BaseCommand):
    help = 'Initialize the complete Hidroven organizational restructuring system'

    def add_arguments(self, parser):
        parser.add_argument(
            '--full-setup',
            action='store_true',
            help='Perform complete system setup including data and configuration',
        )
        parser.add_argument(
            '--config-only',
            action='store_true',
            help='Initialize configuration only',
        )
        parser.add_argument(
            '--data-only',
            action='store_true',
            help='Initialize data only',
        )
        parser.add_argument(
            '--validate',
            action='store_true',
            help='Validate system after initialization',
        )
        parser.add_argument(
            '--create-admin',
            action='store_true',
            help='Create default admin user',
        )

    def handle(self, *args, **options):
        self.stdout.write(
            self.style.SUCCESS('Initializing Hidroven System...')
        )
        
        try:
            if options['full_setup']:
                self.full_system_setup()
            elif options['config_only']:
                self.initialize_configuration()
            elif options['data_only']:
                self.initialize_data()
            else:
                self.stdout.write(
                    self.style.WARNING('Use --full-setup, --config-only, or --data-only')
                )
                return
            
            if options['create_admin']:
                self.create_admin_user()
            
            if options['validate']:
                self.validate_system()
            
            self.stdout.write(
                self.style.SUCCESS('Hidroven system initialization completed!')
            )
            
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'System initialization failed: {str(e)}')
            )

    def full_system_setup(self):
        """Perform complete system setup"""
        self.stdout.write('Performing full system setup...')
        
        with transaction.atomic():
            # 1. Initialize configuration
            self.initialize_configuration()
            
            # 2. Initialize database and data
            self.initialize_data()
            
            # 3. Apply database optimizations
            self.apply_optimizations()
            
            # 4. Initialize system integration
            self.initialize_system_integration()

    def initialize_configuration(self):
        """Initialize system configuration"""
        self.stdout.write('Initializing system configuration...')
        
        # Load and validate configuration
        config_summary = system_config.get_configuration_summary()
        
        self.stdout.write(f"  System mode: {config_summary['mode']}")
        self.stdout.write(f"  Version: {config_summary['version']}")
        self.stdout.write(f"  Warehouses configured: {config_summary['warehouse_count']}")
        self.stdout.write(f"  Enabled features: {len(config_summary['enabled_features'])}")
        
        # Check for configuration issues
        if config_summary['validation_issues']:
            self.stdout.write(
                self.style.WARNING('Configuration validation issues found:')
            )
            for issue in config_summary['validation_issues']:
                self.stdout.write(f"  - {issue}")
        else:
            self.stdout.write(
                self.style.SUCCESS('Configuration validation passed')
            )
        
        # Display enabled features
        self.stdout.write('Enabled features:')
        for feature in config_summary['enabled_features']:
            self.stdout.write(f"  ✓ {feature}")

    def initialize_data(self):
        """Initialize system data"""
        self.stdout.write('Initializing system data...')
        
        # Run migrations
        self.stdout.write('  Running database migrations...')
        call_command('migrate', verbosity=0)
        
        # Set up organizational structure
        self.stdout.write('  Setting up organizational structure...')
        call_command('setup_hidroven_data', verbosity=0)
        
        self.stdout.write(
            self.style.SUCCESS('System data initialized successfully')
        )

    def apply_optimizations(self):
        """Apply database and system optimizations"""
        self.stdout.write('Applying system optimizations...')
        
        # Apply database optimizations
        call_command('optimize_database', '--apply', verbosity=0)
        
        self.stdout.write(
            self.style.SUCCESS('System optimizations applied')
        )

    def initialize_system_integration(self):
        """Initialize system integration layer"""
        self.stdout.write('Initializing system integration...')
        
        # Test system health
        health_report = hidroven_system.get_system_health()
        
        self.stdout.write(f"  Overall system status: {health_report['overall_status']}")
        
        # Display service status
        for service_name, service_status in health_report['services'].items():
            status_symbol = '✓' if service_status['status'] == 'healthy' else '✗'
            self.stdout.write(f"  {status_symbol} {service_name}: {service_status['status']}")
        
        if health_report['overall_status'] == 'healthy':
            self.stdout.write(
                self.style.SUCCESS('System integration initialized successfully')
            )
        else:
            self.stdout.write(
                self.style.WARNING('System integration has issues - check service status')
            )

    def create_admin_user(self):
        """Create default admin user"""
        self.stdout.write('Creating default admin user...')
        
        try:
            admin_user, created = User.objects.get_or_create(
                username='hidroven_admin',
                defaults={
                    'email': 'admin@hidroven.gob.ve',
                    'first_name': 'Administrador',
                    'last_name': 'Hidroven',
                    'role': 'ADMINISTRADOR',
                    'is_staff': True,
                    'is_superuser': True,
                    'is_active': True
                }
            )
            
            if created:
                admin_user.set_password('hidroven2024!')
                admin_user.save()
                
                self.stdout.write(
                    self.style.SUCCESS('Admin user created successfully')
                )
                self.stdout.write('  Username: hidroven_admin')
                self.stdout.write('  Password: hidroven2024!')
                self.stdout.write(
                    self.style.WARNING('Please change the default password after first login')
                )
            else:
                self.stdout.write('Admin user already exists')
                
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Failed to create admin user: {str(e)}')
            )

    def validate_system(self):
        """Validate complete system setup"""
        self.stdout.write('Validating system setup...')
        
        # Run system diagnostics
        diagnostics = hidroven_system.run_system_diagnostics()
        
        self.stdout.write(f"  Tests run: {diagnostics['tests_run']}")
        self.stdout.write(f"  Tests passed: {diagnostics['tests_passed']}")
        self.stdout.write(f"  Tests failed: {diagnostics['tests_failed']}")
        
        if diagnostics['tests_failed'] == 0:
            self.stdout.write(
                self.style.SUCCESS('All system validation tests passed')
            )
        else:
            self.stdout.write(
                self.style.WARNING('Some validation tests failed')
            )
            
            # Show failed tests
            for result in diagnostics['results']:
                if result['status'] == 'failed':
                    self.stdout.write(f"  ✗ {result['test']}: {result.get('error', 'Unknown error')}")

    def display_system_summary(self):
        """Display system setup summary"""
        self.stdout.write('\n' + '='*60)
        self.stdout.write('HIDROVEN SYSTEM SETUP SUMMARY')
        self.stdout.write('='*60)
        
        # Configuration summary
        config_summary = system_config.get_configuration_summary()
        self.stdout.write(f"System Mode: {config_summary['mode']}")
        self.stdout.write(f"Version: {config_summary['version']}")
        self.stdout.write(f"Warehouses: {config_summary['warehouse_count']}")
        
        # System health
        health_report = hidroven_system.get_system_health()
        self.stdout.write(f"System Health: {health_report['overall_status']}")
        
        if health_report.get('statistics'):
            stats = health_report['statistics']
            self.stdout.write(f"Active Warehouses: {stats.get('active_warehouses', 0)}")
            self.stdout.write(f"Total Assets: {stats.get('total_assets', 0)}")
        
        # Feature flags
        enabled_features = config_summary['enabled_features']
        self.stdout.write(f"Enabled Features: {len(enabled_features)}")
        for feature in enabled_features:
            self.stdout.write(f"  ✓ {feature}")
        
        self.stdout.write('='*60)
        self.stdout.write('System is ready for use!')
        self.stdout.write('='*60)