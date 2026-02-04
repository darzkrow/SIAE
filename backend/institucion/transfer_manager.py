# ============================================================================
# TRANSFER MANAGER SERVICE
# ============================================================================

"""
Transfer Manager Service for Hidroven Organizational Restructuring.

This service handles the complete transfer workflow lifecycle including:
- Transfer request creation and validation
- Dual approval workflow enforcement
- Notification system integration for approvers
- Transfer execution management with rollback capability
- Workflow state management
- Business rule enforcement

Requirements implemented:
- 4.1: Transfer request creation and validation logic
- 4.2: Dual approval workflow enforcement
- 4.3: Notification system for approvers
- 4.4: Transfer execution management
- 4.5: Workflow state management
- 4.6: Business rule enforcement
"""

from typing import Dict, List, Optional, Tuple, Any, Union
from django.core.exceptions import ValidationError
from django.utils import timezone
from django.db import transaction
from django.contrib.auth import get_user_model
from django.db.models import Q, Count
from dataclasses import dataclass
from datetime import timedelta
import logging

from .models import (
    SolicitudTraslado, AprobacionTraslado, ActivoInventario, 
    AlmacenRegional, HistorialMovimientoActivo
)
from .state_management import AssetStateManager

User = get_user_model()
logger = logging.getLogger(__name__)


@dataclass
class TransferRequestData:
    """Data class for transfer request creation"""
    activo_id: int
    almacen_origen_id: int
    almacen_destino_id: int
    solicitante_id: int
    motivo: str
    fecha_limite: timezone.datetime
    prioridad: str = 'NORMAL'
    observaciones: str = ''


@dataclass
class TransferValidationResult:
    """Result of transfer request validation"""
    is_valid: bool
    errors: List[str]
    warnings: List[str]
    can_proceed: bool


@dataclass
class ApprovalResult:
    """Result of approval operation"""
    success: bool
    approval: Optional['AprobacionTraslado']
    message: str
    workflow_updated: bool = False


@dataclass
class TransferExecutionResult:
    """Result of transfer execution"""
    success: bool
    solicitud: Optional['SolicitudTraslado']
    message: str
    rollback_data: Optional[Dict[str, Any]] = None


@dataclass
class NotificationData:
    """Data for notification system"""
    recipient: User
    subject: str
    message: str
    notification_type: str
    priority: str = 'NORMAL'
    metadata: Dict[str, Any] = None


