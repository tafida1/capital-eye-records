from .models import Notification


def notification_context(request):
    if not request.user.is_authenticated:
        return {
            "unread_notifications_count": 0,
            "recent_notifications": [],
        }

    notifications = Notification.objects.filter(
        recipient=request.user,
        is_read=False,
    ) | Notification.objects.filter(
        is_global=True,
        is_read=False,
    )

    notifications = notifications.order_by("-created_at")

    return {
        "unread_notifications_count": notifications.count(),
        "recent_notifications": notifications[:5],
    }