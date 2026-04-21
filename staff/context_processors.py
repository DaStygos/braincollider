from problems.models import Submission

def pending_submissions_count(request):
    if request.user.is_authenticated and request.user.is_staff:
        count = Submission.objects.filter(is_correct__isnull=True).count()
        return {'pending_submissions_count': count}
    return {'pending_submissions_count': 0}