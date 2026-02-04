#!/usr/bin/env python
"""
Demo script for SystemConfiguration model functionality.
Shows how to use the system configuration management features.
"""
import os
import sys
import django

# Setup Django environment
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.contrib.auth import get_user_model
from inventario.models import SystemConfiguration
import json

User = get_user_model()


def create_demo_user():
    """Create a demo user for configuration management."""
    user, created = User.objects.get_or_create(
        username='config_admin',
        defaults={
            'email': 'admin@example.com',
            'is_staff': True,
            'is_superuser': True
        }
    )
    if created:
        user.set_password('admin123')
        user.save()
        print(f"✓ Created demo user: {user.username}")
    else:
        print(f"✓ Using existing user: {user.username}")
    return user


def demo_basic_configuration():
    """Demonstrate basic configuration management."""
    print("\n" + "="*60)
    print("BASIC CONFIGURATION MANAGEMENT")
    print("="*60)
    
    user = create_demo_user()
    
    # Create basic configurations
    configs = [
        {
            'key': 'email.smtp_host',
            'value': 'smtp.gmail.com',
            'category': SystemConfiguration.Category.EMAIL,
            'description': 'SMTP server hostname for email delivery'
        },
        {
            'key': 'email.smtp_port',
            'value': 587,
            'category': SystemConfiguration.Category.EMAIL,
            'description': 'SMTP server port'
        },
        {
            'key': 'security.max_login_attempts',
            'value': 5,
            'category': SystemConfiguration.Category.SECURITY,
            'description': 'Maximum failed login attempts before lockout'
        },
        {
            'key': 'ui.items_per_page',
            'value': 25,
            'category': SystemConfiguration.Category.UI,
            'description': 'Number of items to display per page'
        }
    ]
    
    print("\n1. Creating basic configurations...")
    for config_data in configs:
        config = SystemConfiguration.set_config(
            modified_by=user,
            **config_data
        )
        print(f"   ✓ {config.key} = {config.value}")
    
    print("\n2. Retrieving configurations...")
    for config_data in configs:
        value = SystemConfiguration.get_config(config_data['key'])
        print(f"   {config_data['key']} = {value}")


def demo_environment_specific():
    """Demonstrate environment-specific configurations."""
    print("\n" + "="*60)
    print("ENVIRONMENT-SPECIFIC CONFIGURATIONS")
    print("="*60)
    
    user = create_demo_user()
    
    # Create environment-specific configurations
    print("\n1. Creating environment-specific database configurations...")
    
    # Production database config
    SystemConfiguration.set_config(
        key='database.max_connections',
        value=100,
        environment=SystemConfiguration.Environment.PRODUCTION,
        category=SystemConfiguration.Category.PERFORMANCE,
        description='Maximum database connections for production',
        modified_by=user
    )
    
    # Development database config
    SystemConfiguration.set_config(
        key='database.max_connections',
        value=10,
        environment=SystemConfiguration.Environment.DEVELOPMENT,
        category=SystemConfiguration.Category.PERFORMANCE,
        description='Maximum database connections for development',
        modified_by=user
    )
    
    # All environments config (fallback)
    SystemConfiguration.set_config(
        key='database.timeout',
        value=30,
        environment=SystemConfiguration.Environment.ALL,
        category=SystemConfiguration.Category.PERFORMANCE,
        description='Database connection timeout in seconds',
        modified_by=user
    )
    
    print("   ✓ Production max_connections = 100")
    print("   ✓ Development max_connections = 10")
    print("   ✓ All environments timeout = 30")
    
    print("\n2. Testing environment-specific retrieval...")
    
    # Test production environment
    prod_connections = SystemConfiguration.get_config(
        'database.max_connections', 
        environment=SystemConfiguration.Environment.PRODUCTION
    )
    print(f"   Production max_connections: {prod_connections}")
    
    # Test development environment
    dev_connections = SystemConfiguration.get_config(
        'database.max_connections', 
        environment=SystemConfiguration.Environment.DEVELOPMENT
    )
    print(f"   Development max_connections: {dev_connections}")
    
    # Test fallback for staging (should use 'all' environment)
    staging_timeout = SystemConfiguration.get_config(
        'database.timeout', 
        environment=SystemConfiguration.Environment.STAGING
    )
    print(f"   Staging timeout (fallback): {staging_timeout}")


