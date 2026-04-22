from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse

from problems.models import Problem, Submission


class AccountsViewsTests(TestCase):
	def test_signup_creates_user_and_profile(self):
		response = self.client.post(
			reverse("accounts:signup"),
			{
				"username": "newuser",
				"password1": "Testpass123!",
				"password2": "Testpass123!",
			},
		)

		self.assertRedirects(response, reverse("accounts:profile"))
		self.assertTrue(User.objects.filter(username="newuser").exists())
		user = User.objects.get(username="newuser")
		self.assertTrue(hasattr(user, "profile"))

	def test_profile_requires_login(self):
		response = self.client.get(reverse("accounts:profile"))

		self.assertEqual(response.status_code, 302)
		self.assertIn(reverse("accounts:login"), response.url)

	def test_profile_shows_score_and_updates_history(self):
		user = User.objects.create_user(username="player", password="password123")
		problem = Problem.objects.create(
			title="Physics problem",
			statement="Statement",
			solution="Solution",
			category="autre",
			difficulty=3,
		)
		Submission.objects.create(user=user, problem=problem, answer="done", is_correct=True)

		self.client.force_login(user)
		response = self.client.get(reverse("accounts:profile"))

		self.assertEqual(response.status_code, 200)
		self.assertEqual(response.context["total_score"], problem.get_score())
		user.refresh_from_db()
		self.assertEqual(len(user.profile.previous_scores), 1)

	def test_edit_profile_updates_user_fields(self):
		user = User.objects.create_user(username="player", password="password123", email="old@example.com")
		self.client.force_login(user)

		response = self.client.post(
			reverse("accounts:edit_profile"),
			{
				"username": "updated",
				"email": "updated@example.com",
			},
		)

		self.assertRedirects(response, reverse("accounts:profile"))
		user.refresh_from_db()
		self.assertEqual(user.username, "updated")
		self.assertEqual(user.email, "updated@example.com")
