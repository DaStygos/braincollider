from django.shortcuts import render
from django.contrib.auth.models import User
from django.core.paginator import Paginator
from django.db.models import Case, Count, IntegerField, Q, Sum, Value, When
from django.db.models.functions import Coalesce

from core.rate_limits import rate_limit
from problems.models import BAREME

@rate_limit("leaderboard", limit=30, period=60)
def leaderboard(request):
    score_case = Case(
        *[When(submission__problem__difficulty=difficulty, then=Value(points)) for difficulty, points in BAREME.items()],
        default=Value(0),
        output_field=IntegerField(),
    )
    users = User.objects.filter(
        profile__allow_leaderboard_display=True,
    ).annotate(
        total_score=Coalesce(Sum(score_case, filter=Q(submission__is_correct=True)), Value(0)),
        solved_count=Count("submission", filter=Q(submission__is_correct=True)),
    ).filter(total_score__gt=0).order_by("-total_score", "username")
    page_obj = Paginator(users, 100).get_page(request.GET.get("page"))
    leaderboard_data = [{
        "user": user,
        "total_score": user.total_score,
        "solved_count": user.solved_count,
    } for user in page_obj.object_list]

    return render(request, 'leaderboard/leaderboard.html', {
        'leaderboard': leaderboard_data,
        'page_obj': page_obj,
    })
