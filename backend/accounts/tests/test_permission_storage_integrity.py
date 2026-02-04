# ¡Hola! Soy Morris y voy a explicarte cómo funcionan estos tests 🎈
# Estos son como juegos que verifican que todo funcione bien en nuestro sistema de permisos

import pytest
from django.test import TestCase, TransactionTestCase
from django.contrib.contenttypes.models import ContentType
from django.contrib.auth import get_user_model
from django.db import IntegrityError, transaction
from django.utils import timezone
from hypothesis import given, strategies as st, settings, assume
from hypothesis.extra.django import TestCase as HypothesisTestCase
from datetime import timedelta
import json
import uuid

from accounts.models import Permission, Role, RolePermission, UserRole
from test_utils import (
    permission_data_strategy,
    role_data_strategy,
    json_object_strategy,
    PropertyTestMixin,
    DatabaseTestMixin,
    TestDataFactory
)

User = get_user_model()


@pytest.mark.property
class PermissionStorageIntegrityPropertyTest(HypothesisTestCase, PropertyTestMixin, DatabaseTestMixin):
    """
    🎮 ¡Test de Integridad de Permisos! - Por Morris
    
    **Propiedad 12: Los permisos se guardan bien y no se pierden**
    **Valida: Requisito 3.1**
    
    Imagina que tienes una caja de juguetes (la base de datos). Este test verifica que:
    - Cuando guardas un juguete (permiso), siempre está donde lo dejaste
    - Los juguetes no se mezclan ni se pierden
    - Puedes encontrar tus juguetes cuando los necesitas
    - Si borras algo, solo se borra lo que quieres y nada más
    
    ¡Es como asegurarnos de que tu cuarto esté siempre ordenado! 🧸
    """
    
    def setUp(self):
        """🎨 Preparando todo para jugar (configuración inicial)"""
        # Aquí guardamos los tipos de cosas que podemos tener permisos
        # Es como tener diferentes cajas para diferentes tipos de juguetes
        self.content_types = [
            ContentType.objects.get_for_model(User),  # Caja de usuarios
            ContentType.objects.get_for_model(Role),  # Caja de roles
            ContentType.objects.get_for_model(Permission),  # Caja de permisos
        ]
        # Creamos un usuario administrador único para cada prueba
        # ¡Como tener un supervisor diferente para cada juego!
        unique_id = str(uuid.uuid4())[:8]
        self.admin_user = TestDataFactory.create_superuser(username=f"test_admin_{unique_id}")
    
    @given(permission_data_strategy())
    @settings(max_examples=100, deadline=None)
    def test_permission_storage_integrity(self, permission_data):
        """
        🎯 Prueba 1: Verificar que los permisos se guarden correctamente
        
        Propiedad: Cualquier permiso válido debe guardarse bien en la base de datos
        sin perder ninguna información.
        
        ¡Es como guardar tu dibujo favorito y asegurarte de que no se borre! 🖍️
        """
        # Verificamos que los datos sean válidos (como revisar que tu juguete no esté roto)
        assume(len(permission_data['name'].strip()) > 0)  # El nombre no puede estar vacío
        assume(len(permission_data['codename'].strip()) > 0)  # El código tampoco
        assume(permission_data['codename'].replace('_', '').replace('-', '').isalnum())  # Solo letras y números
        
        # Usamos el primer tipo de contenido para mantenerlo simple
        content_type = self.content_types[0]  # ¡Elegimos la primera caja!
        
        # Hacemos el código único para que no haya dos iguales
        # ¡Como ponerle tu nombre a tu juguete para que nadie lo confunda!
        unique_id = str(uuid.uuid4())[:8]
        unique_codename = f"{permission_data['codename'].strip().lower()}_{unique_id}"
        
        # ¡Creamos el permiso! Es como hacer un nuevo juguete 🎨
        permission = Permission.objects.create(
            name=permission_data['name'].strip(),  # El nombre bonito del permiso
            codename=unique_codename,  # Su código especial único
            content_type=content_type,  # En qué caja va
            description=permission_data['description']  # Una descripción de qué hace
        )
        
        # Verificamos que se guardó correctamente (¡revisamos que esté en su lugar!)
        self._verify_permission_storage_integrity(permission, permission_data, content_type, unique_codename)
        
        # Verificamos que las reglas de la base de datos funcionen
        # (como asegurarnos de que no haya dos juguetes con el mismo nombre)
        self._verify_permission_database_constraints(permission)
        
        # Verificamos que todas las conexiones estén bien
        self._verify_permission_referential_integrity(permission)
    
    @given(role_data_strategy())
    @settings(max_examples=100, deadline=None)
    def test_role_storage_integrity(self, role_data):
        """
        🎭 Prueba 2: Verificar que los roles se guarden correctamente
        
        Propiedad: Cualquier rol válido debe guardarse bien sin perder información.
        
        ¡Los roles son como disfraces que le das a las personas para que puedan hacer cosas especiales! 🦸
        """
        # Verificamos que el nombre del rol no esté vacío
        assume(len(role_data['name'].strip()) > 0)
        
        # ¡Creamos el rol!
        role = Role.objects.create(
            name=role_data['name'].strip(),  # El nombre del rol
            description=role_data['description']  # Qué hace este rol
        )
        
        # Verificamos que se guardó bien
        self._verify_role_storage_integrity(role, role_data)
        
        # Verificamos las reglas de la base de datos
        self._verify_role_database_constraints(role)
        
        # Verificamos las conexiones
        self._verify_role_referential_integrity(role)
    
    @given(
        permission_data_strategy(),
        role_data_strategy(),
        st.booleans(),
        st.one_of(st.none(), json_object_strategy(max_leaves=5))
    )
    @settings(max_examples=100, deadline=None)
    def test_role_permission_relationship_integrity(self, permission_data, role_data, granted, conditions):
        """
        🔗 Prueba 3: Verificar que los roles y permisos se conecten bien
        Propiedad: Cuando le das un permiso a un rol, esa conexión debe guardarse
        correctamente y no romperse.
        ¡Es como conectar dos piezas de LEGO y asegurarte de que no se separen! 🧱
        """
        # Verificamos que los datos sean válidos
        assume(len(permission_data['name'].strip()) > 0)
        assume(len(permission_data['codename'].strip()) > 0)
        assume(len(role_data['name'].strip()) > 0)
        assume(permission_data['codename'].replace('_', '').replace('-', '').isalnum())
        
        content_type = self.content_types[0]  # Usamos la primera caja
        
        # Hacemos nombres únicos para evitar confusiones
        unique_id = str(uuid.uuid4())[:8]
        unique_codename = f"{permission_data['codename'].strip().lower()}_{unique_id}"
        unique_role_name = f"{role_data['name'].strip()}_{unique_id}"
        
        # Si no hay condiciones, usamos un diccionario vacío
        if conditions is None:
            conditions = {}
        
        # Creamos el permiso y el rol
        permission = Permission.objects.create(
            name=permission_data['name'].strip(),
            codename=unique_codename,
            content_type=content_type,
            description=permission_data['description']
        )
        
        role = Role.objects.create(
            name=unique_role_name,
            description=role_data['description']
        )
        
        # ¡Conectamos el rol con el permiso! (como unir dos piezas de LEGO)
        role_permission = RolePermission.objects.create(
            role=role,
            permission=permission,
            granted=granted,  # ¿Le damos permiso o se lo quitamos?
            conditions=conditions  # Reglas especiales
        )
        
        # Verificamos que la conexión se guardó bien
        self._verify_role_permission_relationship_integrity(
            role_permission, role, permission, granted, conditions
        )
        
        # Verificamos qué pasa si borramos algo (comportamiento en cascada)
        self._verify_role_permission_cascading_integrity(role_permission, role, permission)
    
    @given(
        role_data_strategy(),
        st.one_of(st.none(), st.datetimes(min_value=timezone.now().replace(tzinfo=None) + timedelta(days=1))),
        st.booleans()
    )
    @settings(max_examples=100, deadline=None)
    def test_user_role_assignment_integrity(self, role_data, expires_at, is_active):
        """
        👤 Prueba 4: Verificar que los usuarios reciban sus roles correctamente
        
        Propiedad: Cuando le das un rol a un usuario, esa asignación debe guardarse
        bien y respetar las fechas de expiración.
        
        ¡Es como darle un pase temporal a tu amigo para entrar a tu club secreto! 🎫
        """
        # Verificamos que el nombre del rol no esté vacío
        assume(len(role_data['name'].strip()) > 0)
        
        # Creamos un usuario de prueba y un rol con nombres únicos
        unique_id = str(uuid.uuid4())[:8]
        user = TestDataFactory.create_user(username=f"test_user_{unique_id}")
        role = Role.objects.create(
            name=f"{role_data['name'].strip()}_{unique_id}",
            description=role_data['description']
        )
        
        # Convertimos la fecha a formato con zona horaria si es necesario
        if expires_at is not None:
            expires_at = timezone.make_aware(expires_at) if timezone.is_naive(expires_at) else expires_at
        
        # ¡Le damos el rol al usuario!
        user_role = UserRole.objects.create(
            user=user,  # El usuario
            role=role,  # El rol que le damos
            assigned_by=self.admin_user,  # Quién le dio el rol
            expires_at=expires_at,  # Cuándo expira (si es que expira)
            is_active=is_active  # ¿Está activo ahora?
        )
        
        # Verificamos que la asignación se guardó bien
        self._verify_user_role_assignment_integrity(
            user_role, user, role, expires_at, is_active
        )
        
        # Verificamos qué pasa si borramos al usuario
        self._verify_user_role_cascading_integrity(user_role, user, role)
    
    @given(
        st.lists(permission_data_strategy(), min_size=1, max_size=5),
        st.lists(role_data_strategy(), min_size=1, max_size=3)
    )
    @settings(max_examples=50, deadline=None)
    def test_complex_permission_system_integrity(self, permissions_data, roles_data):
        """
        🌟 Prueba 5: Verificar que sistemas complejos funcionen bien
        
        Propiedad: Cuando tienes muchos permisos, roles y usuarios, todo debe
        seguir funcionando perfectamente sin errores.
        
        ¡Es como tener una ciudad de juguetes entera y asegurarte de que todo esté en orden! 🏙️
        """
        # Verificamos que todos los datos sean válidos
        for perm_data in permissions_data:
            assume(len(perm_data['name'].strip()) > 0)
            assume(len(perm_data['codename'].strip()) > 0)
            assume(perm_data['codename'].replace('_', '').replace('-', '').isalnum())
        
        for role_data in roles_data:
            assume(len(role_data['name'].strip()) > 0)
        
        # Aseguramos que todos los nombres sean únicos
        unique_id = str(uuid.uuid4())[:8]
        codenames = [f"{p['codename'].strip().lower()}_{unique_id}_{i}" for i, p in enumerate(permissions_data)]
        role_names = [f"{r['name'].strip()}_{unique_id}_{i}" for i, r in enumerate(roles_data)]
        
        content_type = self.content_types[0]  # Usamos la primera caja
        
        # Creamos todos los permisos
        permissions = []
        for i, perm_data in enumerate(permissions_data):
            permission = Permission.objects.create(
                name=f"{perm_data['name'].strip()}_{unique_id}_{i}",
                codename=codenames[i],
                content_type=content_type,
                description=perm_data['description']
            )
            permissions.append(permission)
        
        # Creamos todos los roles
        roles = []
        for i, role_data in enumerate(roles_data):
            role = Role.objects.create(
                name=role_names[i],
                description=role_data['description']
            )
            roles.append(role)
        
        # Conectamos cada rol con cada permiso
        role_permissions = []
        for role in roles:
            for permission in permissions:
                granted = True  # Simplificamos para las pruebas
                conditions = {}  # Sin condiciones especiales
                
                role_permission = RolePermission.objects.create(
                    role=role,
                    permission=permission,
                    granted=granted,
                    conditions=conditions
                )
                role_permissions.append(role_permission)
        
        # Creamos usuarios y les asignamos roles
        users = []
        user_roles = []
        for i, role in enumerate(roles):
            user = TestDataFactory.create_user(username=f"test_user_{unique_id}_{i}")
            users.append(user)
            
            user_role = UserRole.objects.create(
                user=user,
                role=role,
                assigned_by=self.admin_user
            )
            user_roles.append(user_role)
        
        # ¡Verificamos que todo el sistema esté perfecto!
        self._verify_complete_system_integrity(
            permissions, roles, role_permissions, users, user_roles
        )
    
    def _verify_permission_storage_integrity(self, permission, permission_data, content_type, unique_codename):
        """🔍 Verificar que el permiso se guardó correctamente"""
        # Recargamos el permiso desde la base de datos
        stored_permission = Permission.objects.get(id=permission.id)
        
        # Verificamos que todos los campos se guardaron bien
        self.assertEqual(stored_permission.name, permission_data['name'].strip())
        self.assertEqual(stored_permission.codename, unique_codename)
        self.assertEqual(stored_permission.content_type, content_type)
        self.assertEqual(stored_permission.description, permission_data['description'])
        
        # Verificamos las fechas de creación y actualización
        self.assertIsNotNone(stored_permission.created_at)
        self.assertIsNotNone(stored_permission.updated_at)
        self.assertLessEqual(stored_permission.created_at, stored_permission.updated_at)
        
        # Verificamos cómo se muestra el permiso
        expected_str = f"{content_type.app_label}.{unique_codename}"
        self.assertEqual(str(stored_permission), expected_str)
    
    def _verify_permission_database_constraints(self, permission):
        """🚫 Verificar que no se puedan crear permisos duplicados"""
        # Intentamos crear un permiso duplicado (esto debe fallar)
        try:
            with transaction.atomic():
                Permission.objects.create(
                    name="Permiso Duplicado",
                    codename=permission.codename,
                    content_type=permission.content_type,
                    description="Esto debería fallar"
                )
            # Si llegamos aquí, algo salió mal
            self.fail("Se esperaba un error por permiso duplicado")
        except IntegrityError:
            # ¡Perfecto! El error es lo que esperábamos
            pass
    
    def _verify_permission_referential_integrity(self, permission):
        """🔗 Verificar que las conexiones del permiso estén bien"""
        # Verificamos la conexión con el tipo de contenido
        self.assertIsNotNone(permission.content_type)
        self.assertTrue(ContentType.objects.filter(id=permission.content_type.id).exists())
        
        # Verificamos la relación inversa
        self.assertIn(permission, permission.content_type.dynamic_permissions.all())
    
    def _verify_role_storage_integrity(self, role, role_data):
        """🔍 Verificar que el rol se guardó correctamente"""
        # Recargamos el rol desde la base de datos
        stored_role = Role.objects.get(id=role.id)
        
        # Verificamos todos los campos
        self.assertEqual(stored_role.name, role_data['name'].strip())
        self.assertEqual(stored_role.description, role_data['description'])
        self.assertTrue(stored_role.is_active)  # Valor por defecto
        
        # Verificamos las fechas
        self.assertIsNotNone(stored_role.created_at)
        self.assertIsNotNone(stored_role.updated_at)
        self.assertLessEqual(stored_role.created_at, stored_role.updated_at)
        
        # Verificamos cómo se muestra el rol
        self.assertEqual(str(stored_role), role_data['name'].strip())
    
    def _verify_role_database_constraints(self, role):
        """🚫 Verificar que no se puedan crear roles duplicados"""
        # Intentamos crear un rol duplicado (esto debe fallar)
        try:
            with transaction.atomic():
                Role.objects.create(
                    name=role.name,  # Nombre duplicado
                    description="Esto debería fallar"
                )
            # Si llegamos aquí, algo salió mal
            self.fail("Se esperaba un error por rol duplicado")
        except IntegrityError:
            # ¡Perfecto! El error es lo que esperábamos
            pass
    
    def _verify_role_referential_integrity(self, role):
        """🔗 Verificar que las conexiones del rol estén bien"""
        # Verificamos que el rol existe en la base de datos
        self.assertTrue(Role.objects.filter(id=role.id).exists())
        
        # Verificamos la relación con permisos (vacía al inicio)
        self.assertEqual(role.permissions.count(), 0)
    
    def _verify_role_permission_relationship_integrity(self, role_permission, role, permission, granted, conditions):
        """🔗 Verificar que la conexión rol-permiso se guardó bien"""
        # Recargamos desde la base de datos
        stored_rp = RolePermission.objects.get(id=role_permission.id)
        
        # Verificamos todos los campos de la relación
        self.assertEqual(stored_rp.role, role)
        self.assertEqual(stored_rp.permission, permission)
        self.assertEqual(stored_rp.granted, granted)
        self.assertEqual(stored_rp.conditions, conditions)
        
        # Verificamos la fecha de creación
        self.assertIsNotNone(stored_rp.created_at)
        
        # Verificamos las relaciones inversas
        self.assertIn(permission, role.permissions.all())
        
        # Verificamos cómo se muestra
        status = "otorgado" if granted else "denegado"
        expected_str = f"{role.name} - {permission.codename} ({status})"
        self.assertEqual(str(stored_rp), expected_str)
    
    def _verify_role_permission_cascading_integrity(self, role_permission, role, permission):
        """🗑️ Verificar qué pasa cuando borramos cosas"""
        # Guardamos el ID para verificar después
        rp_id = role_permission.id
        
        # Borramos el rol - la relación también debe borrarse
        role.delete()
        self.assertFalse(RolePermission.objects.filter(id=rp_id).exists())
        
        # El permiso debe seguir existiendo
        self.assertTrue(Permission.objects.filter(id=permission.id).exists())
    
    def _verify_user_role_assignment_integrity(self, user_role, user, role, expires_at, is_active):
        """🔍 Verificar que la asignación usuario-rol se guardó bien"""
        # Recargamos desde la base de datos
        stored_ur = UserRole.objects.get(id=user_role.id)
        
        # Verificamos todos los campos
        self.assertEqual(stored_ur.user, user)
        self.assertEqual(stored_ur.role, role)
        self.assertEqual(stored_ur.assigned_by, self.admin_user)
        self.assertEqual(stored_ur.expires_at, expires_at)
        self.assertEqual(stored_ur.is_active, is_active)
        
        # Verificamos la fecha de asignación
        self.assertIsNotNone(stored_ur.assigned_at)
        
        # Verificamos la lógica de expiración
        if expires_at:
            if expires_at > timezone.now():
                self.assertFalse(stored_ur.is_expired)
            # Nota: No podemos probar expiraciones pasadas en property tests
        else:
            self.assertFalse(stored_ur.is_expired)
        
        # Verificamos las relaciones inversas
        self.assertIn(role, user.roles.all())
        
        # Verificamos cómo se muestra
        expected_str = f"{user.username} - {role.name}"
        self.assertEqual(str(stored_ur), expected_str)
    
    def _verify_user_role_cascading_integrity(self, user_role, user, role):
        """🗑️ Verificar qué pasa cuando borramos al usuario"""
        # Guardamos el ID para verificar después
        ur_id = user_role.id
        
        # Borramos el usuario - la asignación también debe borrarse
        user.delete()
        self.assertFalse(UserRole.objects.filter(id=ur_id).exists())
        
        # El rol debe seguir existiendo
        self.assertTrue(Role.objects.filter(id=role.id).exists())
    
    def _verify_complete_system_integrity(self, permissions, roles, role_permissions, users, user_roles):
        """✅ Verificar que todo el sistema esté perfecto"""
        # Verificamos que todos los objetos existan en la base de datos
        for permission in permissions:
            self.assertTrue(Permission.objects.filter(id=permission.id).exists())
        
        for role in roles:
            self.assertTrue(Role.objects.filter(id=role.id).exists())
        
        for role_permission in role_permissions:
            self.assertTrue(RolePermission.objects.filter(id=role_permission.id).exists())
        
        for user in users:
            self.assertTrue(User.objects.filter(id=user.id).exists())
        
        for user_role in user_roles:
            self.assertTrue(UserRole.objects.filter(id=user_role.id).exists())
        
        # Verificamos que las cantidades de relaciones sean correctas
        total_role_permissions = sum(role.permissions.count() for role in roles)
        self.assertEqual(total_role_permissions, len(role_permissions))
        
        total_user_roles = sum(user.roles.count() for user in users)
        self.assertEqual(total_user_roles, len(user_roles))
        
        # Verificamos que no haya registros huérfanos (sin conexiones)
        self.assertNoOrphanedRecords(RolePermission, 'role')
        self.assertNoOrphanedRecords(RolePermission, 'permission')
        self.assertNoOrphanedRecords(UserRole, 'user')
        self.assertNoOrphanedRecords(UserRole, 'role')
        
        # Verificamos la integridad de la base de datos
        self.assertDatabaseIntegrity(Permission)
        self.assertDatabaseIntegrity(Role)
        self.assertDatabaseIntegrity(RolePermission)
        self.assertDatabaseIntegrity(UserRole)
        
        # Probamos que la evaluación de permisos funcione correctamente
        for user in users:
            # Debemos poder obtener los permisos sin errores
            permissions_count = user.get_dynamic_permissions().count()
            self.assertGreaterEqual(permissions_count, 0)
            
            # La verificación de permisos debe funcionar
            for permission in permissions:
                # No debe lanzar excepciones
                has_perm = user.has_dynamic_permission(permission.codename)
                self.assertIsInstance(has_perm, bool)


