from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser, Permission, Role, RolePermission, UserRole


class UserRoleInline(admin.TabularInline):
    model = UserRole
    fk_name = 'user'  # Specify which foreign key to use
    extra = 0
    readonly_fields = ['assigned_at', 'is_expired']
    autocomplete_fields = ['role', 'assigned_by']
    
    def is_expired(self, obj):
        return obj.is_expired
    is_expired.boolean = True
    is_expired.short_description = 'Expired'


class CustomUserAdmin(UserAdmin):
    fieldsets = UserAdmin.fieldsets + (
        (None, {'fields': ('role', 'sucursal', 'preferences', 'last_activity')}),
    )
    list_display = ['username', 'email', 'role', 'sucursal', 'is_staff', 'last_activity']
    readonly_fields = ['last_activity']
    inlines = [UserRoleInline]


class PermissionAdmin(admin.ModelAdmin):
    list_display = ['name', 'codename', 'content_type', 'created_at']
    list_filter = ['content_type', 'created_at']
    search_fields = ['name', 'codename', 'description']
    readonly_fields = ['created_at', 'updated_at']
    ordering = ['content_type__app_label', 'content_type__model', 'codename']


class RolePermissionInline(admin.TabularInline):
    model = RolePermission
    extra = 0
    readonly_fields = ['created_at']


class RoleAdmin(admin.ModelAdmin):
    list_display = ['name', 'description', 'is_active', 'created_at']
    list_filter = ['is_active', 'created_at']
    search_fields = ['name', 'description']
    readonly_fields = ['created_at', 'updated_at']
    inlines = [RolePermissionInline]


class UserRoleAdmin(admin.ModelAdmin):
    list_display = ['user', 'role', 'assigned_by', 'assigned_at', 'expires_at', 'is_active', 'is_expired']
    list_filter = ['role', 'is_active', 'assigned_at', 'expires_at']
    search_fields = ['user__username', 'role__name', 'assigned_by__username']
    readonly_fields = ['assigned_at', 'is_expired']
    autocomplete_fields = ['user', 'role', 'assigned_by']
    
    def is_expired(self, obj):
        return obj.is_expired
    is_expired.boolean = True
    is_expired.short_description = 'Expired'


class RolePermissionAdmin(admin.ModelAdmin):
    list_display = ['role', 'permission', 'granted', 'created_at']
    list_filter = ['granted', 'role', 'permission__content_type', 'created_at']
    search_fields = ['role__name', 'permission__name', 'permission__codename']
    readonly_fields = ['created_at']
    autocomplete_fields = ['role', 'permission']


# Register models
admin.site.register(CustomUser, CustomUserAdmin)
admin.site.register(Permission, PermissionAdmin)
admin.site.register(Role, RoleAdmin)
admin.site.register(UserRole, UserRoleAdmin)
admin.site.register(RolePermission, RolePermissionAdmin)
