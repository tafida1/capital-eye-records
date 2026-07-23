from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.shortcuts import render, redirect, get_object_or_404

from .models import Notification


@login_required
def notification_list(request):
    query = request.GET.get("q", "").strip()
    status = request.GET.get("status", "").strip()

    notifications = Notification.objects.filter(
        Q(recipient=request.user) | Q(is_global=True)
    ).order_by("-created_at")

    if query:
        notifications = notifications.filter(
            Q(title__icontains=query) | Q(message__icontains=query)
        )

    if status == "unread":
        notifications = notifications.filter(is_read=False)
    elif status == "read":
        notifications = notifications.filter(is_read=True)

    return render(request, "notifications/notification_list.html", {
        "notifications": notifications,
        "query": query,
        "status": status,
    })


@login_required
def notification_mark_read(request, pk):
    notification = get_object_or_404(
        Notification,
        Q(pk=pk),
        Q(recipient=request.user) | Q(is_global=True),
    )

    notification.is_read = True
    notification.save(update_fields=["is_read"])

    messages.success(request, "Notification marked as read.")

    if notification.link:
        return redirect(notification.link)

    return redirect("notification_list")


@login_required
def notification_mark_all_read(request):
    Notification.objects.filter(recipient=request.user, is_read=False).update(is_read=True)
    Notification.objects.filter(is_global=True, is_read=False).update(is_read=True)

    messages.success(request, "All notifications marked as read.")
    return redirect("notification_list")