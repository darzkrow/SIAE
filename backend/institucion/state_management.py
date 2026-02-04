# ============================================================================
# ASSET STATE MANAGEMENT SYSTEM
# ============================================================================

from typing import Dict, List, Optional, Tuple, Any
from django.core.exceptions import ValidationError
from django.utils import timezone
from django.db import transaction
from django.contrib.auth import get_user_model
from dataclasses import dataclass
import logging

User = get_user_model()
logger = logging.getLogger(__name__)


@dataclass
class StateTransitionRule:
    """
    Data class to define state transition rules.
    """
    from_state: str
    to_state: str
    allowed: bool
    requires_approval: bool = False
    auto_trigger_conditions: Optional[List[str]] = None
    business_rule_description: str = ""


class AssetStateManager:
    """
    Service class for managing asset states with business rules and audit logging.
    
    Handles:
    - State transition validation with business rules
    - Automatic state updates for transfer workflows
    - State change audit logging
    - Business rule enforcement for valid transitions
    - Integration with transfer workflow system
    
    Asset States:
    - EN_ALMACEN: Asset is stored in warehouse
    - EN_TRANSITO: Asset is being transferred between warehouses
    - INSTALADO: Asset is installed but not yet in use
    - EN_USO: Asset is actively being used
    - MANTENIMIENTO: Asset is under maintenance
    """
    
    # Asset states as defined in requirements
    ASSET_STATES = [
        'EN_ALMACEN',
        'EN_TRANSITO', 
        'INSTALADO',
        'EN_USO',
        'MANTENIMIENTO',
    ]
    
    # State transition rules with business logic
    STATE_TRANSITION_RULES = [
        # From EN_ALMACEN
        StateTransitionRule(
            from_state='EN_ALMACEN',
            to_state='EN_TRANSITO',
            allowed=True,
            auto_trigger_conditions=['transfer_approved'],
            business_rule_description='Asset can be moved from warehouse when transfer is approved'
        ),
        StateTransitionRule(
            from_state='EN_ALMACEN',
            to_state='INSTALADO',
            allowed=True,
            business_rule_description='Asset can be installed directly from warehouse'
        ),
        StateTransitionRule(
            from_state='EN_ALMACEN',
            to_state='MANTENIMIENTO',
            allowed=True,
            business_rule_description='Asset can go to maintenance from warehouse'
        ),
        
        # From EN_TRANSITO
        StateTransitionRule(
            from_state='EN_TRANSITO',
            to_state='EN_ALMACEN',
            allowed=True,
            auto_trigger_conditions=['transfer_completed'],
            business_rule_description='Asset returns to warehouse when transfer is completed'
        ),
        StateTransitionRule(
            from_state='EN_TRANSITO',
            to_state='INSTALADO',
            allowed=True,
            business_rule_description='Asset can be installed directly upon arrival'
        ),
        
        # From INSTALADO
        StateTransitionRule(
            from_state='INSTALADO',
            to_state='EN_USO',
            allowed=True,
            business_rule_description='Installed asset can be put into use'
        ),
        StateTransitionRule(
            from_state='INSTALADO',
            to_state='MANTENIMIENTO',
            allowed=True,
            business_rule_description='Installed asset can go to maintenance'
        ),
        StateTransitionRule(
            from_state='INSTALADO',
            to_state='EN_ALMACEN',
            allowed=True,
            business_rule_description='Installed asset can be returned to warehouse'
        ),
        
        # From EN_USO
        StateTransitionRule(
            from_state='EN_USO',
            to_state='MANTENIMIENTO',
            allowed=True,
            business_rule_description='Asset in use can go to maintenance'
        ),
        StateTransitionRule(
            from_state='EN_USO',
            to_state='EN_ALMACEN',
            allowed=True,
            business_rule_description='Asset in use can be returned to warehouse'
        ),
        
        # From MANTENIMIENTO
        StateTransitionRule(
            from_state='MANTENIMIENTO',
            to_state='EN_ALMACEN',
            allowed=True,
            business_rule_description='Asset from maintenance can return to warehouse'
        ),
        StateTransitionRule(
            from_state='MANTENIMIENTO',
            to_state='INSTALADO',
            allowed=True,
            business_rule_description='Asset from maintenance can be reinstalled'
        ),
        StateTransitionRule(
            from_state='MANTENIMIENTO',
            to_state='EN_USO',
            allowed=True,
            business_rule_description='Asset from maintenance can return to use'
        ),
    ]
    
    # Create lookup dictionary for faster access
    _TRANSITION_RULES_DICT = None
    
    @classmethod
    def _get_transition_rules_dict(cls) -> Dict[Tuple[str, str], StateTransitionRule]:
        """Get transition rules as a dictionary for fast lookup"""
        if cls._TRANSITION_RULES_DICT is None:
            cls._TRANSITION_RULES_DICT = {
                (rule.from_state, rule.to_state): rule
                for rule in cls.STATE_TRANSITION_RULES
            }
        return cls._TRANSITION_RULES_DICT
    
    @classmethod
    def validate_state_transition(cls, from_state: str, to_state: str) -> Tuple[bool, str]:
        """
        Validate if a state transition is allowed according to business rules.
        
        Args:
            from_state: Current state
            to_state: Target state
            
        Returns:
            Tuple[bool, str]: (is_valid, error_message_or_rule_description)
        """
        # Check if states are valid
        if from_state not in cls.ASSET_STATES:
            return False, f"Invalid source state: {from_state}"
        
        if to_state not in cls.ASSET_STATES:
            return False, f"Invalid target state: {to_state}"
        
        # Same state is always valid (no-op)
        if from_state == to_state:
            return True, "No state change required"
        
        # Check transition rules
        rules_dict = cls._get_transition_rules_dict()
        rule = rules_dict.get((from_state, to_state))
        
        if rule and rule.allowed:
            return True, rule.business_rule_description
        else:
            return False, f"Transition from {from_state} to {to_state} is not allowed by business rules"
    
    @classmethod
    def get_allowed_transitions(cls, from_state: str) -> List[Tuple[str, str]]:
        """
        Get all allowed transitions from a given state.
        
        Args:
            from_state: Current state
            
        Returns:
            List[Tuple[str, str]]: List of (target_state, description) tuples
        """
        if from_state not in cls.ASSET_STATES:
            return []
        
        allowed = []
        for rule in cls.STATE_TRANSITION_RULES:
            if rule.from_state == from_state and rule.allowed:
                allowed.append((rule.to_state, rule.business_rule_description))
        
        return allowed
    
    @classmethod
    def can_transition_automatically(cls, from_state: str, to_state: str, 
                                   trigger_condition: str) -> bool:
        """
        Check if a state transition can be triggered automatically.
        
        Args:
            from_state: Current state
            to_state: Target state
            trigger_condition: Condition that triggered the transition
            
        Returns:
            bool: True if automatic transition is allowed
        """
        rules_dict = cls._get_transition_rules_dict()
        rule = rules_dict.get((from_state, to_state))
        
        if not rule or not rule.allowed:
            return False
        
        if not rule.auto_trigger_conditions:
            return False
        
        return trigger_condition in rule.auto_trigger_conditions
    
    @classmethod
    @transaction.atomic
    def change_asset_state(cls, activo, new_state: str, user: User, 
                          motivo: str, observaciones: str = '',
                          auto_triggered: bool = False,
                          trigger_condition: str = None) -> bool:
        """
        Change asset state with validation and audit logging.
        
        Args:
            activo: ActivoInventario instance
            new_state: Target state
            user: User making the change
            motivo: Reason for state change
            observaciones: Additional observations
            auto_triggered: Whether this is an automatic state change
            trigger_condition: Condition that triggered automatic change
            
        Returns:
            bool: True if state change was successful
            
        Raises:
            ValidationError: If state transition is not allowed
        """
        from .models import HistorialMovimientoActivo
        
        old_state = activo.estado
        
        # Validate transition
        is_valid, message = cls.validate_state_transition(old_state, new_state)
        if not is_valid:
            raise ValidationError(f"State transition not allowed: {message}")
        
        # For automatic transitions, validate trigger condition
        if auto_triggered and trigger_condition:
            if not cls.can_transition_automatically(old_state, new_state, trigger_condition):
                raise ValidationError(
                    f"Automatic transition from {old_state} to {new_state} "
                    f"not allowed for trigger: {trigger_condition}"
                )
        
        # No change needed
        if old_state == new_state:
            logger.info(f"Asset {activo.codigo_actual} already in state {new_state}")
            return True
        
        try:
            # Update asset state
            activo.estado = new_state
            activo.actualizado_por = user
            activo.save()
            
            # Create audit record
            movement_type = 'CAMBIO_ESTADO'
            if auto_triggered and trigger_condition:
                movement_type = f'CAMBIO_ESTADO_AUTO_{trigger_condition.upper()}'
            
            audit_motivo = motivo
            if auto_triggered and trigger_condition:
                audit_motivo = f"[AUTOMÁTICO - {trigger_condition}] {motivo}"
            
            HistorialMovimientoActivo.create_movement_record(
                activo=activo,
                tipo_movimiento=movement_type,
                usuario_responsable=user,
                motivo=audit_motivo,
                estado_anterior=old_state,
                estado_nuevo=new_state,
                observaciones=observaciones
            )
            
            logger.info(
                f"Asset {activo.codigo_actual} state changed from {old_state} to {new_state} "
                f"by user {user.username}. Reason: {motivo}"
            )
            
            return True
            
        except Exception as e:
            logger.error(
                f"Failed to change asset {activo.codigo_actual} state from {old_state} "
                f"to {new_state}: {str(e)}"
            )
            raise ValidationError(f"Failed to change asset state: {str(e)}")
    
    @classmethod
    def handle_transfer_state_changes(cls, solicitud_traslado, stage: str, user: User):
        """
        Handle automatic state changes during transfer workflow.
        
        Args:
            solicitud_traslado: SolicitudTraslado instance
            stage: Transfer stage ('approved', 'executed', 'completed')
            user: User performing the action
        """
        activo = solicitud_traslado.activo
        
        try:
            if stage == 'approved':
                # When transfer is approved, asset should go to EN_TRANSITO
                if activo.estado == 'EN_ALMACEN':
                    cls.change_asset_state(
                        activo=activo,
                        new_state='EN_TRANSITO',
                        user=user,
                        motivo=f'Traslado aprobado: {solicitud_traslado.numero_solicitud}',
                        observaciones=f'Traslado de {solicitud_traslado.almacen_origen.prefijo} '
                                    f'a {solicitud_traslado.almacen_destino.prefijo}',
                        auto_triggered=True,
                        trigger_condition='transfer_approved'
                    )
            
            elif stage == 'completed':
                # When transfer is completed, asset should return to EN_ALMACEN
                if activo.estado == 'EN_TRANSITO':
                    cls.change_asset_state(
                        activo=activo,
                        new_state='EN_ALMACEN',
                        user=user,
                        motivo=f'Traslado completado: {solicitud_traslado.numero_solicitud}',
                        observaciones=f'Recibido en {solicitud_traslado.almacen_destino.prefijo}',
                        auto_triggered=True,
                        trigger_condition='transfer_completed'
                    )
            
        except ValidationError as e:
            logger.error(
                f"Failed to handle transfer state change for {activo.codigo_actual} "
                f"at stage {stage}: {str(e)}"
            )
            # Don't re-raise - transfer should continue even if state change fails
            # The state can be corrected manually later
    
    @classmethod
    def validate_transfer_request_state(cls, activo) -> Tuple[bool, str]:
        """
        Validate that an asset can be included in a transfer request.
        
        Args:
            activo: ActivoInventario instance
            
        Returns:
            Tuple[bool, str]: (is_valid, error_message)
        """
        # Assets in transit cannot be transferred
        if activo.estado == 'EN_TRANSITO':
            return False, "Assets in transit cannot be transferred"
        
        # Assets in use or installed may require special approval
        if activo.estado in ['EN_USO', 'INSTALADO']:
            return True, f"Asset is {activo.get_estado_display()} - may require special approval"
        
        # Assets under maintenance can be transferred
        if activo.estado == 'MANTENIMIENTO':
            return True, "Asset under maintenance can be transferred"
        
        # Assets in warehouse are ideal for transfer
        if activo.estado == 'EN_ALMACEN':
            return True, "Asset is available for transfer"
        
        return True, "Asset state allows transfer"
    
    @classmethod
    def get_state_statistics(cls, activos_queryset) -> Dict[str, Any]:
        """
        Get statistics about asset states.
        
        Args:
            activos_queryset: QuerySet of ActivoInventario objects
            
        Returns:
            Dict: Statistics about asset states
        """
        from django.db.models import Count
        
        # Count by state
        state_counts = activos_queryset.values('estado').annotate(
            count=Count('id')
        ).order_by('estado')
        
        # Convert to dictionary
        counts_dict = {item['estado']: item['count'] for item in state_counts}
        
        # Ensure all states are represented
        for state in cls.ASSET_STATES:
            if state not in counts_dict:
                counts_dict[state] = 0
        
        total_assets = sum(counts_dict.values())
        
        # Calculate percentages
        percentages = {}
        for state, count in counts_dict.items():
            percentages[state] = (count / total_assets * 100) if total_assets > 0 else 0
        
        return {
            'total_assets': total_assets,
            'state_counts': counts_dict,
            'state_percentages': percentages,
            'assets_available_for_transfer': counts_dict.get('EN_ALMACEN', 0),
            'assets_in_transit': counts_dict.get('EN_TRANSITO', 0),
            'assets_in_use': counts_dict.get('EN_USO', 0) + counts_dict.get('INSTALADO', 0),
            'assets_under_maintenance': counts_dict.get('MANTENIMIENTO', 0),
        }
    
    @classmethod
    def get_state_transition_history(cls, activo, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Get state transition history for an asset.
        
        Args:
            activo: ActivoInventario instance
            limit: Maximum number of records to return
            
        Returns:
            List[Dict]: List of state transition records
        """
        from .models import HistorialMovimientoActivo
        
        # Get state change records
        state_changes = HistorialMovimientoActivo.objects.filter(
            activo=activo,
            tipo_movimiento__startswith='CAMBIO_ESTADO'
        ).order_by('-fecha_movimiento')[:limit]
        
        history = []
        for record in state_changes:
            history.append({
                'fecha': record.fecha_movimiento,
                'estado_anterior': record.estado_anterior,
                'estado_nuevo': record.estado_nuevo,
                'usuario': record.usuario_responsable.username,
                'motivo': record.motivo,
                'observaciones': record.observaciones,
                'tipo_movimiento': record.get_tipo_movimiento_display(),
                'es_automatico': 'AUTOMÁTICO' in record.motivo,
            })
        
        return history
    
    @classmethod
    def validate_bulk_state_change(cls, activos_queryset, new_state: str) -> Dict[str, Any]:
        """
        Validate bulk state change for multiple assets.
        
        Args:
            activos_queryset: QuerySet of assets to change
            new_state: Target state
            
        Returns:
            Dict: Validation results with valid/invalid assets
        """
        if new_state not in cls.ASSET_STATES:
            return {
                'valid_assets': [],
                'invalid_assets': [],
                'errors': [f"Invalid target state: {new_state}"],
                'can_proceed': False
            }
        
        valid_assets = []
        invalid_assets = []
        errors = []
        
        for activo in activos_queryset:
            is_valid, message = cls.validate_state_transition(activo.estado, new_state)
            
            if is_valid:
                valid_assets.append({
                    'activo': activo,
                    'current_state': activo.estado,
                    'message': message
                })
            else:
                invalid_assets.append({
                    'activo': activo,
                    'current_state': activo.estado,
                    'error': message
                })
        
        return {
            'valid_assets': valid_assets,
            'invalid_assets': invalid_assets,
            'errors': errors,
            'can_proceed': len(valid_assets) > 0,
            'total_assets': len(valid_assets) + len(invalid_assets),
            'valid_count': len(valid_assets),
            'invalid_count': len(invalid_assets)
        }
    
    @classmethod
    @transaction.atomic
    def bulk_change_asset_states(cls, activos_queryset, new_state: str, 
                                user: User, motivo: str, 
                                observaciones: str = '') -> Dict[str, Any]:
        """
        Change state for multiple assets with validation and audit logging.
        
        Args:
            activos_queryset: QuerySet of assets to change
            new_state: Target state
            user: User making the changes
            motivo: Reason for state changes
            observaciones: Additional observations
            
        Returns:
            Dict: Results of bulk operation
        """
        # Validate bulk operation
        validation_result = cls.validate_bulk_state_change(activos_queryset, new_state)
        
        if not validation_result['can_proceed']:
            return {
                'success': False,
                'changed_count': 0,
                'failed_count': validation_result['total_assets'],
                'errors': validation_result['errors'],
                'details': validation_result
            }
        
        changed_count = 0
        failed_count = 0
        errors = []
        
        # Process valid assets
        for asset_info in validation_result['valid_assets']:
            try:
                activo = asset_info['activo']
                cls.change_asset_state(
                    activo=activo,
                    new_state=new_state,
                    user=user,
                    motivo=f"[BULK] {motivo}",
                    observaciones=observaciones,
                    auto_triggered=False
                )
                changed_count += 1
                
            except Exception as e:
                failed_count += 1
                errors.append(f"Asset {activo.codigo_actual}: {str(e)}")
                logger.error(f"Bulk state change failed for {activo.codigo_actual}: {str(e)}")
        
        return {
            'success': changed_count > 0,
            'changed_count': changed_count,
            'failed_count': failed_count + validation_result['invalid_count'],
            'errors': errors,
            'validation_details': validation_result
        }


class AssetStateAuditLogger:
    """
    Specialized logger for asset state changes and audit trail.
    Integrates with the comprehensive AuditTrailService for complete audit coverage.
    """
    
    @classmethod
    def log_state_change_attempt(cls, activo, old_state: str, new_state: str, 
                                user: User, success: bool, error_message: str = '',
                                motivo: str = '', observaciones: str = '',
                                solicitud_traslado=None, ip_address: str = None,
                                user_agent: str = '', session_key: str = '',
                                additional_context: Dict[str, Any] = None):
        """
        Log state change attempts for audit purposes using comprehensive audit trail.
        """
        # Log to standard logger
        log_level = logging.INFO if success else logging.WARNING
        
        message = (
            f"State change attempt for asset {activo.codigo_actual}: "
            f"{old_state} -> {new_state} by {user.username}"
        )
        
        if success:
            message += " [SUCCESS]"
        else:
            message += f" [FAILED: {error_message}]"
        
        logger.log(log_level, message)
        
        # Record in comprehensive audit trail
        try:
            from .services import AuditTrailService
            
            if additional_context is None:
                additional_context = {}
            
            # Add error information to context if failed
            if not success:
                additional_context['error_message'] = error_message
                additional_context['validation_failed'] = True
            
            AuditTrailService.record_state_change(
                activo=activo,
                old_state=old_state,
                new_state=new_state,
                user=user,
                motivo=motivo or ('State change attempt' if success else f'Failed state change: {error_message}'),
                observaciones=observaciones,
                solicitud_traslado=solicitud_traslado,
                ip_address=ip_address,
                user_agent=user_agent,
                session_key=session_key,
                additional_context=additional_context
            )
            
        except Exception as e:
            logger.error(f"Failed to record state change in audit trail: {str(e)}")
    
    @classmethod
    def log_automatic_state_change(cls, activo, trigger_condition: str, 
                                 old_state: str, new_state: str, user: User,
                                 solicitud_traslado=None, ip_address: str = None,
                                 user_agent: str = '', session_key: str = ''):
        """
        Log automatic state changes triggered by system events.
        """
        # Log to standard logger
        logger.info(
            f"Automatic state change for asset {activo.codigo_actual}: "
            f"{old_state} -> {new_state} triggered by {trigger_condition} "
            f"(executed by {user.username})"
        )
        
        # Record in comprehensive audit trail
        try:
            from .services import AuditTrailService
            
            AuditTrailService.record_state_change(
                activo=activo,
                old_state=old_state,
                new_state=new_state,
                user=user,
                motivo=f'Automatic state change triggered by {trigger_condition}',
                observaciones=f'System-triggered state change: {trigger_condition}',
                solicitud_traslado=solicitud_traslado,
                ip_address=ip_address,
                user_agent=user_agent,
                session_key=session_key,
                additional_context={
                    'automatic_change': True,
                    'trigger_condition': trigger_condition,
                    'change_type': 'AUTOMATIC'
                }
            )
            
        except Exception as e:
            logger.error(f"Failed to record automatic state change in audit trail: {str(e)}")
    
    @classmethod
    def log_bulk_state_change(cls, changed_count: int, failed_count: int, 
                            new_state: str, user: User, operation_details: Dict[str, Any] = None,
                            ip_address: str = None, user_agent: str = '', session_key: str = ''):
        """
        Log bulk state change operations.
        """
        # Log to standard logger
        logger.info(
            f"Bulk state change to {new_state} by {user.username}: "
            f"{changed_count} successful, {failed_count} failed"
        )
        
        # Record in comprehensive audit trail as system operation
        try:
            from .services import AuditTrailService
            
            if operation_details is None:
                operation_details = {}
            
            AuditTrailService.record_system_operation(
                accion='BULK_UPDATE',
                descripcion=f'Bulk state change to {new_state}',
                user=user,
                entidades_afectadas=[{
                    'type': 'ActivoInventario',
                    'count': changed_count + failed_count,
                    'successful': changed_count,
                    'failed': failed_count
                }],
                parametros_operacion={
                    'target_state': new_state,
                    'total_assets': changed_count + failed_count,
                    **operation_details
                },
                exitosa=failed_count == 0,
                errores=[f'{failed_count} assets failed to change state'] if failed_count > 0 else [],
                registros_procesados=changed_count + failed_count,
                ip_address=ip_address,
                user_agent=user_agent,
                session_key=session_key,
                additional_context={
                    'operation_type': 'BULK_STATE_CHANGE',
                    'success_rate': changed_count / (changed_count + failed_count) if (changed_count + failed_count) > 0 else 0
                }
            )
            
        except Exception as e:
            logger.error(f"Failed to record bulk state change in audit trail: {str(e)}")
    
    @classmethod
    def log_state_validation_failure(cls, activo, from_state: str, 
                                   to_state: str, reason: str, user: User = None,
                                   ip_address: str = None, user_agent: str = '', session_key: str = ''):
        """
        Log state validation failures for analysis.
        """
        # Log to standard logger
        logger.warning(
            f"State validation failed for asset {activo.codigo_actual}: "
            f"{from_state} -> {to_state} - {reason}"
        )
        
        # Record in comprehensive audit trail if user is available
        if user:
            try:
                from .services import AuditTrailService
                
                AuditTrailService.record_state_change(
                    activo=activo,
                    old_state=from_state,
                    new_state=to_state,
                    user=user,
                    motivo=f'State validation failure: {reason}',
                    observaciones=f'Validation failed for transition {from_state} -> {to_state}',
                    ip_address=ip_address,
                    user_agent=user_agent,
                    session_key=session_key,
                    additional_context={
                        'validation_failed': True,
                        'validation_error': reason,
                        'attempted_transition': f'{from_state} -> {to_state}'
                    }
                )
                
            except Exception as e:
                logger.error(f"Failed to record validation failure in audit trail: {str(e)}")
    
    @classmethod
    def log_transfer_workflow_state_change(cls, solicitud_traslado, stage: str, user: User,
                                         ip_address: str = None, user_agent: str = '', session_key: str = ''):
        """
        Log state changes related to transfer workflow stages.
        """
        activo = solicitud_traslado.activo
        
        # Determine state changes based on workflow stage
        if stage == 'approved':
            old_state = activo.estado
            new_state = 'EN_TRANSITO'
            motivo = f'Transfer approved and executed: {solicitud_traslado.numero_solicitud}'
        elif stage == 'completed':
            old_state = 'EN_TRANSITO'
            new_state = 'EN_ALMACEN'
            motivo = f'Transfer completed: {solicitud_traslado.numero_solicitud}'
        else:
            # Generic workflow state change
            old_state = activo.estado
            new_state = activo.estado  # May not change
            motivo = f'Transfer workflow stage: {stage} for {solicitud_traslado.numero_solicitud}'
        
        # Log to standard logger
        logger.info(
            f"Transfer workflow state change for asset {activo.codigo_actual}: "
            f"Stage {stage} - {old_state} -> {new_state} by {user.username}"
        )
        
        # Record in comprehensive audit trail
        try:
            from .services import AuditTrailService
            
            AuditTrailService.record_state_change(
                activo=activo,
                old_state=old_state,
                new_state=new_state,
                user=user,
                motivo=motivo,
                observaciones=f'Transfer workflow stage: {stage}',
                solicitud_traslado=solicitud_traslado,
                ip_address=ip_address,
                user_agent=user_agent,
                session_key=session_key,
                additional_context={
                    'workflow_stage': stage,
                    'transfer_request': solicitud_traslado.numero_solicitud,
                    'workflow_related': True,
                    'almacen_origen': solicitud_traslado.almacen_origen.prefijo,
                    'almacen_destino': solicitud_traslado.almacen_destino.prefijo
                }
            )
            
        except Exception as e:
            logger.error(f"Failed to record transfer workflow state change in audit trail: {str(e)}")