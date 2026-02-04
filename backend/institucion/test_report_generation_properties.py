"""
Property-based tests for report generation accuracy.

This module contains property-based tests that validate the accuracy and consistency
of report generation functionality in the Hidroven organizational restructuring system.

Requirements tested:
- 12.1: Implement inventory reports grouped by organizational hierarchy
- 12.2: Add asset movement reports with transfer information
- 12.3: Create utilization rate calculations by warehouse and organizational unit
- 12.4: Create summary statistics for each Vicepresidencia

Property tests ensure that report generation is accurate across various input scenarios
and data configurations.
"""

import unittest
from datetime import datetime, timedelta
from decimal import Decimal
from typing import Dict, Any, List

from django.test import TestCase
from django.utils import timezone
from django.contrib.auth import get_user_model
from hypothesis import given, settings, strategies as st
from hypothesis.extra.django import from_model

from accounts.models import CustomUser
from .models import (
    Empresa, Vicepresidencia, UnidadOrganizacional, AlmacenRegional,
    ActivoInventario, SolicitudTraslado, HistorialMovimientoActivo
)
from .services import ReportGenerationService, ReportFilters, ReportData
from inventario.models import ProductoInventario
from catalogo.models import CategoriaProducto, Marca

User = get_user_model()


class ReportGenerationPropertiesTestCase(TestCase):
    """Property-based tests for report generation accuracy"""
    
    def setUp(self):
        """Set up test data"""
        # Create test user
        self.user = CustomUser.objects.create_user(
            username='report_test_user',
            email='report@test.com',
            password='testpass123',
            role='OPERADOR'
        )
        
        # Create organizational hierarchy
        self.empresa = Empresa.objects.create(
            nombre='Hidroven Test',
            codigo='HVT',
            descripcion='Test company'
        )
        
        self.vicepresidencia = Vicepresidencia.objects.create(
            nombre='VP Test',
            codigo='VPT',
            empresa=self.empresa,
            descripcion='Test VP'
        )
        
        self.unidad = UnidadOrganizacional.objects.create(
            nombre='Unidad Test',
            codigo='UT',
            vicepresidencia=self.vicepresidencia,
            descripcion='Test unit'
        )
        
        # Create warehouses
        self.warehouse1 = AlmacenRegional.objects.create(
            nombre='Almacén Zulia Test',
            prefijo='ZUL',
            unidad_organizacional=self.unidad,
            capacidad_maxima=1000,
            ubicacion='Maracaibo'
        )
        
        self.warehouse2 = AlmacenRegional.objects.create(
            nombre='Almacén Caracas Test',
            prefijo='CAR',
            unidad_organizacional=self.unidad,
            capacidad_maxima=800,
            ubicacion='Caracas'
        )
        
        # Create product categories and products
        self.categoria = CategoriaProducto.objects.create(
            nombre='Bombas Test',
            descripcion='Test category'
        )
        
        self.marca = Marca.objects.create(
            nombre='Test Brand',
            descripcion='Test brand'
        )
        
        self.producto = ProductoInventario.objects.create(
            nombre='Bomba Test',
            categoria=self.categoria,
            marca=self.marca,
            precio_unitario=Decimal('1000.00'),
            descripcion='Test product'
        )
    
    def get_report_filters_strategy(self):
        """Strategy for generating ReportFilters instances"""
        base_time = timezone.now()
        
        @st.composite
        def report_filters(draw):
            # Generate date range
            days_back = draw(st.integers(min_value=1, max_value=365))
            start_date = base_time - timedelta(days=days_back)
            end_date = draw(st.one_of(
                st.none(),
                st.datetimes(
                    min_value=start_date,
                    max_value=base_time
                )
            ))
            
            return ReportFilters(
                fecha_inicio=start_date,
                fecha_fin=end_date,
                empresa_id=draw(st.one_of(st.none(), st.just(self.empresa.id))),
                vicepresidencia_id=draw(st.one_of(st.none(), st.just(self.vicepresidencia.id))),
                unidad_organizacional_id=draw(st.one_of(st.none(), st.just(self.unidad.id)))
            )
        
        return report_filters
    
    def get_asset_data_strategy(self):
        """Strategy for generating asset test data"""
        @st.composite
        def asset_data(draw):
            asset_type = draw(st.sampled_from(['BOMBA', 'MOTOR', 'VALVULA', 'MEDIDOR']))
            estado = draw(st.sampled_from(['EN_ALMACEN', 'EN_USO', 'EN_TRANSITO', 'MANTENIMIENTO']))
            warehouse = draw(st.sampled_from([self.warehouse1, self.warehouse2]))
            
            return {
                'tipo_activo': asset_type,
                'estado': estado,
                'almacen_actual': warehouse,
                'producto_inventario': self.producto,
                'valor_unitario': draw(st.decimals(min_value=100, max_value=10000, places=2)),
                'numero_serie': draw(st.text(min_size=5, max_size=20, alphabet=st.characters(whitelist_categories=('Lu', 'Ll', 'Nd')))),
                'descripcion': draw(st.text(min_size=10, max_size=100)),
                'creado_por': self.user
            }
        
        return asset_data
    
    @given(st.data())
    @settings(max_examples=50, deadline=30000)
    def test_property_16_inventory_report_accuracy(self, data):
        """
        **Feature: hidroven-organizational-restructuring, Property 16: Report Generation Accuracy**
        **Validates: Requirements 12.1, 12.2, 12.3, 12.4**
        
        Property: Inventory reports must accurately reflect the actual asset data
        - Total counts must match database queries
        - Grouping by organizational hierarchy must be consistent
        - Calculations must be mathematically correct
        """
        print("Testing inventory report accuracy")
        
        # Generate test assets
        num_assets = data.draw(st.integers(min_value=1, max_value=20))
        assets = []
        
        for i in range(num_assets):
            asset_data = data.draw(self.get_asset_data_strategy()())
            asset = ActivoInventario.objects.create(**asset_data)
            assets.append(asset)
        
        # Generate report filters
        filters = data.draw(self.get_report_filters_strategy()())
        
        try:
            # Generate inventory report
            report = ReportGenerationService.generate_inventory_report(filters)
            
            # Verify report structure
            self.assertIsNotNone(report)
            self.assertIn('data', report.__dict__)
            self.assertIn('statistics', report.__dict__)
            
            # Verify data accuracy
            report_data = report.data
            
            # Check total asset count accuracy
            if 'summary' in report_data:
                reported_total = report_data['summary'].get('total_assets', 0)
                
                # Calculate expected total from database
                query = ActivoInventario.objects.all()
                if filters.fecha_inicio:
                    query = query.filter(fecha_ingreso__gte=filters.fecha_inicio)
                if filters.fecha_fin:
                    query = query.filter(fecha_ingreso__lte=filters.fecha_fin)
                if filters.vicepresidencia_id:
                    query = query.filter(
                        almacen_actual__unidad_organizacional__vicepresidencia_id=filters.vicepresidencia_id
                    )
                
                expected_total = query.count()
                
                # Verify accuracy
                self.assertEqual(
                    reported_total, 
                    expected_total,
                    f"Report total ({reported_total}) doesn't match database count ({expected_total})"
                )
            
            # Verify organizational grouping consistency
            if 'by_vicepresidencia' in report_data:
                vp_data = report_data['by_vicepresidencia']
                
                # Sum of VP totals should equal overall total
                vp_total_sum = sum(vp.get('total_assets', 0) for vp in vp_data.values())
                overall_total = report_data.get('summary', {}).get('total_assets', 0)
                
                if overall_total > 0:  # Only check if we have data
                    self.assertEqual(
                        vp_total_sum,
                        overall_total,
                        f"VP totals sum ({vp_total_sum}) doesn't match overall total ({overall_total})"
                    )
            
            # Verify warehouse grouping consistency
            if 'by_warehouse' in report_data:
                warehouse_data = report_data['by_warehouse']
                
                for warehouse_id, warehouse_info in warehouse_data.items():
                    # Verify warehouse exists
                    self.assertTrue(
                        AlmacenRegional.objects.filter(id=warehouse_id).exists(),
                        f"Warehouse {warehouse_id} in report doesn't exist in database"
                    )
                    
                    # Verify asset counts
                    reported_count = warehouse_info.get('total_assets', 0)
                    actual_count = ActivoInventario.objects.filter(
                        almacen_actual_id=warehouse_id
                    ).count()
                    
                    self.assertEqual(
                        reported_count,
                        actual_count,
                        f"Warehouse {warehouse_id} reported count ({reported_count}) doesn't match actual ({actual_count})"
                    )
            
            print(f"✓ Inventory report accuracy validated for {num_assets} assets")
            
        except Exception as e:
            self.fail(f"Report generation failed: {str(e)}")
    
    @given(st.data())
    @settings(max_examples=30, deadline=30000)
    def test_property_16_movement_report_accuracy(self, data):
        """
        **Feature: hidroven-organizational-restructuring, Property 16: Report Generation Accuracy**
        **Validates: Requirements 12.2, 12.3**
        
        Property: Asset movement reports must accurately reflect transfer history
        - Movement counts must match audit trail records
        - Transfer information must be complete and accurate
        - Date filtering must work correctly
        """
        print("Testing movement report accuracy")
        
        # Create test assets
        num_assets = data.draw(st.integers(min_value=1, max_value=10))
        assets = []
        
        for i in range(num_assets):
            asset_data = data.draw(self.get_asset_data_strategy()())
            asset = ActivoInventario.objects.create(**asset_data)
            assets.append(asset)
        
        # Create movement history
        movements = []
        for asset in assets:
            num_movements = data.draw(st.integers(min_value=0, max_value=5))
            
            for j in range(num_movements):
                movement = HistorialMovimientoActivo.objects.create(
                    activo=asset,
                    tipo_movimiento=data.draw(st.sampled_from(['INGRESO', 'TRASLADO', 'SALIDA'])),
                    almacen_origen=data.draw(st.one_of(st.none(), st.just(self.warehouse1))),
                    almacen_destino=data.draw(st.sampled_from([self.warehouse1, self.warehouse2])),
                    usuario_responsable=self.user,
                    observaciones=data.draw(st.text(min_size=5, max_size=50)),
                    fecha_movimiento=timezone.now() - timedelta(days=data.draw(st.integers(min_value=0, max_value=30)))
                )
                movements.append(movement)
        
        # Generate report filters
        filters = data.draw(self.get_report_filters_strategy()())
        
        try:
            # Generate movement report
            report = ReportGenerationService.generate_movement_report(filters)
            
            # Verify report structure
            self.assertIsNotNone(report)
            self.assertIn('data', report.__dict__)
            
            report_data = report.data
            
            # Verify movement count accuracy
            if 'summary' in report_data:
                reported_movements = report_data['summary'].get('total_movements', 0)
                
                # Calculate expected movements from database
                query = HistorialMovimientoActivo.objects.all()
                if filters.fecha_inicio:
                    query = query.filter(fecha_movimiento__gte=filters.fecha_inicio)
                if filters.fecha_fin:
                    query = query.filter(fecha_movimiento__lte=filters.fecha_fin)
                
                expected_movements = query.count()
                
                self.assertEqual(
                    reported_movements,
                    expected_movements,
                    f"Movement report total ({reported_movements}) doesn't match database count ({expected_movements})"
                )
            
            # Verify movement type grouping
            if 'by_movement_type' in report_data:
                type_data = report_data['by_movement_type']
                
                for movement_type, count in type_data.items():
                    actual_count = HistorialMovimientoActivo.objects.filter(
                        tipo_movimiento=movement_type
                    ).count()
                    
                    self.assertEqual(
                        count,
                        actual_count,
                        f"Movement type {movement_type} count ({count}) doesn't match actual ({actual_count})"
                    )
            
            print(f"✓ Movement report accuracy validated for {len(movements)} movements")
            
        except Exception as e:
            self.fail(f"Movement report generation failed: {str(e)}")
    
    @given(st.data())
    @settings(max_examples=30, deadline=30000)
    def test_property_16_utilization_report_accuracy(self, data):
        """
        **Feature: hidroven-organizational-restructuring, Property 16: Report Generation Accuracy**
        **Validates: Requirements 12.3, 12.4**
        
        Property: Utilization rate calculations must be mathematically correct
        - Utilization percentages must be accurate based on capacity and current inventory
        - Calculations must handle edge cases (empty warehouses, full warehouses)
        - Summary statistics must be consistent across organizational levels
        """
        print("Testing utilization report accuracy")
        
        # Create assets with known distribution
        warehouse_asset_counts = {}
        total_assets = data.draw(st.integers(min_value=0, max_value=50))
        
        for i in range(total_assets):
            warehouse = data.draw(st.sampled_from([self.warehouse1, self.warehouse2]))
            asset_data = data.draw(self.get_asset_data_strategy()())
            asset_data['almacen_actual'] = warehouse
            
            asset = ActivoInventario.objects.create(**asset_data)
            
            warehouse_asset_counts[warehouse.id] = warehouse_asset_counts.get(warehouse.id, 0) + 1
        
        # Generate report filters
        filters = data.draw(self.get_report_filters_strategy()())
        
        try:
            # Generate utilization report
            report = ReportGenerationService.generate_utilization_report(filters)
            
            # Verify report structure
            self.assertIsNotNone(report)
            self.assertIn('data', report.__dict__)
            
            report_data = report.data
            
            # Verify utilization calculations
            if 'warehouse_utilization' in report_data:
                utilization_data = report_data['warehouse_utilization']
                
                for warehouse_id, utilization_info in utilization_data.items():
                    warehouse = AlmacenRegional.objects.get(id=warehouse_id)
                    
                    # Get actual asset count
                    actual_count = ActivoInventario.objects.filter(
                        almacen_actual_id=warehouse_id
                    ).count()
                    
                    # Calculate expected utilization
                    expected_utilization = (actual_count / warehouse.capacidad_maxima) * 100 if warehouse.capacidad_maxima > 0 else 0
                    
                    reported_utilization = utilization_info.get('utilization_percentage', 0)
                    
                    # Allow small floating point differences
                    self.assertAlmostEqual(
                        reported_utilization,
                        expected_utilization,
                        places=2,
                        msg=f"Warehouse {warehouse_id} utilization ({reported_utilization}%) doesn't match expected ({expected_utilization}%)"
                    )
                    
                    # Verify utilization is within valid range
                    self.assertGreaterEqual(
                        reported_utilization,
                        0,
                        f"Utilization percentage cannot be negative: {reported_utilization}%"
                    )
                    
                    self.assertLessEqual(
                        reported_utilization,
                        100,
                        f"Utilization percentage cannot exceed 100%: {reported_utilization}%"
                    )
            
            # Verify summary statistics consistency
            if 'summary' in report_data:
                summary = report_data['summary']
                
                if 'average_utilization' in summary:
                    avg_utilization = summary['average_utilization']
                    
                    # Verify average is within valid range
                    self.assertGreaterEqual(avg_utilization, 0)
                    self.assertLessEqual(avg_utilization, 100)
                    
                    # If we have warehouse data, verify average calculation
                    if 'warehouse_utilization' in report_data:
                        warehouse_utils = [
                            info.get('utilization_percentage', 0)
                            for info in report_data['warehouse_utilization'].values()
                        ]
                        
                        if warehouse_utils:
                            expected_avg = sum(warehouse_utils) / len(warehouse_utils)
                            self.assertAlmostEqual(
                                avg_utilization,
                                expected_avg,
                                places=2,
                                msg=f"Average utilization ({avg_utilization}%) doesn't match calculated average ({expected_avg}%)"
                            )
            
            print(f"✓ Utilization report accuracy validated for {total_assets} assets across warehouses")
            
        except Exception as e:
            self.fail(f"Utilization report generation failed: {str(e)}")
    
    def test_report_generation_edge_cases(self):
        """Test report generation with edge cases"""
        print("Testing report generation edge cases")
        
        # Test with empty database
        empty_filters = ReportFilters(
            fecha_inicio=timezone.now() - timedelta(days=30),
            fecha_fin=timezone.now()
        )
        
        try:
            inventory_report = ReportGenerationService.generate_inventory_report(empty_filters)
            self.assertIsNotNone(inventory_report)
            
            movement_report = ReportGenerationService.generate_movement_report(empty_filters)
            self.assertIsNotNone(movement_report)
            
            utilization_report = ReportGenerationService.generate_utilization_report(empty_filters)
            self.assertIsNotNone(utilization_report)
            
            print("✓ Edge case testing completed successfully")
            
        except Exception as e:
            self.fail(f"Edge case testing failed: {str(e)}")


if __name__ == '__main__':
    unittest.main()