class TransferManager:
    """
    Service class for managing the complete transfer workflow lifecycle.
    
    This service provides a comprehensive interface for:
    - Creating and validating transfer requests
    - Managing dual approval workflows
    - Executing transfers with state management integration
    - Handling notifications and business rule enforcement
    - Providing rollback capabilities for failed operations
    """
    
    # Business rule constants
    MAX_PENDING_REQUESTS_PER_ASSET = 1
    MAX_TRANSFER_DEADLINE_DAYS = 30
    MIN_TRANSFER_DEADLINE_HOURS = 4
    HIGH_PRIORITY_DEADLINE_HOURS = 24
    URGENT_PRIORITY_DEADLINE_HOURS = 4
    
    # Notification types
    NOTIFICATION_TYPES = {
        'APPROVAL_REQUEST': 'Solicitud de Aprobación',
        'APPROVAL_GRANTED': 'Aprobación Otorgada',
        'APPROVAL_REJECTED': 'Aprobación Rechazada',
        'TRANSFER_READY': 'Traslado Listo para Ejecutar',
        'TRANSFER_EXECUTED': 'Traslado Ejecutado',
        'TRANSFER_COMPLETED': 'Traslado Completado',
        'TRANSFER_OVERDUE': 'Traslado Vencido',
        'TRANSFER_CANCELLED': 'Traslado Cancelado',
    }
    
    @classmethod
    @transaction.atomic
    def create_transfer_request(cls, request_data: TransferRequestData) -> Tuple[bool, Union[SolicitudTraslado, str]]:
        """
        Create a new transfer request with comprehensive validation.
        
        Args:
            request_data: TransferRequestData with all required information
            
        Returns:
            Tuple[bool, Union[SolicitudTraslado, str]]: (success, solicitud_or_error_message)
        """
        try:
            # Validate request data
            validation_result = cls.validate_transfer_request(request_data)
            if not validation_result.is_valid:
                return False, f"Validation failed: {'; '.join(validation_result.errors)}"
            
            # Get related objects
            activo = ActivoInventario.objects.get(id=request_data.activo_id)
            almacen_origen = AlmacenRegional.objects.get(id=request_data.almacen_origen_id)
            almacen_destino = AlmacenRegional.objects.get(id=request_data.almacen_destino_id)
            solicitante = User.objects.get(id=request_data.solicitante_id)
            
            # Create transfer request
            solicitud = SolicitudTraslado.objects.create(
                activo=activo,
                almacen_origen=almacen_origen,
                almacen_destino=almacen_destino,
                solicitante=solicitante,
                motivo=request_data.motivo,
                fecha_limite=request_data.fecha_limite,
                prioridad=request_data.prioridad,
                observaciones=request_data.observaciones
            )
            
            # Send notifications to approvers
            cls._send_approval_notifications(solicitud)
            
            # Log creation
            logger.info(
                f"Transfer request created: {solicitud.numero_solicitud} "
                f"for asset {activo.codigo_actual} by {solicitante.username}"
            )
            
            return True, solicitud
            
        except Exception as e:
            logger.error(f"Failed to create transfer request: {str(e)}")
            return False, f"Failed to create transfer request: {str(e)}"
    
    @classmethod
    def validate_transfer_request(cls, request_data: TransferRequestData) -> TransferValidationResult:
        """
        Comprehensive validation of transfer request data.
        
        Args:
            request_data: TransferRequestData to validate
            
        Returns:
            TransferValidationResult: Detailed validation results
        """
        errors = []
        warnings = []
        
        try:
            # Validate objects exist
            try:
                activo = ActivoInventario.objects.get(id=request_data.activo_id)
            except ActivoInventario.DoesNotExist:
                errors.append(f"Asset with ID {request_data.activo_id} does not exist")
                return TransferValidationResult(False, errors, warnings, False)
            
            try:
                almacen_origen = AlmacenRegional.objects.get(id=request_data.almacen_origen_id)
            except AlmacenRegional.DoesNotExist:
                errors.append(f"Origin warehouse with ID {request_data.almacen_origen_id} does not exist")
                return TransferValidationResult(False, errors, warnings, False)
            
            try:
                almacen_destino = AlmacenRegional.objects.get(id=request_data.almacen_destino_id)
            except AlmacenRegional.DoesNotExist:
                errors.append(f"Destination warehouse with ID {request_data.almacen_destino_id} does not exist")
                return TransferValidationResult(False, errors, warnings, False)
            
            try:
                solicitante = User.objects.get(id=request_data.solicitante_id)
            except User.DoesNotExist:
                errors.append(f"Requester with ID {request_data.solicitante_id} does not exist")
                return TransferValidationResult(False, errors, warnings, False)
            
            # Business rule validations
            
            # 1. Same warehouse validation
            if almacen_origen == almacen_destino:
                errors.append("Origin and destination warehouses cannot be the same")
            
            # 2. Asset location validation
            if activo.almacen_actual != almacen_origen:
                errors.append(
                    f"Asset is not in the specified origin warehouse. "
                    f"Current location: {activo.almacen_actual.prefijo}"
                )
            
            # 3. Asset state validation
            can_transfer, state_message = AssetStateManager.validate_transfer_request_state(activo)
            if not can_transfer:
                errors.append(f"Asset state does not allow transfer: {state_message}")
            elif "may require special approval" in state_message:
                warnings.append(state_message)
            
            # 4. Pending requests validation
            pending_count = SolicitudTraslado.objects.filter(
                activo=activo,
                estado__in=['PENDIENTE', 'APROBADA_ORIGEN', 'APROBADA_DESTINO', 'APROBADA_COMPLETA', 'EN_TRANSITO']
            ).count()
            
            if pending_count >= cls.MAX_PENDING_REQUESTS_PER_ASSET:
                errors.append(f"Asset already has {pending_count} pending transfer request(s)")
            
            # 5. Warehouse manager validation
            if not almacen_origen.manager:
                errors.append(f"Origin warehouse {almacen_origen.prefijo} has no assigned manager")
            
            if not almacen_destino.manager:
                errors.append(f"Destination warehouse {almacen_destino.prefijo} has no assigned manager")
            
            # 6. Warehouse status validation
            if not almacen_origen.activo:
                errors.append(f"Origin warehouse {almacen_origen.prefijo} is inactive")
            
            if not almacen_destino.activo:
                errors.append(f"Destination warehouse {almacen_destino.prefijo} is inactive")
            
            # 7. Deadline validation
            now = timezone.now()
            min_deadline = now + timedelta(hours=cls.MIN_TRANSFER_DEADLINE_HOURS)
            max_deadline = now + timedelta(days=cls.MAX_TRANSFER_DEADLINE_DAYS)
            
            if request_data.fecha_limite <= now:
                errors.append("Transfer deadline must be in the future")
            elif request_data.fecha_limite < min_deadline:
                errors.append(f"Transfer deadline must be at least {cls.MIN_TRANSFER_DEADLINE_HOURS} hours from now")
            elif request_data.fecha_limite > max_deadline:
                warnings.append(f"Transfer deadline is more than {cls.MAX_TRANSFER_DEADLINE_DAYS} days away")
            
            # 8. Priority-specific validations
            if request_data.prioridad == 'ALTA':
                recommended_deadline = now + timedelta(hours=cls.HIGH_PRIORITY_DEADLINE_HOURS)
                if request_data.fecha_limite > recommended_deadline:
                    warnings.append(f"High priority transfers should be completed within {cls.HIGH_PRIORITY_DEADLINE_HOURS} hours")
            
            elif request_data.prioridad == 'URGENTE':
                max_urgent_deadline = now + timedelta(hours=cls.URGENT_PRIORITY_DEADLINE_HOURS)
                if request_data.fecha_limite > max_urgent_deadline:
                    errors.append(f"Urgent transfers must be completed within {cls.URGENT_PRIORITY_DEADLINE_HOURS} hours")
            
            # 9. Warehouse capacity validation (if implemented)
            if hasattr(almacen_destino, 'is_at_capacity') and almacen_destino.is_at_capacity():
                if request_data.prioridad not in ['ALTA', 'URGENTE']:
                    errors.append(
                        f"Destination warehouse {almacen_destino.prefijo} is at capacity. "
                        "Only high/urgent priority transfers allowed."
                    )
                else:
                    warnings.append(f"Destination warehouse {almacen_destino.prefijo} is at capacity")
            
            # 10. Motivo validation
            if not request_data.motivo or len(request_data.motivo.strip()) < 10:
                errors.append("Transfer reason must be at least 10 characters long")
            
        except Exception as e:
            errors.append(f"Validation error: {str(e)}")
            logger.error(f"Transfer validation error: {str(e)}")
        
        is_valid = len(errors) == 0
        can_proceed = is_valid
        
        return TransferValidationResult(is_valid, errors, warnings, can_proceed)
    
    @classmethod
    @transaction.atomic
    def approve_transfer(cls, solicitud_id: int, approver: User, 
                        approval_type: str, comments: str = '') -> ApprovalResult:
        """
        Approve a transfer request with dual approval workflow enforcement.
        
        Args:
            solicitud_id: ID of the transfer request
            approver: User performing the approval
            approval_type: 'ORIGEN' or 'DESTINO'
            comments: Optional approval comments
            
        Returns:
            ApprovalResult: Result of the approval operation
        """
        try:
            # Get transfer request
            try:
                solicitud = SolicitudTraslado.objects.select_for_update().get(id=solicitud_id)
            except SolicitudTraslado.DoesNotExist:
                return ApprovalResult(False, None, f"Transfer request {solicitud_id} not found")
            
            # Validate approval authority
            validation_result = cls._validate_approval_authority(solicitud, approver, approval_type)
            if not validation_result['valid']:
                return ApprovalResult(False, None, validation_result['message'])
            
            # Check if already approved/rejected
            existing_approval = AprobacionTraslado.objects.filter(
                solicitud=solicitud,
                tipo_aprobacion=approval_type
            ).first()
            
            if existing_approval:
                return ApprovalResult(
                    False, existing_approval, 
                    f"Transfer already {existing_approval.get_decision_display().lower()} by this approver"
                )
            
            # Create approval record
            approval = AprobacionTraslado.objects.create(
                solicitud=solicitud,
                aprobador=approver,
                tipo_aprobacion=approval_type,
                decision='APROBADO',
                comentarios=comments
            )
            
            # Record approval decision in audit trail
            try:
                from .services import AuditTrailService
                AuditTrailService.record_approval_decision(
                    solicitud_traslado=solicitud,
                    aprobacion=approval,
                    accion='APPROVAL_GRANTED',
                    user=approver,
                    comentarios=comments,
                    additional_context={
                        'approval_type': approval_type,
                        'workflow_stage': 'approval_granted'
                    }
                )
            except Exception as e:
                logger.error(f"Failed to record approval in audit trail: {str(e)}")
            
            # Update solicitud workflow state (handled by AprobacionTraslado.save())
            solicitud.refresh_from_db()
            
            # Send notifications
            cls._send_approval_granted_notifications(solicitud, approval)
            
            # Check if transfer is ready for execution
            if solicitud.can_execute():
                cls._send_transfer_ready_notifications(solicitud)
            
            logger.info(
                f"Transfer {solicitud.numero_solicitud} approved by {approver.username} "
                f"from {approval_type} warehouse"
            )
            
            return ApprovalResult(True, approval, "Transfer approved successfully", True)
            
        except Exception as e:
            logger.error(f"Failed to approve transfer {solicitud_id}: {str(e)}")
            return ApprovalResult(False, None, f"Failed to approve transfer: {str(e)}")
    
    @classmethod
    @transaction.atomic
    def reject_transfer(cls, solicitud_id: int, rejector: User, 
                       rejection_reason: str) -> ApprovalResult:
        """
        Reject a transfer request with proper workflow management.
        
        Args:
            solicitud_id: ID of the transfer request
            rejector: User performing the rejection
            rejection_reason: Reason for rejection
            
        Returns:
            ApprovalResult: Result of the rejection operation
        """
        try:
            # Get transfer request
            try:
                solicitud = SolicitudTraslado.objects.select_for_update().get(id=solicitud_id)
            except SolicitudTraslado.DoesNotExist:
                return ApprovalResult(False, None, f"Transfer request {solicitud_id} not found")
            
            # Determine rejection type based on rejector
            approval_type = None
            if rejector == solicitud.almacen_origen.manager:
                approval_type = 'ORIGEN'
            elif rejector == solicitud.almacen_destino.manager:
                approval_type = 'DESTINO'
            else:
                return ApprovalResult(
                    False, None, 
                    "Only warehouse managers can reject transfer requests"
                )
            
            # Validate rejection is allowed
            if solicitud.estado in ['COMPLETADA', 'RECHAZADA', 'CANCELADA']:
                return ApprovalResult(
                    False, None, 
                    f"Cannot reject transfer in {solicitud.get_estado_display()} state"
                )
            
            # Check if already rejected
            existing_rejection = AprobacionTraslado.objects.filter(
                solicitud=solicitud,
                tipo_aprobacion=approval_type,
                decision='RECHAZADO'
            ).first()
            
            if existing_rejection:
                return ApprovalResult(
                    False, existing_rejection,
                    "Transfer already rejected by this approver"
                )
            
            # Create rejection record
            rejection = AprobacionTraslado.objects.create(
                solicitud=solicitud,
                aprobador=rejector,
                tipo_aprobacion=approval_type,
                decision='RECHAZADO',
                comentarios=rejection_reason
            )
            
            # Record rejection decision in audit trail
            try:
                from .services import AuditTrailService
                AuditTrailService.record_approval_decision(
                    solicitud_traslado=solicitud,
                    aprobacion=rejection,
                    accion='APPROVAL_REJECTED',
                    user=rejector,
                    comentarios=rejection_reason,
                    motivo_rechazo=rejection_reason,
                    additional_context={
                        'approval_type': approval_type,
                        'workflow_stage': 'approval_rejected'
                    }
                )
            except Exception as e:
                logger.error(f"Failed to record rejection in audit trail: {str(e)}")
            
            # Update solicitud state (handled by AprobacionTraslado.save())
            solicitud.refresh_from_db()
            
            # Send rejection notifications
            cls._send_rejection_notifications(solicitud, rejection)
            
            logger.info(
                f"Transfer {solicitud.numero_solicitud} rejected by {rejector.username} "
                f"from {approval_type} warehouse: {rejection_reason}"
            )
            
            return ApprovalResult(True, rejection, "Transfer rejected successfully", True)
            
        except Exception as e:
            logger.error(f"Failed to reject transfer {solicitud_id}: {str(e)}")
            return ApprovalResult(False, None, f"Failed to reject transfer: {str(e)}")
    
    @classmethod
    @transaction.atomic
    def execute_transfer(cls, solicitud_id: int, executor: User) -> TransferExecutionResult:
        """
        Execute an approved transfer with enhanced atomic operations and comprehensive error handling.
        
        This method implements:
        - Atomic transfer execution with proper transaction management
        - Asset code evolution with rollback capability
        - Inventory synchronization with warehouse counts
        - Integration with existing inventory system
        - Comprehensive error handling and logging
        - Complete audit trail recording
        
        Requirements implemented:
        - 4.4: Transfer execution with asset code evolution
        - 4.7: Atomic transfer execution
        - 7.1: Inventory synchronization with warehouse counts
        - 7.2: Rollback capability for failed transfers
        - 7.3: Integration with existing systems
        
        Args:
            solicitud_id: ID of the transfer request
            executor: User executing the transfer
            
        Returns:
            TransferExecutionResult: Result of the execution operation
        """
        rollback_data = {}
        execution_start_time = timezone.now()
        
        try:
            # Get transfer request with select_for_update for atomic operations
            try:
                solicitud = SolicitudTraslado.objects.select_for_update().get(id=solicitud_id)
            except SolicitudTraslado.DoesNotExist:
                return TransferExecutionResult(
                    False, None, f"Transfer request {solicitud_id} not found"
                )
            
            # Validate execution is allowed
            if not solicitud.can_execute():
                return TransferExecutionResult(
                    False, solicitud, 
                    "Transfer cannot be executed - missing approvals or invalid state"
                )
            
            # Store rollback data before making any changes
            rollback_data = {
                'solicitud_id': solicitud.id,
                'original_solicitud_state': solicitud.estado,
                'original_asset_code': solicitud.activo.codigo_actual,
                'original_asset_warehouse': solicitud.activo.almacen_actual.id,
                'original_asset_state': solicitud.activo.estado,
                'execution_timestamp': execution_start_time.isoformat()
            }
            
            # Execute the transfer using the enhanced model method
            solicitud.execute_transfer(executor)
            
            # Calculate execution duration
            execution_duration = (timezone.now() - execution_start_time).total_seconds()
            
            # Send execution notifications
            cls._send_transfer_executed_notifications(solicitud)
            
            logger.info(
                f"Transfer {solicitud.numero_solicitud} executed successfully by {executor.username} "
                f"in {execution_duration:.2f}s"
            )
            
            return TransferExecutionResult(
                True, solicitud, 
                f"Transfer executed successfully in {execution_duration:.2f}s", 
                rollback_data
            )
            
        except ValidationError as e:
            # Handle validation errors (these include rollback information)
            logger.error(f"Transfer execution validation failed for {solicitud_id}: {str(e)}")
            return TransferExecutionResult(
                False, None, str(e), rollback_data
            )
            
        except Exception as e:
            logger.error(f"Unexpected error during transfer execution {solicitud_id}: {str(e)}")
            
            # Attempt emergency rollback if we have rollback data and a solicitud
            if rollback_data and 'solicitud' in locals():
                try:
                    cls._emergency_rollback_transfer_execution(rollback_data)
                    logger.info(f"Emergency rollback completed for transfer {solicitud_id}")
                except Exception as rollback_error:
                    logger.error(f"Emergency rollback failed for transfer {solicitud_id}: {str(rollback_error)}")
            
            return TransferExecutionResult(
                False, None, f"Unexpected error during transfer execution: {str(e)}", rollback_data
            )
    
    @classmethod
    @transaction.atomic
    def complete_transfer(cls, solicitud_id: int, receiver: User) -> TransferExecutionResult:
        """
        Complete a transfer when asset arrives at destination.
        
        Args:
            solicitud_id: ID of the transfer request
            receiver: User receiving the asset
            
        Returns:
            TransferExecutionResult: Result of the completion operation
        """
        try:
            # Get transfer request
            try:
                solicitud = SolicitudTraslado.objects.select_for_update().get(id=solicitud_id)
            except SolicitudTraslado.DoesNotExist:
                return TransferExecutionResult(
                    False, None, f"Transfer request {solicitud_id} not found"
                )
            
            # Validate completion is allowed
            if solicitud.estado != 'EN_TRANSITO':
                return TransferExecutionResult(
                    False, solicitud,
                    f"Transfer cannot be completed - current state: {solicitud.get_estado_display()}"
                )
            
            # Complete the transfer using the model's method
            solicitud.complete_transfer(receiver)
            
            # Send completion notifications
            cls._send_transfer_completed_notifications(solicitud)
            
            logger.info(
                f"Transfer {solicitud.numero_solicitud} completed successfully by {receiver.username}"
            )
            
            return TransferExecutionResult(
                True, solicitud, "Transfer completed successfully"
            )
            
        except Exception as e:
            logger.error(f"Failed to complete transfer {solicitud_id}: {str(e)}")
            return TransferExecutionResult(
                False, None, f"Failed to complete transfer: {str(e)}"
            )
    
    @classmethod
    @transaction.atomic
    def cancel_transfer(cls, solicitud_id: int, canceller: User, 
                       cancellation_reason: str) -> TransferExecutionResult:
        """
        Cancel a transfer request if allowed.
        
        Args:
            solicitud_id: ID of the transfer request
            canceller: User cancelling the transfer
            cancellation_reason: Reason for cancellation
            
        Returns:
            TransferExecutionResult: Result of the cancellation operation
        """
        try:
            # Get transfer request
            try:
                solicitud = SolicitudTraslado.objects.select_for_update().get(id=solicitud_id)
            except SolicitudTraslado.DoesNotExist:
                return TransferExecutionResult(
                    False, None, f"Transfer request {solicitud_id} not found"
                )
            
            # Validate cancellation is allowed
            if not solicitud.can_be_cancelled():
                return TransferExecutionResult(
                    False, solicitud,
                    f"Transfer cannot be cancelled - current state: {solicitud.get_estado_display()}"
                )
            
            # Cancel the transfer using the model's method
            solicitud.cancel_request(canceller, cancellation_reason)
            
            # Send cancellation notifications
            cls._send_transfer_cancelled_notifications(solicitud, canceller, cancellation_reason)
            
            logger.info(
                f"Transfer {solicitud.numero_solicitud} cancelled by {canceller.username}: {cancellation_reason}"
            )
            
            return TransferExecutionResult(
                True, solicitud, "Transfer cancelled successfully"
            )
            
        except Exception as e:
            logger.error(f"Failed to cancel transfer {solicitud_id}: {str(e)}")
            return TransferExecutionResult(
                False, None, f"Failed to cancel transfer: {str(e)}"
            )
    
    @classmethod
    def get_pending_approvals(cls, manager: User) -> List[Dict[str, Any]]:
        """
        Get pending approvals for a warehouse manager.
        
        Args:
            manager: Warehouse manager user
            
        Returns:
            List[Dict]: List of pending approval requests with details
        """
        try:
            pending_requests = SolicitudTraslado.get_pending_for_manager(manager)
            
            approvals = []
            for solicitud in pending_requests:
                approval_status = solicitud.get_approval_status()
                
                # Determine what type of approval is needed from this manager
                needs_origin_approval = (
                    solicitud.almacen_origen.manager == manager and 
                    approval_status['pendiente_origen']
                )
                needs_destination_approval = (
                    solicitud.almacen_destino.manager == manager and 
                    approval_status['pendiente_destino']
                )
                
                if needs_origin_approval or needs_destination_approval:
                    approvals.append({
                        'solicitud': solicitud,
                        'approval_type': 'ORIGEN' if needs_origin_approval else 'DESTINO',
                        'warehouse': solicitud.almacen_origen if needs_origin_approval else solicitud.almacen_destino,
                        'priority': solicitud.prioridad,
                        'days_until_deadline': solicitud.get_days_until_deadline(),
                        'is_overdue': solicitud.is_overdue(),
                        'asset_info': {
                            'codigo': solicitud.activo.codigo_actual,
                            'tipo': solicitud.activo.tipo_activo,
                            'descripcion': solicitud.activo.descripcion,
                        },
                        'requester': solicitud.solicitante,
                        'created_date': solicitud.fecha_solicitud,
                        'deadline': solicitud.fecha_limite,
                        'reason': solicitud.motivo,
                    })
            
            # Sort by priority and deadline
            priority_order = {'URGENTE': 0, 'ALTA': 1, 'NORMAL': 2, 'BAJA': 3}
            approvals.sort(key=lambda x: (
                priority_order.get(x['priority'], 4),
                x['deadline']
            ))
            
            return approvals
            
        except Exception as e:
            logger.error(f"Failed to get pending approvals for {manager.username}: {str(e)}")
            return []
    
    @classmethod
    def get_manager_dashboard_data(cls, manager: User) -> Dict[str, Any]:
        """
        Get comprehensive dashboard data for a warehouse manager.
        
        Args:
            manager: Warehouse manager user
            
        Returns:
            Dict: Dashboard data with statistics and pending items
        """
        try:
            # Get basic statistics
            stats = SolicitudTraslado.get_dashboard_stats_for_manager(manager)
            
            # Get pending approvals
            pending_approvals = cls.get_pending_approvals(manager)
            
            # Get high priority requests
            high_priority = SolicitudTraslado.get_high_priority_requests(manager)
            
            # Get overdue requests
            overdue_requests = SolicitudTraslado.objects.filter(
                Q(almacen_origen__manager=manager) | Q(almacen_destino__manager=manager),
                fecha_limite__lt=timezone.now(),
                estado__in=['PENDIENTE', 'APROBADA_ORIGEN', 'APROBADA_DESTINO', 'APROBADA_COMPLETA']
            ).select_related('activo', 'almacen_origen', 'almacen_destino', 'solicitante')
            
            # Get recent activity
            week_ago = timezone.now() - timedelta(days=7)
            recent_activity = SolicitudTraslado.objects.filter(
                Q(almacen_origen__manager=manager) | Q(almacen_destino__manager=manager),
                fecha_solicitud__gte=week_ago
            ).select_related('activo', 'almacen_origen', 'almacen_destino', 'solicitante')
            
            return {
                'statistics': stats,
                'pending_approvals': pending_approvals,
                'pending_count': len(pending_approvals),
                'high_priority_requests': list(high_priority),
                'high_priority_count': high_priority.count(),
                'overdue_requests': list(overdue_requests),
                'overdue_count': overdue_requests.count(),
                'recent_activity': list(recent_activity),
                'recent_activity_count': recent_activity.count(),
                'managed_warehouses': AlmacenRegional.objects.filter(manager=manager, activo=True),
            }
            
        except Exception as e:
            logger.error(f"Failed to get dashboard data for {manager.username}: {str(e)}")
            return {
                'statistics': {},
                'pending_approvals': [],
                'pending_count': 0,
                'high_priority_requests': [],
                'high_priority_count': 0,
                'overdue_requests': [],
                'overdue_count': 0,
                'recent_activity': [],
                'recent_activity_count': 0,
                'managed_warehouses': [],
                'error': str(e)
            }
    
    # ========================================================================
    # PRIVATE HELPER METHODS
    # ========================================================================
    
    @classmethod
    def _validate_approval_authority(cls, solicitud: SolicitudTraslado, 
                                   approver: User, approval_type: str) -> Dict[str, Any]:
        """Validate that user has authority to approve the transfer"""
        if approval_type == 'ORIGEN':
            if approver != solicitud.almacen_origen.manager:
                return {
                    'valid': False,
                    'message': 'Only the origin warehouse manager can approve from origin'
                }
        elif approval_type == 'DESTINO':
            if approver != solicitud.almacen_destino.manager:
                return {
                    'valid': False,
                    'message': 'Only the destination warehouse manager can approve from destination'
                }
        else:
            return {
                'valid': False,
                'message': 'Invalid approval type. Must be ORIGEN or DESTINO'
            }
        
        # Check if transfer is in a state that allows approval
        if solicitud.estado in ['COMPLETADA', 'RECHAZADA', 'CANCELADA']:
            return {
                'valid': False,
                'message': f'Transfer cannot be approved in {solicitud.get_estado_display()} state'
            }
        
        return {'valid': True, 'message': 'Approval authority validated'}
    
    @classmethod
    def _rollback_transfer_execution(cls, rollback_data: Dict[str, Any]):
        """Rollback a failed transfer execution"""
        try:
            activo = ActivoInventario.objects.get(id=rollback_data['activo_id'])
            original_warehouse = AlmacenRegional.objects.get(id=rollback_data['original_warehouse'])
            solicitud = SolicitudTraslado.objects.get(id=rollback_data['solicitud_id'])
            
            # Restore asset state using raw update to bypass validation
            ActivoInventario.objects.filter(id=activo.id).update(
                codigo_actual=rollback_data['original_code'],
                almacen_actual=original_warehouse,
                estado=rollback_data['original_state']
            )
            
            # Restore solicitud state using raw update to bypass validation
            SolicitudTraslado.objects.filter(id=solicitud.id).update(
                estado=rollback_data['original_solicitud_state'],
                fecha_ejecucion=None,
                ejecutado_por=None
            )
            
            logger.info(f"Transfer execution rollback completed for solicitud {solicitud.numero_solicitud}")
            
        except Exception as e:
            logger.error(f"Failed to rollback transfer execution: {str(e)}")
            raise
    
    @classmethod
    def _emergency_rollback_transfer_execution(cls, rollback_data: Dict[str, Any]):
        """Emergency rollback for unexpected failures during transfer execution"""
        try:
            from .services import AuditTrailService
            from django.contrib.auth import get_user_model
            
            User = get_user_model()
            
            # Try to get system user for emergency operations
            try:
                system_user = User.objects.filter(username='system').first()
                if not system_user:
                    system_user = User.objects.filter(is_superuser=True).first()
            except Exception:
                system_user = None
            
            # Perform the rollback
            if 'solicitud_id' in rollback_data:
                try:
                    solicitud = SolicitudTraslado.objects.get(id=rollback_data['solicitud_id'])
                    
                    # Restore solicitud state
                    SolicitudTraslado.objects.filter(id=solicitud.id).update(
                        estado=rollback_data.get('original_solicitud_state', 'APROBADA_COMPLETA'),
                        fecha_ejecucion=None,
                        ejecutado_por=None
                    )
                    
                    # Restore asset state if we have the data
                    if 'original_asset_code' in rollback_data:
                        ActivoInventario.objects.filter(id=solicitud.activo.id).update(
                            codigo_actual=rollback_data['original_asset_code'],
                            almacen_actual_id=rollback_data.get('original_asset_warehouse'),
                            estado=rollback_data.get('original_asset_state', 'EN_ALMACEN')
                        )
                    
                    # Record emergency rollback in audit trail
                    if system_user:
                        try:
                            AuditTrailService.record_system_operation(
                                accion='EMERGENCY_ROLLBACK',
                                descripcion=f'Emergency rollback for failed transfer execution: {solicitud.numero_solicitud}',
                                user=system_user,
                                entidades_afectadas=[
                                    {'type': 'SolicitudTraslado', 'id': solicitud.id, 'numero': solicitud.numero_solicitud},
                                    {'type': 'ActivoInventario', 'id': solicitud.activo.id, 'codigo': solicitud.activo.codigo_actual}
                                ],
                                parametros_operacion=rollback_data,
                                exitosa=True,
                                puede_revertir=False
                            )
                        except Exception as audit_error:
                            logger.error(f"Failed to record emergency rollback in audit trail: {str(audit_error)}")
                    
                    logger.info(f"Emergency rollback completed for transfer {rollback_data['solicitud_id']}")
                    
                except Exception as e:
                    logger.error(f"Emergency rollback failed: {str(e)}")
                    raise
            
        except Exception as e:
            logger.error(f"Critical failure in emergency rollback: {str(e)}")
            raise
    
    # ========================================================================
    # NOTIFICATION SYSTEM INTEGRATION
    # ========================================================================
    
    @classmethod
    def _send_approval_notifications(cls, solicitud: SolicitudTraslado):
        """Send notifications to approvers when transfer request is created"""
        try:
            # Notify origin manager
            if solicitud.almacen_origen.manager:
                cls._send_notification(NotificationData(
                    recipient=solicitud.almacen_origen.manager,
                    subject=f"Nueva solicitud de traslado - {solicitud.numero_solicitud}",
                    message=f"Se ha creado una nueva solicitud de traslado para el activo {solicitud.activo.codigo_actual} "
                           f"desde su almacén {solicitud.almacen_origen.prefijo} hacia {solicitud.almacen_destino.prefijo}. "
                           f"Motivo: {solicitud.motivo}",
                    notification_type='APPROVAL_REQUEST',
                    priority=solicitud.prioridad,
                    metadata={
                        'solicitud_id': solicitud.id,
                        'approval_type': 'ORIGEN',
                        'asset_code': solicitud.activo.codigo_actual,
                        'deadline': solicitud.fecha_limite.isoformat()
                    }
                ))
            
            # Notify destination manager
            if solicitud.almacen_destino.manager:
                cls._send_notification(NotificationData(
                    recipient=solicitud.almacen_destino.manager,
                    subject=f"Nueva solicitud de traslado - {solicitud.numero_solicitud}",
                    message=f"Se ha creado una nueva solicitud de traslado para el activo {solicitud.activo.codigo_actual} "
                           f"desde {solicitud.almacen_origen.prefijo} hacia su almacén {solicitud.almacen_destino.prefijo}. "
                           f"Motivo: {solicitud.motivo}",
                    notification_type='APPROVAL_REQUEST',
                    priority=solicitud.prioridad,
                    metadata={
                        'solicitud_id': solicitud.id,
                        'approval_type': 'DESTINO',
                        'asset_code': solicitud.activo.codigo_actual,
                        'deadline': solicitud.fecha_limite.isoformat()
                    }
                ))
            
        except Exception as e:
            logger.error(f"Failed to send approval notifications for {solicitud.numero_solicitud}: {str(e)}")
    
    @classmethod
    def _send_approval_granted_notifications(cls, solicitud: SolicitudTraslado, 
                                           approval: AprobacionTraslado):
        """Send notifications when an approval is granted"""
        try:
            # Notify the requester
            cls._send_notification(NotificationData(
                recipient=solicitud.solicitante,
                subject=f"Aprobación otorgada - {solicitud.numero_solicitud}",
                message=f"Su solicitud de traslado {solicitud.numero_solicitud} ha sido aprobada por "
                       f"el gerente del almacén {approval.get_tipo_aprobacion_display().lower()}. "
                       f"Comentarios: {approval.comentarios or 'Sin comentarios'}",
                notification_type='APPROVAL_GRANTED',
                metadata={
                    'solicitud_id': solicitud.id,
                    'approval_type': approval.tipo_aprobacion,
                    'approver': approval.aprobador.username
                }
            ))
            
            # If this completes the dual approval, notify both managers
            if solicitud.can_execute():
                for manager in [solicitud.almacen_origen.manager, solicitud.almacen_destino.manager]:
                    if manager and manager != approval.aprobador:
                        cls._send_notification(NotificationData(
                            recipient=manager,
                            subject=f"Traslado listo para ejecutar - {solicitud.numero_solicitud}",
                            message=f"El traslado {solicitud.numero_solicitud} ha recibido ambas aprobaciones "
                                   f"y está listo para ser ejecutado.",
                            notification_type='TRANSFER_READY',
                            priority=solicitud.prioridad,
                            metadata={
                                'solicitud_id': solicitud.id,
                                'asset_code': solicitud.activo.codigo_actual
                            }
                        ))
            
        except Exception as e:
            logger.error(f"Failed to send approval granted notifications: {str(e)}")
    
    @classmethod
    def _send_rejection_notifications(cls, solicitud: SolicitudTraslado, 
                                    rejection: AprobacionTraslado):
        """Send notifications when a transfer is rejected"""
        try:
            # Notify the requester
            cls._send_notification(NotificationData(
                recipient=solicitud.solicitante,
                subject=f"Solicitud rechazada - {solicitud.numero_solicitud}",
                message=f"Su solicitud de traslado {solicitud.numero_solicitud} ha sido rechazada por "
                       f"el gerente del almacén {rejection.get_tipo_aprobacion_display().lower()}. "
                       f"Motivo: {rejection.comentarios}",
                notification_type='APPROVAL_REJECTED',
                metadata={
                    'solicitud_id': solicitud.id,
                    'rejection_reason': rejection.comentarios,
                    'rejector': rejection.aprobador.username
                }
            ))
            
            # Notify the other manager (if they haven't acted yet)
            other_manager = (solicitud.almacen_destino.manager 
                           if rejection.tipo_aprobacion == 'ORIGEN' 
                           else solicitud.almacen_origen.manager)
            
            if other_manager and other_manager != rejection.aprobador:
                cls._send_notification(NotificationData(
                    recipient=other_manager,
                    subject=f"Solicitud rechazada - {solicitud.numero_solicitud}",
                    message=f"La solicitud de traslado {solicitud.numero_solicitud} ha sido rechazada "
                           f"por el gerente del almacén {rejection.get_tipo_aprobacion_display().lower()}. "
                           f"No se requiere acción adicional.",
                    notification_type='APPROVAL_REJECTED',
                    metadata={
                        'solicitud_id': solicitud.id,
                        'rejection_reason': rejection.comentarios
                    }
                ))
            
        except Exception as e:
            logger.error(f"Failed to send rejection notifications: {str(e)}")
    
    @classmethod
    def _send_transfer_ready_notifications(cls, solicitud: SolicitudTraslado):
        """Send notifications when transfer is ready for execution"""
        try:
            # This is handled in _send_approval_granted_notifications
            # when the second approval completes the dual approval
            pass
            
        except Exception as e:
            logger.error(f"Failed to send transfer ready notifications: {str(e)}")
    
    @classmethod
    def _send_transfer_executed_notifications(cls, solicitud: SolicitudTraslado):
        """Send notifications when transfer is executed"""
        try:
            # Notify requester
            cls._send_notification(NotificationData(
                recipient=solicitud.solicitante,
                subject=f"Traslado ejecutado - {solicitud.numero_solicitud}",
                message=f"Su solicitud de traslado {solicitud.numero_solicitud} ha sido ejecutada. "
                       f"El activo {solicitud.activo.codigo_actual} está ahora en tránsito hacia "
                       f"{solicitud.almacen_destino.prefijo}.",
                notification_type='TRANSFER_EXECUTED',
                metadata={
                    'solicitud_id': solicitud.id,
                    'asset_code': solicitud.activo.codigo_actual,
                    'execution_date': solicitud.fecha_ejecucion.isoformat()
                }
            ))
            
            # Notify destination manager
            if solicitud.almacen_destino.manager:
                cls._send_notification(NotificationData(
                    recipient=solicitud.almacen_destino.manager,
                    subject=f"Activo en tránsito - {solicitud.numero_solicitud}",
                    message=f"El activo {solicitud.activo.codigo_actual} está en tránsito hacia su almacén "
                           f"{solicitud.almacen_destino.prefijo}. Por favor, confirme la recepción cuando llegue.",
                    notification_type='TRANSFER_EXECUTED',
                    priority=solicitud.prioridad,
                    metadata={
                        'solicitud_id': solicitud.id,
                        'asset_code': solicitud.activo.codigo_actual,
                        'expected_arrival': solicitud.fecha_limite.isoformat()
                    }
                ))
            
        except Exception as e:
            logger.error(f"Failed to send transfer executed notifications: {str(e)}")
    
    @classmethod
    def _send_transfer_completed_notifications(cls, solicitud: SolicitudTraslado):
        """Send notifications when transfer is completed"""
        try:
            # Notify requester
            cls._send_notification(NotificationData(
                recipient=solicitud.solicitante,
                subject=f"Traslado completado - {solicitud.numero_solicitud}",
                message=f"Su solicitud de traslado {solicitud.numero_solicitud} ha sido completada exitosamente. "
                       f"El activo {solicitud.activo.codigo_actual} ha sido recibido en "
                       f"{solicitud.almacen_destino.prefijo}.",
                notification_type='TRANSFER_COMPLETED',
                metadata={
                    'solicitud_id': solicitud.id,
                    'asset_code': solicitud.activo.codigo_actual,
                    'completion_date': solicitud.fecha_completada.isoformat()
                }
            ))
            
            # Notify origin manager
            if solicitud.almacen_origen.manager:
                cls._send_notification(NotificationData(
                    recipient=solicitud.almacen_origen.manager,
                    subject=f"Traslado completado - {solicitud.numero_solicitud}",
                    message=f"El traslado del activo {solicitud.activo.codigo_actual} desde su almacén "
                           f"{solicitud.almacen_origen.prefijo} ha sido completado exitosamente.",
                    notification_type='TRANSFER_COMPLETED',
                    metadata={
                        'solicitud_id': solicitud.id,
                        'asset_code': solicitud.activo.codigo_actual,
                        'completion_date': solicitud.fecha_completada.isoformat()
                    }
                ))
            
        except Exception as e:
            logger.error(f"Failed to send transfer completed notifications: {str(e)}")
    
    @classmethod
    def _send_transfer_cancelled_notifications(cls, solicitud: SolicitudTraslado, 
                                             canceller: User, reason: str):
        """Send notifications when transfer is cancelled"""
        try:
            # Notify all involved parties except the canceller
            recipients = [solicitud.solicitante]
            
            if solicitud.almacen_origen.manager and solicitud.almacen_origen.manager != canceller:
                recipients.append(solicitud.almacen_origen.manager)
            
            if solicitud.almacen_destino.manager and solicitud.almacen_destino.manager != canceller:
                recipients.append(solicitud.almacen_destino.manager)
            
            for recipient in recipients:
                cls._send_notification(NotificationData(
                    recipient=recipient,
                    subject=f"Traslado cancelado - {solicitud.numero_solicitud}",
                    message=f"La solicitud de traslado {solicitud.numero_solicitud} ha sido cancelada "
                           f"por {canceller.username}. Motivo: {reason}",
                    notification_type='TRANSFER_CANCELLED',
                    metadata={
                        'solicitud_id': solicitud.id,
                        'canceller': canceller.username,
                        'cancellation_reason': reason
                    }
                ))
            
        except Exception as e:
            logger.error(f"Failed to send transfer cancelled notifications: {str(e)}")
    
    @classmethod
    def _send_notification(cls, notification_data: NotificationData):
        """
        Send notification through the notification system.
        
        This is a placeholder for integration with the actual notification system.
        In a real implementation, this would integrate with email, SMS, or 
        in-app notification systems.
        """
        try:
            # Log the notification for now
            logger.info(
                f"NOTIFICATION [{notification_data.notification_type}] "
                f"to {notification_data.recipient.username}: {notification_data.subject}"
            )
            
            # TODO: Integrate with actual notification system
            # Examples:
            # - Send email via Django's email backend
            # - Create in-app notification record
            # - Send SMS via external service
            # - Push notification to mobile app
            # - Integration with Slack/Teams/etc.
            
            # For now, we'll create a simple log entry
            # In production, replace this with actual notification delivery
            
        except Exception as e:
            logger.error(f"Failed to send notification: {str(e)}")


