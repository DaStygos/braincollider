from django.shortcuts import render, get_object_or_404, redirect
from .models import CATEGORY_CHOICES, DIFFICULTY_CHOICES, Problem, Submission, SubmissionComment
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from notifications.utils import create_notification


def _get_submission_status_sets(user):
    if not user.is_authenticated:
        return set(), set(), set()

    latest_submissions = {}
    user_submissions = Submission.objects.filter(user=user).order_by("problem_id", "-submitted_at", "-id")
    for submission in user_submissions:
        latest_submissions.setdefault(submission.problem_id, submission.is_correct)

    correct_problems = {problem_id for problem_id, is_correct in latest_submissions.items() if is_correct is True}
    wrong_problems = {problem_id for problem_id, is_correct in latest_submissions.items() if is_correct is False}
    pending_problems = {problem_id for problem_id, is_correct in latest_submissions.items() if is_correct is None}
    return correct_problems, wrong_problems, pending_problems


def index(request):
    problems = Problem.objects.all()
    correct_problems, wrong_problems, pending_problems = _get_submission_status_sets(request.user)

    search = request.GET.get("q", "").strip()
    category = request.GET.get("category", "")
    difficulty = request.GET.get("difficulty", "")
    status = request.GET.get("status", "")

    valid_categories = {value for value, _ in CATEGORY_CHOICES}
    valid_difficulties = {str(value) for value, _ in DIFFICULTY_CHOICES}

    if search:
        problems = problems.filter(title__icontains=search)
    if category in valid_categories:
        problems = problems.filter(category=category)
    if difficulty in valid_difficulties:
        problems = problems.filter(difficulty=int(difficulty))
    if status == "correct":
        problems = problems.filter(id__in=correct_problems)
    elif status == "wrong":
        problems = problems.filter(id__in=wrong_problems)
    elif status == "pending":
        problems = problems.filter(id__in=pending_problems)
    elif status == "unsolved":
        submitted_problem_ids = correct_problems | wrong_problems | pending_problems
        problems = problems.exclude(id__in=submitted_problem_ids)

    problems = problems.order_by("category", "difficulty", "title")

    context = {
        "problems": problems,
        "category_choices": CATEGORY_CHOICES,
        "difficulty_choices": DIFFICULTY_CHOICES,
        "selected_search": search,
        "selected_category": category,
        "selected_difficulty": difficulty,
        "selected_status": status,
        "correct_problems": correct_problems,
        "wrong_problems": wrong_problems,
        "pending_problems": pending_problems,
    }
    return render(request, "problems/index.html", context)


@login_required
def problem_detail(request, pk):
    problem = get_object_or_404(Problem, pk=pk)
    # Récupère la soumission la plus récente de l'utilisateur pour ce problème.
    submission = Submission.objects.filter(user=request.user, problem=problem).order_by("-submitted_at").first()

    if request.method == "POST":
        # Soumission validée : l'utilisateur ne peut plus rien soumettre depuis cette vue.
        if submission and submission.status == "accepted":
            return redirect("problems:problem_detail", pk=problem.pk)

        # Rétrocompat : champ `answer` (legacy).
        answer = request.POST.get("answer")
        if answer is not None:
            answer = answer.strip()
            if submission:
                submission.answer = answer
                submission.is_correct = None
                submission.status = "pending"
                submission.save()
            else:
                submission = Submission.objects.create(
                    user=request.user,
                    problem=problem,
                    answer=answer,
                    is_correct=None,
                    status="pending",
                )
                problem.total_submissions += 1
                problem.save()
            return redirect("problems:problem_detail", pk=problem.pk)

        content = request.POST.get("content", "").strip()
        if not content:
            return redirect("problems:problem_detail", pk=problem.pk)

        # Soumission refusée → nouvelle soumission from scratch.
        if submission and submission.status == "rejected":
            submission = Submission.objects.create(
                user=request.user,
                problem=problem,
                answer=content,
                is_correct=None,
                status="pending",
            )
            problem.total_submissions += 1
            problem.save()
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
        submission = Submission.objects.create(
            user=request.user,
            problem=problem,
            answer=content,
            is_correct=None,
            status="pending",
        )
        problem.total_submissions += 1
        problem.save()
        return redirect("problems:problem_detail", pk=problem.pk)

    # Toutes les soumissions sauf la plus récente, pour l'historique
    previous_submissions = (
        Submission.objects
        .filter(user=request.user, problem=problem)
        .order_by("-submitted_at")
        .prefetch_related("comments")[1:]
    )

    return render(request, "problems/problem_detail.html", {
        "problem": problem,
        "submission": submission,
        "previous_submissions": previous_submissions,
    })