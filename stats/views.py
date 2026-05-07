from datetime import timedelta

from django.contrib.auth.models import User
from django.db.models import Case, Count, IntegerField, Q, Sum, Value, When
from django.db.models.functions import Coalesce, TruncDate
from django.shortcuts import render
from django.utils import timezone

from problems.models import CATEGORY_CHOICES, Problem, Submission


def _submission_score_case(prefix=""):
    lookup = f"{prefix}problem__difficulty"
    return Case(
        When(**{lookup: 1}, then=Value(100)),
        When(**{lookup: 2}, then=Value(300)),
        When(**{lookup: 3}, then=Value(500)),
        When(**{lookup: 4}, then=Value(750)),
        When(**{lookup: 5}, then=Value(1000)),
        default=Value(0),
        output_field=IntegerField(),
    )


def _daily_series(start_date, days, rows, value_key):
    values_by_day = {row["day"]: row[value_key] for row in rows}
    return [values_by_day.get(start_date + timedelta(days=offset), 0) for offset in range(days)]


def dashboard(request):
    today = timezone.localdate()
    days = 30
    start_date = today - timedelta(days=days - 1)
    day_range = [start_date + timedelta(days=offset) for offset in range(days)]

    total_users = User.objects.count()
    active_users = User.objects.filter(submission__isnull=False).distinct().count()
    new_users_30d = User.objects.filter(date_joined__date__gte=start_date).count()

    total_problems = Problem.objects.count()
    total_submissions = Submission.objects.count()
    correct_submissions = Submission.objects.filter(is_correct=True).count()
    pending_submissions = Submission.objects.filter(is_correct__isnull=True).count()
    reviewed_submissions = Submission.objects.filter(is_correct__isnull=False).count()

    total_points = Submission.objects.filter(is_correct=True).aggregate(
        total=Coalesce(Sum(_submission_score_case()), 0)
    )["total"]

    top_users = list(
        User.objects.select_related("profile")
        .annotate(
            total_score=Coalesce(Sum(_submission_score_case("submission__")), 0),
            correct_count=Count("submission", filter=Q(submission__is_correct=True)),
        )
        .filter(total_score__gt=0)
        .order_by("-total_score", "username")[:5]
    )

    top_problems = list(
        Problem.objects.annotate(
            solved_count=Count("submission", filter=Q(submission__is_correct=True)),
        )
        .filter(solved_count__gt=0)
        .order_by("-solved_count", "title")[:5]
    )

    for problem in top_problems:
        problem.total_points = problem.solved_count * problem.get_score()

    points_rows = list(
        Submission.objects.filter(is_correct=True, submitted_at__date__gte=start_date)
        .annotate(day=TruncDate("submitted_at"))
        .values("day")
        .annotate(points=Sum(_submission_score_case()), count=Count("id"))
        .order_by("day")
    )
    corrections_rows = list(
        Submission.objects.filter(is_correct__isnull=False, submitted_at__date__gte=start_date)
        .annotate(day=TruncDate("submitted_at"))
        .values("day")
        .annotate(count=Count("id"))
        .order_by("day")
    )

    category_rows = list(
        Submission.objects.filter(is_correct=True)
        .values("problem__category")
        .annotate(count=Count("id"), points=Sum(_submission_score_case()))
        .order_by("-points", "problem__category")
    )

    category_labels = dict(CATEGORY_CHOICES)

    activity_labels = [day.strftime("%d/%m") for day in day_range]
    activity_points = _daily_series(start_date, days, points_rows, "points")
    activity_corrections = _daily_series(start_date, days, corrections_rows, "count")

    return render(request, "stats/dashboard.html", {
        "total_users": total_users,
        "active_users": active_users,
        "new_users_30d": new_users_30d,
        "total_problems": total_problems,
        "total_submissions": total_submissions,
        "correct_submissions": correct_submissions,
        "pending_submissions": pending_submissions,
        "reviewed_submissions": reviewed_submissions,
        "total_points": total_points,
        "success_rate": round((correct_submissions / reviewed_submissions) * 100, 1) if reviewed_submissions else 0,
        "average_points_per_user": round(total_points / active_users, 1) if active_users else 0,
        "activity_labels": activity_labels,
        "activity_points": activity_points,
        "activity_corrections": activity_corrections,
        "top_users": top_users,
        "top_problems": top_problems,
        "category_rows": [
            {
                "label": category_labels.get(row["problem__category"], row["problem__category"]),
                "count": row["count"],
                "points": row["points"],
            }
            for row in category_rows
        ],
    })