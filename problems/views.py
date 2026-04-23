from django.shortcuts import render, get_object_or_404, redirect
from .models import Problem, Submission
from django.contrib.auth.decorators import login_required


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
    # Verifie si l'utilisateur a deja soumis une reponse.
    submission = Submission.objects.filter(user=request.user, problem=problem).first()

    if request.method == "POST":
        answer = request.POST.get("answer", "").strip()

        # Cree ou met a jour la soumission.
        if submission:
            submission.answer = answer
            submission.is_correct = None
            submission.save()
        else:
            submission = Submission.objects.create(
                user=request.user,
                problem=problem,
                answer=answer,
                is_correct=None
            )
            problem.total_submissions += 1
            problem.save()

        return redirect("problems:problem_detail", pk=problem.pk)

    return render(request, "problems/problem_detail.html", {
        "problem": problem,
        "submission": submission,
    })