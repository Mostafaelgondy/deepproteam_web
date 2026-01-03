from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User

class CustomUserAdmin(UserAdmin):
    model = User
    list_display = ['username', 'email', 'is_staff', 'role', 'is_approved']
    fieldsets = UserAdmin.fieldsets + (
        (None, {'fields': ('role', 'phone_number', 'address', 'is_approved')}),
    )

admin.site.register(User, CustomUserAdmin)
