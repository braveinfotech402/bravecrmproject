from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import CustomUser,Client,Domain,Reseller

class CustomUserAdmin(BaseUserAdmin):
    model = CustomUser
    list_display = ('email', 'is_superadmin', 'is_reseller', 'is_client', 'is_staff_user','is_lead', 'is_active')
    list_filter = ('is_superadmin', 'is_reseller', 'is_client', 'is_staff_user', 'is_lead')
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Profile', {'fields': ('first_name', 'last_name', 'profile_image')}),
        ('Verification', {'fields': ('is_verified', 'verification_code')}),
        ('Roles', {'fields': ('is_superadmin', 'is_reseller', 'is_client', 'is_staff_user')}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser')}),
        ('Important Dates', {'fields': ('last_login', 'date_joined')}),
    )
    search_fields = ('email',)
    ordering = ('email',)

admin.site.register(CustomUser, CustomUserAdmin)
admin.site.register(Client)
admin.site.register(Domain)
admin.site.register(Reseller)


