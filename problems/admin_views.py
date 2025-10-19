from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.admin.views.decorators import staff_member_required
from .models import Submission

@staff_member_required
def pending_submissions(request):
    """Liste toutes les soumissions non encore corrigées"""
    submissions = Submission.objects.filter(is_correct__isnull=True).select_related('user', 'problem')
    return render(request, "problems/pending_submissions.html", {"submissions": submissions})


@staff_member_required
def submission_detail(request, pk):
    """Affiche une soumission et permet de la corriger"""
    submission = get_object_or_404(Submission, pk=pk)

    if request.method == "POST":
        decision = request.POST.get("decision")
        if decision == "correct":
            submission.is_correct = True
        elif decision == "incorrect":
            submission.is_correct = False
        submission.save()
        return redirect("problems:pending_submissions")

    return render(request, "problems/submission_detail.html", {"submission": submission})
