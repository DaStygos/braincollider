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
    submissions = Submission.objects.filter(status__in=["pending", "clarification"]).select_related("user", "problem")
    if not user.is_authenticated or user.is_staff:
        return submissions

    solved_problem_ids = Submission.objects.filter(
        user=user,
        is_correct=True,
    ).values_list("problem_id", flat=True).distinct()
    return submissions.filter(problem_id__in=solved_problem_ids)


def get_pending_review_rows(user):
    """Return queue rows where the latest message is from the submission owner."""
    submissions = get_accessible_pending_submissions(user).prefetch_related("comments")
    rows = []

    for submission in submissions:
        last_comment = submission.comments.last()
        if last_comment:
            last_author = last_comment.author
            last_at = last_comment.created_at
        else:
            last_author = submission.user
            last_at = submission.submitted_at

        if last_author == submission.user:
            rows.append({"submission": submission, "last_at": last_at})

    rows.sort(key=lambda row: row["last_at"])
    return rows