class TransferWorkflowStateManager:
    """
    Helper class for managing transfer workflow states and transitions.
    """
    
    # Valid state transitions
    STATE_TRANSITIONS = {
        'PENDIENTE': ['APROBADA_ORIGEN', 'APROBADA_DESTINO', 'RECHAZADA', 'CANCELADA'],
        'APROBADA_ORIGEN': ['APROBADA_COMPLETA', 'RECHAZADA', 'CANCELADA'],
        'APROBADA_DESTINO': ['APROBADA_COMPLETA', 'RECHAZADA', 'CANCELADA'],
        'APROBADA_COMPLETA': ['EN_TRANSITO', 'CANCELADA'],
        'EN_TRANSITO': ['COMPLETADA'],
        'COMPLETADA': [],  # Terminal state
        'RECHAZADA': [],   # Terminal state
        'CANCELADA': [],   # Terminal state
    }
    
    @classmethod
    def is_valid_transition(cls, from_state: str, to_state: str) -> bool:
        """Check if state transition is valid"""
        return to_state in cls.STATE_TRANSITIONS.get(from_state, [])
    
    @classmethod
    def get_valid_transitions(cls, from_state: str) -> List[str]:
        """Get list of valid transitions from current state"""
        return cls.STATE_TRANSITIONS.get(from_state, [])
    
    @classmethod
    def is_terminal_state(cls, state: str) -> bool:
        """Check if state is terminal (no further transitions allowed)"""
        return len(cls.STATE_TRANSITIONS.get(state, [])) == 0
    
    @classmethod
    def can_be_cancelled(cls, state: str) -> bool:
        """Check if transfer can be cancelled in current state"""
        return 'CANCELADA' in cls.STATE_TRANSITIONS.get(state, [])
    
    @classmethod
    def requires_dual_approval(cls, state: str) -> bool:
        """Check if state requires dual approval to proceed"""
        return state in ['PENDIENTE', 'APROBADA_ORIGEN', 'APROBADA_DESTINO']


