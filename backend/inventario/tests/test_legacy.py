"""
Pruebas unitarias refactorizadas para el sistema de inventario.
"""
from django.test import TestCase
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from decimal import Decimal
from django.utils import timezone
from django.contrib.contenttypes.models import ContentType
from institucion.models import OrganizacionCentral, Sucursal, Acueducto
from geography.models import Ubicacion
from catalogo.models import CategoriaProducto, Marca
from inventario.models import (
    Pipe, PumpAndMotor, Accessory, ChemicalProduct,
    MovimientoInventario,
    StockPipe, StockPumpAndMotor, StockAccessory, StockChemical,
    UnitOfMeasure, Supplier, InventoryAudit, FichaTecnicaMotor
)

User = get_user_model()

# BASE TEST CASE
# ============================================================================
class BaseInventarioTestCase(TestCase):
    """
    Clase base para las pruebas de inventario.
    Configura los datos iniciales una vez para todas las pruebas heredadas.
    """
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        # Crear datos base que no cambian entre pruebas
        cls.organizacion = OrganizacionCentral.objects.create(nombre='Pruebas Corp')
        cls.sucursal_principal = Sucursal.objects.create(nombre='Sucursal Principal', 
                                                         organizacion_central=cls.organizacion)
        cls.sucursal_secundaria = Sucursal.objects.create(nombre='Sucursal Secundaria', 
                                                          organizacion_central=cls.organizacion)

        cls.acueducto_principal = Acueducto.objects.create(nombre='Acueducto Principal', 
                                                           sucursal=cls.sucursal_principal)
        cls.acueducto_secundario = Acueducto.objects.create(nombre='Acueducto Secundario', 
                                                           sucursal=cls.sucursal_secundaria)

        cls.ubicacion_principal = Ubicacion.objects.create(
            nombre='Almacén Principal',
            acueducto=cls.acueducto_principal,
            tipo='ALMACEN'
        )
        cls.ubicacion_secundaria = Ubicacion.objects.create(
            nombre='Almacén Secundario',
            acueducto=cls.acueducto_secundario,
            tipo='ALMACEN'
        )
        
        cls.categoria_tuberia = CategoriaProducto.objects.create(nombre='Tuberías', codigo='TUB')
        cls.categoria_bomba = CategoriaProducto.objects.create(nombre='Bombas y Motores', codigo='BOM') # Requerido por validación
        cls.proveedor = Supplier.objects.create(nombre='Proveedor de Prueba')
        cls.unidad_longitud = UnitOfMeasure.objects.create(nombre='Metro', simbolo='m', tipo='LONGITUD')
        cls.unidad_unitaria = UnitOfMeasure.objects.create(nombre='Unidad', simbolo='u', tipo='UNIDAD') # Añadido
        cls.marca_bomba = Marca.objects.create(nombre='Marca de Prueba') # Añadido para bombas

        # Crear una instancia de Pipe para usar en las pruebas
        cls.pipe_instance = Pipe.objects.create(
            nombre='Tubería PVC 6"',
            sku='TEST-PIPE-001',
            categoria=cls.categoria_tuberia,
            proveedor=cls.proveedor,
            unidad_medida=cls.unidad_longitud,
            material='PVC',
            diametro_nominal=6,
            unidad_diametro='PULGADAS',
            presion_nominal='PN10',
            longitud_unitaria=6.0,
            tipo_union='CAMPANA',
            tipo_uso='POTABLE'      # Corregido de 'PRESION'
        )

