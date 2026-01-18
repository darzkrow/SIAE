from rest_framework.routers import DefaultRouter
from django.urls import path, include
from .views import NotificacionViewSet, AlertaViewSet

router = DefaultRouter()
router.register(r'notificaciones', NotificacionViewSet)
router.register(r'alertas', AlertaViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
