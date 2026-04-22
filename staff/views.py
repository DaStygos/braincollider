from django.shortcuts import render, redirect, get_object_or_404
from django.core.exceptions import PermissionDenied
from notifications.models import Notification
from problems.models import Submission
from .forms import ProblemSuggestionForm
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .permissions import can_access_pending_submissions, can_review_problem, get_accessible_pending_submissions

@login_required
def pending_submissions(request):
    if not can_access_pending_submissions(request.user):
        raise PermissionDenied
    submissions = get_accessible_pending_submissions(request.user)
    return render(request, "staff/pending_submissions.html", {"submissions": submissions})


@login_required
def submission_detail(request, pk):
    submission = get_object_or_404(Submission, pk=pk)
    if not can_review_problem(request.user, submission.problem):
        raise PermissionDenied

    if request.method == "POST":
        decision = request.POST.get("decision")
        if decision == "correct":
            if submission.is_correct == None:
                submission.problem.correct_submissions += 1
                submission.problem.save()
            submission.is_correct = True
        elif decision == "incorrect":
            submission.is_correct = False
        submission.save()
        Notification.objects.create(
            user=submission.user,
            message=f"Votre soumission pour le problème '{submission.problem.title}' a été évaluée comme {'correcte' if submission.is_correct else 'incorrecte'}.",
        )
        return redirect("staff:pending_submissions")

    return render(request, "staff/submission_detail.html", {"submission": submission})

@login_required
def suggest_problem(request):
    if request.method == "POST":
        form = ProblemSuggestionForm(request.POST)
        if form.is_valid():
            suggestion = form.save(commit=False)
            suggestion.author = request.user
            suggestion.save()
            Notification.objects.create(
                user=request.user,
                message=f"Merci pour votre suggestion de problème '{suggestion.title}'. Elle sera examinée par notre équipe.",
            )
            return redirect("problems:index")
    else:
        form = ProblemSuggestionForm()

    return render(request, "staff/suggest_problem.html", {"form": form})