class PipeModelTests(BaseInventarioTestCase):
    """Pruebas para el modelo Pipe."""

    def test_crear_pipe(self):
        """Verifica que se pueda crear una instancia de Pipe correctamente."""
        # La instancia `cls.pipe_instance` ya se creó en setUpClass
        self.assertIsNotNone(self.pipe_instance)
        self.assertEqual(Pipe.objects.count(), 1)

        # Crear una nueva para asegurar que no hay conflictos
        pipe = Pipe.objects.create(
            nombre='Tubería de prueba',
            sku='TEST-PIPE-002',
            categoria=self.categoria_tuberia,
            proveedor=self.proveedor,
            unidad_medida=self.unidad_longitud,
            material='PVC',
            diametro_nominal=4,
            unidad_diametro='PULGADAS',
            presion_nominal='PN16',
            longitud_unitaria=3.0,
            tipo_union='ROSCADA',   # Corregido de 'ROSCA'
            tipo_uso='RIEGO'
        )
        self.assertEqual(pipe.nombre, 'Tubería de prueba')
        self.assertTrue(str(pipe).startswith('TEST-PIPE-002'))

    def test_longitud_negativa_invalida(self):
        """Verifica que no se pueda crear una tubería con longitud negativa."""
        with self.assertRaises(ValidationError):
            pipe = Pipe(
                nombre='Tubería Inválida',
                sku='TEST-PIPE-003',
                categoria=self.categoria_tuberia,
                proveedor=self.proveedor,
                unidad_medida=self.unidad_longitud,
                material='PVC',
                diametro_nominal=4,
                unidad_diametro='PULGADAS',
                presion_nominal='PN10',
                longitud_unitaria=-1.0,  # Longitud inválida
                tipo_union='SOLDABLE', # Corregido de 'SOLDADA'
                tipo_uso='SERVIDAS'    # Corregido de 'DRENAJE'
            )
            pipe.full_clean() # La validación se dispara aquí


# ============================================================================
# PUMP AND MOTOR TESTS
# ============================================================================
class PumpAndMotorModelTests(BaseInventarioTestCase):
    """Pruebas para el modelo PumpAndMotor."""

    def test_crear_bomba_y_calculo_kw(self):
        """Verifica la creación de una bomba y el cálculo automático de kW."""
        bomba = PumpAndMotor.objects.create(
            nombre='Bomba Centrífuga 5HP',
            sku='TEST-PUMP-001',
            categoria=self.categoria_tuberia, # Reutilizando categoría por simplicidad
            proveedor=self.proveedor,
            unidad_medida=self.unidad_unitaria,
            tipo_equipo='BOMBA_CENTRIFUGA',
            marca=self.marca_bomba,
            modelo='Modelo-X',
            numero_serie='SN-12345',
            potencia_hp=Decimal('5.0'),
            voltaje=220,
            fases='TRIFASICO'
        )
        self.assertIsNotNone(bomba)
        self.assertEqual(PumpAndMotor.objects.count(), 1)
        
        # Verificar cálculo de potencia en kW
        # 5 HP * 0.7457 = 3.7285
        self.assertEqual(bomba.potencia_kw, Decimal('3.73'))
        self.assertEqual(bomba.get_potencia_display(), f"{bomba.potencia_hp} HP ({bomba.potencia_kw:.2f} kW)")

    def test_potencia_negativa_invalida(self):
        """Verifica que no se pueda crear un equipo con potencia negativa."""
        with self.assertRaises(ValidationError):
            bomba_invalida = PumpAndMotor(
                nombre='Bomba Inválida',
                sku='TEST-PUMP-002',
                categoria=self.categoria_tuberia,
                proveedor=self.proveedor,
                unidad_medida=self.unidad_unitaria,
                tipo_equipo='BOMBA_SUMERGIBLE',
                marca=self.marca_bomba,
                modelo='Modelo-Y',
                numero_serie='SN-54321',
                potencia_hp=Decimal('-1.0'), # Potencia inválida
                voltaje=440,
                fases='TRIFASICO'
            )
            bomba_invalida.full_clean()


# ============================================================================
# ACCESSORY TESTS
# ============================================================================
class AccessoryModelTests(BaseInventarioTestCase):
    """Pruebas para el modelo Accessory."""

    def test_crear_accesorio(self):
        """Verifica la creación de un accesorio."""
        codo = Accessory.objects.create(
            nombre='Codo de 90° PVC',
            sku='TEST-ACC-001',
            categoria=self.categoria_tuberia,
            proveedor=self.proveedor,
            unidad_medida=self.unidad_unitaria,
            tipo_accesorio='CODO',
            material='PVC',
            diametro_entrada=Decimal('4.0'),
            unidad_diametro='PULGADAS',
            presion_trabajo='PN10',
            tipo_conexion='SOLDABLE',
            angulo=90
        )
        self.assertIsNotNone(codo)
        self.assertEqual(Accessory.objects.count(), 1)
        self.assertEqual(codo.get_dimension_display(), '4.0 PULGADAS')

    def test_diametro_negativo_invalido(self):
        """Verifica que no se pueda crear un accesorio con diámetro negativo."""
        with self.assertRaises(ValidationError):
            accesorio_invalido = Accessory(
                nombre='Accesorio Inválido',
                sku='TEST-ACC-002',
                categoria=self.categoria_tuberia,
                proveedor=self.proveedor,
                unidad_medida=self.unidad_unitaria,
                tipo_accesorio='TEE',
                material='HIERRO',
                diametro_entrada=Decimal('-1.0'), # Diámetro inválido
                unidad_diametro='PULGADAS',
                tipo_conexion='ROSCADA'
            )
            accesorio_invalido.full_clean()


