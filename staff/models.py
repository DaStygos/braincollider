from django.db import models
from django.contrib.auth.models import User
from django.dispatch import receiver
from notifications.models import Notification
from problems.models import CATEGORY_CHOICES, DIFFICULTY_CHOICES
from django.db.models.signals import post_save

STATUS_CHOICES = [
    ("pending", "En attente"),
    ("accepted", "Acceptée"),
    ("rejected", "Rejetée"),
]

class ProblemSuggestion(models.Model):
    title = models.CharField(max_length=200)
    statement = models.TextField()
    solution = models.TextField(blank=True)
    category = models.CharField(max_length=10, choices=CATEGORY_CHOICES, default="autre")
    difficulty = models.PositiveSmallIntegerField(choices=DIFFICULTY_CHOICES, default=1)

    author = models.ForeignKey(User, on_delete=models.CASCADE)
    suggested_at = models.DateTimeField(auto_now_add=True)


    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default="pending")

    def __str__(self):
        return f"[{self.get_status_display()}] {self.title}"

@receiver(post_save, sender=ProblemSuggestion)
def create_problem_on_acceptance(sender, instance, created, **kwargs):
    if not created and instance.status == "accepted":
        from problems.models import Problem
        Problem.objects.create(
            title=instance.title,
            statement=instance.statement,
            solution=instance.solution,
            category=instance.category,
            difficulty=instance.difficulty,
        )
        Notification.objects.create(
            user=instance.author,
            message=f"Votre suggestion de problème '{instance.title}' a été acceptée et ajoutée à la base de problèmes. Merci de votre contribution !",
        )
    elif instance.status == "rejected":
        Notification.objects.create(
            user=instance.author,
            message=f"Votre suggestion de problème '{instance.title}' a été rejetée.",
        )
    
