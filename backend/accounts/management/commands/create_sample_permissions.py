"""
Management command to create sample permissions and roles for testing.
This demonstrates the dynamic permission system functionality.
"""

from django.core.management.base import BaseCommand
from django.contrib.contenttypes.models import ContentType
from django.contrib.auth import get_user_model
from accounts.models import Permission, Role, RolePermission, UserRole

User = get_user_model()


class Command(BaseCommand):
    help = 'Create sample permissions and roles for testing the dynamic permission system'

    def add_arguments(self, parser):
        parser.add_argument(
            '--clear',
            action='store_true',
            help='Clear existing permissions and roles before creating new ones',
        )

    def handle(self, *args, **options):
        if options['clear']:
            self.stdout.write('Clearing existing permissions and roles...')
            UserRole.objects.all().delete()
            RolePermission.objects.all().delete()
            Role.objects.all().delete()
            Permission.objects.all().delete()

        self.stdout.write('Creating sample permissions and roles...')

        # Get content types for different models
        user_ct = ContentType.objects.get_for_model(User)
        
        # Create permissions for user management
        permissions_data = [
            ('Can view users', 'view_user', 'Allows viewing user details and lists'),
            ('Can add users', 'add_user', 'Allows creating new users'),
            ('Can change users', 'change_user', 'Allows editing existing users'),
            ('Can delete users', 'delete_user', 'Allows deleting users'),
            ('Can assign roles', 'assign_roles', 'Allows assigning roles to users'),
            ('Can manage permissions', 'manage_permissions', 'Allows managing system permissions'),
        ]

        permissions = {}
        for name, codename, description in permissions_data:
            permission, created = Permission.objects.get_or_create(
                codename=codename,
                content_type=user_ct,
                defaults={
                    'name': name,
                    'description': description
                }
            )
            permissions[codename] = permission
            if created:
                self.stdout.write(f'  Created permission: {permission}')
            else:
                self.stdout.write(f'  Permission already exists: {permission}')

        # Create roles
        roles_data = [
            ('Administrator', 'Full system access with all permissions', [
                'view_user', 'add_user', 'change_user', 'delete_user', 
                'assign_roles', 'manage_permissions'
            ]),
            ('User Manager', 'Can manage users but not system permissions', [
                'view_user', 'add_user', 'change_user', 'assign_roles'
            ]),
            ('Viewer', 'Read-only access to user information', [
                'view_user'
            ]),
            ('Editor', 'Can view and edit users but not create or delete', [
                'view_user', 'change_user'
            ]),
        ]

        roles = {}
        for role_name, description, permission_codenames in roles_data:
            role, created = Role.objects.get_or_create(
                name=role_name,
                defaults={'description': description}
            )
            roles[role_name] = role
            if created:
                self.stdout.write(f'  Created role: {role}')
            else:
                self.stdout.write(f'  Role already exists: {role}')

            # Assign permissions to role
            for codename in permission_codenames:
                if codename in permissions:
                    role_perm, created = RolePermission.objects.get_or_create(
                        role=role,
                        permission=permissions[codename],
                        defaults={'granted': True}
                    )
                    if created:
                        self.stdout.write(f'    Assigned permission {codename} to {role_name}')

        # Create sample users and assign roles
        admin_user, created = User.objects.get_or_create(
            username='admin_sample',
            defaults={
                'email': 'admin@example.com',
                'first_name': 'Admin',
                'last_name': 'User',
                'is_staff': True,
                'is_superuser': True,
                'role': User.ROLE_ADMIN
            }
        )
        if created:
            admin_user.set_password('admin123')
            admin_user.save()
            self.stdout.write(f'  Created admin user: {admin_user.username}')
        else:
            self.stdout.write(f'  Admin user already exists: {admin_user.username}')

        # Assign Administrator role to admin user
        user_role, created = UserRole.objects.get_or_create(
            user=admin_user,
            role=roles['Administrator'],
            defaults={'assigned_by': admin_user}
        )
        if created:
            self.stdout.write(f'    Assigned Administrator role to {admin_user.username}')

        # Create a regular user
        regular_user, created = User.objects.get_or_create(
            username='user_sample',
            defaults={
                'email': 'user@example.com',
                'first_name': 'Regular',
                'last_name': 'User',
                'role': User.ROLE_OPERADOR
            }
        )
        if created:
            regular_user.set_password('user123')
            regular_user.save()
            self.stdout.write(f'  Created regular user: {regular_user.username}')
        else:
            self.stdout.write(f'  Regular user already exists: {regular_user.username}')

        # Assign Editor role to regular user
        user_role, created = UserRole.objects.get_or_create(
            user=regular_user,
            role=roles['Editor'],
            defaults={'assigned_by': admin_user}
        )
        if created:
            self.stdout.write(f'    Assigned Editor role to {regular_user.username}')

        self.stdout.write(
            self.style.SUCCESS(
                '\nSample permissions and roles created successfully!\n'
                'You can now test the dynamic permission system:\n'
                '- Admin user: admin_sample / admin123 (Administrator role)\n'
                '- Regular user: user_sample / user123 (Editor role)\n'
            )
        )

        # Display permission summary
        self.stdout.write('\nPermission Summary:')
        for role_name, role in roles.items():
            perms = role.permissions.filter(rolepermission__granted=True)
            perm_list = ', '.join([p.codename for p in perms])
            self.stdout.write(f'  {role_name}: {perm_list}')