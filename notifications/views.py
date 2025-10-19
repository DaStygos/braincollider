from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from .models import Notification

# Create your views here.

@login_required
def notifications_list(request):
    unread_notifications = Notification.objects.filter(user=request.user, read=False).order_by('-created_at')
    unread_count = unread_notifications.count()
    read_notifications = Notification.objects.filter(user=request.user, read=True).order_by('-created_at')
    return render(request, "notifications/notifications_list.html", {"unread_notifications": unread_notifications, "read_notifications": read_notifications, "unread_count": unread_count})

@login_required
def mark_as_read(request, pk):
    notification = get_object_or_404(Notification, pk=pk, user=request.user)
    notification.read = True
    notification.save()
    return redirect("notifications:notifications_list")