def demo_complex_values():
    """Demonstrate storing complex JSON values."""
    print("\n" + "="*60)
    print("COMPLEX JSON CONFIGURATIONS")
    print("="*60)
    
    user = create_demo_user()
    
    # Complex configuration values
    complex_configs = [
        {
            'key': 'notifications.email_settings',
            'value': {
                'enabled': True,
                'templates': {
                    'welcome': 'welcome_email.html',
                    'password_reset': 'password_reset.html'
                },
                'retry_attempts': 3,
                'batch_size': 50
            },
            'category': SystemConfiguration.Category.NOTIFICATIONS,
            'description': 'Email notification configuration'
        },
        {
            'key': 'integration.api_endpoints',
            'value': {
                'external_services': [
                    {'name': 'weather_api', 'url': 'https://api.weather.com', 'timeout': 10},
                    {'name': 'maps_api', 'url': 'https://api.maps.com', 'timeout': 5}
                ],
                'rate_limits': {
                    'requests_per_minute': 100,
                    'burst_limit': 20
                }
            },
            'category': SystemConfiguration.Category.INTEGRATION,
            'description': 'External API integration settings'
        }
    ]
    
    print("\n1. Creating complex JSON configurations...")
    for config_data in complex_configs:
        config = SystemConfiguration.set_config(
            modified_by=user,
            **config_data
        )
        print(f"   ✓ {config.key}")
        print(f"     Value: {json.dumps(config.value, indent=6)}")
    
    print("\n2. Retrieving and using complex configurations...")
    
    # Retrieve email settings
    email_settings = SystemConfiguration.get_config('notifications.email_settings')
    if email_settings:
        print(f"   Email notifications enabled: {email_settings['enabled']}")
        print(f"   Welcome template: {email_settings['templates']['welcome']}")
        print(f"   Retry attempts: {email_settings['retry_attempts']}")
    
    # Retrieve API settings
    api_settings = SystemConfiguration.get_config('integration.api_endpoints')
    if api_settings:
        print(f"   External services count: {len(api_settings['external_services'])}")
        print(f"   Rate limit: {api_settings['rate_limits']['requests_per_minute']} req/min")


def demo_sensitive_configurations():
    """Demonstrate sensitive configuration handling."""
    print("\n" + "="*60)
    print("SENSITIVE CONFIGURATIONS")
    print("="*60)
    
    user = create_demo_user()
    
    print("\n1. Creating sensitive configurations...")
    
    # Create sensitive configurations
    sensitive_configs = [
        {
            'key': 'email.smtp_password',
            'value': 'super_secret_password',
            'category': SystemConfiguration.Category.EMAIL,
            'is_sensitive': True,
            'description': 'SMTP server password'
        },
        {
            'key': 'integration.api_key',
            'value': 'sk-1234567890abcdef',
            'category': SystemConfiguration.Category.INTEGRATION,
            'is_sensitive': True,
            'description': 'External API authentication key'
        },
        {
            'key': 'database.connection_string',
            'value': 'postgresql://user:password@localhost:5432/db',
            'category': SystemConfiguration.Category.GENERAL,
            'is_sensitive': True,
            'description': 'Database connection string'
        }
    ]
    
    for config_data in sensitive_configs:
        config = SystemConfiguration.set_config(
            modified_by=user,
            **config_data
        )
        print(f"   ✓ {config.key} (sensitive)")
    
    print("\n2. Testing sensitive configuration filtering...")
    
    # Get all email configurations (excluding sensitive)
    email_configs = SystemConfiguration.get_by_category(
        SystemConfiguration.Category.EMAIL,
        include_sensitive=False
    )
    print(f"   Email configs (non-sensitive): {email_configs.count()}")
    for config in email_configs:
        print(f"     - {config.key}")
    
    # Get all email configurations (including sensitive)
    email_configs_all = SystemConfiguration.get_by_category(
        SystemConfiguration.Category.EMAIL,
        include_sensitive=True
    )
    print(f"   Email configs (all): {email_configs_all.count()}")
    for config in email_configs_all:
        sensitive_marker = " (sensitive)" if config.is_sensitive else ""
        print(f"     - {config.key}{sensitive_marker}")


