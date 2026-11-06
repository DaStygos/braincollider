from django import forms

from .models import Post, Topic
from problems.models import Problem


class ProblemSearchSelect(forms.SelectMultiple):
    template_name = "django/forms/widgets/select.html"


class TopicForm(forms.ModelForm):
    description = forms.CharField(
        label="Description / contexte",
        max_length=10000,
        help_text="Présentez votre question ou apportez le contexte utile.",
        widget=forms.Textarea(
            attrs={
                "class": "form-control",
                "rows": 6,
                "placeholder": "Décrivez votre question ou son contexte…",
            }
        ),
    )

    class Meta:
        model = Topic
        fields = ["title", "description", "tags", "problems"]
        labels = {"title": "Titre du sujet", "tags": "Étiquettes", "problems": "Problèmes associés"}
        help_texts = {"tags": "Choisissez les étiquettes qui décrivent votre sujet."}
        widgets = {
            "title": forms.TextInput(
                attrs={"class": "form-control", "placeholder": "Ex. : Question sur la mécanique"}
            ),
            "tags": forms.CheckboxSelectMultiple(
                attrs={"class": "form-check-input"}
            ),
            "problems": ProblemSearchSelect(
                attrs={
                    "class": "form-select",
                    "size": 8,
                    "data-problem-picker": "true",
                    "aria-label": "Problèmes associés",
                }
            ),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["problems"].queryset = Problem.objects.order_by("title")
        self.fields["problems"].label_from_instance = (
            lambda problem: f"{problem.title} · {problem.get_category_display()}"
        )


class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ["content"]
        labels = {"content": "Votre réponse"}
        widgets = {
            "content": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 5,
                    "placeholder": "Rédigez votre réponse…",
                }
            )
        }
