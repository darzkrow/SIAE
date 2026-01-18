from django.core.management.base import BaseCommand
from django.conf import settings
from django.core.mail import send_mail
from django.utils import timezone
from datetime import timedelta
from django.contrib.contenttypes.models import ContentType

from notificaciones.models import Alerta, Notificacion
from inventario.models import StockChemical, StockPipe, StockPumpAndMotor, StockAccessory

class Command(BaseCommand):
    help = 'Revisa las alertas de stock y crea notificaciones si el stock está por debajo del umbral.'

    def handle(self, *args, **options):
        now = timezone.now()
        created = 0
        
        # Mapeo de modelos de stock por tipo de producto
        stock_models = {
            'chemicalproduct': StockChemical,
            'pipe': StockPipe,
            'pumpandmotor': StockPumpAndMotor,
            'accessory': StockAccessory,
        }

        for alerta in Alerta.objects.filter(activo=True):
            model_name = alerta.content_type.model
            StockModel = stock_models.get(model_name)
            
            if not StockModel:
                continue

            try:
                # Buscar stock en la ubicación del acueducto
                # Nota: El modelo Alerta asume acueducto corporativo
                stock = StockModel.objects.get(
                    producto_id=alerta.object_id, 
                    ubicacion__acueducto=alerta.acueducto
                )
                cantidad = stock.cantidad
            except StockModel.DoesNotExist:
                cantidad = 0

            if cantidad <= alerta.umbral_minimo:
                # Evitar notificaciones duplicadas en 24h
                # Buscamos en el mensaje si ya existe
                mensaje_base = f"Alerta: Stock bajo para {alerta.producto}"
                if Notificacion.objects.filter(
                    mensaje__icontains=mensaje_base,
                    creada_en__gt=now - timedelta(hours=24)
                ).exists():
                    continue

                mensaje = (
                    f"{mensaje_base} en {alerta.acueducto}. "
                    f"Cantidad actual: {cantidad}. Umbral: {alerta.umbral_minimo}."
                )

                notif = Notificacion.objects.create(
                    mensaje=mensaje,
                    tipo='WARNING'
                )
                created += 1

                # Enviar email si está configurado
                email_to = getattr(settings, 'STOCK_ALERT_EMAILS', None)
                if email_to:
                    try:
                        send_mail(
                            subject='Alerta de stock bajo - SIAE',
                            message=mensaje,
                            from_email=getattr(settings, 'DEFAULT_FROM_EMAIL', None),
                            recipient_list=email_to if isinstance(email_to, (list, tuple)) else [email_to],
                            fail_silently=False,
                        )
                    except Exception as e:
                        self.stdout.write(self.style.ERROR(f"Error enviando email: {e}"))

        self.stdout.write(self.style.SUCCESS(f'Notificaciones creadas: {created}'))
