from django.contrib import admin
from django.contrib.auth.models import User
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import Profile

# Inline pour le profil
class ProfileInline(admin.StackedInline):
    model = Profile
    can_delete = False
    verbose_name_plural = 'Profil'

# Étendre UserAdmin pour inclure l'inline
class UserAdmin(BaseUserAdmin):
    inlines = (ProfileInline,)

# Désenregistrer l'ancien UserAdmin et enregistrer le nouveau
admin.site.unregister(User)
admin.site.register(User, UserAdmin)
