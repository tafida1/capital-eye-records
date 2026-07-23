from .models import Notification


def create_notification(
    title,
    message,
    notification_type=Notification.NotificationType.INFO,
    recipient=None,
    link="",
    is_global=False,
):
    return Notification.objects.create(
        recipient=recipient,
        title=title,
        message=message,
        notification_type=notification_type,
        link=link,
        is_global=is_global,
    )