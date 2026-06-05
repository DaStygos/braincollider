from django.shortcuts import render, redirect, get_object_or_404
from django.core.exceptions import PermissionDenied
from django.db.models import Q
from notifications.utils import create_notification
from problems.models import Submission, SubmissionComment
from .forms import ProblemSuggestionForm
from django.contrib.auth.decorators import login_required
from .permissions import can_access_pending_submissions, can_review_problem, get_accessible_pending_submissions, get_pending_review_rows

@login_required
def pending_submissions(request):
    if not can_access_pending_submissions(request.user):
        raise PermissionDenied
    rows = get_pending_review_rows(request.user)

    return render(request, "staff/pending_submissions.html", {"rows": rows})


@login_required
def submission_detail(request, pk):
    submission = get_object_or_404(Submission, pk=pk)
    if not can_review_problem(request.user, submission.problem):
        raise PermissionDenied

    if request.method == "POST":
        # Unified composer: handle reviewer comment (content) and optional decision
        content = request.POST.get("content", "").strip()
        decision = request.POST.get("decision")

        # If reviewer added content, store it as a SubmissionComment
        comment_obj = None
        # If reviewer provided content but no explicit decision, treat it as a clarification request
        if content and not decision:
            decision = "clarify"

        if content:
            comment_obj = SubmissionComment.objects.create(
                submission=submission,
                author=request.user,
                text=content,
                is_reviewer=True,
            )

            # notify the submission owner about the new comment
            create_notification(
                user=submission.user,
                message=(f"Le correcteur a ajouté un commentaire à votre soumission pour '{submission.problem.title}'."),
            )

        # If a decision was made, process it
        if decision:
            if decision == "correct":
                if submission.is_correct is None:
                    submission.problem.correct_submissions += 1
                    submission.problem.save()
                submission.is_correct = True
                submission.status = "accepted"
            elif decision == "clarify":
                # Request clarifications from the submission owner
                submission.is_correct = None
                submission.status = "clarification"
            elif decision == "incorrect":
                submission.is_correct = False
                submission.status = "rejected"

            submission.save()

            # Notify user with optional comment included
            if decision == "clarify":
                notif_msg = f"Le correcteur a demandé des précisions pour votre soumission au problème '{submission.problem.title}'."
                if comment_obj:
                    notif_msg += f" Précision demandée: {comment_obj.text}"
            else:
                notif_msg = f"Votre soumission pour le problème '{submission.problem.title}' a été évaluée. "
                if submission.status == "accepted":
                    notif_msg += "Elle a été marquée comme correcte."
                elif submission.status == "rejected":
                    notif_msg += "Elle a été marquée comme incorrecte."

                if comment_obj:
                    notif_msg += f" Commentaire du correcteur: {comment_obj.text}"

            create_notification(user=submission.user, message=notif_msg)

            # After making a decision, navigate the reviewer to the next
            # accessible pending submission in chronological order. If none,
            # return to the pending submissions list.
            accessible = get_accessible_pending_submissions(request.user).order_by('submitted_at', 'pk')
            next_submission = accessible.filter(
                Q(submitted_at__gt=submission.submitted_at) |
                Q(submitted_at=submission.submitted_at, pk__gt=submission.pk)
            ).first()

            if next_submission:
                return redirect("staff:submission_detail", pk=next_submission.pk)
            return redirect("staff:pending_submissions")

        # If no decision, return to the submission detail so the reviewer can continue the discussion
        return redirect("staff:submission_detail", pk=submission.pk)

    return render(request, "staff/submission_detail.html", {"submission": submission})

@login_required
def suggest_problem(request):
    if request.method == "POST":
        form = ProblemSuggestionForm(request.POST)
        if form.is_valid():
            suggestion = form.save(commit=False)
            suggestion.author = request.user
            suggestion.save()
            create_notification(
                user=request.user,
                message=(
                    f"Merci pour votre suggestion de problème '{suggestion.title}'. "
                    "Elle sera examinée par notre équipe."
                ),
            )
            return redirect("problems:index")
    else:
        form = ProblemSuggestionForm()

    return render(request, "staff/suggest_problem.html", {"form": form})