# ============================================================================
# BUSINESS RULE VALIDATORS
# ============================================================================

class TransferBusinessRuleValidator:
    """
    Centralized business rule validation for transfer operations.
    """
    
    @classmethod
    def validate_warehouse_compatibility(cls, origen: AlmacenRegional, 
                                       destino: AlmacenRegional) -> Tuple[bool, str]:
        """Validate that warehouses are compatible for transfers"""
        # Same organizational unit check
        if origen.unidad_organizacional != destino.unidad_organizacional:
            # Allow transfers between different units but log as warning
            return True, "Transfer between different organizational units - may require additional approval"
        
        return True, "Warehouses are compatible"
    
    @classmethod
    def validate_asset_compatibility(cls, activo: ActivoInventario, 
                                   destino: AlmacenRegional) -> Tuple[bool, str]:
        """Validate that asset is compatible with destination warehouse"""
        # This could include checks for:
        # - Asset type compatibility with warehouse
        # - Environmental requirements
        # - Security clearance levels
        # - Storage capacity requirements
        
        # For now, basic validation
        return True, "Asset is compatible with destination warehouse"
    
    @classmethod
    def validate_transfer_timing(cls, fecha_limite: timezone.datetime, 
                               prioridad: str) -> Tuple[bool, str]:
        """Validate transfer timing based on priority"""
        now = timezone.now()
        
        if prioridad == 'URGENTE':
            max_hours = 4
            if fecha_limite > now + timedelta(hours=max_hours):
                return False, f"Urgent transfers must be completed within {max_hours} hours"
        
        elif prioridad == 'ALTA':
            recommended_hours = 24
            if fecha_limite > now + timedelta(hours=recommended_hours):
                return True, f"High priority transfers should be completed within {recommended_hours} hours"
        
        return True, "Transfer timing is acceptable"