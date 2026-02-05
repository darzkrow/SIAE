from django_filters import rest_framework as filters
from stock.models import MovimientoInventario
from institucion.models import AlmacenRegional, Subalmacen

class MovimientoInventarioFilter(filters.FilterSet):
    almacen_origen = filters.ModelChoiceFilter(
        queryset=AlmacenRegional.objects.all(),
        field_name='ubicacion_origen__almacen_regional',
        label='Almacén Regional Origen'
    )
    subalmacen_origen = filters.ModelChoiceFilter(
        queryset=Subalmacen.objects.all(),
        field_name='ubicacion_origen__subalmacen',
        label='Subalmacén Origen'
    )
    almacen_destino = filters.ModelChoiceFilter(
        queryset=AlmacenRegional.objects.all(),
        field_name='ubicacion_destino__almacen_regional',
        label='Almacén Regional Destino'
    )
    subalmacen_destino = filters.ModelChoiceFilter(
        queryset=Subalmacen.objects.all(),
        field_name='ubicacion_destino__subalmacen',
        label='Subalmacén Destino'
    )

    class Meta:
        model = MovimientoInventario
        fields = ['tipo_movimiento', 'almacen_origen', 'subalmacen_origen', 'almacen_destino', 'subalmacen_destino', 'status']
