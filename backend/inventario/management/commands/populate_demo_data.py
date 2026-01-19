from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils import timezone
from decimal import Decimal
from django.contrib.auth import get_user_model

from inventario.models import (
    OrganizacionCentral, Sucursal, Acueducto,
    UnitOfMeasure, Supplier,
    ChemicalProduct, Pipe, PumpAndMotor, Accessory,
    StockChemical, StockPipe, StockPumpAndMotor, StockAccessory,
)
from geography.models import Ubicacion
from catalogo.models import CategoriaProducto


class Command(BaseCommand):
    help = 'Populate demo data (realistic but fictitious) for hydrological organizations and inventory'

    def handle(self, *args, **options):
        with transaction.atomic():
            self.stdout.write('Creando organizaciones y sucursales...')

            orgs = []
            org_names = [
                ('Hidrocapital', 'J-12345678-9'),
                ('Hidrosuroeste', 'J-98765432-1'),
                ('Hidrocentro', 'J-11223344-5'),
                ('Hidrocaribe', 'J-55667788-0'),
            ]
            for name, rif in org_names:
                org, _ = OrganizacionCentral.objects.get_or_create(nombre=name, defaults={'rif': rif})
                orgs.append(org)

            # Crear sucursales y acueductos
            sucursales = []
            acueductos = []

            mapping = {
                'Hidrocapital': [
                    ('Acueducto Capital - Miranda', 'CAP-MIR', 'Caracas, Miranda'),
                    ('Acueducto Varga', 'VARGA', 'Vargas, La Guaira'),
                ],
                'Hidrosuroeste': [
                    ('Acueducto Táchira', 'TACH', 'San Cristóbal, Táchira'),
                    ('Acueducto Mérida', 'MERI', 'Mérida, Mérida'),
                ],
                'Hidrocentro': [
                    ('Acueducto Centro', 'CENT', 'Carabobo, Valencia'),
                ],
                'Hidrocaribe': [
                    ('Acueducto Caribe', 'CARIB', 'Anzoátegui, Barcelona'),
                ],
            }

            for org in orgs:
                s_name = f"Sucursal {org.nombre}"
                # Generar un código único para la sucursal evitando colisiones
                base_code = org.nombre[:6].upper()
                code = base_code
                idx = 1
                while Sucursal.objects.filter(codigo=code).exists():
                    code = f"{base_code}{idx}"
                    idx += 1

                suc, _ = Sucursal.objects.get_or_create(
                    nombre=s_name,
                    organizacion_central=org,
                    defaults={'codigo': code, 'direccion': f'Oficina central {org.nombre}'}
                )
                sucursales.append(suc)

                for ac in mapping.get(org.nombre, []):
                    ac_name, ac_code, ubic = ac
                    a, _ = Acueducto.objects.get_or_create(
                        nombre=ac_name,
                        sucursal=suc,
                        defaults={'codigo': ac_code, 'ubicacion': ubic}
                    )
                    acueductos.append(a)

            self.stdout.write(f'Creadas {len(orgs)} organizaciones, {len(sucursales)} sucursales y {len(acueductos)} acueductos')

            # Categorías y unidades
            self.stdout.write('Creando categorías, unidades y proveedores...')
            categories = {
                'Químicos': 'QUI',
                'Tuberías': 'TUB',
                'Bombas': 'BOM',
                'Accesorios': 'ACC',
            }
            cat_objs = {}
            for name, code in categories.items():
                c, _ = CategoriaProducto.objects.get_or_create(nombre=name, defaults={'codigo': code, 'descripcion': f'Categoría {name}'})
                cat_objs[name] = c

            uoms = [
                ('Kilogramo', 'kg', 'PESO'),
                ('Metro', 'm', 'LONGITUD'),
                ('Unidad', 'un', 'UNIDAD'),
                ('Litro', 'l', 'VOLUMEN'),
                ('Milímetro', 'mm', 'LONGITUD'),
                ('Pulgada', 'in', 'LONGITUD'),
            ]
            uom_objs = {}
            for nombre, simbolo, tipo in uoms:
                u, _ = UnitOfMeasure.objects.get_or_create(nombre=nombre, simbolo=simbolo, defaults={'tipo': tipo})
                uom_objs[nombre] = u

            suppliers_data = [
                ('Servicios Hidráulicos del Centro C.A.', 'J-20123456-7', 'SERVCENT'),
                ('Insumos y Suministros Hídricos S.A.', 'J-20987654-3', 'INSUMOSHI'),
                ('Bombas y Motores Industriales C.A.', 'J-20332211-5', 'BOMIND'),
            ]
            supplier_objs = {}
            for nombre, rif, code in suppliers_data:
                s, _ = Supplier.objects.get_or_create(nombre=nombre, defaults={'rif': rif, 'codigo': code, 'contacto_nombre': 'Contacto', 'telefono': '0212-555-0000', 'email': f'ventas@{nombre.lower().replace(" ", "")}.com'})
                supplier_objs[nombre] = s

            # Productos - Químicos
            self.stdout.write('Creando productos y stocks...')
            chem_products = []
            cloro, _ = ChemicalProduct.objects.get_or_create(
                nombre='Cloro Gaseoso 12.5%',
                defaults={
                    'sku': '',
                    'descripcion': 'Cloro para desinfección',
                    'categoria': cat_objs['Químicos'],
                    'unidad_medida': uom_objs['Kilogramo'],
                    'stock_actual': Decimal('500.000'),
                    'stock_minimo': Decimal('100.000'),
                    'precio_unitario': Decimal('2.50'),
                    'proveedor': supplier_objs[suppliers_data[1][0]],
                    'es_peligroso': True,
                    'nivel_peligrosidad': 'ALTO',
                    'fecha_caducidad': timezone.now().date().replace(year=timezone.now().year + 1),
                    'concentracion': Decimal('12.50'),
                    'unidad_concentracion': 'PORCENTAJE',
                    'presentacion': 'TAMBOR',
                }
            )
            chem_products.append(cloro)

            sulfato, _ = ChemicalProduct.objects.get_or_create(
                nombre='Sulfato de Aluminio 17%',
                defaults={
                    'sku': '',
                    'descripcion': 'Coagulante para clarificación',
                    'categoria': cat_objs['Químicos'],
                    'unidad_medida': uom_objs['Kilogramo'],
                    'stock_actual': Decimal('200.000'),
                    'stock_minimo': Decimal('50.000'),
                    'precio_unitario': Decimal('1.20'),
                    'proveedor': supplier_objs[suppliers_data[1][0]],
                    'es_peligroso': False,
                    'nivel_peligrosidad': 'BAJO',
                    'fecha_caducidad': timezone.now().date().replace(year=timezone.now().year + 2),
                    'concentracion': Decimal('17.00'),
                    'presentacion': 'SACO',
                }
            )
            chem_products.append(sulfato)

            # Tuberías
            pvc_pipe, _ = Pipe.objects.get_or_create(
                nombre='Tubería PVC Clase 10 - 100 mm',
                defaults={
                    'sku': '',
                    'descripcion': 'Tubo PVC para conducción principal',
                    'categoria': cat_objs['Tuberías'],
                    'unidad_medida': uom_objs['Metro'],
                    'stock_actual': Decimal('1000.000'),
                    'stock_minimo': Decimal('100.000'),
                    'precio_unitario': Decimal('15.00'),
                    'proveedor': supplier_objs[suppliers_data[0][0]],
                    'material': 'PVC',
                    'diametro_nominal': Decimal('100.00'),
                    'unidad_diametro': 'MM',
                    'presion_nominal': 'PN10',
                    'tipo_union': 'SOLDABLE',
                    'tipo_uso': 'POTABLE',
                    'longitud_unitaria': Decimal('6.00'),
                }
            )

            pead_pipe, _ = Pipe.objects.get_or_create(
                nombre='Tubería PEAD - 63 mm',
                defaults={
                    'sku': '',
                    'descripcion': 'Tubo PEAD para redes secundarias',
                    'categoria': cat_objs['Tuberías'],
                    'unidad_medida': uom_objs['Metro'],
                    'stock_actual': Decimal('500.000'),
                    'stock_minimo': Decimal('50.000'),
                    'precio_unitario': Decimal('10.00'),
                    'proveedor': supplier_objs[suppliers_data[0][0]],
                    'material': 'PEAD',
                    'diametro_nominal': Decimal('63.00'),
                    'unidad_diametro': 'MM',
                    'presion_nominal': 'PN16',
                    'tipo_union': 'FUSION',
                    'tipo_uso': 'POTABLE',
                    'longitud_unitaria': Decimal('6.00'),
                }
            )

            # Bombas (omitidas temporalmente si el modelo requiere validación especial)
            pump1 = None

            # Accesorios
            valvula, _ = Accessory.objects.get_or_create(
                nombre='Válvula de Bola 3"',
                defaults={
                    'sku': '',
                    'descripcion': 'Válvula para control de paso',
                    'categoria': cat_objs['Accesorios'],
                    'unidad_medida': uom_objs['Unidad'],
                    'stock_actual': Decimal('200.000'),
                    'stock_minimo': Decimal('20.000'),
                    'precio_unitario': Decimal('45.00'),
                    'proveedor': supplier_objs[suppliers_data[0][0]],
                    'tipo_accesorio': 'VALVULA',
                    'subtipo': 'BOLA',
                    'diametro_entrada': Decimal('3.00'),
                    'unidad_diametro': 'PULGADAS',
                    'tipo_conexion': 'BRIDADA',
                    'presion_trabajo': 'PN16',
                    'material': 'HIERRO',
                }
            )

            for ac in acueductos:
                # Crear/usar una Ubicacion asociada al acueducto para stocks
                almacen_nombre = f"Almacén {ac.codigo or ac.nombre}"
                ubic, _ = Ubicacion.objects.get_or_create(
                    nombre=almacen_nombre,
                    acueducto=ac,
                    defaults={
                        'tipo': Ubicacion.TipoUbicacion.ALMACEN,
                        'descripcion': f'Almacén principal de {ac.nombre}'
                    }
                )

                StockChemical.objects.get_or_create(
                    producto=cloro,
                    ubicacion=ubic,
                    defaults={'cantidad': Decimal('100.000'), 'lote': 'L-CL-001', 'fecha_vencimiento': cloro.fecha_caducidad}
                )
                StockChemical.objects.get_or_create(
                    producto=sulfato,
                    ubicacion=ubic,
                    defaults={'cantidad': Decimal('50.000'), 'lote': 'L-SUL-001', 'fecha_vencimiento': sulfato.fecha_caducidad}
                )
                StockPipe.objects.get_or_create(producto=pvc_pipe, ubicacion=ubic, defaults={'cantidad': Decimal('100.000')})
                StockPipe.objects.get_or_create(producto=pead_pipe, ubicacion=ubic, defaults={'cantidad': Decimal('50.000')})
                # Omitir stock de bombas si no existe el producto creado
                if pump1:
                    StockPumpAndMotor.objects.get_or_create(producto=pump1, ubicacion=ubic, defaults={'cantidad': 1, 'estado_operativo': 'OPERATIVO'})
                StockAccessory.objects.get_or_create(producto=valvula, ubicacion=ubic, defaults={'cantidad': Decimal('20.000')})

            # Usuarios
            User = get_user_model()
            self.stdout.write('Creando usuarios de ejemplo...')
            admin, _ = User.objects.get_or_create(
                username='admin',
                defaults={'email': 'admin@gsih.com', 'is_superuser': True, 'is_staff': True, 'role': getattr(User, 'ROLE_ADMIN', 'ADMIN')}
            )
            # Ensure admin has correct role and password
            updated = False
            if getattr(admin, 'role', None) != getattr(User, 'ROLE_ADMIN', 'ADMIN'):
                admin.role = getattr(User, 'ROLE_ADMIN', 'ADMIN')
                updated = True
            if not admin.password:
                admin.set_password('admin123')
                updated = True
            if updated:
                admin.save()

            # Operadores por sucursal
            for suc in sucursales:
                uname = f"oper_{suc.codigo.lower()}"
                u, _ = User.objects.get_or_create(username=uname, defaults={'email': f'{uname}@gsih.com', 'role': 'OPERADOR', 'sucursal': suc})
                if not u.password:
                    u.set_password('oper1234')
                    u.save()

            # Resumen
            self.stdout.write('Poblado completado.')
            self.stdout.write(f'Organizaciones: {OrganizacionCentral.objects.count()}')
            self.stdout.write(f'Sucursales: {Sucursal.objects.count()}')
            self.stdout.write(f'Acueductos: {Acueducto.objects.count()}')
            self.stdout.write(f'Categories: {CategoriaProducto.objects.count()}')
            self.stdout.write(f'UnitOfMeasure: {UnitOfMeasure.objects.count()}')
            self.stdout.write(f'Suppliers: {Supplier.objects.count()}')
            self.stdout.write(f'ChemicalProducts: {ChemicalProduct.objects.count()}')
            self.stdout.write(f'Pipes: {Pipe.objects.count()}')
            self.stdout.write(f'PumpAndMotor: {PumpAndMotor.objects.count()}')
            self.stdout.write(f'Accessory: {Accessory.objects.count()}')
            self.stdout.write(f'StockChemical: {StockChemical.objects.count()}')
            self.stdout.write(f'StockPipe: {StockPipe.objects.count()}')
            self.stdout.write(f'StockPumpAndMotor: {StockPumpAndMotor.objects.count()}')
            self.stdout.write(f'StockAccessory: {StockAccessory.objects.count()}')
            self.stdout.write(f'Usuarios: {User.objects.count()}')
