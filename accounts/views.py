import json
from django.core.serializers.json import DjangoJSONEncoder
from django.http import JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from .forms import SignUpForm, UserUpdateForm, ProfileUpdateForm
from problems.models import Submission, Problem
from dateutil import parser

User = get_user_model()


def _build_profile_context(user):
    submissions = Submission.objects.filter(user=user).select_related("problem").order_by("-submitted_at")[:20]
    total_submissions = Submission.objects.filter(user=user).count()
    correct_submissions = Submission.objects.filter(user=user, is_correct=True).count()
    total_score = user.profile.get_total_score()
    score_history = user.profile.previous_scores
    chart_labels = [parser.parse(entry[1]).strftime("%d/%m/%Y") for entry in score_history]
    chart_data = [entry[0] for entry in score_history]

    return {
        "profile_user": user,
        "submissions": submissions,
        "total_submissions": total_submissions,
        "correct_submissions": correct_submissions,
        "success_rate": round((correct_submissions / total_submissions) * 100, 1) if total_submissions > 0 else 0,
        "total_score": total_score,
        "chart_labels": json.dumps(chart_labels, cls=DjangoJSONEncoder),
        "chart_data": json.dumps(chart_data, cls=DjangoJSONEncoder),
    }


def _search_users(query, limit=8):
    if len(query) < 2:
        return []

    return list(
        User.objects.filter(
            Q(username__icontains=query)
            | Q(first_name__icontains=query)
            | Q(last_name__icontains=query)
        ).order_by("username")[:limit]
    )


def _search_problems(query, limit=8):
    if len(query) < 2:
        return []

    return list(
        Problem.objects.filter(
            Q(title__icontains=query)
            | Q(statement__icontains=query)
            | Q(category__icontains=query)
        ).order_by("title")[:limit]
    )

def signup(request):
    if request.method == "POST":
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect("accounts:profile")
    else:
        form = SignUpForm()
    return render(request, "accounts/signup.html", {"form": form})

@login_required
def profile(request):
    context = _build_profile_context(request.user)
    return render(request, "accounts/profile.html", context)


def public_profile(request, username):
    profile_user = get_object_or_404(User, username=username)
    context = _build_profile_context(profile_user)
    return render(request, "accounts/public_profile.html", context)


def user_search(request):
    query = request.GET.get("q", "").strip()
    users = _search_users(query, limit=30)
    problems = _search_problems(query, limit=30)

    if len(users) == 1 and users[0].username.lower() == query.lower():
        return redirect("accounts:public_profile", username=users[0].username)

    exact_problem = next((problem for problem in problems if problem.title.lower() == query.lower()), None)
    if exact_problem:
        return redirect("problems:problem_detail", pk=exact_problem.pk)

    return render(request, "accounts/user_search.html", {
        "query": query,
        "users": users,
        "problems": problems,
    })

@login_required
def edit_profile(request):
    if request.method == 'POST':
        user_form = UserUpdateForm(request.POST, instance=request.user)
        profile_form = ProfileUpdateForm(request.POST, request.FILES, instance=request.user.profile)
        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            return redirect('accounts:profile') 
    else:
        user_form = UserUpdateForm(instance=request.user)
        profile_form = ProfileUpdateForm(instance=request.user.profile)

    return render(request, 'accounts/edit_profile.html', {
        'user_form': user_form,
        'profile_form': profile_form
    })


def matching_users(request):
    query = request.GET.get("q", "").strip()
    results = []

    if len(query) >= 2:
        users = _search_users(query, limit=4)
        problems = _search_problems(query, limit=4)

        results = [
            {
                "kind": "user",
                "label": user.username,
                "secondary": (f"{user.first_name} {user.last_name}").strip(),
                "url": f"/accounts/u/{user.username}/",
            }
            for user in users
        ] + [
            {
                "kind": "problem",
                "label": problem.title,
                "secondary": problem.get_category_display(),
                "url": f"/problems/{problem.pk}/",
            }
            for problem in problems
        ]

    return JsonResponse({"results": results})
