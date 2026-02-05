from core.serializers import BaseModelSerializer
from proveedores.models import Supplier

class SupplierSerializer(BaseModelSerializer):
    class Meta(BaseModelSerializer.Meta):
        model = Supplier
        fields = BaseModelSerializer.Meta.fields + [
            'nombre', 'rif', 'codigo', 'contacto_nombre',
            'telefono', 'email', 'direccion', 'activo'
        ]
