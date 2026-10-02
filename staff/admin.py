from django.contrib import admin
from .models import ProblemSuggestion


@admin.action(description="Accepter les suggestions sélectionnées")
def accept_suggestions(modeladmin, request, queryset):
    suggestions = queryset.filter(status="pending")
    updated = 0
    for suggestion in suggestions:
        suggestion.status = "accepted"
        suggestion.save()
        updated += 1
    modeladmin.message_user(request, f"{updated} suggestion(s) acceptée(s).")


@admin.action(description="Rejeter les suggestions sélectionnées")
def reject_suggestions(modeladmin, request, queryset):
    suggestions = queryset.filter(status="pending")
    updated = 0
    for suggestion in suggestions:
        suggestion.status = "rejected"
        suggestion.save()
        updated += 1
    modeladmin.message_user(request, f"{updated} suggestion(s) rejetée(s).")


@admin.register(ProblemSuggestion)
class ProblemSuggestionAdmin(admin.ModelAdmin):
    list_display = ("title", "author", "category", "difficulty", "suggested_at", "status")
    list_filter = ("status", "suggested_at")
    search_fields = ("title", "statement")
    readonly_fields = ("author", "suggested_at")
    actions = (accept_suggestions, reject_suggestions)
    fieldsets = (
        ("Suggestion", {
            "fields": ("title", "statement", "solution", "category", "difficulty"),
        }),
        ("Validation", {
            "fields": ("status",),
            "description": "Relisez le contenu puis choisissez une décision. Les actions de validation sont aussi disponibles dans la liste.",
        }),
        ("Informations", {
            "fields": ("author", "suggested_at"),
        }),
    )