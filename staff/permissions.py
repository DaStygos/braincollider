from problems.models import Submission


def can_access_pending_submissions(user):
    if not user.is_authenticated:
        return False
    if user.is_staff:
        return True
    return Submission.objects.filter(user=user, is_correct=True).exists()


def can_review_problem(user, problem):
    if not user.is_authenticated:
        return False
    if user.is_staff:
        return True
    return Submission.objects.filter(user=user, problem=problem, is_correct=True).exists()


def get_accessible_pending_submissions(user):
    submissions = Submission.objects.filter(is_correct__isnull=True).select_related("user", "problem")
    if not user.is_authenticated or user.is_staff:
        return submissions

    solved_problem_ids = Submission.objects.filter(
        user=user,
        is_correct=True,
    ).values_list("problem_id", flat=True).distinct()
    return submissions.filter(problem_id__in=solved_problem_ids)