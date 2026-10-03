from django import forms
from django.conf import settings
from django.contrib.auth.models import User
from .models import ProblemSuggestion


class ProblemSuggestionForm(forms.ModelForm):
    author_type = forms.ChoiceField(
        choices=(),
        label="Type d'auteur",
        required=False,
        widget=forms.Select(attrs={"class": "form-select", "id": "id_author_type"}),
    )
    author_year = forms.ChoiceField(
        choices=(),
        label="Année",
        required=False,
        widget=forms.Select(attrs={"class": "form-select", "id": "id_author_year"}),
    )
    author = forms.ModelChoiceField(
        queryset=User.objects.none(),
        required=False,
        widget=forms.HiddenInput(),
    )

    def __init__(self, *args, user=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.user = user
        allowed_usernames = set(settings.PROBLEM_SUGGESTION_AUTHOR_USERNAMES)
        allowed_usernames.add(user.username)
        self.fields["author"].queryset = User.objects.filter(
            username__in=allowed_usernames,
        )
        current_user_value = "__current_user__"
        self.fields["author_type"].choices = [
            (current_user_value, f"Moi ({user.username})"),
            *[
                (name, name)
                for name in settings.PROBLEM_SUGGESTION_AUTHOR_NAMES
            ],
        ]
        self.fields["author_year"].choices = [
            (str(year), str(year))
            for year in settings.PROBLEM_SUGGESTION_AUTHOR_YEARS
        ]
        self.fields["author_type"].initial = current_user_value

    def clean(self):
        cleaned_data = super().clean()
        author_type = cleaned_data.get("author_type")
        author_year = cleaned_data.get("author_year")

        if not author_type:
            cleaned_data["author"] = cleaned_data.get("author") or self.user
            return cleaned_data
        if author_type == "__current_user__":
            cleaned_data["author"] = self.user
            return cleaned_data

        allowed_names = settings.PROBLEM_SUGGESTION_AUTHOR_NAMES
        allowed_years = {str(year) for year in settings.PROBLEM_SUGGESTION_AUTHOR_YEARS}
        if author_type not in allowed_names:
            self.add_error("author_type", "Ce type d'auteur n'est pas disponible.")
        if author_year not in allowed_years:
            self.add_error("author_year", "Veuillez choisir une année.")
        if self.errors:
            return cleaned_data

        username = f"{author_type} - {author_year}"
        author, created = User.objects.get_or_create(username=username)
        if created:
            author.is_active = False
            author.set_unusable_password()
            author.save(update_fields=["is_active", "password"])
        cleaned_data["author"] = author
        return cleaned_data

    class Meta:
        model = ProblemSuggestion
        fields = [
            "title", "statement", "solution", "category", "difficulty",
            "author_type", "author_year", "author",
        ]
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
