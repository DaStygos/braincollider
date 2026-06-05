from django import forms
from django.contrib.auth.forms import UserCreationForm, PasswordChangeForm
from django.contrib.auth.models import User
from .models import Profile


FORM_CONTROL_CLASS = {"class": "form-control"}


def form_control_attrs(**extra_attrs):
    attrs = FORM_CONTROL_CLASS.copy()
    attrs.update(extra_attrs)
    return attrs

class SignUpForm(UserCreationForm):
    accepted_terms = forms.BooleanField(
        label="J'accepte les CGU",
        required=True,
        widget=forms.CheckboxInput(),
    )
    allow_leaderboard_display = forms.BooleanField(
        label="J'autorise l'affichage de mon pseudo et de mon profil dans les classements",
        required=False,
        widget=forms.CheckboxInput(),
    )
    age_confirmation = forms.BooleanField(
        label="Je confirme avoir 15 ans ou disposer de l'autorisation de mon tuteur légal",
        required=True,
        widget=forms.CheckboxInput(),
    )

    class Meta:
        model = User
        fields = ("username", "password1", "password2")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for fieldname in ["username", "password1", "password2"]:
            self.fields[fieldname].help_text = None
        self.fields["password1"].widget.attrs.setdefault("autocomplete", "new-password")
        self.fields["password2"].widget.attrs.setdefault("autocomplete", "new-password")

    def save(self, commit=True):
        user = super().save(commit=commit)
        if commit:
            profile = user.profile
            profile.accepted_terms = self.cleaned_data["accepted_terms"]
            profile.allow_leaderboard_display = self.cleaned_data["allow_leaderboard_display"]
            profile.age_confirmation = self.cleaned_data["age_confirmation"]
            profile.save(update_fields=["accepted_terms", "allow_leaderboard_display", "age_confirmation"])
        return user

class PasswordChangeFormCustom(PasswordChangeForm):
    old_password = forms.CharField(
        label="Ancien mot de passe",
        widget=forms.PasswordInput(attrs=form_control_attrs(placeholder='Ancien mot de passe')),
    )
    new_password1 = forms.CharField(
        label="Nouveau mot de passe",
        widget=forms.PasswordInput(attrs=form_control_attrs(placeholder='Nouveau mot de passe')),
    )
    new_password2 = forms.CharField(
        label="Confirmer le nouveau mot de passe",
        widget=forms.PasswordInput(attrs=form_control_attrs(placeholder='Confirmer le nouveau mot de passe')),
    )

class ProfileUpdateForm(forms.ModelForm):
    allow_leaderboard_display = forms.BooleanField(
        label="Afficher mon pseudo et mon profil dans les classements",
        required=False,
        widget=forms.CheckboxInput(),
    )

    class Meta:
        model = Profile
        fields = ['avatar', 'allow_leaderboard_display']

        widgets = {
            'avatar': forms.ClearableFileInput(attrs={
                **FORM_CONTROL_CLASS,
            }),
            'allow_leaderboard_display': forms.CheckboxInput(),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["allow_leaderboard_display"].initial = self.instance.allow_leaderboard_display


class UserUpdateForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['username', 'email']
        widgets = {
            'username': forms.TextInput(attrs=form_control_attrs(placeholder="Nom d'utilisateur")),
            'email': forms.EmailInput(attrs=form_control_attrs(placeholder='Adresse email')),
        }
