from django.db import models


class SystemSetting(models.Model):
    hospital_name = models.CharField(
        max_length=200,
        default="CAPITAL EYE HOSPITAL",
    )

    system_name = models.CharField(
        max_length=200,
        default="CAPITAL EYE HOSPITAL RECORDS SYSTEM",
    )

    hospital_address = models.TextField(blank=True)
    hospital_phone = models.CharField(max_length=50, blank=True)
    hospital_email = models.EmailField(blank=True)

    receipt_footer = models.TextField(
        blank=True,
        default="Thank you for choosing Capital Eye Hospital.",
    )

    report_footer = models.TextField(
        blank=True,
        default="Generated from CAPITAL EYE HOSPITAL RECORDS SYSTEM.",
    )

    backup_reminder_text = models.CharField(
        max_length=255,
        default="Remember to backup clinic records regularly.",
    )

    default_currency = models.CharField(
        max_length=10,
        default="₦",
    )

    allow_duplicate_warning = models.BooleanField(default=True)
    enable_audit_logs = models.BooleanField(default=True)

    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "System Setting"
        verbose_name_plural = "System Settings"

    def __str__(self):
        return self.system_name

    @classmethod
    def get_settings(cls):
        obj, created = cls.objects.get_or_create(pk=1)
        return obj