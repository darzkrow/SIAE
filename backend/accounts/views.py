from rest_framework import viewsets, permissions
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.authtoken.models import Token
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from .models import CustomUser
from .serializers import CustomUserSerializer
from inventario.permissions import CanManageUsers
from drf_spectacular.utils import extend_schema

class CustomAuthToken(ObtainAuthToken):
    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data,
                                           context={'request': request})
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        token, created = Token.objects.get_or_create(user=user)
        return Response({
            'token': token.key,
            'user_id': user.pk,
            'username': user.username,
            'role': user.role,
            'sucursal_id': user.sucursal.id if user.sucursal else None
        })

class UserViewSet(viewsets.ModelViewSet):
    queryset = CustomUser.objects.all()
    serializer_class = CustomUserSerializer
    permission_classes = [CanManageUsers]

@api_view(['GET'])
@permission_classes([IsAuthenticated])
@extend_schema(exclude=True)
def user_profile(request):
    """
    Endpoint para obtener el perfil del usuario autenticado
    """
    user = request.user
    return Response({
        'id': user.id,
        'username': user.username,
        'email': user.email,
        'first_name': user.first_name,
        'last_name': user.last_name,
        'role': user.role,
        'sucursal': {
            'id': user.sucursal.id,
            'nombre': user.sucursal.nombre,
            'organizacion_central': user.sucursal.organizacion_central.nombre
        } if user.sucursal else None,
        'is_admin': user.role == CustomUser.ROLE_ADMIN,
        'permissions': {
            'can_manage_users': user.role == CustomUser.ROLE_ADMIN,
            'can_approve_movements': user.role == CustomUser.ROLE_ADMIN,
            'can_view_all_sucursales': user.role == CustomUser.ROLE_ADMIN,
        }
    })
