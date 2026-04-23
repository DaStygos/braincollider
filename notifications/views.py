from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from .models import Notification


def _notifications_for_user(user):
    return Notification.objects.filter(user=user).order_by("-created_at")


@login_required
def notifications_list(request):
    notifications = _notifications_for_user(request.user)
    unread_notifications = notifications.filter(read=False)
    unread_count = unread_notifications.count()
    read_notifications = notifications.filter(read=True)
    context = {
        "unread_notifications": unread_notifications,
        "read_notifications": read_notifications,
        "unread_count": unread_count,
    }
    return render(request, "notifications/notifications_list.html", context)


@login_required
def mark_as_read(request, pk):
    notification = get_object_or_404(Notification, pk=pk, user=request.user)
    notification.read = True
    notification.save(update_fields=["read"])
    return redirect("notifications:notifications_list")