"""
Script para probar la generación de QR codes
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from institucion.models import SolicitudTraslado, AlmacenRegional, ActivoInventario
from django.contrib.auth import get_user_model
from datetime import datetime, timedelta

User = get_user_model()

def test_qr_generation():
    print("🧪 Probando generación de QR codes...")
    
    # Verificar que existen almacenes
    almacenes = AlmacenRegional.objects.all()
    if almacenes.count() < 2:
        print("❌ Error: Se necesitan al menos 2 almacenes para crear solicitud de traslado")
        print("   Crea almacenes primero en el admin de Django")
        return
    
    # Verificar que existe al menos un activo
    activos = ActivoInventario.objects.all()
    if activos.count() == 0:
        print("❌ Error: Se necesita al menos 1 activo para crear solicitud de traslado")
        print("   Crea un activo primero en el admin de Django")
        return
    
    # Obtener o crear usuario
    user, created = User.objects.get_or_create(
        username='admin',
        defaults={
            'email': 'admin@hidroven.com',
            'is_staff': True,
            'is_superuser': True
        }
    )
    if created:
        user.set_password('admin123')
        user.save()
        print(f"✅ Usuario creado: {user.username}")
    
    # Crear solicitud de traslado
    print("\n1️⃣ Creando solicitud de traslado...")
    
    almacen_origen = almacenes.first()
    almacen_destino = almacenes.last()
    activo = activos.first()
    
    # Generar número de solicitud único
    numero = f"SOL-TEST-{datetime.now().strftime('%Y%m%d%H%M%S')}"
    
    solicitud = SolicitudTraslado.objects.create(
        numero_solicitud=numero,
        activo=activo,
        almacen_origen=almacen_origen,
        almacen_destino=almacen_destino,
        solicitante=user,
        motivo='Prueba de generación de QR code',
        fecha_limite=datetime.now() + timedelta(days=7),
        prioridad='NORMAL',
        estado='PENDIENTE'
    )
    
    print(f"✅ Solicitud creada: {solicitud.numero_solicitud}")
    
    # Generar QR code
    print("\n2️⃣ Generando QR code...")
    try:
        solicitud.generar_qr_code()
        print(f"✅ QR code generado exitosamente!")
        print(f"   📄 Archivo: {solicitud.qr_code.name if solicitud.qr_code else 'No generado'}")
        print(f"   🔗 URL: {solicitud.qr_url}")
        print(f"   📅 Generado en: {solicitud.qr_generado_en}")
    except Exception as e:
        print(f"❌ Error al generar QR: {str(e)}")
        import traceback
        traceback.print_exc()
    
    # Verificar campos
    print("\n3️⃣ Verificando campos QR...")
    solicitud.refresh_from_db()
    
    checks = {
        'qr_code existe': bool(solicitud.qr_code),
        'qr_url existe': bool(solicitud.qr_url),
        'qr_generado_en existe': bool(solicitud.qr_generado_en),
    }
    
    for check, result in checks.items():
        status = "✅" if result else "❌"
        print(f"   {status} {check}")
    
    # Mostrar información de la solicitud
    print("\n📋 INFORMACIÓN DE LA SOLICITUD:")
    print(f"   Número: {solicitud.numero_solicitud}")
    print(f"   Estado: {solicitud.estado}")
    print(f"   Origen: {solicitud.almacen_origen.nombre}")
    print(f"   Destino: {solicitud.almacen_destino.nombre}")
    print(f"   Activo: {solicitud.activo.codigo_actual}")
    print(f"   QR URL: {solicitud.qr_url}")
    
    if solicitud.qr_code:
        print(f"   QR File: {solicitud.qr_code.path}")
        print(f"\n   ℹ️  Para ver el QR, abre: http://localhost:8000{solicitud.qr_code.url}")
    
    print("\n✅ Prueba de QR completada!")

if __name__ == '__main__':
    test_qr_generation()
