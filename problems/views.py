from functools import wraps

from django.contrib.auth.views import redirect_to_login
from django.shortcuts import render, get_object_or_404, redirect
from .models import (
    CATEGORY_CHOICES,
    DIFFICULTY_CHOICES,
    Problem,
    Submission,
    SubmissionComment,
)
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.utils.http import url_has_allowed_host_and_scheme
from core.rate_limits import rate_limit


def login_required_for_post(view):
    @wraps(view)
    def wrapped(request, *args, **kwargs):
        if request.method == "POST" and not request.user.is_authenticated:
            return redirect_to_login(request.get_full_path())
        return view(request, *args, **kwargs)

    return wrapped


def _create_pending_submission(user, problem, answer):
    submission = Submission.objects.create(
        user=user,
        problem=problem,
        answer=answer,
        is_correct=None,
        status="pending",
    )
    problem.total_submissions += 1
    problem.save()
    return submission


def _get_submission_status_sets(user):
    if not user.is_authenticated:
        return set(), set(), set()

    latest_submissions = {}
    user_submissions = Submission.objects.filter(user=user).order_by(
        "problem_id", "-submitted_at", "-id"
    )
    for submission in user_submissions:
        latest_submissions.setdefault(submission.problem_id, submission.is_correct)

    correct_problems = {
        problem_id
        for problem_id, is_correct in latest_submissions.items()
        if is_correct is True
    }
    wrong_problems = {
        problem_id
        for problem_id, is_correct in latest_submissions.items()
        if is_correct is False
    }
    pending_problems = {
        problem_id
        for problem_id, is_correct in latest_submissions.items()
        if is_correct is None
    }
    return correct_problems, wrong_problems, pending_problems


def index(request):
    problems = Problem.objects.all()
    correct_problems, wrong_problems, pending_problems = _get_submission_status_sets(
        request.user
    )

    search = request.GET.get("q", "").strip()
    category = request.GET.get("category", "")
    difficulty = request.GET.get("difficulty", "")
    author = request.GET.get("author", "")
    status = request.GET.get("status", "")

    valid_categories = {value for value, _ in CATEGORY_CHOICES}
    valid_difficulties = {str(value) for value, _ in DIFFICULTY_CHOICES}

    if search:
        problems = problems.filter(title__icontains=search)
    if category in valid_categories:
        problems = problems.filter(category=category)
    if difficulty in valid_difficulties:
        problems = problems.filter(difficulty=int(difficulty))
    if author.isdigit():
        problems = problems.filter(author_id=int(author))
    if status == "correct":
        problems = problems.filter(id__in=correct_problems)
    elif status == "wrong":
        problems = problems.filter(id__in=wrong_problems)
    elif status == "pending":
        problems = problems.filter(id__in=pending_problems)
    elif status == "unsolved":
        submitted_problem_ids = correct_problems | wrong_problems | pending_problems
        problems = problems.exclude(id__in=submitted_problem_ids)
    elif status == "saved" and request.user.is_authenticated:
        problems = problems.filter(saved_by__user=request.user)

    problems = problems.order_by("category", "difficulty", "title")
    problem_count = problems.count()

    context = {
        "problems": problems,
        "problem_count": problem_count,
        "category_choices": CATEGORY_CHOICES,
        "difficulty_choices": DIFFICULTY_CHOICES,
        "author_choices": User.objects.filter(
            authored_problems__isnull=False,
        )
        .distinct()
        .order_by("username"),
        "selected_search": search,
        "selected_category": category,
        "selected_difficulty": difficulty,
        "selected_author": author,
        "selected_status": status,
        "saved_problem_ids": set(request.user.saved_problems.values_list("problem_id", flat=True)) if request.user.is_authenticated else set(),
        "correct_problems": correct_problems,
        "wrong_problems": wrong_problems,
        "pending_problems": pending_problems,
    }
    return render(request, "problems/index.html", context)


@login_required
@require_POST
def toggle_saved_problem(request, pk):
    problem = get_object_or_404(Problem, pk=pk)
    saved, created = request.user.saved_problems.get_or_create(problem=problem)
    if not created:
        saved.delete()
        messages.info(request, "Problème retiré de votre liste à revoir.")
    else:
        messages.success(request, "Problème ajouté à votre liste à revoir.")
    next_url = request.POST.get("next", "")
    if not url_has_allowed_host_and_scheme(
        next_url, allowed_hosts={request.get_host()}
    ):
        next_url = "problems:problem_detail"
        return redirect(next_url, pk=problem.pk)
    return redirect(next_url)


@login_required_for_post
@rate_limit("problem-submission", limit=30, period=60 * 60, methods={"POST"})
def problem_detail(request, pk):
    problem = get_object_or_404(Problem, pk=pk)
    # Récupère la soumission la plus récente de l'utilisateur pour ce problème.
    submission = None
    if request.user.is_authenticated:
        submission = (
            Submission.objects.filter(user=request.user, problem=problem)
            .order_by("-submitted_at")
            .first()
        )

    if request.method == "POST":
        # Soumission validée : l'utilisateur ne peut plus rien soumettre depuis cette vue.
        if submission and submission.status == "accepted":
            return redirect("problems:problem_detail", pk=problem.pk)

        # Rétrocompat : champ `answer` (legacy).
        answer = request.POST.get("answer")
        if answer is not None:
            answer = answer.strip()
            if not answer:
                messages.warning(request, "Votre réponse ne peut pas être vide.")
                return redirect("problems:problem_detail", pk=problem.pk)
            if submission:
                submission.answer = answer
                submission.is_correct = None
                submission.status = "pending"
                submission.save()
            else:
                submission = _create_pending_submission(request.user, problem, answer)
            return redirect("problems:problem_detail", pk=problem.pk)

        content = request.POST.get("content", "").strip()
        if not content:
            messages.warning(
                request, "Écrivez votre réponse ou votre commentaire avant l’envoi."
            )
            return redirect("problems:problem_detail", pk=problem.pk)

        # Soumission refusée → nouvelle soumission from scratch.
        if submission and submission.status == "rejected":
            submission = _create_pending_submission(request.user, problem, content)
            return redirect("problems:problem_detail", pk=problem.pk)

        if submission:
            # Soumission existante (pending ou clarification) : ajout d'un commentaire.
            if submission.user != request.user:
                return redirect("problems:problem_detail", pk=problem.pk)

            SubmissionComment.objects.create(
                submission=submission,
                author=request.user,
                text=content,
                is_reviewer=False,
            )
            submission.status = "pending"
            submission.save()
            return redirect("problems:problem_detail", pk=problem.pk)

        # Aucune soumission : création initiale.
        submission = _create_pending_submission(request.user, problem, content)
        return redirect("problems:problem_detail", pk=problem.pk)

    # Toutes les soumissions sauf la plus récente, pour l'historique
    previous_submissions = Submission.objects.none()
    if request.user.is_authenticated:
        previous_submissions = (
            Submission.objects.filter(user=request.user, problem=problem)
            .order_by("-submitted_at")
            .prefetch_related("comments")[1:]
        )

    return render(
        request,
        "problems/problem_detail.html",
        {
            "problem": problem,
            "saved_problem_ids": set(request.user.saved_problems.values_list("problem_id", flat=True)) if request.user.is_authenticated else set(),
            "submission": submission,
            "previous_submissions": previous_submissions,
        },
    )
