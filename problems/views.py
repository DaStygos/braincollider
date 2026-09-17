from django.shortcuts import render, get_object_or_404, redirect
from .models import Problem, Submission, SubmissionComment
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from notifications.utils import create_notification


def _group_problems_by_category(problems):
    problems_by_category = {}
    for problem in problems:
        problems_by_category.setdefault(problem.category, []).append(problem)
    return problems_by_category


def _get_submission_status_sets(user):
    if not user.is_authenticated:
        return set(), set(), set()

    user_submissions = Submission.objects.filter(user=user)
    correct_problems = set(user_submissions.filter(is_correct=True).values_list("problem_id", flat=True))
    wrong_problems = set(user_submissions.filter(is_correct=False).values_list("problem_id", flat=True))
    pending_problems = set(user_submissions.filter(is_correct=None).values_list("problem_id", flat=True))
    return correct_problems, wrong_problems, pending_problems


def index(request):
    problems = Problem.objects.all()
    problems_by_category = _group_problems_by_category(problems)
    correct_problems, wrong_problems, pending_problems = _get_submission_status_sets(request.user)

    context = {
        "problems_by_category": problems_by_category,
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