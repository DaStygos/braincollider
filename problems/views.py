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
    else:
        correct_problems = set()
        wrong_problems = set()

    context = {
        "problems_by_category": problems_by_category,
        "correct_problems": correct_problems,
        "wrong_problems": wrong_problems,
    }
    print(wrong_problems)
    return render(request, "problems/index.html", context)

@login_required
def problem_detail(request, problem_id):
    problem = get_object_or_404(Problem, id=problem_id)
    feedback = None

    # Vérifie si l'utilisateur a déjà soumis une réponse
    existing_submission = Submission.objects.filter(user=request.user, problem=problem).first()

    if request.method == "POST" and not existing_submission:
        answer = request.POST.get("answer", "").strip()
        # Crée la soumission
        submission = Submission.objects.create(
            user=request.user,
            problem=problem,
            answer=answer,
            is_correct=(answer == problem.correct_answer)  # Correction automatique
        )
        feedback = "Bonne réponse !" if submission.is_correct else "Réponse incorrecte."

    context = {
        "problem": problem,
        "submission": existing_submission,
        "feedback": feedback,
    }
    return render(request, "problems/problem_detail.html", context)