class PermissionStorageIntegrityTransactionTest(TransactionTestCase):
    """
    🔄 Tests de Transacciones - Por Morris
    
    Estos tests verifican que los permisos se guarden bien incluso cuando
    algo sale mal y tenemos que deshacer cambios (rollback).
    
    ¡Es como cuando haces un dibujo y si no te gusta, puedes borrarlo
    y volver a empezar sin arruinar el papel! 📝
    """
    
    @pytest.mark.property
    def test_permission_storage_transaction_integrity(self):
        """
        🎯 Prueba de Transacciones para Permisos
        
        **Propiedad 12: Integridad de Almacenamiento de Permisos**
        **Valida: Requisito 3.1**
        
        Verificamos que los permisos mantengan su integridad incluso cuando
        las transacciones se revierten (rollback).
        
        ¡Es como asegurarnos de que si algo sale mal, podemos volver atrás
        sin romper nada! 🔙
        """
        content_type = ContentType.objects.get_for_model(User)
        
        # Probamos una transacción exitosa
        with transaction.atomic():
            permission = Permission.objects.create(
                name="Permiso de Prueba",
                codename="test_perm",
                content_type=content_type,
                description="Descripción de prueba"
            )
            permission_id = permission.id
        
        # Verificamos que el permiso se guardó
        self.assertTrue(Permission.objects.filter(id=permission_id).exists())
        
        # Probamos una transacción que se revierte
        try:
            with transaction.atomic():
                permission2 = Permission.objects.create(
                    name="Permiso de Prueba 2",
                    codename="test_perm_2",
                    content_type=content_type,
                    description="Descripción de prueba 2"
                )
                permission2_id = permission2.id
                
                # Forzamos un rollback lanzando una excepción
                raise IntegrityError("Rollback forzado")
        except IntegrityError:
            pass
        
        # Verificamos que permission2 NO se guardó debido al rollback
        self.assertFalse(Permission.objects.filter(id=permission2_id).exists())
        
        # Verificamos que el permiso original sigue existiendo
        self.assertTrue(Permission.objects.filter(id=permission_id).exists())
    
    @pytest.mark.property
    def test_role_permission_transaction_integrity(self):
        """
        🔗 Prueba de Transacciones para Relaciones Rol-Permiso
        
        Verificamos que las relaciones entre roles y permisos mantengan su
        integridad bajo escenarios de rollback.
        
        ¡Es como asegurarnos de que si intentamos conectar dos piezas de LEGO
        y no funciona, las piezas originales no se rompan! 🧱
        """
        content_type = ContentType.objects.get_for_model(User)
        
        # Creamos los objetos base
        permission = Permission.objects.create(
            name="Permiso de Prueba",
            codename="test_perm",
            content_type=content_type
        )
        role = Role.objects.create(name="Rol de Prueba")
        
        # Probamos una transacción exitosa
        with transaction.atomic():
            role_permission = RolePermission.objects.create(
                role=role,
                permission=permission,
                granted=True
            )
            rp_id = role_permission.id
        
        # Verificamos que la relación se guardó
        self.assertTrue(RolePermission.objects.filter(id=rp_id).exists())
        self.assertIn(permission, role.permissions.all())
        
        # Probamos una transacción que se revierte
        try:
            with transaction.atomic():
                role_permission2 = RolePermission.objects.create(
                    role=role,
                    permission=permission,
                    granted=False  # Esto creará un duplicado y fallará
                )
                # Esto fallará por la restricción de unicidad, causando rollback
        except IntegrityError:
            pass
        
        # Verificamos que la relación original sigue existiendo y sin cambios
        self.assertTrue(RolePermission.objects.filter(id=rp_id).exists())
        stored_rp = RolePermission.objects.get(id=rp_id)
        self.assertTrue(stored_rp.granted)  # Debe seguir siendo True
        
        # Verificamos que solo existe una relación
        self.assertEqual(RolePermission.objects.filter(role=role, permission=permission).count(), 1)