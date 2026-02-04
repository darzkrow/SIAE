"""
Management command for continuous system health monitoring.
"""

import time
import json
from datetime import datetime, timedelta
from django.core.management.base import BaseCommand
from django.utils import timezone

from institucion.system_integration import hidroven_system
from institucion.system_config import system_config


class Command(BaseCommand):
    help = 'Monitor Hidroven system health and performance'

    def add_arguments(self, parser):
        parser.add_argument(
            '--continuous',
            action='store_true',
            help='Run continuous monitoring (Ctrl+C to stop)',
        )
        parser.add_argument(
            '--interval',
            type=int,
            default=60,
            help='Monitoring interval in seconds (default: 60)',
        )
        parser.add_argument(
            '--output-file',
            type=str,
            help='Output monitoring data to JSON file',
        )
        parser.add_argument(
            '--alert-threshold',
            type=str,
            choices=['low', 'medium', 'high'],
            default='medium',
            help='Alert threshold level (default: medium)',
        )

    def handle(self, *args, **options):
        self.continuous = options['continuous']
        self.interval = options['interval']
        self.output_file = options['output_file']
        self.alert_threshold = options['alert_threshold']
        
        self.stdout.write(
            self.style.SUCCESS('Starting Hidroven system health monitoring...')
        )
        
        if self.continuous:
            self.run_continuous_monitoring()
        else:
            self.run_single_check()

    def run_single_check(self):
        """Run a single health check"""
        self.stdout.write('Running system health check...')
        
        health_data = self.collect_health_data()
        self.display_health_report(health_data)
        
        if self.output_file:
            self.save_health_data(health_data)

    def run_continuous_monitoring(self):
        """Run continuous health monitoring"""
        self.stdout.write(f'Starting continuous monitoring (interval: {self.interval}s)')
        self.stdout.write('Press Ctrl+C to stop monitoring')
        
        try:
            while True:
                health_data = self.collect_health_data()
                self.display_health_summary(health_data)
                self.check_alerts(health_data)
                
                if self.output_file:
                    self.save_health_data(health_data)
                
                time.sleep(self.interval)
                
        except KeyboardInterrupt:
            self.stdout.write('\nMonitoring stopped by user')

    def collect_health_data(self):
        """Collect comprehensive health data"""
        timestamp = timezone.now()
        
        # Get system health
        health_report = hidroven_system.get_system_health()
        
        # Get configuration summary
        config_summary = system_config.get_configuration_summary()
        
        # Get system diagnostics
        diagnostics = hidroven_system.run_system_diagnostics()
        
        return {
            'timestamp': timestamp.isoformat(),
            'health_report': health_report,
            'config_summary': config_summary,
            'diagnostics': diagnostics,
            'monitoring_metadata': {
                'interval': self.interval,
                'alert_threshold': self.alert_threshold
            }
        }

    def display_health_report(self, health_data):
        """Display detailed health report"""
        health_report = health_data['health_report']
        config_summary = health_data['config_summary']
        diagnostics = health_data['diagnostics']
        
        self.stdout.write('\n' + '='*60)
        self.stdout.write('HIDROVEN SYSTEM HEALTH REPORT')
        self.stdout.write('='*60)
        self.stdout.write(f"Timestamp: {health_data['timestamp']}")
        self.stdout.write(f"Overall Status: {health_report['overall_status']}")
        
        # Service status
        self.stdout.write('\nService Status:')
        for service_name, service_status in health_report['services'].items():
            status_color = self.style.SUCCESS if service_status['status'] == 'healthy' else self.style.ERROR
            self.stdout.write(f"  {service_name}: {status_color(service_status['status'])}")
        
        # System statistics
        if health_report.get('statistics'):
            self.stdout.write('\nSystem Statistics:')
            for stat_name, stat_value in health_report['statistics'].items():
                self.stdout.write(f"  {stat_name}: {stat_value}")
        
        # Diagnostics
        self.stdout.write('\nDiagnostics:')
        self.stdout.write(f"  Tests run: {diagnostics['tests_run']}")
        self.stdout.write(f"  Tests passed: {diagnostics['tests_passed']}")
        self.stdout.write(f"  Tests failed: {diagnostics['tests_failed']}")
        
        # Alerts
        if health_report.get('alerts'):
            self.stdout.write('\nAlerts:')
            for alert in health_report['alerts']:
                alert_color = self.style.ERROR if alert['severity'] == 'high' else self.style.WARNING
                self.stdout.write(f"  {alert_color(alert['type'])}: {alert['message']}")
        else:
            self.stdout.write('\nNo alerts')
        
        # Configuration
        self.stdout.write('\nConfiguration:')
        self.stdout.write(f"  Mode: {config_summary['mode']}")
        self.stdout.write(f"  Version: {config_summary['version']}")
        self.stdout.write(f"  Warehouses: {config_summary['warehouse_count']}")
        self.stdout.write(f"  Enabled features: {len(config_summary['enabled_features'])}")
        
        self.stdout.write('='*60)

    def display_health_summary(self, health_data):
        """Display brief health summary for continuous monitoring"""
        health_report = health_data['health_report']
        diagnostics = health_data['diagnostics']
        timestamp = datetime.fromisoformat(health_data['timestamp'].replace('Z', '+00:00'))
        
        # Format timestamp
        time_str = timestamp.strftime('%H:%M:%S')
        
        # Count healthy services
        services = health_report['services']
        healthy_count = sum(1 for s in services.values() if s['status'] == 'healthy')
        total_services = len(services)
        
        # Get statistics
        stats = health_report.get('statistics', {})
        total_assets = stats.get('total_assets', 0)
        pending_transfers = stats.get('pending_transfers', 0)
        
        # Display summary line
        status_color = self.style.SUCCESS if health_report['overall_status'] == 'healthy' else self.style.ERROR
        
        summary = (f"[{time_str}] Status: {status_color(health_report['overall_status'])} | "
                  f"Services: {healthy_count}/{total_services} | "
                  f"Assets: {total_assets} | "
                  f"Pending: {pending_transfers} | "
                  f"Tests: {diagnostics['tests_passed']}/{diagnostics['tests_run']}")
        
        self.stdout.write(summary)

    def check_alerts(self, health_data):
        """Check for alerts based on threshold"""
        health_report = health_data['health_report']
        alerts = health_report.get('alerts', [])
        
        # Filter alerts based on threshold
        threshold_levels = {
            'low': ['low', 'medium', 'high'],
            'medium': ['medium', 'high'],
            'high': ['high']
        }
        
        relevant_alerts = [
            alert for alert in alerts 
            if alert['severity'] in threshold_levels[self.alert_threshold]
        ]
        
        if relevant_alerts:
            self.stdout.write(
                self.style.WARNING(f'  ALERTS ({len(relevant_alerts)}):')
            )
            for alert in relevant_alerts:
                alert_color = self.style.ERROR if alert['severity'] == 'high' else self.style.WARNING
                self.stdout.write(f"    {alert_color(alert['message'])}")

    def save_health_data(self, health_data):
        """Save health data to JSON file"""
        try:
            # Convert datetime objects to strings for JSON serialization
            serializable_data = self.make_json_serializable(health_data)
            
            with open(self.output_file, 'a') as f:
                json.dump(serializable_data, f)
                f.write('\n')
                
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Failed to save health data: {str(e)}')
            )

    def make_json_serializable(self, obj):
        """Convert objects to JSON-serializable format"""
        if isinstance(obj, dict):
            return {key: self.make_json_serializable(value) for key, value in obj.items()}
        elif isinstance(obj, list):
            return [self.make_json_serializable(item) for item in obj]
        elif hasattr(obj, 'isoformat'):  # datetime objects
            return obj.isoformat()
        else:
            return obj