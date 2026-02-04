"""
System Configuration Management for Hidroven Organizational Restructuring.

This module provides centralized configuration management for:
- Warehouse prefixes and business rules
- System initialization parameters
- Performance tuning settings
- Feature flags and toggles
- Integration settings
"""

import logging
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, field
from enum import Enum

from django.conf import settings
from django.core.cache import cache
from django.core.exceptions import ValidationError

logger = logging.getLogger(__name__)


class SystemMode(Enum):
    """System operation modes"""
    DEVELOPMENT = "development"
    TESTING = "testing"
    STAGING = "staging"
    PRODUCTION = "production"


class FeatureFlag(Enum):
    """Feature flags for system functionality"""
    AUTO_APPROVAL_ENABLED = "auto_approval_enabled"
    BATCH_TRANSFERS_ENABLED = "batch_transfers_enabled"
    ADVANCED_REPORTING_ENABLED = "advanced_reporting_enabled"
    REAL_TIME_NOTIFICATIONS = "real_time_notifications"
    AUDIT_TRAIL_COMPRESSION = "audit_trail_compression"
    PERFORMANCE_MONITORING = "performance_monitoring"


@dataclass
class WarehouseConfig:
    """Configuration for warehouse operations"""
    prefijo: str
    nombre: str
    region: str
    capacidad_maxima: int
    auto_approval_threshold: int = 100
    notification_emails: List[str] = field(default_factory=list)
    business_rules: Dict[str, Any] = field(default_factory=dict)


@dataclass
class SystemConfiguration:
    """Main system configuration"""
    mode: SystemMode = SystemMode.DEVELOPMENT
    version: str = "1.0.0"
    
    # Warehouse configurations
    warehouses: Dict[str, WarehouseConfig] = field(default_factory=dict)
    
    # Business rules
    max_transfer_value: float = 1000000.0
    max_assets_per_transfer: int = 50
    approval_timeout_hours: int = 72
    audit_retention_days: int = 2555  # 7 years
    
    # Performance settings
    cache_timeout_seconds: int = 3600
    batch_size: int = 1000
    max_concurrent_transfers: int = 10
    
    # Feature flags
    feature_flags: Dict[FeatureFlag, bool] = field(default_factory=dict)
    
    # Integration settings
    external_systems: Dict[str, Dict[str, Any]] = field(default_factory=dict)
    
    # Notification settings
    notification_settings: Dict[str, Any] = field(default_factory=dict)


