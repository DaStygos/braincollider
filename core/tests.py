from django.test import TestCase, override_settings
from django.urls import reverse
from django.contrib.auth.models import User

from problems.models import Problem, Submission


class CoreViewsTests(TestCase):
	def test_home_page_loads(self):
		response = self.client.get(reverse("core:home"))

		self.assertEqual(response.status_code, 200)

	def test_home_page_exposes_live_platform_metrics(self):
		problem = Problem.objects.create(
			title="Problem",
			statement="Statement",
			solution="Solution",
		)
		user = User.objects.create_user(username="solver", password="password")
		Submission.objects.create(
			user=user,
			problem=problem,
			answer="Answer",
			is_correct=True,
		)

		response = self.client.get(reverse("core:home"))

		self.assertEqual(response.context["home_metrics"], {
			"problem_count": 1,
			"accepted_submission_count": 1,
			"solving_member_count": 1,
		})
		self.assertNotContains(response, "120+")
		self.assertNotContains(response, "+12%")
		self.assertNotContains(response, "#14")

	@override_settings(DEBUG=False)
	def test_unknown_url_renders_not_found_page(self):
		response = self.client.get("/url-inconnue/", follow=False)

		self.assertEqual(response.status_code, 404)
		self.assertTemplateUsed(response, "errors/404.html")
		self.assertContains(response, "Page introuvable", status_code=404)

	@override_settings(DEBUG=False)
	def test_unknown_problem_url_identifies_problem(self):
		user = User.objects.create_user(username="tester", password="password")
		self.client.force_login(user)

		response = self.client.get("/problems/140/", follow=False)

		self.assertEqual(response.status_code, 404)
		self.assertContains(response, "Problème introuvable", status_code=404)

	@override_settings(DEBUG=False)
	def test_unknown_user_url_identifies_user(self):
		response = self.client.get("/accounts/u/inconnu/", follow=False)

		self.assertEqual(response.status_code, 404)
		self.assertContains(response, "Utilisateur introuvable", status_code=404)
