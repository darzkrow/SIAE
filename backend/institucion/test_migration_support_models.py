"""
Unit tests for migration support models.

Tests the MigracionOrganizacional and AcueductoNuevo models to ensure
they work correctly for tracking organizational structure migration.
"""

import pytest
from django.test import TestCase
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.utils import timezone
from django.db import IntegrityError

from .models import (
    # Old structure
    OrganizacionCentral, Sucursal, Acueducto,
    # New structure
    Empresa, Vicepresidencia, UnidadOrganizacional, AlmacenRegional,
    # Migration support
    MigracionOrganizacional, AcueductoNuevo
)

User = get_user_model()


class MigracionOrganizacionalModelTest(TestCase):
    """Test cases for MigracionOrganizacional model"""
    
    def setUp(self):
        """Set up test data"""
        # Create test user
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        
        # Create old structure
        self.org_central = OrganizacionCentral.objects.create(
            nombre='Hidroven Central',
            rif='J-12345678-9'
        )
        
        self.sucursal = Sucursal.objects.create(
            nombre='Sucursal Zulia',
            organizacion_central=self.org_central,
            codigo='SUC-ZUL',
            direccion='Maracaibo, Zulia'
        )
        
        self.acueducto = Acueducto.objects.create(
            nombre='Acueducto Maracaibo',
            sucursal=self.sucursal,
            codigo='ACU-MAR',
            ubicacion='Maracaibo'
        )
        
        # Create new structure
        self.empresa = Empresa.objects.create(
            nombre='Hidroven',
            codigo='HIDROVEN'
        )
        
        self.vicepresidencia = Vicepresidencia.objects.create(
            empresa=self.empresa,
            nombre='VP Operaciones Hídricas',
            codigo='VP-OPE',
            tipo='OPERACIONES_HIDRICAS'
        )
        
        self.unidad_organizacional = UnidadOrganizacional.objects.create(
            vicepresidencia=self.vicepresidencia,
            nombre='Gerencia Regional Zulia',
            codigo='GER-ZUL',
            tipo='GERENCIA'
        )
    
    def test_create_migration_organizacion_central(self):
        """Test creating migration for OrganizacionCentral"""
        migracion = MigracionOrganizacional.crear_migracion_organizacion(
            organizacion_central=self.org_central,
            empresa=self.empresa,
            usuario=self.user
        )
        
        self.assertEqual(migracion.organizacion_central_id, self.org_central.id)
        self.assertEqual(migracion.empresa, self.empresa)
        self.assertEqual(migracion.migrado_por, self.user)
        self.assertEqual(migracion.estado_migracion, 'PENDIENTE')
        self.assertFalse(migracion.validado)
        self.assertTrue(migracion.puede_revertir)
        
        # Check original data snapshot
        self.assertIn('organizacion_central', migracion.datos_originales)
        self.assertEqual(
            migracion.datos_originales['organizacion_central']['nombre'],
            self.org_central.nombre
        )
    
    def test_create_migration_sucursal(self):
        """Test creating migration for Sucursal"""
        migracion = MigracionOrganizacional.crear_migracion_sucursal(
            sucursal=self.sucursal,
            vicepresidencia=self.vicepresidencia,
            usuario=self.user
        )
        
        self.assertEqual(migracion.sucursal_id, self.sucursal.id)
        self.assertEqual(migracion.organizacion_central_id, self.org_central.id)
        self.assertEqual(migracion.vicepresidencia, self.vicepresidencia)
        self.assertEqual(migracion.empresa, self.empresa)
        
        # Check original data snapshot
        self.assertIn('sucursal', migracion.datos_originales)
        self.assertEqual(
            migracion.datos_originales['sucursal']['codigo'],
            self.sucursal.codigo
        )
    
    def test_create_migration_acueducto(self):
        """Test creating migration for Acueducto"""
        migracion = MigracionOrganizacional.crear_migracion_acueducto(
            acueducto=self.acueducto,
            unidad_organizacional=self.unidad_organizacional,
            usuario=self.user
        )
        
        self.assertEqual(migracion.acueducto_id, self.acueducto.id)
        self.assertEqual(migracion.sucursal_id, self.sucursal.id)
        self.assertEqual(migracion.organizacion_central_id, self.org_central.id)
        self.assertEqual(migracion.unidad_organizacional, self.unidad_organizacional)
        self.assertEqual(migracion.vicepresidencia, self.vicepresidencia)
        self.assertEqual(migracion.empresa, self.empresa)
        
        # Check original data snapshot
        self.assertIn('acueducto', migracion.datos_originales)
        self.assertEqual(
            migracion.datos_originales['acueducto']['ubicacion'],
            self.acueducto.ubicacion
        )
    
    def test_migration_status_workflow(self):
        """Test migration status workflow"""
        migracion = MigracionOrganizacional.objects.create(
            organizacion_central_id=self.org_central.id,
            empresa=self.empresa,
            migrado_por=self.user
        )
        
        # Initial state
        self.assertEqual(migracion.estado_migracion, 'PENDIENTE')
        self.assertFalse(migracion.validado)
        
        # Mark as completed
        migracion.marcar_como_completada(self.user)
        migracion.refresh_from_db()
        self.assertEqual(migracion.estado_migracion, 'COMPLETADA')
        
        # Validate migration
        migracion.validar_migracion(self.user)
        migracion.refresh_from_db()
        self.assertTrue(migracion.validado)
        self.assertEqual(migracion.validado_por, self.user)
        self.assertIsNotNone(migracion.fecha_validacion)
        
        # Revert migration
        migracion.revertir_migracion(self.user, 'Test reversion')
        migracion.refresh_from_db()
        self.assertEqual(migracion.estado_migracion, 'REVERTIDA')
        self.assertEqual(migracion.revertido_por, self.user)
        self.assertIsNotNone(migracion.fecha_reversion)
        self.assertIn('Test reversion', migracion.notas)
    
    def test_migration_error_handling(self):
        """Test migration error and warning handling"""
        migracion = MigracionOrganizacional.objects.create(
            organizacion_central_id=self.org_central.id,
            empresa=self.empresa,
            migrado_por=self.user
        )
        
        # Add error
        migracion.agregar_error('Test error message')
        migracion.refresh_from_db()
        self.assertEqual(len(migracion.errores), 1)
        self.assertEqual(migracion.errores[0]['mensaje'], 'Test error message')
        
        # Add warning
        migracion.agregar_warning('Test warning message')
        migracion.refresh_from_db()
        self.assertEqual(len(migracion.warnings), 1)
        self.assertEqual(migracion.warnings[0]['mensaje'], 'Test warning message')
        
        # Mark as failed
        migracion.marcar_como_fallida(['Critical error'])
        migracion.refresh_from_db()
        self.assertEqual(migracion.estado_migracion, 'FALLIDA')
        self.assertIn('Critical error', migracion.errores)
    
    def test_migration_validation_constraints(self):
        """Test migration model validation constraints"""
        # Test that at least one old reference is required
        with self.assertRaises(ValidationError):
            migracion = MigracionOrganizacional(
                empresa=self.empresa,
                migrado_por=self.user
            )
            migracion.full_clean()
        
        # Test that completed migrations need new references
        with self.assertRaises(ValidationError):
            migracion = MigracionOrganizacional(
                organizacion_central_id=self.org_central.id,
                estado_migracion='COMPLETADA',
                migrado_por=self.user
            )
            migracion.full_clean()
    
    def test_migration_display_methods(self):
        """Test migration display methods"""
        migracion = MigracionOrganizacional.objects.create(
            organizacion_central_id=self.org_central.id,
            sucursal_id=self.sucursal.id,
            acueducto_id=self.acueducto.id,
            empresa=self.empresa,
            vicepresidencia=self.vicepresidencia,
            unidad_organizacional=self.unidad_organizacional,
            migrado_por=self.user
        )
        
        # Test old reference display (should show most specific)
        old_display = migracion.get_old_reference_display()
        self.assertIn('Acueducto', old_display)
        self.assertIn(self.acueducto.nombre, old_display)
        
        # Test new reference display (should show most specific)
        new_display = migracion.get_new_reference_display()
        self.assertIn('Unidad', new_display)
        self.assertIn(self.unidad_organizacional.nombre, new_display)
        
        # Test string representation
        str_repr = str(migracion)
        self.assertIn('Migración:', str_repr)
        self.assertIn('→', str_repr)
    
    def test_migration_class_methods(self):
        """Test migration class methods for querying"""
        # Create migrations with different states
        MigracionOrganizacional.objects.create(
            organizacion_central_id=self.org_central.id,
            empresa=self.empresa,
            migrado_por=self.user,
            estado_migracion='PENDIENTE'
        )
        
        MigracionOrganizacional.objects.create(
            sucursal_id=self.sucursal.id,
            vicepresidencia=self.vicepresidencia,
            migrado_por=self.user,
            estado_migracion='COMPLETADA'
        )
        
        MigracionOrganizacional.objects.create(
            acueducto_id=self.acueducto.id,
            unidad_organizacional=self.unidad_organizacional,
            migrado_por=self.user,
            estado_migracion='FALLIDA'
        )
        
        # Test query methods
        pendientes = MigracionOrganizacional.obtener_migraciones_pendientes()
        self.assertEqual(pendientes.count(), 1)
        
        completadas = MigracionOrganizacional.obtener_migraciones_completadas()
        self.assertEqual(completadas.count(), 1)
        
        fallidas = MigracionOrganizacional.obtener_migraciones_fallidas()
        self.assertEqual(fallidas.count(), 1)
    
    def test_migration_integrity_validation(self):
        """Test migration integrity validation"""
        # Create some migrations
        MigracionOrganizacional.objects.create(
            organizacion_central_id=self.org_central.id,
            empresa=self.empresa,
            migrado_por=self.user,
            estado_migracion='COMPLETADA'
        )
        
        # Run integrity validation
        resultado = MigracionOrganizacional.validar_integridad_migracion()
        
        self.assertIn('errores', resultado)
        self.assertIn('warnings', resultado)
        self.assertIn('total_migraciones', resultado)
        self.assertIn('completadas', resultado)
        self.assertIn('pendientes', resultado)
        self.assertIn('fallidas', resultado)
        
        self.assertEqual(resultado['total_migraciones'], 1)
        self.assertEqual(resultado['completadas'], 1)


