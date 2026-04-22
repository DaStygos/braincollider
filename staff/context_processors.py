from problems.models import Submission
from .permissions import can_access_pending_submissions, get_accessible_pending_submissions

def pending_submissions_count(request):
    can_access = can_access_pending_submissions(request.user)
    if can_access:
        count = get_accessible_pending_submissions(request.user).count()
        return {
            'pending_submissions_count': count,
            'can_access_pending_submissions': True,
        }
    return {
        'pending_submissions_count': 0,
        'can_access_pending_submissions': False,
    }