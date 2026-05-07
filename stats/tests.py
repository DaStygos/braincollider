from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse

from problems.models import Problem, Submission


class StatsViewsTests(TestCase):
    def setUp(self):
        self.alice = User.objects.create_user(username="alice", password="password123")
        self.bob = User.objects.create_user(username="bob", password="password123")
        self.problem = Problem.objects.create(
            title="Physics problem",
            statement="Statement",
            solution="Solution",
            category="meca",
            difficulty=3,
        )
        Submission.objects.create(user=self.alice, problem=self.problem, answer="ok", is_correct=True)
        Submission.objects.create(user=self.bob, problem=self.problem, answer="review", is_correct=False)

    def test_dashboard_is_accessible_and_exposes_key_metrics(self):
        response = self.client.get(reverse("stats:dashboard"))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context["total_users"], 2)
        self.assertEqual(response.context["total_problems"], 1)
        self.assertEqual(response.context["total_submissions"], 2)
        self.assertEqual(response.context["correct_submissions"], 1)
        self.assertEqual(response.context["pending_submissions"], 0)
        self.assertEqual(len(response.context["activity_labels"]), len(response.context["activity_points"]))