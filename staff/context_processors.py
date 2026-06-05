from problems.models import Submission
from .permissions import can_access_pending_submissions, get_pending_review_rows

def pending_submissions_count(request):
    can_access = can_access_pending_submissions(request.user)
    if can_access:
        count = len(get_pending_review_rows(request.user))
        return {
            'pending_submissions_count': count,
            'can_access_pending_submissions': True,
        }
    return {
        'pending_submissions_count': 0,
        'can_access_pending_submissions': False,
    }