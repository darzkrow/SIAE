# Generated migration for Subalmacén model

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('geography', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('institucion', '0001_initial'),  # Adjust to your latest migration
    ]

    operations = [
        migrations.CreateModel(
            name='Subalmacen',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('nombre', models.CharField(help_text='Nombre del subalmacén', max_length=200)),
                ('codigo', models.CharField(help_text='Código único (ej: SUB-ZUL-001)', max_length=20, unique=True)),
                ('direccion', models.TextField(blank=True, help_text='Dirección completa')),
                ('coordenadas_gps', models.CharField(blank=True, help_text='Coordenadas GPS (lat,lng)', max_length=100)),
                ('capacidad', models.IntegerField(blank=True, help_text='Capacidad de almacenamiento', null=True)),
                ('activo', models.BooleanField(default=True)),
                ('descripcion', models.TextField(blank=True)),
                ('estado', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='subalmacenes', to='geography.state')),
                ('municipio', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='subalmacenes', to='geography.municipality')),
                ('parroquia', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='subalmacenes', to='geography.parish')),
                ('responsable', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='subalmacenes_responsable', to=settings.AUTH_USER_MODEL)),
                ('sucursal', models.ForeignKey(help_text='Sucursal a la que pertenece', on_delete=django.db.models.deletion.CASCADE, related_name='subalmacenes', to='institucion.sucursal')),
            ],
            options={
                'verbose_name': 'Subalmacén',
                'verbose_name_plural': 'Subalmacenes',
                'ordering': ['estado__name', 'sucursal__nombre', 'nombre'],
                'unique_together': {('nombre', 'sucursal')},
                'indexes': [
                    models.Index(fields=['estado', 'activo'], name='institucion_estado_activo_idx'),
                    models.Index(fields=['sucursal', 'activo'], name='institucion_sucursal_activo_idx'),
                    models.Index(fields=['codigo'], name='institucion_codigo_idx'),
                ],
            },
        ),
        
        # Add QR code fields to SolicitudTraslado
        migrations.AddField(
            model_name='solicitudtraslado',
            name='qr_code',
            field=models.ImageField(blank=True, help_text='Código QR para aprobación rápida', null=True, upload_to='qr_codes/traslados/'),
        ),
        migrations.AddField(
            model_name='solicitudtraslado',
            name='qr_url',
            field=models.URLField(blank=True, help_text='URL de aprobación contenida en el QR'),
        ),
        migrations.AddField(
            model_name='solicitudtraslado',
            name='qr_generado_en',
            field=models.DateTimeField(blank=True, help_text='Fecha de generación del QR', null=True),
        ),
    ]
