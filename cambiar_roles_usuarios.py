#!/usr/bin/env python
"""
Script para cambiar los roles de los usuarios:
- admin → ADMIN
- admin2 → OPERADOR
"""

import os
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from accounts.models import CustomUser

def cambiar_roles():
    print("=" * 60)
    print("CAMBIO DE ROLES DE USUARIOS")
    print("=" * 60)
    print()
    
    # Cambiar admin a ADMIN
    try:
        admin_user = CustomUser.objects.get(username='admin')
        admin_user.role = 'ADMIN'
        admin_user.save()
        print(f"✅ Usuario 'admin' → Rol: {admin_user.role}")
    except CustomUser.DoesNotExist:
        print("❌ Usuario 'admin' no encontrado")
    
    # Cambiar admin2 a OPERADOR
    try:
        admin2_user = CustomUser.objects.get(username='admin2')
        admin2_user.role = 'OPERADOR'
        admin2_user.save()
        print(f"✅ Usuario 'admin2' → Rol: {admin2_user.role}")
    except CustomUser.DoesNotExist:
        print("❌ Usuario 'admin2' no encontrado")
    
    print()
    print("=" * 60)
    print("USUARIOS ACTUALES:")
    print("=" * 60)
    
    usuarios = CustomUser.objects.all()
    for usuario in usuarios:
        print(f"  • {usuario.username}: {usuario.role}")
    
    print()
    print("✅ Cambio de roles completado")

if __name__ == '__main__':
    cambiar_roles()
