from django import forms
from django.contrib.admin.views.decorators import staff_member_required
from .models import ProblemSuggestion

class ProblemSuggestionForm(forms.ModelForm):
    class Meta:
        model = ProblemSuggestion
        fields = ["title", "statement", "solution", "category", "difficulty"]