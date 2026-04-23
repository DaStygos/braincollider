from notifications.models import Notification


def create_notification(user, message):
    return Notification.objects.create(user=user, message=message)
