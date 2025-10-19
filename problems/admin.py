from django.contrib import admin
from django.contrib.auth.models import User
from django.contrib.auth.admin import UserAdmin
from .models import Submission, Problem

@admin.register(Problem)
class ProblemAdmin(admin.ModelAdmin):
    list_display = ('title', 'category', 'difficulty')
    search_fields = ('title',)

@admin.register(Submission)
class SubmissionAdmin(admin.ModelAdmin):
    list_display = ("user", "problem", "is_correct", "submitted_at")
    list_filter = ("is_correct", "problem")
    readonly_fields = ('user', 'problem', 'answer', 'submitted_at')

# Étendre l'admin de User
class SubmissionInline(admin.TabularInline):
    model = Submission
    fields = ('problem', 'answer', 'is_correct', 'submitted_at')
    readonly_fields = ('problem', 'answer', 'submitted_at')
    extra = 0

class CustomUserAdmin(UserAdmin):
    inlines = [SubmissionInline]

# Déenregistrer l'ancien UserAdmin et enregistrer le nouveau
admin.site.unregister(User)
admin.site.register(User, CustomUserAdmin)

