from django.shortcuts import render, get_object_or_404, redirect
from .models import Problem, Submission
from django.contrib.auth.decorators import login_required

def index(request):
    problems = Problem.objects.all()

    # Grouper par catégorie
    problems_by_category = {}
    for problem in problems:
        problems_by_category.setdefault(problem.category, []).append(problem)

    # Récupérer les soumissions de l'utilisateur connecté
    if request.user.is_authenticated:
        user_submissions = Submission.objects.filter(user=request.user)
        correct_problems = set(user_submissions.filter(is_correct=True).values_list('problem_id', flat=True))
        wrong_problems = set(user_submissions.filter(is_correct=False).values_list('problem_id', flat=True))
        pending_problems = set(user_submissions.filter(is_correct=None).values_list('problem_id', flat=True))
    else:
        correct_problems = set()
        wrong_problems = set()
        pending_problems = set()

    context = {
        "problems_by_category": problems_by_category,
        "correct_problems": correct_problems,
        "wrong_problems": wrong_problems,
        "pending_problems": pending_problems,
    }
    print(wrong_problems)
    return render(request, "problems/index.html", context)

@login_required
def problem_detail(request, pk):
    problem = get_object_or_404(Problem, pk=pk)
    submission = None

    # Vérifie si l'utilisateur a déjà soumis une réponse
    try:
        submission = Submission.objects.get(user=request.user, problem=problem)
    except Submission.DoesNotExist:
        pass

    if request.method == "POST":
        answer = request.POST.get("answer", "").strip()

        # Crée ou met à jour la soumission, sans correction automatique
        if submission:
            submission.answer = answer
            submission.is_correct = None  # en attente
            submission.save()
        else:
            submission = Submission.objects.create(
                user=request.user,
                problem=problem,
                answer=answer,
                is_correct=None  # pas encore corrigée
            )

        return redirect("problems:problem_detail", pk=problem.pk)

    return render(request, "problems/problem_detail.html", {
        "problem": problem,
        "submission": submission,
    })