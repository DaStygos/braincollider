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

	def test_reviewer_only_sees_open_submissions_for_solved_problems(self):
		self.client.force_login(self.reviewer)

		response = self.client.get(reverse("staff:pending_submissions"))

		self.assertContains(response, self.accessible_submission.problem.title)
		self.assertNotContains(response, self.hidden_submission.problem.title)

	def test_reviewer_can_open_matching_submission_detail(self):
		self.client.force_login(self.reviewer)

		response = self.client.get(reverse("staff:submission_detail", args=[self.accessible_submission.pk]))

		self.assertEqual(response.status_code, 200)

	def test_reviewer_cannot_open_unrelated_open_submission_detail(self):
		self.client.force_login(self.reviewer)

		response = self.client.get(reverse("staff:submission_detail", args=[self.hidden_submission.pk]))

		self.assertEqual(response.status_code, 403)

	def test_pending_submission_with_reviewer_comment_stays_in_queue(self):
		from problems.models import SubmissionComment

		SubmissionComment.objects.create(
			submission=self.hidden_submission,
			author=self.reviewer,
			text="Question sur cette soumission",
			is_reviewer=True,
		)
		self.client.force_login(self.reviewer)

		response = self.client.get(reverse("staff:pending_submissions"))

		self.assertNotContains(response, self.hidden_submission.problem.title)

	def test_clarification_waiting_for_owner_is_informational_only(self):
		from problems.models import SubmissionComment

		self.accessible_submission.status = "clarification"
		self.accessible_submission.save(update_fields=["status"])
		SubmissionComment.objects.create(
			submission=self.accessible_submission,
			author=self.reviewer,
			text="Pouvez-vous préciser votre raisonnement ?",
			is_reviewer=True,
		)
		self.client.force_login(self.reviewer)

		response = self.client.get(reverse("staff:pending_submissions"))

		self.assertEqual(response.context["rows"], [])
		self.assertEqual(
			response.context["owner_response_rows"][0]["submission"],
			self.accessible_submission,
		)
		self.assertEqual(response.context["pending_submissions_count"], 0)

	def test_reviewer_cannot_modify_own_submission(self):
		own_submission = Submission.objects.filter(user=self.reviewer).first()
		self.client.force_login(self.reviewer)

		response = self.client.post(
			reverse("staff:submission_detail", args=[own_submission.pk]),
			{"decision": "correct"},
		)

		self.assertEqual(response.status_code, 403)

	def test_submission_owner_cannot_view_own_uncorrected_submission(self):
		own_submission = Submission.objects.create(
			user=self.reviewer,
			problem=self.problem_b,
			answer="my answer",
			is_correct=None,
		)
		self.client.force_login(self.reviewer)

		response = self.client.get(
			reverse("staff:submission_detail", args=[own_submission.pk]),
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

	def test_reviewer_can_view_processed_submission_in_own_history(self):
		processed = Submission.objects.create(
			user=self.other_user,
			problem=self.problem_a,
			answer="processed",
			is_correct=True,
			status="accepted",
			reviewed_by=self.reviewer,
		)
		self.client.force_login(self.reviewer)

		response = self.client.get(reverse("staff:submission_detail", args=[processed.pk]))

		self.assertEqual(response.status_code, 200)
		self.assertNotContains(response, 'name="decision"')

	def test_reviewer_history_only_contains_own_processed_submissions(self):
		Submission.objects.create(
			user=self.other_user,
			problem=self.problem_a,
			answer="mine",
			is_correct=True,
			status="accepted",
			reviewed_by=self.reviewer,
		)
		Submission.objects.create(
			user=self.other_user,
			problem=self.problem_a,
			answer="other",
			is_correct=False,
			status="rejected",
			reviewed_by=self.staff_user,
		)
		self.client.force_login(self.reviewer)

		response = self.client.get(reverse("staff:pending_submissions"))

		self.assertContains(response, "Historique de vos corrections")
		self.assertEqual(len(response.context["history_rows"]), 1)
		self.assertEqual(response.context["history_rows"][0]["submission"].answer, "mine")

	def test_decision_records_reviewer(self):
		self.client.force_login(self.reviewer)

		response = self.client.post(
			reverse("staff:submission_detail", args=[self.accessible_submission.pk]),
			{"decision": "correct"},
		)

		self.assertEqual(response.status_code, 302)
		self.accessible_submission.refresh_from_db()
		self.assertEqual(self.accessible_submission.reviewed_by, self.reviewer)

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

		accepted_problem = Problem.objects.get(title="Accepted problem")
		self.assertEqual(accepted_problem.author, self.reviewer)
		notification = self.reviewer.notification_set.get(message__contains="acceptée")
		self.assertEqual(
			notification.redirect_url,
			reverse("problems:problem_detail", kwargs={"pk": accepted_problem.pk}),
		)

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
