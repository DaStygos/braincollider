from django import forms
from django.core.exceptions import ValidationError


class BroadcastNotificationForm(forms.Form):
    message = forms.CharField(
        label='Message',
        widget=forms.Textarea(attrs={'rows': 6, 'autofocus': True}),
        max_length=1000,
    )
    redirect_url = forms.CharField(
        label='Lien de redirection (optionnel)',
        required=False,
        max_length=500,
    )

    def clean_redirect_url(self):
        url = self.cleaned_data["redirect_url"].strip()
        if url and (not url.startswith("/") or url.startswith("//") or "\\" in url):
            raise ValidationError("Utilisez un chemin local commençant par /.")
        return url
