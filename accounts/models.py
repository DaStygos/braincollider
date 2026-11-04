# accounts/models.py
from django.db import models
from django.db.models import Case, IntegerField, Sum, Value, When
from django.db.models.functions import Coalesce
from django.contrib.auth.models import User
from django.templatetags.static import static
from django.utils import timezone

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    avatar = models.ImageField(upload_to='avatars/', blank=True, null=True)
    previous_scores = models.JSONField(default=list, blank=True)
    accepted_terms = models.BooleanField(default=False)
    allow_leaderboard_display = models.BooleanField(default=False)
    age_confirmation = models.BooleanField(default=False)

    def get_avatar_url(self):
        if self.avatar:
            return self.avatar.url
        return static('/images/default_avatar.png')
    
    def get_submissions(self):
        return self.user.submission_set.all()

    def get_total_score(self):
        from problems.models import BAREME, Submission

        score_case = Case(
            *[When(problem__difficulty=difficulty, then=Value(points)) for difficulty, points in BAREME.items()],
            default=Value(0),
            output_field=IntegerField(),
        )
        return Submission.objects.filter(user=self.user, is_correct=True).aggregate(
            score=Coalesce(Sum(score_case), Value(0))
        )["score"]

    def record_score_if_changed(self):
        score = self.get_total_score()
        if not self.previous_scores or self.previous_scores[-1][0] != score:
            self.previous_scores.append((score, timezone.now().isoformat()))
            self.save(update_fields=["previous_scores"])
        return score

    def get_unread_notifications_count(self):
        return self.user.notification_set.filter(read=False).count()

    def __str__(self):
        return self.user.username
