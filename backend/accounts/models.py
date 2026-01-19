from django.db import models
from django.contrib.auth.models import AbstractUser, UserManager

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

    # Use custom manager to enforce role for superusers
    objects = CustomUserManager()

    def __str__(self):
        return f"{self.username} ({self.role})"
    
    class Meta:
        verbose_name = 'Usuario'
        verbose_name_plural = 'Usuarios'

