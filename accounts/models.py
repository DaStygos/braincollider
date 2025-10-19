# accounts/models.py
from django.db import models
from django.contrib.auth.models import User
from django.templatetags.static import static
from django.utils import timezone

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    avatar = models.ImageField(upload_to='avatars/', default='avatars/default_avatar.png', blank=True)
    previous_scores = models.JSONField(default=list, blank=True)

    def get_avatar_url(self):
        if self.avatar:
            return self.avatar.url
        return static('/images/default_avatar.png')
    
    def get_submissions(self):
        return self.user.submission_set.all()

    def get_total_score(self):
        submissions = self.get_submissions()
        score = sum(submission.problem.get_score() for submission in submissions if submission.is_correct)
        if not self.previous_scores or self.previous_scores[-1][0] != score:
            self.previous_scores.append((score, timezone.now().isoformat()))
            self.save()
        return score

    def get_unread_notifications_count(self):
        return self.user.notification_set.filter(read=False).count()

    def __str__(self):
        return self.user.username
