from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from core.viewsets import BaseAPIViewSet
from core.filters import ProductFilterSet
from productos.models import (
    UnitOfMeasure, ChemicalProduct, 
    Pipe, PumpAndMotor, Accessory
)
from proveedores.models import Supplier
from productos.serializers import (
    UnitOfMeasureSerializer,
    ChemicalProductSerializer, ChemicalProductListSerializer,
    PipeSerializer, PipeListSerializer,
    PumpAndMotorSerializer, PumpAndMotorListSerializer,
    AccessorySerializer, AccessoryListSerializer
)
from proveedores.serializers import SupplierSerializer

class UnitOfMeasureViewSet(BaseAPIViewSet):
    queryset = UnitOfMeasure.objects.all()
    serializer_class = UnitOfMeasureSerializer
    search_fields = ['nombre', 'simbolo']

# SupplierViewSet moved to proveedores app

class ChemicalProductViewSet(BaseAPIViewSet):
    queryset = ChemicalProduct.objects.select_related('categoria', 'unidad_medida', 'proveedor').all()
    serializer_class = ChemicalProductSerializer
    filterset_class = ProductFilterSet
    search_fields = ['sku', 'nombre', 'descripcion', 'numero_un']
    
    def get_serializer_class(self):
        if self.action == 'list':
            return ChemicalProductListSerializer
        return ChemicalProductSerializer

class PipeViewSet(BaseAPIViewSet):
    queryset = Pipe.objects.select_related('categoria', 'unidad_medida', 'proveedor').all()
    serializer_class = PipeSerializer
    filterset_class = ProductFilterSet
    search_fields = ['sku', 'nombre', 'material']
    
    def get_serializer_class(self):
        if self.action == 'list':
            return PipeListSerializer
        return PipeSerializer

class PumpAndMotorViewSet(BaseAPIViewSet):
    queryset = PumpAndMotor.objects.select_related('categoria', 'unidad_medida', 'proveedor', 'marca').all()
    serializer_class = PumpAndMotorSerializer
    filterset_class = ProductFilterSet
    search_fields = ['sku', 'nombre', 'modelo', 'numero_serie']
    
    def get_serializer_class(self):
        if self.action == 'list':
            return PumpAndMotorListSerializer
        return PumpAndMotorSerializer

class AccessoryViewSet(BaseAPIViewSet):
    queryset = Accessory.objects.select_related('categoria', 'unidad_medida', 'proveedor').all()
    serializer_class = AccessorySerializer
    filterset_class = ProductFilterSet
    search_fields = ['sku', 'nombre', 'tipo_accesorio']
    
    def get_serializer_class(self):
        if self.action == 'list':
            return AccessoryListSerializer
        return AccessorySerializer