def demo_export_import():
    """Demonstrate configuration export and import."""
    print("\n" + "="*60)
    print("CONFIGURATION EXPORT/IMPORT")
    print("="*60)
    
    user = create_demo_user()
    
    print("\n1. Exporting configurations...")
    
    # Export all configurations (excluding sensitive)
    export_data = SystemConfiguration.export_configurations(
        include_sensitive=False
    )
    
    print(f"   ✓ Exported {len(export_data['configurations'])} configurations")
    print(f"   Export timestamp: {export_data['export_timestamp']}")
    print(f"   Include sensitive: {export_data['include_sensitive']}")
    
    # Show sample of exported data
    if export_data['configurations']:
        sample_config = export_data['configurations'][0]
        print(f"   Sample config: {sample_config['key']} = {sample_config['value']}")
    
    print("\n2. Simulating import to different environment...")
    
    # Modify export data for import simulation
    import_data = {
        'configurations': [
            {
                'key': 'imported.test_setting',
                'value': 'imported_value',
                'category': 'general',
                'environment': 'development',
                'is_sensitive': False,
                'description': 'Test imported configuration'
            },
            {
                'key': 'imported.another_setting',
                'value': {'nested': 'data', 'count': 42},
                'category': 'performance',
                'environment': 'all',
                'is_sensitive': False,
                'description': 'Another test configuration'
            }
        ]
    }
    
    # Import configurations
    import_results = SystemConfiguration.import_configurations(
        import_data,
        modified_by=user
    )
    
    print(f"   ✓ Import results:")
    print(f"     Created: {import_results['created']}")
    print(f"     Updated: {import_results['updated']}")
    print(f"     Skipped: {import_results['skipped']}")
    print(f"     Errors: {len(import_results['errors'])}")
    
    # Verify imported configurations
    print("\n3. Verifying imported configurations...")
    for config_data in import_data['configurations']:
        value = SystemConfiguration.get_config(
            config_data['key'],
            environment=config_data['environment']
        )
        print(f"   {config_data['key']} = {value}")


def demo_configuration_categories():
    """Demonstrate configuration organization by categories."""
    print("\n" + "="*60)
    print("CONFIGURATION CATEGORIES")
    print("="*60)
    
    print("\n1. Available categories:")
    for category_code, category_name in SystemConfiguration.Category.choices:
        print(f"   - {category_code}: {category_name}")
    
    print("\n2. Configurations by category:")
    for category_code, category_name in SystemConfiguration.Category.choices:
        configs = SystemConfiguration.get_by_category(category_code)
        if configs.exists():
            print(f"\n   {category_name} ({configs.count()} configs):")
            for config in configs[:3]:  # Show first 3
                print(f"     - {config.key}: {config.value}")
            if configs.count() > 3:
                print(f"     ... and {configs.count() - 3} more")


def main():
    """Run all demonstrations."""
    print("SystemConfiguration Model Demonstration")
    print("="*60)
    
    try:
        # Clear existing demo configurations
        from django.db.models import Q
        demo_prefixes = ['email.', 'database.', 'security.', 'ui.', 'notifications.', 'integration.', 'imported.']
        query = Q()
        for prefix in demo_prefixes:
            query |= Q(key__startswith=prefix)
        SystemConfiguration.objects.filter(query).delete()
        
        # Run demonstrations
        demo_basic_configuration()
        demo_environment_specific()
        demo_complex_values()
        demo_sensitive_configurations()
        demo_export_import()
        demo_configuration_categories()
        
        print("\n" + "="*60)
        print("DEMONSTRATION COMPLETED SUCCESSFULLY")
        print("="*60)
        
        # Show summary
        total_configs = SystemConfiguration.objects.count()
        print(f"\nTotal configurations in system: {total_configs}")
        
    except Exception as e:
        print(f"\n❌ Error during demonstration: {e}")
        import traceback
        traceback.print_exc()


if __name__ == '__main__':
    main()