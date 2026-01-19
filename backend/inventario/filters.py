from django_filters import rest_framework as filters
from .models import MovimientoInventario
from institucion.models import Acueducto

class MovimientoInventarioFilter(filters.FilterSet):
    acueducto_origen = filters.ModelChoiceFilter(
        queryset=Acueducto.objects.all(),
        field_name='ubicacion_origen__acueducto',
        label='Acueducto Origen'
    )
    acueducto_destino = filters.ModelChoiceFilter(
        queryset=Acueducto.objects.all(),
        field_name='ubicacion_destino__acueducto',
        label='Acueducto Destino'
    )

    class Meta:
        model = MovimientoInventario
        fields = ['tipo_movimiento', 'acueducto_origen', 'acueducto_destino']
