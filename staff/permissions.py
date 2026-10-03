from django.db.models import Q

from problems.models import Submission


def can_access_pending_submissions(user):
    return user.is_authenticated


def can_review_problem(user, problem):
    if not user.is_authenticated:
        return False
    if user.is_staff:
        return True
    return Submission.objects.filter(user=user, problem=problem, is_correct=True).exists()


def can_view_submission(user, submission):
    if not user.is_authenticated:
        return False
    if submission.user_id == user.id:
        return submission.status in {"pending", "clarification"}
    if submission.status in {"pending", "clarification"}:
        return True
    if user.is_staff or submission.reviewed_by_id == user.id:
        return True
    if submission.comments.filter(author=user, is_reviewer=True).exists():
        return True
    return can_review_problem(user, submission.problem)


def can_modify_submission(user, submission):
    if not user.is_authenticated or submission.user_id == user.id:
        return False
    if submission.status in {"accepted", "rejected"} or submission.is_correct is not None:
        return False
    return can_view_submission(user, submission)


def get_accessible_pending_submissions(user):
    submissions = Submission.objects.filter(
        is_correct__isnull=True,
    ).select_related("user", "problem")
    return submissions if user.is_authenticated else submissions.none()


def get_pending_review_rows(user):
    """Return all submissions that have not received a correctness decision."""
    submissions = get_accessible_pending_submissions(user).prefetch_related("comments")
    rows = []

    for submission in submissions:
        last_comment = submission.comments.last()
        if last_comment:
            last_at = last_comment.created_at
        else:
            last_at = submission.submitted_at

        rows.append({"submission": submission, "last_at": last_at})

    rows.sort(key=lambda row: row["last_at"])
    return rows


def get_review_history_rows(user):
    if not user.is_authenticated:
        return []

    submissions = Submission.objects.filter(
        status__in=["accepted", "rejected"],
    ).select_related("user", "problem").prefetch_related("comments")
    submissions = submissions.filter(
        Q(reviewed_by=user) |
        Q(comments__author=user, comments__is_reviewer=True),
    ).distinct()

    return [
        {"submission": submission, "last_at": submission.submitted_at}
        for submission in submissions.order_by("-submitted_at")
    ]