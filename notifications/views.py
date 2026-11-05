from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.contrib import messages
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
@require_POST
def mark_as_read(request, pk):
    notification = get_object_or_404(Notification, pk=pk, user=request.user)
    if not notification.read:
        notification.read = True
        notification.save(update_fields=["read"])
        messages.success(request, "La notification a été marquée comme lue.")
    return redirect("notifications:notifications_list")


@login_required
@require_POST
def mark_all_as_read(request):
    updated_count = _notifications_for_user(request.user).filter(read=False).update(read=True)
    if updated_count:
        messages.success(request, f"{updated_count} notification(s) marquée(s) comme lue(s).")
    return redirect("notifications:notifications_list")
