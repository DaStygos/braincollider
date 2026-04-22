from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse

from .models import Problem, Submission


class ProblemsViewsTests(TestCase):
	def setUp(self):
		self.user = User.objects.create_user(username="solver", password="password123")
		self.problem_a = Problem.objects.create(
			title="Problem A",
			statement="Statement A",
			solution="Solution A",
			category="meca",
			difficulty=1,
		)
		self.problem_b = Problem.objects.create(
			title="Problem B",
			statement="Statement B",
			solution="Solution B",
			category="opt",
			difficulty=2,
		)

	def test_index_groups_problems_and_tracks_user_state(self):
		Submission.objects.create(user=self.user, problem=self.problem_a, answer="ok", is_correct=True)
		Submission.objects.create(user=self.user, problem=self.problem_b, answer="nope", is_correct=False)
		pending_problem = Problem.objects.create(
			title="Problem C",
			statement="Statement C",
			solution="Solution C",
			category="meca",
			difficulty=3,
		)
		Submission.objects.create(user=self.user, problem=pending_problem, answer="pending", is_correct=None)

		self.client.force_login(self.user)
		response = self.client.get(reverse("problems:index"))

		self.assertEqual(response.status_code, 200)
		self.assertIn(self.problem_a.id, response.context["correct_problems"])
		self.assertIn(self.problem_b.id, response.context["wrong_problems"])
		self.assertIn(pending_problem.id, response.context["pending_problems"])
		self.assertIn("meca", response.context["problems_by_category"])
		self.assertIn("opt", response.context["problems_by_category"])

	def test_problem_detail_requires_login(self):
		response = self.client.get(reverse("problems:problem_detail", args=[self.problem_a.pk]))

		self.assertEqual(response.status_code, 302)
		self.assertIn(reverse("accounts:login"), response.url)

	def test_problem_detail_creates_submission(self):
		self.client.force_login(self.user)

		response = self.client.post(
			reverse("problems:problem_detail", args=[self.problem_a.pk]),
			{"answer": "My answer"},
		)

		self.assertRedirects(response, reverse("problems:problem_detail", args=[self.problem_a.pk]))
		submission = Submission.objects.get(user=self.user, problem=self.problem_a)
		self.assertEqual(submission.answer, "My answer")
		self.assertIsNone(submission.is_correct)
		self.problem_a.refresh_from_db()
		self.assertEqual(self.problem_a.total_submissions, 1)

	def test_problem_detail_updates_existing_submission(self):
		submission = Submission.objects.create(
			user=self.user,
			problem=self.problem_a,
			answer="Old answer",
			is_correct=True,
		)
		self.problem_a.total_submissions = 1
		self.problem_a.save()

		self.client.force_login(self.user)
		response = self.client.post(
			reverse("problems:problem_detail", args=[self.problem_a.pk]),
			{"answer": "Updated answer"},
		)

		self.assertRedirects(response, reverse("problems:problem_detail", args=[self.problem_a.pk]))
		submission.refresh_from_db()
		self.assertEqual(submission.answer, "Updated answer")
		self.assertIsNone(submission.is_correct)
		self.problem_a.refresh_from_db()
		self.assertEqual(self.problem_a.total_submissions, 1)

	def test_problem_get_score_matches_difficulty(self):
		self.assertEqual(self.problem_a.get_score(), 100)
		self.assertEqual(self.problem_b.get_score(), 300)
