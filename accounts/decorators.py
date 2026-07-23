from functools import wraps
from django.contrib import messages
from django.shortcuts import redirect


def role_required(*allowed_roles):
    def decorator(view_func):
        @wraps(view_func)
        def wrapper(request, *args, **kwargs):
            user = request.user

            if not user.is_authenticated:
                return redirect("login")

            if user.is_superuser or user.role in allowed_roles:
                return view_func(request, *args, **kwargs)

            messages.error(request, "You do not have permission to access that page.")
            return redirect("dashboard")

        return wrapper
    return decorator


def admin_required(view_func):
    return role_required("SUPER_ADMIN", "HOSPITAL_ADMIN")(view_func)


def clinical_staff_required(view_func):
    return role_required(
        "SUPER_ADMIN",
        "HOSPITAL_ADMIN",
        "DOCTOR",
        "NURSE",
        "LAB_STAFF",
    )(view_func)


def records_staff_required(view_func):
    return role_required(
        "SUPER_ADMIN",
        "HOSPITAL_ADMIN",
        "RECEPTIONIST",
        "RECORDS_OFFICER",
    )(view_func)


def finance_staff_required(view_func):
    return role_required(
        "SUPER_ADMIN",
        "HOSPITAL_ADMIN",
        "CASHIER",
    )(view_func)