class HidrovenSystemConfig:
    """
    Centralized system configuration manager.
    
    This class provides:
    - Configuration loading and validation
    - Runtime configuration updates
    - Feature flag management
    - System health monitoring configuration
    - Integration settings management
    """
    
    _instance = None
    _config: SystemConfiguration = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        if self._config is None:
            self._config = self._load_default_configuration()
            self._apply_django_settings()
            logger.info("System configuration initialized")
    
    @property
    def config(self) -> SystemConfiguration:
        """Get current system configuration"""
        return self._config
    
    def _load_default_configuration(self) -> SystemConfiguration:
        """Load default system configuration"""
        config = SystemConfiguration()
        
        # Set default warehouse configurations
        config.warehouses = {
            'ZUL': WarehouseConfig(
                prefijo='ZUL',
                nombre='Almacén Regional Zulia',
                region='Occidental',
                capacidad_maxima=5000,
                auto_approval_threshold=100,
                business_rules={
                    'requires_dual_approval': True,
                    'max_single_transfer_value': 50000.0,
                    'restricted_asset_types': ['EQUIPO_CRITICO']
                }
            ),
            'CAR': WarehouseConfig(
                prefijo='CAR',
                nombre='Almacén Regional Caracas',
                region='Central',
                capacidad_maxima=8000,
                auto_approval_threshold=200,
                business_rules={
                    'requires_dual_approval': True,
                    'max_single_transfer_value': 100000.0,
                    'restricted_asset_types': ['EQUIPO_CRITICO', 'QUIMICO_PELIGROSO']
                }
            ),
            'MIR': WarehouseConfig(
                prefijo='MIR',
                nombre='Almacén Regional Miranda',
                region='Central',
                capacidad_maxima=4500,
                auto_approval_threshold=150,
                business_rules={
                    'requires_dual_approval': False,
                    'max_single_transfer_value': 75000.0
                }
            ),
            'ARA': WarehouseConfig(
                prefijo='ARA',
                nombre='Almacén Regional Aragua',
                region='Central',
                capacidad_maxima=3500,
                auto_approval_threshold=100,
                business_rules={
                    'requires_dual_approval': False,
                    'max_single_transfer_value': 50000.0
                }
            ),
            'LAR': WarehouseConfig(
                prefijo='LAR',
                nombre='Almacén Regional Lara',
                region='Occidental',
                capacidad_maxima=3000,
                auto_approval_threshold=80,
                business_rules={
                    'requires_dual_approval': False,
                    'max_single_transfer_value': 40000.0
                }
            ),
            'TAC': WarehouseConfig(
                prefijo='TAC',
                nombre='Almacén Regional Táchira',
                region='Occidental',
                capacidad_maxima=2500,
                auto_approval_threshold=60,
                business_rules={
                    'requires_dual_approval': False,
                    'max_single_transfer_value': 30000.0
                }
            ),
            'BOL': WarehouseConfig(
                prefijo='BOL',
                nombre='Almacén Regional Bolívar',
                region='Oriental',
                capacidad_maxima=4000,
                auto_approval_threshold=120,
                business_rules={
                    'requires_dual_approval': True,
                    'max_single_transfer_value': 60000.0
                }
            ),
            'ANZ': WarehouseConfig(
                prefijo='ANZ',
                nombre='Almacén Regional Anzoátegui',
                region='Oriental',
                capacidad_maxima=3500,
                auto_approval_threshold=100,
                business_rules={
                    'requires_dual_approval': False,
                    'max_single_transfer_value': 50000.0
                }
            ),
            'MON': WarehouseConfig(
                prefijo='MON',
                nombre='Almacén Regional Monagas',
                region='Oriental',
                capacidad_maxima=2800,
                auto_approval_threshold=80,
                business_rules={
                    'requires_dual_approval': False,
                    'max_single_transfer_value': 40000.0
                }
            )
        }
        
        # Set default feature flags
        config.feature_flags = {
            FeatureFlag.AUTO_APPROVAL_ENABLED: True,
            FeatureFlag.BATCH_TRANSFERS_ENABLED: True,
            FeatureFlag.ADVANCED_REPORTING_ENABLED: True,
            FeatureFlag.REAL_TIME_NOTIFICATIONS: False,
            FeatureFlag.AUDIT_TRAIL_COMPRESSION: False,
            FeatureFlag.PERFORMANCE_MONITORING: True
        }
        
        # Set notification settings
        config.notification_settings = {
            'email_enabled': True,
            'sms_enabled': False,
            'push_notifications_enabled': False,
            'notification_batch_size': 50,
            'notification_retry_attempts': 3,
            'high_priority_immediate': True
        }
        
        return config
    
    def _apply_django_settings(self):
        """Apply Django settings overrides"""
        # Override with Django settings if available
        if hasattr(settings, 'HIDROVEN_CONFIG'):
            django_config = settings.HIDROVEN_CONFIG
            
            # Apply system mode
            if 'MODE' in django_config:
                self._config.mode = SystemMode(django_config['MODE'])
            
            # Apply business rule overrides
            if 'BUSINESS_RULES' in django_config:
                for key, value in django_config['BUSINESS_RULES'].items():
                    setattr(self._config, key, value)
            
            # Apply feature flag overrides
            if 'FEATURE_FLAGS' in django_config:
                for flag_name, enabled in django_config['FEATURE_FLAGS'].items():
                    try:
                        flag = FeatureFlag(flag_name)
                        self._config.feature_flags[flag] = enabled
                    except ValueError:
                        logger.warning(f"Unknown feature flag: {flag_name}")
    
    def get_warehouse_config(self, prefijo: str) -> Optional[WarehouseConfig]:
        """Get configuration for specific warehouse"""
        return self._config.warehouses.get(prefijo)
    
    def is_feature_enabled(self, feature: FeatureFlag) -> bool:
        """Check if a feature flag is enabled"""
        return self._config.feature_flags.get(feature, False)
    
    def get_business_rule(self, warehouse_prefijo: str, rule_name: str, default=None):
        """Get business rule for specific warehouse"""
        warehouse_config = self.get_warehouse_config(warehouse_prefijo)
        if warehouse_config:
            return warehouse_config.business_rules.get(rule_name, default)
        return default
    
    def update_feature_flag(self, feature: FeatureFlag, enabled: bool):
        """Update feature flag at runtime"""
        self._config.feature_flags[feature] = enabled
        
        # Cache the update
        cache_key = f"feature_flag_{feature.value}"
        cache.set(cache_key, enabled, timeout=self._config.cache_timeout_seconds)
        
        logger.info(f"Feature flag {feature.value} set to {enabled}")
    
    def get_system_limits(self) -> Dict[str, Any]:
        """Get system operational limits"""
        return {
            'max_transfer_value': self._config.max_transfer_value,
            'max_assets_per_transfer': self._config.max_assets_per_transfer,
            'approval_timeout_hours': self._config.approval_timeout_hours,
            'audit_retention_days': self._config.audit_retention_days,
            'max_concurrent_transfers': self._config.max_concurrent_transfers
        }
    
    def validate_configuration(self) -> List[str]:
        """Validate current configuration and return any issues"""
        issues = []
        
        # Validate warehouse configurations
        for prefijo, warehouse_config in self._config.warehouses.items():
            if len(prefijo) != 3:
                issues.append(f"Warehouse prefix {prefijo} must be exactly 3 characters")
            
            if warehouse_config.capacidad_maxima <= 0:
                issues.append(f"Warehouse {prefijo} capacity must be positive")
            
            if warehouse_config.auto_approval_threshold < 0:
                issues.append(f"Warehouse {prefijo} auto-approval threshold must be non-negative")
        
        # Validate business rules
        if self._config.max_transfer_value <= 0:
            issues.append("Max transfer value must be positive")
        
        if self._config.max_assets_per_transfer <= 0:
            issues.append("Max assets per transfer must be positive")
        
        if self._config.approval_timeout_hours <= 0:
            issues.append("Approval timeout must be positive")
        
        return issues
    
    def get_configuration_summary(self) -> Dict[str, Any]:
        """Get summary of current configuration"""
        return {
            'mode': self._config.mode.value,
            'version': self._config.version,
            'warehouse_count': len(self._config.warehouses),
            'enabled_features': [
                flag.value for flag, enabled in self._config.feature_flags.items() 
                if enabled
            ],
            'system_limits': self.get_system_limits(),
            'validation_issues': self.validate_configuration()
        }
    
    def export_configuration(self) -> Dict[str, Any]:
        """Export configuration for backup or transfer"""
        return {
            'mode': self._config.mode.value,
            'version': self._config.version,
            'warehouses': {
                prefijo: {
                    'prefijo': wh.prefijo,
                    'nombre': wh.nombre,
                    'region': wh.region,
                    'capacidad_maxima': wh.capacidad_maxima,
                    'auto_approval_threshold': wh.auto_approval_threshold,
                    'notification_emails': wh.notification_emails,
                    'business_rules': wh.business_rules
                }
                for prefijo, wh in self._config.warehouses.items()
            },
            'business_rules': {
                'max_transfer_value': self._config.max_transfer_value,
                'max_assets_per_transfer': self._config.max_assets_per_transfer,
                'approval_timeout_hours': self._config.approval_timeout_hours,
                'audit_retention_days': self._config.audit_retention_days
            },
            'feature_flags': {
                flag.value: enabled 
                for flag, enabled in self._config.feature_flags.items()
            },
            'notification_settings': self._config.notification_settings
        }
    
    def import_configuration(self, config_data: Dict[str, Any]):
        """Import configuration from backup or external source"""
        try:
            # Validate imported data
            if 'warehouses' not in config_data:
                raise ValidationError("Configuration must include warehouses")
            
            # Create new configuration
            new_config = SystemConfiguration()
            
            # Import basic settings
            if 'mode' in config_data:
                new_config.mode = SystemMode(config_data['mode'])
            
            if 'version' in config_data:
                new_config.version = config_data['version']
            
            # Import warehouse configurations
            for prefijo, wh_data in config_data['warehouses'].items():
                new_config.warehouses[prefijo] = WarehouseConfig(
                    prefijo=wh_data['prefijo'],
                    nombre=wh_data['nombre'],
                    region=wh_data['region'],
                    capacidad_maxima=wh_data['capacidad_maxima'],
                    auto_approval_threshold=wh_data.get('auto_approval_threshold', 100),
                    notification_emails=wh_data.get('notification_emails', []),
                    business_rules=wh_data.get('business_rules', {})
                )
            
            # Import business rules
            if 'business_rules' in config_data:
                br = config_data['business_rules']
                new_config.max_transfer_value = br.get('max_transfer_value', 1000000.0)
                new_config.max_assets_per_transfer = br.get('max_assets_per_transfer', 50)
                new_config.approval_timeout_hours = br.get('approval_timeout_hours', 72)
                new_config.audit_retention_days = br.get('audit_retention_days', 2555)
            
            # Import feature flags
            if 'feature_flags' in config_data:
                for flag_name, enabled in config_data['feature_flags'].items():
                    try:
                        flag = FeatureFlag(flag_name)
                        new_config.feature_flags[flag] = enabled
                    except ValueError:
                        logger.warning(f"Unknown feature flag in import: {flag_name}")
            
            # Import notification settings
            if 'notification_settings' in config_data:
                new_config.notification_settings = config_data['notification_settings']
            
            # Validate new configuration
            temp_config = self._config
            self._config = new_config
            issues = self.validate_configuration()
            
            if issues:
                self._config = temp_config
                raise ValidationError(f"Configuration validation failed: {issues}")
            
            logger.info("Configuration imported successfully")
            
        except Exception as e:
            logger.error(f"Configuration import failed: {str(e)}")
            raise ValidationError(f"Configuration import failed: {str(e)}")


# Global configuration instance
system_config = HidrovenSystemConfig()