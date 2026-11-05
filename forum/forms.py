from django import forms

from .models import Post, Topic


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
        fields = ["title", "description", "tags"]
        labels = {"title": "Titre du sujet", "tags": "Étiquettes"}
        help_texts = {"tags": "Choisissez les étiquettes qui décrivent votre sujet."}
        widgets = {
            "title": forms.TextInput(
                attrs={"class": "form-control", "placeholder": "Ex. : Question sur la mécanique"}
            ),
            "tags": forms.CheckboxSelectMultiple(
                attrs={"class": "form-check-input"}
            ),
        }


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
