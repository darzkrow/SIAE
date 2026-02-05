from core.viewsets import BaseAPIViewSet
from activos.models import MaterialEstrategico, ActivoFijo, FichaTecnicaMotor, RegistroMantenimiento
from activos.serializers import (
    MaterialEstrategicoSerializer, ActivoFijoSerializer,
    FichaTecnicaMotorSerializer, RegistroMantenimientoSerializer
)

class MaterialEstrategicoViewSet(BaseAPIViewSet):
    queryset = MaterialEstrategico.objects.all()
    serializer_class = MaterialEstrategicoSerializer

class ActivoFijoViewSet(BaseAPIViewSet):
    queryset = ActivoFijo.objects.all()
    serializer_class = ActivoFijoSerializer

class FichaTecnicaMotorViewSet(BaseAPIViewSet):
    queryset = FichaTecnicaMotor.objects.all()
    serializer_class = FichaTecnicaMotorSerializer

class RegistroMantenimientoViewSet(BaseAPIViewSet):
    queryset = RegistroMantenimiento.objects.all()
    serializer_class = RegistroMantenimientoSerializer