# ============================================================================
# STOCK TESTS
# ============================================================================
class StockModelTests(BaseInventarioTestCase):
    """Pruebas para los modelos de Stock de productos."""

    def test_crear_stock_por_producto(self):
        """Crea stock para Pipe, PumpAndMotor y Accessory y valida campos."""
        # Stock de Tubería
        stock_pipe = StockPipe.objects.create(
            producto=self.pipe_instance,
            ubicacion=self.ubicacion_principal,
            cantidad=Decimal('10.000')
        )
        self.assertIsNotNone(stock_pipe)
        self.assertEqual(StockPipe.objects.count(), 1)
        # metros_totales = cantidad * longitud_unitaria
        self.assertEqual(stock_pipe.metros_totales, Decimal('10.000') * self.pipe_instance.longitud_unitaria)

        # Crear equipo para stock
        bomba = PumpAndMotor.objects.create(
            nombre='Bomba 3HP',
            sku='STOCK-PUMP-001',
            categoria=self.categoria_tuberia,
            proveedor=self.proveedor,
            unidad_medida=self.unidad_unitaria,
            tipo_equipo='BOMBA_PERIFERICA',
            marca=self.marca_bomba,
            modelo='BX-3',
            numero_serie='STOCK-SN-001',
            potencia_hp=Decimal('3.0'),
            voltaje=220,
            fases='MONOFASICO'
        )
        stock_pump = StockPumpAndMotor.objects.create(
            producto=bomba,
            ubicacion=self.ubicacion_principal,
            cantidad=1,
            estado_operativo='NUEVO'
        )
        self.assertIsNotNone(stock_pump)
        self.assertEqual(StockPumpAndMotor.objects.count(), 1)

        # Crear accesorio para stock
        accesorio = Accessory.objects.create(
            nombre='Válvula Bola 1"',
            sku='STOCK-ACC-001',
            categoria=self.categoria_tuberia,
            proveedor=self.proveedor,
            unidad_medida=self.unidad_unitaria,
            tipo_accesorio='VALVULA',
            subtipo='BOLA',
            material='PVC',
            diametro_entrada=Decimal('1.0'),
            unidad_diametro='PULGADAS',
            tipo_conexion='ROSCADA',
            presion_trabajo='PN10'
        )
        stock_acc = StockAccessory.objects.create(
            producto=accesorio,
            ubicacion=self.ubicacion_principal,
            cantidad=Decimal('5.000')
        )
        self.assertIsNotNone(stock_acc)
        self.assertEqual(StockAccessory.objects.count(), 1)

    def test_cantidad_negativa_invalida(self):
        """Verifica que no se permitan cantidades negativas en stock."""
        # StockPipe negativo
        with self.assertRaises(ValidationError):
            sp = StockPipe(
                producto=self.pipe_instance,
                ubicacion=self.ubicacion_principal,
                cantidad=Decimal('-1.000')
            )
            sp.full_clean()

        # StockPumpAndMotor negativo
        with self.assertRaises(ValidationError):
            sm = StockPumpAndMotor(
                producto=PumpAndMotor.objects.create(
                    nombre='Bomba Test',
                    sku='NEG-PUMP-001',
                    categoria=self.categoria_tuberia,
                    proveedor=self.proveedor,
                    unidad_medida=self.unidad_unitaria,
                    tipo_equipo='MOTOR_ELECTRICO',
                    marca=self.marca_bomba,
                    modelo='NEG-1',
                    numero_serie='NEG-SN-1',
                    potencia_hp=Decimal('1.0'),
                    voltaje=110,
                    fases='MONOFASICO'
                ),
                ubicacion=self.ubicacion_principal,
                cantidad=-1
            )
            sm.full_clean()

        # StockAccessory negativo
        with self.assertRaises(ValidationError):
            sa = StockAccessory(
                producto=Accessory.objects.create(
                    nombre='Acc Test',
                    sku='NEG-ACC-001',
                    categoria=self.categoria_tuberia,
                    proveedor=self.proveedor,
                    unidad_medida=self.unidad_unitaria,
                    tipo_accesorio='UNION',
                    material='PVC',
                    diametro_entrada=Decimal('2.0'),
                    unidad_diametro='PULGADAS',
                    tipo_conexion='RAPIDA',
                    presion_trabajo='PN6'
                ),
                ubicacion=self.ubicacion_principal,
                cantidad=Decimal('-0.500')
            )
            sa.full_clean()

    def test_unicidad_producto_ubicacion(self):
        """Impide duplicar el mismo producto en la misma ubicación."""
        StockPipe.objects.create(
            producto=self.pipe_instance,
            ubicacion=self.ubicacion_principal,
            cantidad=Decimal('1.000')
        )
        from django.db import IntegrityError
        with self.assertRaises(IntegrityError):
            StockPipe.objects.create(
                producto=self.pipe_instance,
                ubicacion=self.ubicacion_principal,
                cantidad=Decimal('2.000')
            )


