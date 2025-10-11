from django.contrib import admin
from django.contrib.auth.models import User
from django.contrib.auth.admin import UserAdmin
from .models import Submission, Problem

@admin.register(Problem)
class ProblemAdmin(admin.ModelAdmin):
    list_display = ('title', 'category', 'difficulty')
    search_fields = ('title',)

# Créer un inline pour les soumissions
class SubmissionInline(admin.TabularInline):
    model = Submission
    extra = 0  # pas de formulaire vide supplémentaire
    readonly_fields = ('problem',)  # si tu veux empêcher la modification du problème
    can_delete = True

# Étendre l'admin de User
class CustomUserAdmin(UserAdmin):
    inlines = [SubmissionInline]

# Déenregistrer l'ancien UserAdmin et enregistrer le nouveau
admin.site.unregister(User)
admin.site.register(User, CustomUserAdmin)

