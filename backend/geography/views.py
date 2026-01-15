from rest_framework import viewsets
from .models import State, Municipality, Parish
from .serializers import StateSerializer, MunicipalitySerializer, ParishSerializer
from rest_framework.permissions import IsAuthenticatedOrReadOnly


class StateViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = State.objects.all()
    serializer_class = StateSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]


class MunicipalityViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Municipality.objects.select_related('state').all()
    serializer_class = MunicipalitySerializer
    permission_classes = [IsAuthenticatedOrReadOnly]


class ParishViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Parish.objects.select_related('municipality__state').all()
    serializer_class = ParishSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
