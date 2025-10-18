from django import forms
from django.contrib.auth.forms import UserCreationForm, PasswordChangeForm
from django.contrib.auth.models import User
from .models import Profile

class SignUpForm(UserCreationForm):
    class Meta:
        model = User
        fields = ("username", "password1", "password2")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for fieldname in ["username", "password1", "password2"]:
            self.fields[fieldname].help_text = None

class PasswordChangeFormCustom(PasswordChangeForm):
    old_password = forms.CharField(label="Ancien mot de passe", widget=forms.PasswordInput(attrs={
        'class': 'form-control',
        'placeholder': 'Ancien mot de passe',
    }))
    new_password1 = forms.CharField(label="Nouveau mot de passe", widget=forms.PasswordInput(attrs={
        'class': 'form-control',
        'placeholder': 'Nouveau mot de passe',
    }))
    new_password2 = forms.CharField(label="Confirmer le nouveau mot de passe", widget=forms.PasswordInput(attrs={
        'class': 'form-control',
        'placeholder': 'Confirmer le nouveau mot de passe',
    }))

class ProfileUpdateForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['avatar']

        widgets = {
            'avatar': forms.ClearableFileInput(attrs={
                'class': 'form-control',
            }),
        }


class UserUpdateForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['username', 'email']
        widgets = {
            'username': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': "Nom d'utilisateur"
            }),
            'email': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'Adresse email'
            }),
            'avatar': forms.ClearableFileInput(attrs={
                'class': 'form-control',
                'placeholder': 'Photo de profil'
            }),
        }
