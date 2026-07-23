from django.conf import settings
from django.db import models
from django.utils import timezone


class Notification(models.Model):
    class NotificationType(models.TextChoices):
        INFO = "INFO", "Information"
        WARNING = "WARNING", "Warning"
        SUCCESS = "SUCCESS", "Success"
        DANGER = "DANGER", "Danger"
        APPOINTMENT = "APPOINTMENT", "Appointment"
        BACKUP = "BACKUP", "Backup"
        SYSTEM = "SYSTEM", "System Announcement"

    recipient = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="notifications",
        null=True,
        blank=True,
        help_text="Leave blank for global notification.",
    )

    title = models.CharField(max_length=200)
    message = models.TextField()
    notification_type = models.CharField(
        max_length=30,
        choices=NotificationType.choices,
        default=NotificationType.INFO,
    )

    link = models.CharField(max_length=255, blank=True)
    is_read = models.BooleanField(default=False)
    is_global = models.BooleanField(default=False)

    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["recipient", "is_read"]),
            models.Index(fields=["is_global", "is_read"]),
            models.Index(fields=["created_at"]),
        ]

    def __str__(self):
        return self.title