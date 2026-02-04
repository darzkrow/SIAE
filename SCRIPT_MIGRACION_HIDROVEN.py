#!/usr/bin/env python
"""
Script de migración de datos para la nueva estructura organizacional de Hidroven.
Este script migra de la estructura antigua (OrganizacionCentral -> Sucursal -> Acueducto)
a la nueva estructura (Empresa -> Vicepresidencia -> UnidadOrganizacional -> Acueducto).
"""

import os
import sys
import django
from django.db import transaction
from django.contrib.auth import get_user_model
from datetime import datetime

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

# Importar modelos
from institucion.models import OrganizacionCentral, Sucursal, Acueducto
from nuevos_modelos import (
    Empresa, Vicepresidencia, UnidadOrganizacional, 
    AcueductoNuevo, MigracionOrganizacional
)

User = get_user_model()

class MigradorHidroven:
    """Clase principal para manejar la migración organizacional"""
    
    def __init__(self):
        self.usuario_sistema = self._obtener_usuario_sistema()
        self.empresa_hidroven = None
        self.vicepresidencias = {}
        self.mapeo_migracion = {}
        
    def _obtener_usuario_sistema(self):
        """Obtiene o crea un usuario del sistema para la migración"""
        usuario, created = User.objects.get_or_create(
            username='sistema_migracion',
            defaults={
                'email': 'sistema@hidroven.gob.ve',
                'first_name': 'Sistema',
                'last_name': 'Migración',
                'is_staff': True,
                'is_active': True
            }
        )
        if created:
            print(f"✅ Usuario del sistema creado: {usuario.username}")
        return usuario
    
    def crear_empresa_hidroven(self):
        """Crea la empresa principal Hidroven"""
        print("\n🏢 Creando empresa Hidroven...")
        
        # Buscar un usuario admin para asignar como presidente
        presidente = User.objects.filter(
            is_superuser=True
        ).first() or self.usuario_sistema
        
        self.empresa_hidroven, created = Empresa.objects.get_or_create(
            nombre='Hidroven',
            defaults={
                'rif': 'G-20000000-0',  # RIF ejemplo
                'presidente': presidente,
                'direccion': 'Caracas, Venezuela',
                'telefono': '+58-212-0000000',
                'email': 'info@hidroven.gob.ve',
                'activa': True,
                'creado_por': self.usuario_sistema
            }
        )
        
        if created:
            print(f"✅ Empresa creada: {self.empresa_hidroven.nombre}")
        else:
            print(f"ℹ️  Empresa ya existe: {self.empresa_hidroven.nombre}")
        
        return self.empresa_hidroven
    
    def crear_vicepresidencias(self):
        """Crea las tres vicepresidencias de Hidroven"""
        print("\n🏛️ Creando vicepresidencias...")
        
        vicepresidencias_config = [
            {
                'tipo': 'COMERCIALIZACION',
                'nombre': 'Vicepresidencia de Comercialización',
                'codigo': 'VP-COM',
                'descripcion': 'Responsable de la comercialización y atención al cliente'
            },
            {
                'tipo': 'OPERACIONES',
                'nombre': 'Vicepresidencia de Operaciones Hídricas',
                'codigo': 'VP-OPE',
                'descripcion': 'Responsable de las operaciones técnicas y mantenimiento'
            },
            {
                'tipo': 'ADMINISTRATIVA',
                'nombre': 'Vicepresidencia Administrativa',
                'codigo': 'VP-ADM',
                'descripcion': 'Responsable de la administración y recursos humanos'
            }
        ]
        
        for config in vicepresidencias_config:
            # Buscar un usuario para asignar como vicepresidente
            vicepresidente = User.objects.filter(
                is_staff=True
            ).exclude(
                id=self.empresa_hidroven.presidente.id
            ).first() or self.usuario_sistema
            
            vp, created = Vicepresidencia.objects.get_or_create(
                empresa=self.empresa_hidroven,
                tipo=config['tipo'],
                defaults={
                    'nombre': config['nombre'],
                    'codigo': config['codigo'],
                    'vicepresidente': vicepresidente,
                    'descripcion': config['descripcion'],
                    'activa': True,
                    'creado_por': self.usuario_sistema
                }
            )
            
            self.vicepresidencias[config['tipo']] = vp
            
            if created:
                print(f"✅ Vicepresidencia creada: {vp.nombre}")
            else:
                print(f"ℹ️  Vicepresidencia ya existe: {vp.nombre}")
    
    def mapear_organizaciones_antiguas(self):
        """Mapea las organizaciones centrales antiguas a vicepresidencias"""
        print("\n🗺️ Mapeando organizaciones antiguas...")
        
        # Estrategia de mapeo basada en nombres/características
        mapeo_estrategico = {
            # Palabras clave para identificar el tipo de organización
            'comercial': 'COMERCIALIZACION',
            'comercio': 'COMERCIALIZACION',
            'ventas': 'COMERCIALIZACION',
            'cliente': 'COMERCIALIZACION',
            'operacion': 'OPERACIONES',
            'operativo': 'OPERACIONES',
            'tecnico': 'OPERACIONES',
            'mantenimiento': 'OPERACIONES',
            'produccion': 'OPERACIONES',
            'hidrico': 'OPERACIONES',
            'agua': 'OPERACIONES',
            'admin': 'ADMINISTRATIVA',
            'administrativo': 'ADMINISTRATIVA',
            'recursos': 'ADMINISTRATIVA',
            'finanzas': 'ADMINISTRATIVA',
            'contable': 'ADMINISTRATIVA'
        }
        
        organizaciones = OrganizacionCentral.objects.all()
        
        for org in organizaciones:
            # Determinar vicepresidencia basada en el nombre
            vp_tipo = 'OPERACIONES'  # Por defecto, operaciones (más común)
            
            nombre_lower = org.nombre.lower()
            for palabra_clave, tipo_vp in mapeo_estrategico.items():
                if palabra_clave in nombre_lower:
                    vp_tipo = tipo_vp
                    break
            
            self.mapeo_migracion[org.id] = {
                'organizacion': org,
                'vicepresidencia_tipo': vp_tipo,
                'vicepresidencia': self.vicepresidencias[vp_tipo]
            }
            
            print(f"📍 {org.nombre} -> {self.vicepresidencias[vp_tipo].nombre}")
    
    def migrar_sucursales_a_unidades(self):
        """Migra sucursales a unidades organizacionales"""
        print("\n🏢 Migrando sucursales a unidades organizacionales...")
        
        for org_id, mapeo in self.mapeo_migracion.items():
            org = mapeo['organizacion']
            vp = mapeo['vicepresidencia']
            
            sucursales = Sucursal.objects.filter(organizacion_central=org)
            
            for sucursal in sucursales:
                # Determinar tipo de unidad basado en el nombre
                tipo_unidad = self._determinar_tipo_unidad(sucursal.nombre)
                
                # Buscar responsable
                responsable = User.objects.filter(
                    is_staff=True
                ).first() or self.usuario_sistema
                
                # Crear unidad organizacional
                unidad, created = UnidadOrganizacional.objects.get_or_create(
                    vicepresidencia=vp,
                    codigo=f"{vp.codigo}-{sucursal.codigo or sucursal.id}",
                    defaults={
                        'tipo': tipo_unidad,
                        'nombre': sucursal.nombre,
                        'responsable': responsable,
                        'direccion': sucursal.direccion,
                        'telefono': sucursal.telefono,
                        'activa': True,
                        'creado_por': self.usuario_sistema
                    }
                )
                
                # Actualizar mapeo
                self.mapeo_migracion[org_id][f'sucursal_{sucursal.id}'] = {
                    'sucursal_antigua': sucursal,
                    'unidad_nueva': unidad
                }
                
                if created:
                    print(f"✅ Unidad creada: {unidad.nombre} en {vp.codigo}")
                else:
                    print(f"ℹ️  Unidad ya existe: {unidad.nombre}")
    
    def _determinar_tipo_unidad(self, nombre):
        """Determina el tipo de unidad organizacional basado en el nombre"""
        nombre_lower = nombre.lower()
        
        if any(palabra in nombre_lower for palabra in ['direccion', 'director']):
            return 'DIRECCION'
        elif any(palabra in nombre_lower for palabra in ['gerencia', 'gerente']):
            return 'GERENCIA'
        elif any(palabra in nombre_lower for palabra in ['coordinacion', 'coordinador']):
            return 'COORDINACION'
        elif any(palabra in nombre_lower for palabra in ['departamento', 'depto']):
            return 'DEPARTAMENTO'
        elif any(palabra in nombre_lower for palabra in ['division', 'div']):
            return 'DIVISION'
        elif any(palabra in nombre_lower for palabra in ['oficina', 'of']):
            return 'OFICINA'
        else:
            return 'GERENCIA'  # Por defecto
    
    def migrar_acueductos(self):
        """Migra acueductos al nuevo modelo"""
        print("\n💧 Migrando acueductos...")
        
        for org_id, mapeo in self.mapeo_migracion.items():
            org = mapeo['organizacion']
            
            # Obtener todas las sucursales de esta organización
            sucursales = Sucursal.objects.filter(organizacion_central=org)
            
            for sucursal in sucursales:
                if f'sucursal_{sucursal.id}' not in mapeo:
                    continue
                    
                unidad_nueva = mapeo[f'sucursal_{sucursal.id}']['unidad_nueva']
                acueductos = Acueducto.objects.filter(sucursal=sucursal)
                
                for acueducto in acueductos:
                    # Determinar tipo de sistema
                    tipo_sistema = self._determinar_tipo_sistema(acueducto.nombre)
                    
                    # Buscar responsable operativo
                    responsable = User.objects.filter(
                        is_staff=True
                    ).first() or self.usuario_sistema
                    
                    # Crear nuevo acueducto
                    acueducto_nuevo, created = AcueductoNuevo.objects.get_or_create(
                        unidad_organizacional=unidad_nueva,
                        codigo=f"{unidad_nueva.codigo}-{acueducto.codigo or acueducto.id}",
                        defaults={
                            'tipo_sistema': tipo_sistema,
                            'nombre': acueducto.nombre,
                            'responsable_operativo': responsable,
                            'ubicacion': acueducto.ubicacion,
                            'activo': True,
                            'creado_por': self.usuario_sistema
                        }
                    )
                    
                    # Registrar migración
                    MigracionOrganizacional.objects.get_or_create(
                        organizacion_central_antigua=org,
                        sucursal_antigua=sucursal,
                        acueducto_antiguo=acueducto,
                        defaults={
                            'empresa_nueva': self.empresa_hidroven,
                            'vicepresidencia_nueva': mapeo['vicepresidencia'],
                            'unidad_organizacional_nueva': unidad_nueva,
                            'acueducto_nuevo': acueducto_nuevo,
                            'migrado_por': self.usuario_sistema,
                            'notas': f'Migración automática desde {org.nombre}',
                            'exitosa': True
                        }
                    )
                    
                    if created:
                        print(f"✅ Acueducto migrado: {acueducto_nuevo.nombre}")
                    else:
                        print(f"ℹ️  Acueducto ya migrado: {acueducto_nuevo.nombre}")
    
    def _determinar_tipo_sistema(self, nombre):
        """Determina el tipo de sistema basado en el nombre"""
        nombre_lower = nombre.lower()
        
        if any(palabra in nombre_lower for palabra in ['planta', 'tratamiento', 'potabilizadora']):
            return 'PLANTA'
        elif any(palabra in nombre_lower for palabra in ['bombeo', 'bomba', 'estacion']):
            return 'BOMBEO'
        elif any(palabra in nombre_lower for palabra in ['embalse', 'represa', 'dique']):
            return 'EMBALSE'
        elif any(palabra in nombre_lower for palabra in ['pozo', 'perforacion']):
            return 'POZO'
        else:
            return 'ACUEDUCTO'  # Por defecto
    
    def generar_reporte_migracion(self):
        """Genera un reporte de la migración realizada"""
        print("\n📊 Generando reporte de migración...")
        
        total_migraciones = MigracionOrganizacional.objects.count()
        migraciones_exitosas = MigracionOrganizacional.objects.filter(exitosa=True).count()
        
        print(f"\n{'='*50}")
        print(f"📋 REPORTE DE MIGRACIÓN HIDROVEN")
        print(f"{'='*50}")
        print(f"📅 Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"👤 Usuario: {self.usuario_sistema.username}")
        print(f"\n🏢 EMPRESA CREADA:")
        print(f"   • {self.empresa_hidroven.nombre} (RIF: {self.empresa_hidroven.rif})")
        print(f"   • Presidente: {self.empresa_hidroven.presidente.get_full_name() or self.empresa_hidroven.presidente.username}")
        
        print(f"\n🏛️ VICEPRESIDENCIAS CREADAS:")
        for vp in self.vicepresidencias.values():
            unidades_count = vp.unidades_organizacionales.count()
            acueductos_count = sum(u.acueductos.count() for u in vp.unidades_organizacionales.all())
            print(f"   • {vp.nombre}")
            print(f"     - Código: {vp.codigo}")
            print(f"     - Responsable: {vp.vicepresidente.get_full_name() or vp.vicepresidente.username}")
            print(f"     - Unidades: {unidades_count}")
            print(f"     - Acueductos: {acueductos_count}")
        
        print(f"\n📊 ESTADÍSTICAS DE MIGRACIÓN:")
        print(f"   • Total de migraciones: {total_migraciones}")
        print(f"   • Migraciones exitosas: {migraciones_exitosas}")
        print(f"   • Tasa de éxito: {(migraciones_exitosas/total_migraciones*100):.1f}%" if total_migraciones > 0 else "   • Tasa de éxito: N/A")
        
        print(f"\n✅ Migración completada exitosamente!")
        print(f"{'='*50}")
    
    def ejecutar_migracion_completa(self):
        """Ejecuta la migración completa paso a paso"""
        print("🚀 Iniciando migración organizacional de Hidroven...")
        print("="*60)
        
        try:
            with transaction.atomic():
                # Paso 1: Crear empresa
                self.crear_empresa_hidroven()
                
                # Paso 2: Crear vicepresidencias
                self.crear_vicepresidencias()
                
                # Paso 3: Mapear organizaciones antiguas
                self.mapear_organizaciones_antiguas()
                
                # Paso 4: Migrar sucursales
                self.migrar_sucursales_a_unidades()
                
                # Paso 5: Migrar acueductos
                self.migrar_acueductos()
                
                # Paso 6: Generar reporte
                self.generar_reporte_migracion()
                
        except Exception as e:
            print(f"❌ Error durante la migración: {str(e)}")
            print("🔄 Realizando rollback...")
            raise
    
    def rollback_migracion(self):
        """Revierte la migración (para testing)"""
        print("🔄 Iniciando rollback de migración...")
        
        with transaction.atomic():
            # Eliminar registros de migración
            MigracionOrganizacional.objects.all().delete()
            
            # Eliminar acueductos nuevos
            AcueductoNuevo.objects.all().delete()
            
            # Eliminar unidades organizacionales
            UnidadOrganizacional.objects.all().delete()
            
            # Eliminar vicepresidencias
            Vicepresidencia.objects.all().delete()
            
            # Eliminar empresa
            if self.empresa_hidroven:
                self.empresa_hidroven.delete()
            
            print("✅ Rollback completado")


def main():
    """Función principal del script"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Migración organizacional Hidroven')
    parser.add_argument('--rollback', action='store_true', help='Revertir migración')
    parser.add_argument('--dry-run', action='store_true', help='Simular migración sin cambios')
    
    args = parser.parse_args()
    
    migrador = MigradorHidroven()
    
    if args.rollback:
        migrador.rollback_migracion()
    elif args.dry_run:
        print("🧪 Modo simulación - No se realizarán cambios")
        # Aquí se podría implementar lógica de simulación
    else:
        migrador.ejecutar_migracion_completa()


if __name__ == '__main__':
    main()