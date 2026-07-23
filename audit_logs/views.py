from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.shortcuts import render

from accounts.decorators import admin_required
from .models import AuditLog


@login_required
@admin_required
def audit_log_list(request):
    query = request.GET.get("q", "").strip()
    action = request.GET.get("action", "").strip()
    module = request.GET.get("module", "").strip()

    logs = AuditLog.objects.select_related("user").all()

    if query:
        logs = logs.filter(
            Q(user__username__icontains=query)
            | Q(user__first_name__icontains=query)
            | Q(user__last_name__icontains=query)
            | Q(module__icontains=query)
            | Q(description__icontains=query)
            | Q(object_repr__icontains=query)
            | Q(ip_address__icontains=query)
        )

    if action:
        logs = logs.filter(action=action)

    if module:
        logs = logs.filter(module__icontains=module)

    return render(request, "audit_logs/audit_log_list.html", {
        "logs": logs,
        "query": query,
        "action": action,
        "module": module,
        "action_choices": AuditLog.ActionType.choices,
    })