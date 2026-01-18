from django.db import models
from django.contrib.auth.models import AbstractUser

class CustomUser(AbstractUser):
    ROLE_ADMIN = 'ADMIN'
    ROLE_OPERADOR = 'OPERADOR'
    ROLE_CHOICES = [
        (ROLE_ADMIN, 'Administrador'),
        (ROLE_OPERADOR, 'Operador'),
    ]
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default=ROLE_OPERADOR)
    sucursal = models.ForeignKey('institucion.Sucursal', on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        return f"{self.username} ({self.role})"
    
    class Meta:
        verbose_name = 'Usuario'
        verbose_name_plural = 'Usuarios'