# ============================================================================
# CHEMICAL PRODUCT TESTS
# ============================================================================
class ChemicalProductModelTests(BaseInventarioTestCase):
    """Pruebas para el modelo ChemicalProduct y su stock/movimientos."""

    def test_crear_quimico_no_peligroso(self):
        quimico = ChemicalProduct.objects.create(
            nombre='Cloro Granulado',
            sku='CHEM-001',
            categoria=self.categoria_tuberia,
            proveedor=self.proveedor,
            unidad_medida=self.unidad_unitaria,
            presentacion='SACO',
            unidad_concentracion='PORCENTAJE',
            es_peligroso=False
        )
        self.assertIsNotNone(quimico)

    def test_quimico_peligroso_sin_nivel_invalido(self):
        with self.assertRaises(ValidationError):
            q = ChemicalProduct(
                nombre='Ácido Clorhídrico',
                sku='CHEM-002',
                categoria=self.categoria_tuberia,
                proveedor=self.proveedor,
                unidad_medida=self.unidad_unitaria,
                es_peligroso=True
            )
            q.full_clean()

    def test_expiracion(self):
        ayer = timezone.now().date() - timezone.timedelta(days=1)
        mañana = timezone.now().date() + timezone.timedelta(days=1)
        q_exp = ChemicalProduct.objects.create(
            nombre='Alumbre', sku='CHEM-003', categoria=self.categoria_tuberia,
            proveedor=self.proveedor, unidad_medida=self.unidad_unitaria,
            fecha_caducidad=ayer
        )
        q_noexp = ChemicalProduct.objects.create(
            nombre='Polímero', sku='CHEM-004', categoria=self.categoria_tuberia,
            proveedor=self.proveedor, unidad_medida=self.unidad_unitaria,
            fecha_caducidad=mañana
        )
        self.assertTrue(q_exp.is_expired())
        self.assertFalse(q_noexp.is_expired())

    def test_stock_chemical_y_movimiento_entrada(self):
        q = ChemicalProduct.objects.create(
            nombre='Hipoclorito', sku='CHEM-005', categoria=self.categoria_tuberia,
            proveedor=self.proveedor, unidad_medida=self.unidad_unitaria
        )
        ct = ContentType.objects.get_for_model(ChemicalProduct)
        MovimientoInventario.objects.create(
            content_type=ct, object_id=q.id,
            tipo_movimiento='ENTRADA', status='APROBADO',
            cantidad=Decimal('10.000'), ubicacion_destino=self.ubicacion_principal
        )
        stock = StockChemical.objects.get(producto=q, ubicacion=self.ubicacion_principal)
        self.assertEqual(stock.cantidad, Decimal('10.000'))


