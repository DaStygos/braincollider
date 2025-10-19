from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.admin.views.decorators import staff_member_required
from django.utils import timezone

from notifications.models import Notification
from .models import Submission

@staff_member_required
def pending_submissions(request):
    submissions = Submission.objects.filter(is_correct__isnull=True).select_related('user', 'problem')
    return render(request, "problems/pending_submissions.html", {"submissions": submissions})


@staff_member_required
def submission_detail(request, pk):
    submission = get_object_or_404(Submission, pk=pk)

    if request.method == "POST":
        decision = request.POST.get("decision")
        if decision == "correct":
            submission.is_correct = True
            Notification.objects.create(
                user=submission.user,
                message=f"Votre soumission pour le problème '{submission.problem.title}' a été acceptée."
            )
            submission.user.profile.previous_scores.append((submission.score + submission.user.profile.get_total_score(), timezone.now().isoformat()))
        elif decision == "incorrect":
            submission.is_correct = False
            Notification.objects.create(
                user=submission.user,
                message=f"Votre soumission pour le problème '{submission.problem.title}' a été rejetée."
            )
        submission.save()
        return redirect("problems:pending_submissions")

    return render(request, "problems/submission_detail.html", {"submission": submission})
