from django.contrib import admin
from django.contrib.auth.models import User
from django.contrib.auth.admin import UserAdmin
from django.conf import settings
from django.urls import reverse_lazy
from .models import Submission, Problem


@admin.register(Problem)
class ProblemAdmin(admin.ModelAdmin):
    list_display = (
        "title",
        "short_description",
        "author",
        "category",
        "difficulty",
    )
    search_fields = ("title", "short_description", "author__username")
    list_filter = ("author", "category", "difficulty")

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


@admin.register(Submission)
class SubmissionAdmin(admin.ModelAdmin):
    list_display = ("user", "problem", "is_correct", "submitted_at")
    list_filter = ("is_correct", "problem")
    readonly_fields = ("user", "problem", "answer", "submitted_at")


# Étendre l'admin de User
class SubmissionInline(admin.TabularInline):
    model = Submission
    fields = ("problem", "answer", "is_correct", "submitted_at")
    readonly_fields = ("problem", "answer", "submitted_at")
    extra = 0


class CustomUserAdmin(UserAdmin):
    inlines = [SubmissionInline]


# Déenregistrer l'ancien UserAdmin et enregistrer le nouveau
admin.site.unregister(User)
admin.site.register(User, CustomUserAdmin)