# ============================================================================
# MOVIMIENTO EDGE CASES & AJUSTE
# ============================================================================
class MovimientoEdgeCasesTests(BaseInventarioTestCase):
    def test_entrada_sin_destino_error_auditoria_limpia(self):
        ct = ContentType.objects.get_for_model(Pipe)
        from django.core.exceptions import ValidationError as DjangoValidationError
        try:
            MovimientoInventario.objects.create(
                content_type=ct, object_id=self.pipe_instance.id,
                tipo_movimiento='ENTRADA', status='APROBADO',
                cantidad=Decimal('1.000')
            )
            self.fail('Debe requerir destino para entrada')
        except DjangoValidationError:
            InventoryAudit.objects.all().delete()

    def test_salida_sin_origen_error_auditoria_limpia(self):
        ct = ContentType.objects.get_for_model(Pipe)
        from django.core.exceptions import ValidationError as DjangoValidationError
        try:
            MovimientoInventario.objects.create(
                content_type=ct, object_id=self.pipe_instance.id,
                tipo_movimiento='SALIDA', status='APROBADO',
                cantidad=Decimal('1.000')
            )
            self.fail('Debe requerir origen para salida')
        except DjangoValidationError:
            InventoryAudit.objects.all().delete()

    def test_ajuste_suma_destino(self):
        ct = ContentType.objects.get_for_model(Accessory)
        acc = Accessory.objects.create(
            nombre='Unión 1"', sku='ACC-AJ-1', categoria=self.categoria_tuberia,
            proveedor=self.proveedor, unidad_medida=self.unidad_unitaria,
            tipo_accesorio='UNION', material='PVC',
            diametro_entrada=Decimal('1.0'), unidad_diametro='PULGADAS',
            tipo_conexion='RAPIDA', presion_trabajo='PN6'
        )
        MovimientoInventario.objects.create(
            content_type=ct, object_id=acc.id,
            tipo_movimiento='AJUSTE', status='APROBADO',
            cantidad=Decimal('2.000'), ubicacion_destino=self.ubicacion_principal
        )
        stock = StockAccessory.objects.get(producto=acc, ubicacion=self.ubicacion_principal)
        self.assertEqual(stock.cantidad, Decimal('2.000'))

    def test_ajuste_resta_origen(self):
        ct = ContentType.objects.get_for_model(Pipe)
        # Inicializar stock
        StockPipe.objects.create(producto=self.pipe_instance, ubicacion=self.ubicacion_principal, cantidad=Decimal('3.000'))
        MovimientoInventario.objects.create(
            content_type=ct, object_id=self.pipe_instance.id,
            tipo_movimiento='AJUSTE', status='APROBADO',
            cantidad=Decimal('1.000'), ubicacion_origen=self.ubicacion_principal
        )
        stock = StockPipe.objects.get(producto=self.pipe_instance, ubicacion=self.ubicacion_principal)
        self.assertEqual(stock.cantidad, Decimal('2.000'))
