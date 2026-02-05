from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone
from .models import Notificacion, Alerta
from .tasks import broadcast_notification, send_telegram_notification
from stock.models import Stock, MovimientoInventario
from compras.models import OrdenCompra

def create_and_broadcast(mensaje, tipo='INFO', usuario=None):
    """Auxiliar para crear la notificación en DB y enviarla por WebSocket."""
    notif = Notificacion.objects.create(
        mensaje=mensaje,
        tipo=tipo,
        usuario=usuario
    )
    
    payload = {
        'id': str(notif.id),
        'mensaje': mensaje,
        'tipo': tipo,
        'timestamp': timezone.now().isoformat(),
        'leida': False
    }
    
    # Enviar al usuario específico si existe, sino al global
    user_id = usuario.id if usuario else None
    broadcast_notification.delay(payload, user_id=user_id)
    
    # Si es crítica o de stock, intentar Telegram
    if tipo in ['CRITICAL', 'WARNING']:
        send_telegram_notification.delay(mensaje)

@receiver(post_save, sender=Stock)
def stock_alert_signal(sender, instance, **kwargs):
    """Monitorea el stock actual contra el mínimo."""
    if instance.stock_actual <= instance.stock_minimo:
        mensaje = f"⚠️ Stock Bajo: {instance.producto} tiene {instance.cantidad} unidades en {instance.ubicacion} (Mínimo: {instance.stock_minimo})."
        create_and_broadcast(mensaje, tipo='WARNING')

@receiver(post_save, sender=OrdenCompra)
def orden_compra_workflow_signal(sender, instance, created, **kwargs):
    """Notifica cambios en el workflow de órdenes de compra."""
    if created:
        mensaje = f"📜 Nueva Orden de Compra: {instance.codigo} generada."
        create_and_broadcast(mensaje, tipo='INFO')
    else:
        # Detectar cambios de estado
        if instance.status == OrdenCompra.Status.PENDIENTE_PRESUPUESTO:
             mensaje = f"💰 Orden {instance.codigo} aprobada por Comercialización. Pendiente Presupuesto."
             create_and_broadcast(mensaje, tipo='INFO')
        elif instance.status == OrdenCompra.Status.PENDIENTE_FINANZAS:
             mensaje = f"🏦 Orden {instance.codigo} aprobada por Presupuesto. Pendiente Finanzas."
             create_and_broadcast(mensaje, tipo='INFO')
        elif instance.status == OrdenCompra.Status.PENDIENTE_COMPRAS:
             mensaje = f"🛒 Orden {instance.codigo} aprobada por Finanzas. Lista para Ejecución."
             create_and_broadcast(mensaje, tipo='INFO')
        elif instance.status == OrdenCompra.Status.COMPLETADO:
             mensaje = f"✅ Orden {instance.codigo} ha sido Ejecutada exitosamente."
             create_and_broadcast(mensaje, tipo='SUCCESS')
        elif instance.status == OrdenCompra.Status.CANCELADO:
             mensaje = f"❌ Orden {instance.codigo} ha sido Cancelada. Motivo: {instance.motivo_cancelacion}"
             create_and_broadcast(mensaje, tipo='CRITICAL')

@receiver(post_save, sender=MovimientoInventario)
def movimiento_inventario_signal(sender, instance, **kwargs):
    """Notifica sobre transferencias y ajustes."""
    if instance.tipo_movimiento == MovimientoInventario.TipoMovimiento.TRANSFER and instance.ubicacion_destino:
        mensaje = f"🚛 Transferencia recibida: {instance.cantidad} de {instance.producto} en {instance.ubicacion_destino}."
        create_and_broadcast(mensaje, tipo='SUCCESS', usuario=instance.creado_por)
