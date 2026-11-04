from django.shortcuts import render
from django.contrib.auth.models import User
from django.core.paginator import Paginator
from django.db.models import Count, Q, Sum, Value
from django.db.models.functions import Coalesce

from core.rate_limits import rate_limit
from problems.models import submission_score_expression


@rate_limit("leaderboard", limit=30, period=60)
def leaderboard(request):
    users = (
        User.objects.filter(
            profile__allow_leaderboard_display=True,
        )
        .annotate(
            total_score=Coalesce(
                Sum(
                    submission_score_expression("submission__"),
                    filter=Q(submission__is_correct=True),
                ),
                Value(0),
            ),
            solved_count=Count("submission", filter=Q(submission__is_correct=True)),
        )
        .filter(total_score__gt=0)
        .order_by("-total_score", "username")
    )
    page_obj = Paginator(users, 100).get_page(request.GET.get("page"))
    leaderboard_data = [
        {
            "user": user,
            "total_score": user.total_score,
            "solved_count": user.solved_count,
        }
        for user in page_obj.object_list
    ]

    return render(
        request,
        "leaderboard/leaderboard.html",
        {
            "leaderboard": leaderboard_data,
            "page_obj": page_obj,
        },
    )
