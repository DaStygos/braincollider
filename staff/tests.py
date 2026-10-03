from django.contrib.auth.models import User
from django.test import TestCase, override_settings
from django.urls import reverse

from problems.models import Problem, Submission
from .models import ProblemSuggestion


class PendingSubmissionsAccessTests(TestCase):
	def setUp(self):
		self.staff_user = User.objects.create_user(
			username="staff",
			password="password123",
			is_staff=True,
		)
		self.reviewer = User.objects.create_user(username="reviewer", password="password123")
		self.other_user = User.objects.create_user(username="other", password="password123")

		self.problem_a = Problem.objects.create(
			title="Problem A",
			statement="Statement A",
			category="autre",
			solution="Solution A",
			difficulty=1,
		)
		self.problem_b = Problem.objects.create(
			title="Problem B",
			statement="Statement B",
			category="autre",
			solution="Solution B",
			difficulty=1,
		)

		Submission.objects.create(
			user=self.reviewer,
			problem=self.problem_a,
			answer="42",
			is_correct=True,
		)
		self.accessible_submission = Submission.objects.create(
			user=self.other_user,
			problem=self.problem_a,
			answer="wrong",
			is_correct=None,
		)
		self.hidden_submission = Submission.objects.create(
			user=self.other_user,
			problem=self.problem_b,
			answer="wrong",
			is_correct=None,
		)

	def test_reviewer_only_sees_submissions_for_completed_problem(self):
		self.client.force_login(self.reviewer)

		response = self.client.get(reverse("staff:pending_submissions"))

		self.assertContains(response, self.accessible_submission.problem.title)
		self.assertNotContains(response, self.hidden_submission.problem.title)

	def test_reviewer_can_open_matching_submission_detail(self):
		self.client.force_login(self.reviewer)

		response = self.client.get(reverse("staff:submission_detail", args=[self.accessible_submission.pk]))

		self.assertEqual(response.status_code, 200)

	def test_reviewer_cannot_open_unrelated_submission_detail(self):
		self.client.force_login(self.reviewer)

		response = self.client.get(reverse("staff:submission_detail", args=[self.hidden_submission.pk]))

		self.assertEqual(response.status_code, 403)

	def test_reviewer_cannot_modify_own_submission(self):
		own_submission = Submission.objects.filter(user=self.reviewer).first()
		self.client.force_login(self.reviewer)

		response = self.client.post(
			reverse("staff:submission_detail", args=[own_submission.pk]),
			{"decision": "correct"},
		)

		self.assertEqual(response.status_code, 403)

	def test_reviewer_cannot_modify_processed_submission(self):
		processed = Submission.objects.create(
			user=self.other_user,
			problem=self.problem_a,
			answer="processed",
			is_correct=True,
			status="accepted",
		)
		self.client.force_login(self.reviewer)

		response = self.client.post(
			reverse("staff:submission_detail", args=[processed.pk]),
			{"decision": "incorrect"},
		)

		self.assertEqual(response.status_code, 403)
		processed.refresh_from_db()
		self.assertEqual(processed.status, "accepted")

	def test_staff_sees_everything(self):
		self.client.force_login(self.staff_user)

		response = self.client.get(reverse("staff:pending_submissions"))

		self.assertContains(response, self.accessible_submission.problem.title)
		self.assertContains(response, self.hidden_submission.problem.title)

	def test_pending_submissions_can_be_filtered(self):
		self.client.force_login(self.staff_user)

		response = self.client.get(
			reverse("staff:pending_submissions"),
			{"q": self.accessible_submission.problem.title},
		)

		self.assertContains(response, self.accessible_submission.problem.title)
		self.assertNotContains(response, self.hidden_submission.problem.title)

	def test_suggest_problem_creates_suggestion(self):
		self.client.force_login(self.reviewer)

		response = self.client.post(
			reverse("staff:suggest_problem"),
			{
				"title": "Suggested problem",
				"statement": "Statement",
				"solution": "Solution",
				"category": "autre",
				"difficulty": 2,
			},
		)

		self.assertRedirects(response, reverse("problems:index"))
		suggestion = ProblemSuggestion.objects.get(title="Suggested problem")
		self.assertEqual(suggestion.author, self.reviewer)

	@override_settings(
		PROBLEM_SUGGESTION_AUTHOR_NAMES=["QCM français"],
		PROBLEM_SUGGESTION_AUTHOR_YEARS=[2024, 2025],
	)
	def test_suggest_problem_builds_configured_author_from_type_and_year(self):
		self.client.force_login(self.reviewer)

		response = self.client.post(
			reverse("staff:suggest_problem"),
			{
				"title": "Suggested with year",
				"statement": "Statement",
				"solution": "Solution",
				"category": "autre",
				"difficulty": 2,
				"author_type": "QCM français",
				"author_year": "2025",
			},
		)

		self.assertRedirects(response, reverse("problems:index"))
		suggestion = ProblemSuggestion.objects.get(title="Suggested with year")
		self.assertEqual(suggestion.author.username, "QCM français - 2025")

	@override_settings(PROBLEM_SUGGESTION_AUTHOR_USERNAMES=["other"])
	def test_suggest_problem_can_choose_an_allowed_author(self):
		self.client.force_login(self.reviewer)

		response = self.client.post(
			reverse("staff:suggest_problem"),
			{
				"title": "Suggested for other",
				"statement": "Statement",
				"solution": "Solution",
				"category": "autre",
				"difficulty": 2,
				"author": self.other_user.pk,
			},
		)

		self.assertRedirects(response, reverse("problems:index"))
		suggestion = ProblemSuggestion.objects.get(title="Suggested for other")
		self.assertEqual(suggestion.author, self.other_user)

	@override_settings(PROBLEM_SUGGESTION_AUTHOR_USERNAMES=["other"])
	def test_suggest_problem_rejects_an_unlisted_author(self):
		self.client.force_login(self.reviewer)

		response = self.client.post(
			reverse("staff:suggest_problem"),
			{
				"title": "Invalid author",
				"statement": "Statement",
				"solution": "Solution",
				"category": "autre",
				"difficulty": 2,
				"author": self.staff_user.pk,
			},
		)

		self.assertEqual(response.status_code, 200)
		self.assertFalse(ProblemSuggestion.objects.filter(title="Invalid author").exists())

	def test_accepting_problem_suggestion_creates_problem_and_notification(self):
		suggestion = ProblemSuggestion.objects.create(
			title="Accepted problem",
			statement="Statement",
			solution="Solution",
			category="autre",
			difficulty=2,
			author=self.reviewer,
		)

		suggestion.status = "accepted"
		suggestion.save()

		self.assertTrue(Problem.objects.filter(title="Accepted problem").exists())
		self.assertTrue(self.reviewer.notification_set.filter(message__contains="acceptée").exists())

	def test_rejecting_problem_suggestion_creates_notification(self):
		suggestion = ProblemSuggestion.objects.create(
			title="Rejected problem",
			statement="Statement",
			solution="Solution",
			category="autre",
			difficulty=2,
			author=self.reviewer,
		)

		suggestion.status = "rejected"
		suggestion.save()

		self.assertFalse(Problem.objects.filter(title="Rejected problem").exists())
		self.assertTrue(self.reviewer.notification_set.filter(message__contains="rejetée").exists())
