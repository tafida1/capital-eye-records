from django.conf import settings
from django.db import models
from django.utils import timezone


class AuditLog(models.Model):
    class ActionType(models.TextChoices):
        LOGIN = "LOGIN", "Login"
        LOGOUT = "LOGOUT", "Logout"
        CREATE = "CREATE", "Create"
        UPDATE = "UPDATE", "Update"
        DELETE = "DELETE", "Delete"
        VIEW = "VIEW", "View"
        EXPORT = "EXPORT", "Export"
        IMPORT = "IMPORT", "Import"
        PRINT = "PRINT", "Print/PDF"
        BACKUP = "BACKUP", "Backup"
        RESTORE = "RESTORE", "Restore"
        OTHER = "OTHER", "Other"

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="audit_logs",
    )

    action = models.CharField(
        max_length=30,
        choices=ActionType.choices,
        default=ActionType.OTHER,
    )

    module = models.CharField(max_length=100)
    description = models.TextField()

    object_id = models.CharField(max_length=100, blank=True)
    object_repr = models.CharField(max_length=255, blank=True)

    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(blank=True)

    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["action"]),
            models.Index(fields=["module"]),
            models.Index(fields=["created_at"]),
            models.Index(fields=["user"]),
        ]

    def __str__(self):
        return f"{self.created_at} - {self.user} - {self.action}"