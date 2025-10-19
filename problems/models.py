from django.db import models
from django.contrib.auth.models import User

CATEGORY_CHOICES = [
    ('meca', 'Mécanique'),
    ('opt', 'Optique'),
    ('ond', 'Ondes'),
    ('thermo', 'Thermodynamique'),
    ('elec', 'Électromagnétisme'),
    ('autre', 'Autre'),
]

DIFFICULTY_CHOICES = [
    (1, '★☆☆☆☆'),
    (2, '★★☆☆☆'),
    (3, '★★★☆☆'),
    (4, '★★★★☆'),
    (5, '★★★★★'),
]

BAREME = {
    1: 100,
    2: 300,
    3: 500,
    4: 750,
    5: 1000,
}

class Problem(models.Model):
    title = models.CharField(max_length=200)
    statement = models.TextField()
    category = models.CharField(max_length=10, choices=CATEGORY_CHOICES, default='autre')
    expected_solution = models.TextField()
    difficulty = models.PositiveSmallIntegerField(choices=DIFFICULTY_CHOICES, default=1)

    def __str__(self):
        return self.title

    def get_score(self):
        return BAREME.get(self.difficulty, 0)


class Submission(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    problem = models.ForeignKey(Problem, on_delete=models.CASCADE)
    answer = models.TextField()
    is_correct = models.BooleanField(null=True, blank=True)
    submitted_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.problem.title}"
