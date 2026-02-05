import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from inventario.models import Stock, ChemicalProduct
from compras.models import OrdenCompra
from notificaciones.models import Notificacion
from django.contrib.contenttypes.models import ContentType

def test_stock_signal():
    print("Testing Stock Signal...")
    product = ChemicalProduct.objects.first()
    if not product:
        print("No ChemicalProduct found to test.")
        return
        
    content_type = ContentType.objects.get_for_model(product)
    stock, _ = Stock.objects.get_or_create(
        content_type=content_type,
        object_id=product.id,
        defaults={'stock_actual': 100, 'stock_minimo': 10}
    )
    
    print(f"Setting stock below minimum for {product}...")
    stock.stock_actual = 5
    stock.save()
    
    last_notif = Notificacion.objects.first()
    print(f"Last Notification: {last_notif.mensaje if last_notif else 'NONE'}")

def test_purchase_signal():
    print("\nTesting Purchase Order Signal...")
    # Manual trigger for a new order
    from django.contrib.auth import get_user_model
    User = get_user_model()
    admin = User.objects.filter(is_superuser=True).first()
    
    order = OrdenCompra.objects.create(
        solicitante=admin,
        notas="Test notification"
    )
    print(f"Created Order: {order.codigo}")
    
    last_notif = Notificacion.objects.first()
    print(f"Last Notification: {last_notif.mensaje if last_notif else 'NONE'}")

if __name__ == "__main__":
    test_stock_signal()
    test_purchase_signal()
