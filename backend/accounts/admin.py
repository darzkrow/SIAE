from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from accounts.models import CustomUser

@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    list_display = ('username', 'email', 'role', 'sucursal', 'is_staff')
    list_filter = ('role', 'is_staff', 'is_superuser', 'is_active', 'sucursal')
    search_fields = ('username', 'first_name', 'last_name', 'email')
    
    fieldsets = UserAdmin.fieldsets + (
        ('Información de Rol y Sucursal', {'fields': ('role', 'sucursal')}),
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
        ('Información de Rol y Sucursal', {'fields': ('role', 'sucursal')}),
    )
