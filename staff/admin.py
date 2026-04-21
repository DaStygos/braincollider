from django.contrib import admin
from .models import ProblemSuggestion

# Register your models here.
@admin.register(ProblemSuggestion)
class ProblemSuggestionAdmin(admin.ModelAdmin):
    list_display = ("title", "author", "suggested_at", "status")
    list_filter = ("status", "suggested_at")
    search_fields = ("title", "description")