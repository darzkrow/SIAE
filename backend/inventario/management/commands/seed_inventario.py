from django.core.management.base import BaseCommand

from inventario.models import (
    OrganizacionCentral, Sucursal, Acueducto, Categoria, Tuberia, Equipo
)
from django.contrib.auth import get_user_model

class Command(BaseCommand):
    help = 'Crea Hidroven, 16 sucursales, acueductos y usuario admin (idempotente)'

    def handle(self, *args, **options):
        User = get_user_model()
        if not User.objects.filter(username='admin').exists():
            User.objects.create_superuser('admin', 'admin@example.com', 'admin')
        # Ensure admin has ADMIN role
        admin = User.objects.get(username='admin')
        if getattr(admin, 'role', None) != getattr(User, 'ROLE_ADMIN', 'ADMIN'):
            admin.role = getattr(User, 'ROLE_ADMIN', 'ADMIN')
            admin.save()
            self.stdout.write(self.style.SUCCESS('Superuser "admin" created (password: admin)'))
        else:
            self.stdout.write('Superuser "admin" already exists')

        oc, _ = OrganizacionCentral.objects.get_or_create(nombre='Hidroven', defaults={'rif': ''})
        self.stdout.write(self.style.SUCCESS(f'Organización central: {oc.nombre}'))

        # Define 16 sucursales (include Hidrocapital explicitly)
        sucursal_names = [
            'Hidrocapital',
        ] + [f'Sucursal {i}' for i in range(2, 17)]

        sucursales = []
        for name in sucursal_names:
            s, created = Sucursal.objects.get_or_create(nombre=name, organizacion_central=oc)
            sucursales.append(s)
            if created:
                self.stdout.write(self.style.SUCCESS(f'  Creada sucursal: {s.nombre}'))

        # For Hidrocapital create 7 acueductos
        hidrocapital = Sucursal.objects.get(nombre='Hidrocapital')
        for i in range(1, 8):
            a_name = f'Acueducto {i} (Hidrocapital)'
            Acueducto.objects.get_or_create(nombre=a_name, sucursal=hidrocapital)

        # For other sucursales create 2 acueductos each
        for s in sucursales:
            if s.nombre == 'Hidrocapital':
                continue
            Acueducto.objects.get_or_create(nombre=f'Acueducto A ({s.nombre})', sucursal=s)
            Acueducto.objects.get_or_create(nombre=f'Acueducto B ({s.nombre})', sucursal=s)

        # Create a couple of categorias and sample items
        cat_tuberia, _ = Categoria.objects.get_or_create(nombre='Tuberías')
        cat_equipos, _ = Categoria.objects.get_or_create(nombre='Equipos')

        # Sample tuberia
        tub, _ = Tuberia.objects.get_or_create(
            nombre='Tubería PVC 100mm', categoria=cat_tuberia,
            defaults={'descripcion': 'Tubería PVC 100 mm', 'material': 'PVC', 'tipo_uso': 'POTABLE', 'diametro_nominal_mm': 100, 'longitud_m': 6.0}
        )

        # Sample equipo
        eq, _ = Equipo.objects.get_or_create(
            numero_serie='SN-EX-0001', nombre='Motobomba Modelo X', categoria=cat_equipos,
            defaults={'descripcion': 'Motobomba de prueba', 'marca': 'MarcaX', 'modelo': 'X1', 'potencia_hp': 5.5}
        )

        self.stdout.write(self.style.SUCCESS('Seed completado: sucursales, acueductos y artículos ejemplo creados.'))
