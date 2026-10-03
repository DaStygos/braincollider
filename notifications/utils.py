from notifications.models import Notification


def create_notification(user, message, redirect_url=""):
    return Notification.objects.create(
        user=user,
        message=message,
        redirect_url=redirect_url,
    )
