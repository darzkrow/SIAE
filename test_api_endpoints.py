#!/usr/bin/env python
"""
Script para probar los nuevos endpoints de la API
"""
import requests
import json

BASE_URL = 'http://localhost:8000/api'

def test_endpoints():
    print("🧪 Probando nuevos endpoints de la API...")
    
    # Primero hacer login para obtener token
    login_data = {
        'username': 'admin',
        'password': 'admin'
    }
    
    try:
        response = requests.post(f'{BASE_URL}/accounts/api-token-auth/', json=login_data)
        if response.status_code == 200:
            token = response.json()['token']
            headers = {'Authorization': f'Token {token}'}
            print("✅ Login exitoso")
        else:
            print("❌ Error en login:", response.text)
            return
    except requests.exceptions.ConnectionError:
        print("❌ No se puede conectar al servidor. ¿Está ejecutándose en localhost:8000?")
        return
    
    # Probar endpoint de perfil de usuario
    print("\n📋 Probando endpoint /api/accounts/me/")
    try:
        response = requests.get(f'{BASE_URL}/accounts/me/', headers=headers)
        if response.status_code == 200:
            user_data = response.json()
            print(f"✅ Perfil de usuario: {user_data['username']} ({user_data['role']})")
        else:
            print("❌ Error en perfil:", response.text)
    except Exception as e:
        print(f"❌ Error: {e}")
    
    # Probar endpoint de auditoría
    print("\n📋 Probando endpoint /api/audits/")
    try:
        response = requests.get(f'{BASE_URL}/audits/', headers=headers)
        if response.status_code == 200:
            audits = response.json()
            print(f"✅ Auditorías: {audits.get('count', len(audits.get('results', audits)))} registros")
        else:
            print("❌ Error en auditorías:", response.text)
    except Exception as e:
        print(f"❌ Error: {e}")
    
    # Probar endpoint de reportes - dashboard stats
    print("\n📋 Probando endpoint /api/reportes/dashboard_stats/")
    try:
        response = requests.get(f'{BASE_URL}/reportes/dashboard_stats/', headers=headers)
        if response.status_code == 200:
            stats = response.json()
            print("✅ Estadísticas del dashboard:")
            for key, value in stats.items():
                print(f"   {key}: {value}")
        else:
            print("❌ Error en estadísticas:", response.text)
    except Exception as e:
        print(f"❌ Error: {e}")
    
    # Probar endpoint de reportes - stock por sucursal
    print("\n📋 Probando endpoint /api/reportes/stock_por_sucursal/")
    try:
        response = requests.get(f'{BASE_URL}/reportes/stock_por_sucursal/', headers=headers)
        if response.status_code == 200:
            stock_data = response.json()
            print(f"✅ Stock por sucursal: {len(stock_data)} sucursales")
            if stock_data:
                print(f"   Ejemplo: {stock_data[0]['nombre']} - Stock total: {stock_data[0]['stock_total']}")
        else:
            print("❌ Error en stock por sucursal:", response.text)
    except Exception as e:
        print(f"❌ Error: {e}")
    
    # Probar endpoint de alertas críticas
    print("\n📋 Probando endpoint /api/reportes/alertas_stock_bajo/")
    try:
        response = requests.get(f'{BASE_URL}/reportes/alertas_stock_bajo/', headers=headers)
        if response.status_code == 200:
            alertas = response.json()
            print(f"✅ Alertas de stock bajo: {len(alertas)} alertas críticas")
        else:
            print("❌ Error en alertas:", response.text)
    except Exception as e:
        print(f"❌ Error: {e}")
    
    # Probar filtros en movimientos
    print("\n📋 Probando filtros en /api/movimientos/")
    try:
        response = requests.get(f'{BASE_URL}/movimientos/?tipo_movimiento=ENTRADA', headers=headers)
        if response.status_code == 200:
            movimientos = response.json()
            count = movimientos.get('count', len(movimientos.get('results', movimientos)))
            print(f"✅ Movimientos filtrados por ENTRADA: {count} registros")
        else:
            print("❌ Error en filtros de movimientos:", response.text)
    except Exception as e:
        print(f"❌ Error: {e}")
    
    print("\n🎉 Pruebas completadas!")

if __name__ == '__main__':
    test_endpoints()