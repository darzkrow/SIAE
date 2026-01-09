from django.core.management.base import BaseCommand
from django.conf import settings
from django.core.mail import send_mail
from django.utils import timezone
from datetime import timedelta

from inventario.models import (
    AlertaStock, StockTuberia, StockEquipo, Notification
)


class Command(BaseCommand):
    help = 'Revisa las alertas de stock y crea notificaciones si el stock está por debajo del umbral.'

    def handle(self, *args, **options):
        now = timezone.now()
        created = 0
        for alerta in AlertaStock.objects.filter(activo=True):
            # obtener stock según tipo
            if alerta.tuberia:
                try:
                    stock = StockTuberia.objects.get(tuberia=alerta.tuberia, acueducto=alerta.acueducto)
                    cantidad = stock.cantidad
                except StockTuberia.DoesNotExist:
                    cantidad = 0
            else:
                try:
                    stock = StockEquipo.objects.get(equipo=alerta.equipo, acueducto=alerta.acueducto)
                    cantidad = stock.cantidad
                except StockEquipo.DoesNotExist:
                    cantidad = 0

            if cantidad <= alerta.umbral_minimo:
                # evitar crear notificaciones repetidas demasiado seguidas: 24h
                last = alerta.notifications.order_by('-creada_en').first()
                if last and last.creada_en > now - timedelta(hours=24):
                    continue

                mensaje = (
                    f"Alerta: Stock bajo para {'Tubería' if alerta.tuberia else 'Equipo'} "
                    f"{alerta.tuberia or alerta.equipo} en {alerta.acueducto}. "
                    f"Cantidad actual: {cantidad}. Umbral: {alerta.umbral_minimo}."
                )

                notif = Notification.objects.create(alerta=alerta, mensaje=mensaje, meta={'cantidad': cantidad, 'umbral': alerta.umbral_minimo})
                created += 1

                # enviar email si está configurado
                email_to = getattr(settings, 'STOCK_ALERT_EMAILS', None)
                if email_to:
                    try:
                        send_mail(
                            subject='Alerta de stock bajo',
                            message=mensaje,
                            from_email=getattr(settings, 'DEFAULT_FROM_EMAIL', None),
                            recipient_list=email_to if isinstance(email_to, (list, tuple)) else [email_to],
                            fail_silently=False,
                        )
                        notif.mark_sent()
                    except Exception as e:
                        # guardar meta con el error
                        notif.meta = {'error': str(e)}
                        notif.save()

        self.stdout.write(self.style.SUCCESS(f'Notificaciones creadas: {created}'))
