from django.db import models
from django.contrib.auth.models import AbstractUser, UserManager
from django.contrib.contenttypes.models import ContentType


class Permission(models.Model):
    """
    Dynamic permission model for granular access control.
    Replaces hardcoded permissions with database-driven approach.
    """
    name = models.CharField(max_length=100, unique=True, help_text="Human-readable permission name")
    codename = models.CharField(max_length=100, unique=True, help_text="Unique permission identifier")
    content_type = models.ForeignKey(
        ContentType, 
        on_delete=models.CASCADE,
        related_name='dynamic_permissions',
        help_text="The model this permission applies to"
    )
    description = models.TextField(blank=True, help_text="Detailed description of what this permission allows")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Permiso'
        verbose_name_plural = 'Permisos'
        unique_together = ('content_type', 'codename')
        ordering = ['content_type__app_label', 'content_type__model', 'codename']
    
    def __str__(self):
        return f"{self.content_type.app_label}.{self.codename}"


class Role(models.Model):
    """
    Role model for grouping permissions.
    Provides a way to assign multiple permissions to users through roles.
    """
    name = models.CharField(max_length=50, unique=True, help_text="Role name")
    description = models.TextField(blank=True, help_text="Role description")
    permissions = models.ManyToManyField(
        Permission, 
        through='RolePermission',
        blank=True,
        help_text="Permissions granted to this role"
    )
    is_active = models.BooleanField(default=True, help_text="Whether this role is active")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Rol'
        verbose_name_plural = 'Roles'
        ordering = ['name']
    
    def __str__(self):
        return self.name


class RolePermission(models.Model):
    """
    Through model for Role-Permission relationship.
    Allows for additional metadata on permission assignments.
    """
    role = models.ForeignKey(Role, on_delete=models.CASCADE)
    permission = models.ForeignKey(Permission, on_delete=models.CASCADE)
    granted = models.BooleanField(default=True, help_text="Whether permission is granted or denied")
    conditions = models.JSONField(
        default=dict, 
        blank=True,
        help_text="Additional conditions for permission (JSON format)"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = 'Permiso de Rol'
        verbose_name_plural = 'Permisos de Roles'
        unique_together = ('role', 'permission')
    
    def __str__(self):
        status = "granted" if self.granted else "denied"
        return f"{self.role.name} - {self.permission.codename} ({status})"


class UserRole(models.Model):
    """
    Through model for User-Role relationship.
    Tracks role assignments with metadata like assignment date and expiration.
    """
    user = models.ForeignKey('CustomUser', on_delete=models.CASCADE)
    role = models.ForeignKey(Role, on_delete=models.CASCADE)
    assigned_by = models.ForeignKey(
        'CustomUser', 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        related_name='assigned_roles',
        help_text="User who assigned this role"
    )
    assigned_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField(
        null=True, 
        blank=True,
        help_text="When this role assignment expires (optional)"
    )
    is_active = models.BooleanField(default=True, help_text="Whether this role assignment is active")
    
    class Meta:
        verbose_name = 'Rol de Usuario'
        verbose_name_plural = 'Roles de Usuarios'
        unique_together = ('user', 'role')
        ordering = ['-assigned_at']
    
    def __str__(self):
        return f"{self.user.username} - {self.role.name}"
    
    @property
    def is_expired(self):
        """Check if the role assignment has expired."""
        if not self.expires_at:
            return False
        from django.utils import timezone
        return timezone.now() > self.expires_at

class CustomUserManager(UserManager):
    def create_superuser(self, username, email=None, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        # Ensure superusers are assigned ADMIN role
        extra_fields['role'] = CustomUser.ROLE_ADMIN
        return super().create_superuser(username, email, password, **extra_fields)


class CustomUser(AbstractUser):
    ROLE_ADMIN = 'ADMIN'
    ROLE_OPERADOR = 'OPERADOR'
    ROLE_CHOICES = [
        (ROLE_ADMIN, 'Administrador'),
        (ROLE_OPERADOR, 'Operador'),
    ]
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default=ROLE_OPERADOR)
    sucursal = models.ForeignKey('institucion.Sucursal', on_delete=models.SET_NULL, null=True, blank=True)
    
    # Dynamic role system - many-to-many relationship with Role model
    roles = models.ManyToManyField(
        Role, 
        through=UserRole,
        through_fields=('user', 'role'),
        blank=True,
        help_text="Dynamic roles assigned to this user"
    )
    
    # Additional fields for enhanced functionality
    preferences = models.JSONField(
        default=dict, 
        blank=True,
        help_text="User preferences and settings (JSON format)"
    )
    last_activity = models.DateTimeField(auto_now=True, help_text="Last activity timestamp")

    # Use custom manager to enforce role for superusers
    objects = CustomUserManager()

    def __str__(self):
        return f"{self.username} ({self.role})"
    
    def get_dynamic_permissions(self):
        """
        Get all permissions from assigned dynamic roles.
        Returns a queryset of Permission objects.
        """
        from django.utils import timezone
        now = timezone.now()
        
        # Get active role assignments that haven't expired
        active_user_roles = self.userrole_set.filter(
            is_active=True,
            role__is_active=True
        ).filter(
            models.Q(expires_at__isnull=True) | models.Q(expires_at__gt=now)
        )
        
        # Get permissions from active roles where permission is granted
        permissions = Permission.objects.filter(
            rolepermission__role__in=[ur.role for ur in active_user_roles],
            rolepermission__granted=True
        ).distinct()
        
        return permissions
    
    def has_dynamic_permission(self, permission_codename, content_type=None):
        """
        Check if user has a specific dynamic permission.
        
        Args:
            permission_codename: The codename of the permission to check
            content_type: Optional ContentType to filter by
            
        Returns:
            bool: True if user has the permission, False otherwise
        """
        permissions = self.get_dynamic_permissions()
        
        if content_type:
            permissions = permissions.filter(content_type=content_type)
            
        return permissions.filter(codename=permission_codename).exists()
    
    class Meta:
        verbose_name = 'Usuario'
        verbose_name_plural = 'Usuarios'

