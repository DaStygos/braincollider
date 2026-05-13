from django import forms
from django.contrib.admin.views.decorators import staff_member_required
from .models import ProblemSuggestion

class ProblemSuggestionForm(forms.ModelForm):
    class Meta:
        model = ProblemSuggestion
        fields = ["title", "statement", "solution", "category", "difficulty"]
        widgets = {
            "title": forms.TextInput(attrs={"class": "form-control", "placeholder": "Titre du problème"}),
            "statement": forms.Textarea(attrs={
                "class": "form-control",
                "rows": 8,
                "data-live-math-preview": "statement-preview",
            }),
            "solution": forms.Textarea(attrs={
                "class": "form-control",
                "rows": 8,
                "data-live-math-preview": "solution-preview",
            }),
            "category": forms.Select(attrs={"class": "form-select"}),
            "difficulty": forms.Select(attrs={"class": "form-select"}),
        }