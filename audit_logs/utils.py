from .models import AuditLog


def get_client_ip(request):
    x_forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")

    if x_forwarded_for:
        return x_forwarded_for.split(",")[0]

    return request.META.get("REMOTE_ADDR")


def log_activity(
    request,
    action,
    module,
    description,
    object_id="",
    object_repr="",
):
    user = request.user if request.user.is_authenticated else None

    AuditLog.objects.create(
        user=user,
        action=action,
        module=module,
        description=description,
        object_id=str(object_id) if object_id else "",
        object_repr=str(object_repr) if object_repr else "",
        ip_address=get_client_ip(request),
        user_agent=request.META.get("HTTP_USER_AGENT", ""),
    )