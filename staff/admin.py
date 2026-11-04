from django.contrib import admin
from django.conf import settings
from django.urls import reverse_lazy
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
    list_display = (
        "title",
        "short_description",
        "author",
        "category",
        "difficulty",
        "suggested_at",
        "status",
    )
    list_filter = ("status", "suggested_at")
    search_fields = ("title", "short_description", "statement")
    readonly_fields = ("author", "suggested_at")
    actions = (accept_suggestions, reject_suggestions)

    class Media:
        css = {
            "all": (
                "https://cdn.jsdelivr.net/npm/katex@0.16.11/dist/katex.min.css",
            )
        }
        js = (
            "https://cdn.jsdelivr.net/npm/katex@0.16.11/dist/katex.min.js",
            "https://cdn.jsdelivr.net/npm/katex@0.16.11/dist/contrib/auto-render.min.js",
            "js/statement-image-upload.js",
            "js/admin-problem-preview.js",
        )

    def formfield_for_dbfield(self, db_field, request, **kwargs):
        formfield = super().formfield_for_dbfield(db_field, request, **kwargs)
        if db_field.name == "statement" and formfield:
            formfield.widget.attrs["data-image-upload-url"] = reverse_lazy(
                "staff:upload_statement_image"
            )
            formfield.widget.attrs["data-admin-statement-preview"] = "true"
            formfield.widget.attrs["data-media-prefix"] = settings.MEDIA_URL
        return formfield

    fieldsets = (
        (
            "Suggestion",
            {
                "fields": (
                    "title",
                    "short_description",
                    "statement",
                    "solution",
                    "category",
                    "difficulty",
                ),
            },
        ),
        (
            "Validation",
            {
                "fields": ("status",),
                "description": "Relisez le contenu puis choisissez une décision. Les actions de validation sont aussi disponibles dans la liste.",
            },
        ),
        (
            "Informations",
            {
                "fields": ("author", "suggested_at"),
            },
        ),
    )
