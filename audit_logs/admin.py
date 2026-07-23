from django.contrib import admin
from .models import AuditLog


@admin.register(AuditLog)
class AuditLogAdmin(admin.ModelAdmin):
    list_display = (
        "created_at",
        "user",
        "action",
        "module",
        "object_repr",
        "ip_address",
    )

    list_filter = (
        "action",
        "module",
        "created_at",
        "user",
    )

    search_fields = (
        "user__username",
        "user__first_name",
        "user__last_name",
        "module",
        "description",
        "object_repr",
        "ip_address",
    )

    readonly_fields = (
        "user",
        "action",
        "module",
        "description",
        "object_id",
        "object_repr",
        "ip_address",
        "user_agent",
        "created_at",
    )

    date_hierarchy = "created_at"
    ordering = ("-created_at",)
    list_per_page = 50

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return request.user.is_superuser