"""
Script para probar la generación de QR codes en SolicitudTraslado
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.contrib.auth import get_user_model
from institucion.models import (
    AlmacenRegional, SolicitudTraslado, Subalmacen,
    OrganizacionCentral, Sucursal
)
from inventario.models import ChemicalProduct
from geography.models import State

User = get_user_model()

def test_qr_generation():
    print("🧪 Iniciando pruebas de generación de QR codes...\n")
    
    # 1. Obtener o crear usuario de prueba
    print("1️⃣ Obteniendo usuario de prueba...")
    user, created = User.objects.get_or_create(
        username='test_user',
        defaults={
            'email': 'test@siae.com',
            'first_name': 'Test',
            'last_name': 'User'
        }
    )
    if created:
        user.set_password('testpass123')
        user.save()
        print(f"   ✅ Usuario creado: {user.username}")
    else:
        print(f"   ℹ️  Usuario existente: {user.username}")
    
    # 2. Obtener almacenes
    print("\n2️⃣ Obteniendo almacenes...")
    almacenes = AlmacenRegional.objects.all()[:2]
    
    if almacenes.count() < 2:
        print("   ⚠️  No hay suficientes almacenes. Creando almacenes de prueba...")
        # Crear organización y sucursal si no existen
        org, _ = OrganizacionCentral.objects.get_or_create(
            nombre='Hidroven Test',
            defaults={'rif': 'J-99999999-9'}
        )
        
        # Crear almacenes
        almacen_origen, _ = AlmacenRegional.objects.get_or_create(
            nombre='Almacén Origen Test',
            defaults={
                'prefijo': 'AO',
                'ubicacion': 'Caracas',
                'capacidad_maxima': 1000,
                'manager': user
            }
        )
        
        almacen_destino, _ = AlmacenRegional.objects.get_or_create(
            nombre='Almacén Destino Test',
            defaults={
                'prefijo': 'AD',
                'ubicacion': 'Maracaibo',
                'capacidad_maxima': 1000,
                'manager': user
            }
        )
        
        almacenes = [almacen_origen, almacen_destino]
        print(f"   ✅ Almacenes creados")
    else:
        print(f"   ✅ Almacenes encontrados: {almacenes.count()}")
    
    almacen_origen = almacenes[0]
    almacen_destino = almacenes[1]
    
    print(f"   📦 Origen: {almacen_origen.nombre}")
    print(f"   📦 Destino: {almacen_destino.nombre}")
    
    # 3. Obtener o crear producto químico
    print("\n3️⃣ Obteniendo producto de inventario...")
    producto, created = ChemicalProduct.objects.get_or_create(
        sku='CHEM-TEST-001',
        defaults={
            'nombre': 'Producto Químico Test',
            'descripcion': 'Producto de prueba para QR',
            'stock_actual': 100,
            'stock_minimo': 10,
            'precio_unitario': 50.00,
            'activo': True
        }
    )
    if created:
        print(f"   ✅ Producto creado: {producto.sku}")
    else:
        print(f"   ℹ️  Producto existente: {producto.sku}")
    
    # 4. Crear solicitud de traslado
    print("\n4️⃣ Creando solicitud de traslado...")
    solicitud = SolicitudTraslado.objects.create(
        almacen_origen=almacen_origen,
        almacen_destino=almacen_destino,
        solicitante=user,
        motivo='Prueba de generación de QR code',
        prioridad='MEDIA'
    )
    print(f"   ✅ Solicitud creada: {solicitud.numero_solicitud}")
    print(f"   📋 Estado: {solicitud.estado}")
    
    # 5. Verificar generación de QR
    print("\n5️⃣ Verificando generación de QR code...")
    
    if solicitud.qr_code:
        print(f"   ✅ QR Code generado exitosamente!")
        print(f"   📄 Archivo: {solicitud.qr_code.name}")
        print(f"   🔗 URL: {solicitud.qr_url}")
        print(f"   ⏰ Generado en: {solicitud.qr_generado_en}")
        
        # Verificar que el archivo existe
        qr_path = solicitud.qr_code.path
        if os.path.exists(qr_path):
            file_size = os.path.getsize(qr_path)
            print(f"   💾 Tamaño del archivo: {file_size} bytes")
            print(f"   📂 Ruta completa: {qr_path}")
        else:
            print(f"   ⚠️  El archivo QR no existe en el sistema de archivos")
    else:
        print(f"   ❌ QR Code NO fue generado")
        print(f"   ℹ️  Intentando generar manualmente...")
        
        # Intentar generar manualmente
        try:
            solicitud.generar_qr_code()
            solicitud.save()
            print(f"   ✅ QR generado manualmente")
            print(f"   📄 Archivo: {solicitud.qr_code.name}")
            print(f"   🔗 URL: {solicitud.qr_url}")
        except Exception as e:
            print(f"   ❌ Error al generar QR: {str(e)}")
    
    # 6. Resumen
    print("\n" + "="*60)
    print("📊 RESUMEN DE LA PRUEBA")
    print("="*60)
    print(f"Solicitud ID: {solicitud.id}")
    print(f"Número: {solicitud.numero_solicitud}")
    print(f"Estado: {solicitud.estado}")
    print(f"Origen: {almacen_origen.nombre}")
    print(f"Destino: {almacen_destino.nombre}")
    print(f"Producto: {producto.sku}")
    print(f"QR Generado: {'✅ SÍ' if solicitud.qr_code else '❌ NO'}")
    
    if solicitud.qr_code:
        print(f"\n🎯 URL de Aprobación:")
        print(f"   {solicitud.qr_url}")
        print(f"\n📱 Para aprobar, escanea el QR o visita:")
        print(f"   Origen: {solicitud.qr_url}aprobar-origen/")
        print(f"   Destino: {solicitud.qr_url}aprobar-destino/")
    
    print("="*60)
    print("\n✅ Prueba completada exitosamente!")
    
    return solicitud

if __name__ == '__main__':
    try:
        solicitud = test_qr_generation()
    except Exception as e:
        print(f"\n❌ Error durante la prueba: {str(e)}")
        import traceback
        traceback.print_exc()
