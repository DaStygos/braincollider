# accounts/models.py
from django.db import models
from django.contrib.auth.models import User
from django.templatetags.static import static

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    avatar = models.ImageField(upload_to='avatars/', default='avatars/default_avatar.png', blank=True)

    def get_avatar_url(self):
        if self.avatar:
            return self.avatar.url
        return static('/images/default_avatar.png')

    def __str__(self):
        return self.user.username