# ============================================================================
# MOVIMIENTO INVENTARIO TESTS (Integración entre apps)
# ============================================================================
class MovimientoInventarioTests(BaseInventarioTestCase):
    """Pruebas de integración para movimientos y actualización de stock/auditoría."""

    def test_entrada_pipe_aprobado_incrementa_stock_y_audita(self):
        ct = ContentType.objects.get_for_model(Pipe)
        movimiento = MovimientoInventario.objects.create(
            content_type=ct,
            object_id=self.pipe_instance.id,
            tipo_movimiento='ENTRADA',
            status='APROBADO',
            cantidad=Decimal('2.000'),
            ubicacion_destino=self.ubicacion_principal
        )
        stock = StockPipe.objects.get(producto=self.pipe_instance, ubicacion=self.ubicacion_principal)
        self.assertEqual(stock.cantidad, Decimal('2.000'))
        self.assertTrue(movimiento.audits.filter(status=InventoryAudit.STATUS_SUCCESS).exists())

    def test_salida_pipe_insuficiente_stock_lanza_error(self):
        # Asegurar stock inicial insuficiente
        StockPipe.objects.create(producto=self.pipe_instance, ubicacion=self.ubicacion_principal, cantidad=Decimal('1.000'))
        ct = ContentType.objects.get_for_model(Pipe)
        from django.core.exceptions import ValidationError as DjangoValidationError
        try:
            MovimientoInventario.objects.create(
                content_type=ct,
                object_id=self.pipe_instance.id,
                tipo_movimiento='SALIDA',
                status='APROBADO',
                cantidad=Decimal('2.000'),
                ubicacion_origen=self.ubicacion_principal
            )
            self.fail("Se esperaba ValidationError por stock insuficiente")
        except DjangoValidationError:
            # Debe quedar una auditoría con estado FAILED; limpiar para evitar FK inválidos en teardown
            self.assertTrue(InventoryAudit.objects.filter(status=InventoryAudit.STATUS_FAILED).exists())
            InventoryAudit.objects.all().delete()

    def test_transfer_pump_actualiza_stocks_y_ficha_instalacion(self):
        # Crear equipo y stock en origen
        bomba = PumpAndMotor.objects.create(
            nombre='Bomba Transfer',
            sku='TR-PUMP-001',
            categoria=self.categoria_tuberia,
            proveedor=self.proveedor,
            unidad_medida=self.unidad_unitaria,
            tipo_equipo='MOTOR_ELECTRICO',
            marca=self.marca_bomba,
            modelo='TR-1',
            numero_serie='TR-SN-1',
            potencia_hp=Decimal('1.0'),
            voltaje=110,
            fases='MONOFASICO'
        )
        StockPumpAndMotor.objects.create(producto=bomba, ubicacion=self.ubicacion_principal, cantidad=1)

        # Crear ubicación de instalación
        ubicacion_instalacion = Ubicacion.objects.create(
            nombre='Instalación Secundaria',
            acueducto=self.acueducto_secundario,
            tipo='INSTALACION'
        )

        ct = ContentType.objects.get_for_model(PumpAndMotor)
        # Crear usuario para campos requeridos en compras.OrdenCompra
        user_model = get_user_model()
        solicitante = user_model.objects.create_user(username='soli', password='x')
        aprobador = user_model.objects.create_user(username='aprob', password='x')

        movimiento = MovimientoInventario.objects.create(
            content_type=ct,
            object_id=bomba.id,
            tipo_movimiento='TRANSFER',
            status='APROBADO',
            cantidad=Decimal('1.000'),
            ubicacion_origen=self.ubicacion_principal,
            ubicacion_destino=ubicacion_instalacion,
            creado_por=solicitante,
            aprobado_por=aprobador
        )

        stock_origen = StockPumpAndMotor.objects.get(producto=bomba, ubicacion=self.ubicacion_principal)
        stock_destino = StockPumpAndMotor.objects.get(producto=bomba, ubicacion=ubicacion_instalacion)
        self.assertEqual(stock_origen.cantidad, 0)
        self.assertEqual(stock_destino.cantidad, 1)

        ficha = FichaTecnicaMotor.objects.get(equipo=bomba)
        self.assertEqual(ficha.estado_actual, 'Instalado')

    def test_aprobacion_posterior_actualiza_stock(self):
        ct = ContentType.objects.get_for_model(Accessory)
        accesorio = Accessory.objects.create(
            nombre='Brida 2"',
            sku='AP-ACC-001',
            categoria=self.categoria_tuberia,
            proveedor=self.proveedor,
            unidad_medida=self.unidad_unitaria,
            tipo_accesorio='BRIDA',
            material='PVC',
            diametro_entrada=Decimal('2.0'),
            unidad_diametro='PULGADAS',
            tipo_conexion='BRIDADA',
            presion_trabajo='PN16'
        )
        movimiento = MovimientoInventario.objects.create(
            content_type=ct,
            object_id=accesorio.id,
            tipo_movimiento='ENTRADA',
            status='PENDIENTE',
            cantidad=Decimal('3.000'),
            ubicacion_destino=self.ubicacion_principal
        )
        # Aún no debe haber stock
        self.assertFalse(StockAccessory.objects.filter(producto=accesorio, ubicacion=self.ubicacion_principal).exists())

        # Aprobar y guardar
        movimiento.status = 'APROBADO'
        movimiento.save()

        stock = StockAccessory.objects.get(producto=accesorio, ubicacion=self.ubicacion_principal)
        self.assertEqual(stock.cantidad, Decimal('3.000'))
