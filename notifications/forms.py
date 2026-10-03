from django import forms


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