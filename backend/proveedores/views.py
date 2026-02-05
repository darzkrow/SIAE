from core.viewsets import BaseAPIViewSet
from proveedores.models import Supplier
from proveedores.serializers import SupplierSerializer

class SupplierViewSet(BaseAPIViewSet):
    queryset = Supplier.objects.all()
    serializer_class = SupplierSerializer
    search_fields = ['nombre', 'rif', 'codigo']