class AcueductoNuevoModelTest(TestCase):
    """Test cases for AcueductoNuevo model"""
    
    def setUp(self):
        """Set up test data"""
        # Create test user
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        
        # Create new structure
        self.empresa = Empresa.objects.create(
            nombre='Hidroven',
            codigo='HIDROVEN'
        )
        
        self.vicepresidencia = Vicepresidencia.objects.create(
            empresa=self.empresa,
            nombre='VP Operaciones Hídricas',
            codigo='VP-OPE',
            tipo='OPERACIONES_HIDRICAS'
        )
        
        self.unidad_organizacional = UnidadOrganizacional.objects.create(
            vicepresidencia=self.vicepresidencia,
            nombre='Gerencia Regional Zulia',
            codigo='GER-ZUL',
            tipo='GERENCIA'
        )
    
    def test_create_acueducto_nuevo(self):
        """Test creating new acueducto"""
        acueducto = AcueductoNuevo.objects.create(
            unidad_organizacional=self.unidad_organizacional,
            tipo_sistema='ACUEDUCTO',
            nombre='Acueducto Maracaibo Norte',
            codigo='ACU-MAR-N',
            responsable_operativo=self.user,
            ubicacion='Maracaibo Norte',
            capacidad_produccion=1500.50,
            poblacion_servida=250000,
            creado_por=self.user
        )
        
        self.assertEqual(acueducto.nombre, 'Acueducto Maracaibo Norte')
        self.assertEqual(acueducto.codigo, 'ACU-MAR-N')
        self.assertEqual(acueducto.tipo_sistema, 'ACUEDUCTO')
        self.assertEqual(acueducto.unidad_organizacional, self.unidad_organizacional)
        self.assertEqual(acueducto.responsable_operativo, self.user)
        self.assertTrue(acueducto.activo)
        self.assertIsNotNone(acueducto.fecha_creacion)
    
    def test_acueducto_nuevo_properties(self):
        """Test acueducto nuevo properties"""
        acueducto = AcueductoNuevo.objects.create(
            unidad_organizacional=self.unidad_organizacional,
            nombre='Test Acueducto',
            codigo='TEST-001',
            responsable_operativo=self.user
        )
        
        # Test property methods
        self.assertEqual(acueducto.vicepresidencia, self.vicepresidencia)
        self.assertEqual(acueducto.empresa, self.empresa)
        
        # Test organizational path
        ruta = acueducto.ruta_organizacional_completa
        self.assertIn(self.empresa.nombre, ruta)
        self.assertIn(self.vicepresidencia.nombre, ruta)
        self.assertIn(self.unidad_organizacional.nombre, ruta)
        self.assertIn(acueducto.nombre, ruta)
        
        # Test full path
        full_path = acueducto.get_full_path()
        self.assertIn('→', full_path)
        self.assertIn(acueducto.nombre, full_path)
    
    def test_acueducto_nuevo_validation(self):
        """Test acueducto nuevo validation"""
        # Create first acueducto
        AcueductoNuevo.objects.create(
            unidad_organizacional=self.unidad_organizacional,
            nombre='First Acueducto',
            codigo='UNIQUE-001',
            responsable_operativo=self.user
        )
        
        # Try to create second acueducto with same codigo in same unidad
        with self.assertRaises(ValidationError):
            acueducto = AcueductoNuevo(
                unidad_organizacional=self.unidad_organizacional,
                nombre='Second Acueducto',
                codigo='UNIQUE-001',  # Same codigo
                responsable_operativo=self.user
            )
            acueducto.full_clean()
    
    def test_acueducto_nuevo_string_representation(self):
        """Test string representation"""
        acueducto = AcueductoNuevo.objects.create(
            unidad_organizacional=self.unidad_organizacional,
            nombre='Test Acueducto',
            codigo='TEST-001',
            responsable_operativo=self.user
        )
        
        str_repr = str(acueducto)
        self.assertIn(acueducto.nombre, str_repr)
        self.assertIn(self.unidad_organizacional.codigo, str_repr)
    
    def test_acueducto_nuevo_different_tipos(self):
        """Test creating acueductos with different system types"""
        tipos = ['ACUEDUCTO', 'PLANTA_TRATAMIENTO', 'SISTEMA_BOMBEO', 'EMBALSE', 'POZO']
        
        for i, tipo in enumerate(tipos):
            acueducto = AcueductoNuevo.objects.create(
                unidad_organizacional=self.unidad_organizacional,
                tipo_sistema=tipo,
                nombre=f'Sistema {tipo} {i+1}',
                codigo=f'{tipo[:3]}-{i+1:03d}',
                responsable_operativo=self.user
            )
            
            self.assertEqual(acueducto.tipo_sistema, tipo)
            self.assertEqual(acueducto.get_tipo_sistema_display(), dict(AcueductoNuevo.TIPO_SISTEMA_CHOICES)[tipo])


