from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse

from problems.models import Problem, Submission


class LeaderboardViewsTests(TestCase):
	def test_leaderboard_sorts_and_filters_zero_scores(self):
		top_user = User.objects.create_user(username="top", password="password123")
		low_user = User.objects.create_user(username="low", password="password123")
		zero_user = User.objects.create_user(username="zero", password="password123")

		high_problem = Problem.objects.create(
			title="High",
			statement="Statement",
			solution="Solution",
			category="autre",
			difficulty=5,
		)
		low_problem = Problem.objects.create(
			title="Low",
			statement="Statement",
			solution="Solution",
			category="autre",
			difficulty=1,
		)

		Submission.objects.create(user=top_user, problem=high_problem, answer="ok", is_correct=True)
		Submission.objects.create(user=low_user, problem=low_problem, answer="ok", is_correct=True)
		Submission.objects.create(user=zero_user, problem=low_problem, answer="wrong", is_correct=False)

		response = self.client.get(reverse("leaderboard:leaderboard"))

		self.assertEqual(response.status_code, 200)
		leaderboard = response.context["leaderboard"]
		self.assertEqual([entry["user"].username for entry in leaderboard], ["top", "low"])
		self.assertEqual(leaderboard[0]["total_score"], high_problem.get_score())
		self.assertEqual(leaderboard[1]["total_score"], low_problem.get_score())
