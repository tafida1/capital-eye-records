from django.contrib import admin
from .models import SystemSetting


@admin.register(SystemSetting)
class SystemSettingAdmin(admin.ModelAdmin):
    list_display = (
        "hospital_name",
        "system_name",
        "hospital_phone",
        "hospital_email",
        "updated_at",
    )

    readonly_fields = ("updated_at",)

    fieldsets = (
        ("Hospital Identity", {
            "fields": (
                "hospital_name",
                "system_name",
                "hospital_address",
                "hospital_phone",
                "hospital_email",
            )
        }),
        ("Reports and Receipts", {
            "fields": (
                "receipt_footer",
                "report_footer",
                "default_currency",
            )
        }),
        ("System Behavior", {
            "fields": (
                "backup_reminder_text",
                "allow_duplicate_warning",
                "enable_audit_logs",
            )
        }),
        ("System Info", {
            "fields": (
                "updated_at",
            )
        }),
    )

    def has_add_permission(self, request):
        return not SystemSetting.objects.exists()

    def has_delete_permission(self, request, obj=None):
        return False