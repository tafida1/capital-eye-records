from django.contrib import admin
from .models import Notification


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = (
        "title",
        "notification_type",
        "recipient",
        "is_global",
        "is_read",
        "created_at",
    )

    list_filter = (
        "notification_type",
        "is_global",
        "is_read",
        "created_at",
    )

    search_fields = (
        "title",
        "message",
        "recipient__username",
        "recipient__first_name",
        "recipient__last_name",
    )

    readonly_fields = ("created_at",)
    date_hierarchy = "created_at"