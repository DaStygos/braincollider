from django import forms


class BroadcastNotificationForm(forms.Form):
    message = forms.CharField(
        label='Message',
        widget=forms.Textarea(attrs={'rows': 6, 'autofocus': True}),
        max_length=1000,
    )