class MigrationIntegrationTest(TestCase):
    """Integration tests for migration support models"""
    
    def setUp(self):
        """Set up test data"""
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        
        # Create complete old structure
        self.org_central = OrganizacionCentral.objects.create(
            nombre='Hidroven Central',
            rif='J-12345678-9'
        )
        
        self.sucursal = Sucursal.objects.create(
            nombre='Sucursal Zulia',
            organizacion_central=self.org_central,
            codigo='SUC-ZUL'
        )
        
        self.acueducto_old = Acueducto.objects.create(
            nombre='Acueducto Maracaibo',
            sucursal=self.sucursal,
            codigo='ACU-MAR'
        )
        
        # Create complete new structure
        self.empresa = Empresa.objects.create(
            nombre='Hidroven',
            codigo='HIDROVEN'
        )
        
        self.vicepresidencia = Vicepresidencia.objects.create(
            empresa=self.empresa,
            nombre='VP Operaciones Hídricas',
            codigo='VP-OPE',
            tipo='OPERACIONES_HIDRICAS'
        )
        
        self.unidad_organizacional = UnidadOrganizacional.objects.create(
            vicepresidencia=self.vicepresidencia,
            nombre='Gerencia Regional Zulia',
            codigo='GER-ZUL',
            tipo='GERENCIA'
        )
        
        self.acueducto_new = AcueductoNuevo.objects.create(
            unidad_organizacional=self.unidad_organizacional,
            nombre='Acueducto Maracaibo Nuevo',
            codigo='ACU-MAR-NEW',
            responsable_operativo=self.user
        )
    
    def test_complete_migration_workflow(self):
        """Test complete migration workflow from old to new structure"""
        # Create migration for acueducto
        migracion = MigracionOrganizacional.crear_migracion_acueducto(
            acueducto=self.acueducto_old,
            unidad_organizacional=self.unidad_organizacional,
            usuario=self.user
        )
        
        # Link to new acueducto
        migracion.acueducto_nuevo = self.acueducto_new
        migracion.save()
        
        # Complete migration workflow
        migracion.marcar_como_completada(self.user)
        migracion.validar_migracion(self.user)
        
        # Verify complete mapping
        self.assertEqual(migracion.acueducto_id, self.acueducto_old.id)
        self.assertEqual(migracion.sucursal_id, self.sucursal.id)
        self.assertEqual(migracion.organizacion_central_id, self.org_central.id)
        self.assertEqual(migracion.acueducto_nuevo, self.acueducto_new)
        self.assertEqual(migracion.unidad_organizacional, self.unidad_organizacional)
        self.assertEqual(migracion.vicepresidencia, self.vicepresidencia)
        self.assertEqual(migracion.empresa, self.empresa)
        
        # Verify status
        self.assertEqual(migracion.estado_migracion, 'COMPLETADA')
        self.assertTrue(migracion.validado)
        
        # Verify data preservation
        self.assertIn('acueducto', migracion.datos_originales)
        original_data = migracion.datos_originales['acueducto']
        self.assertEqual(original_data['nombre'], self.acueducto_old.nombre)
        self.assertEqual(original_data['codigo'], self.acueducto_old.codigo)
    
    def test_migration_rollback_scenario(self):
        """Test migration rollback scenario"""
        # Create and complete migration
        migracion = MigracionOrganizacional.crear_migracion_sucursal(
            sucursal=self.sucursal,
            vicepresidencia=self.vicepresidencia,
            usuario=self.user
        )
        
        migracion.marcar_como_completada(self.user)
        migracion.validar_migracion(self.user)
        
        # Simulate need for rollback
        migracion.revertir_migracion(self.user, 'Data integrity issue found')
        
        # Verify rollback
        self.assertEqual(migracion.estado_migracion, 'REVERTIDA')
        self.assertIsNotNone(migracion.fecha_reversion)
        self.assertEqual(migracion.revertido_por, self.user)
        self.assertIn('Data integrity issue found', migracion.notas)
        
        # Verify original data is still available
        self.assertIn('sucursal', migracion.datos_originales)
        original_data = migracion.datos_originales['sucursal']
        self.assertEqual(original_data['nombre'], self.sucursal.nombre)