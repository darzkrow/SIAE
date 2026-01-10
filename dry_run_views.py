import os
import django
import sys
from django.conf import settings

# Configurar Django
sys.path.append(os.getcwd())
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from inventario import views
from rest_framework.test import APIRequestFactory, force_authenticate
from django.contrib.auth import get_user_model

User = get_user_model()

def test_viewsets():
    factory = APIRequestFactory()
    user = User.objects.first()
    
    viewsets_to_test = [
        (views.ChemicalProductViewSet, 'chemicals'),
        (views.PipeViewSet, 'pipes'),
        (views.PumpAndMotorViewSet, 'pumps'),
        (views.AccessoryViewSet, 'accessories'),
        (views.MovimientoInventarioViewSet, 'movimientos'),
        (views.RefactoredReportesViewSet, 'reportes-v2'),
        (views.NotificacionViewSet, 'notificaciones'),
        (views.AlertaViewSet, 'alertas')
    ]
    
    for vs_class, name in viewsets_to_test:
        print(f"Testing {vs_class.__name__}...")
        try:
            # Test list/get
            request = factory.get(f'/api/{name}/')
            if user:
                force_authenticate(request, user=user)
            
            # Use appropriate actions
            if vs_class == views.RefactoredReportesViewSet:
                view = vs_class.as_view({'get': 'dashboard_stats'})
                response = view(request)
                print(f"  dashboard_stats: {response.status_code}")
                
                view = vs_class.as_view({'get': 'movimientos_recientes'})
                response = view(request)
                print(f"  movimientos_recientes: {response.status_code}")
                
                view = vs_class.as_view({'get': 'stock_por_sucursal'})
                response = view(request)
                print(f"  stock_por_sucursal: {response.status_code}")
                
                view = vs_class.as_view({'get': 'resumen_movimientos'})
                response = view(request)
                print(f"  resumen_movimientos: {response.status_code}")
            else:
                view = vs_class.as_view({'get': 'list'})
                response = view(request)
                print(f"  list: {response.status_code}")
            
        except Exception as e:
            print(f"  FAILED {vs_class.__name__}: {type(e).__name__}: {e}")
            import traceback
            traceback.print_exc()

if __name__ == "__main__":
    test_viewsets()
