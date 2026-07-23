from django.contrib import messages
from django.contrib.auth import login, logout, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from .forms import LoginForm, UserPasswordChangeForm, CustomUserCreationForm, CustomUserChangeForm, StaffPasswordResetForm, OwnPasswordChangeForm
from audit_logs.utils import log_activity
from audit_logs.models import AuditLog
from django.db.models import Count, Q
from .decorators import admin_required
from .models import User


def login_view(request):
    if request.user.is_authenticated:
        return redirect("dashboard")

    form = LoginForm(request, data=request.POST or None)

    if request.method == "POST":
        if form.is_valid():
            user = form.get_user()

            if not user.is_active:
                messages.error(request, "This account has been disabled.")
                return redirect("login")

            login(request, user)
            log_activity(
                request,
                AuditLog.ActionType.LOGIN,
                "Authentication",
                f"{user.username} logged in.",
                object_id=user.pk,
                object_repr=user.username,
            )
            messages.success(request, f"Welcome back, {user.get_full_name() or user.username}.")
            return redirect("dashboard")

        messages.error(request, "Invalid username or password.")

    return render(request, "accounts/login.html", {"form": form})


@login_required
def logout_view(request):
    log_activity(
        request,
        AuditLog.ActionType.LOGOUT,
        "Authentication",
        f"{request.user.username} logged out.",
        object_id=request.user.pk,
        object_repr=request.user.username,
    )
    logout(request)
    messages.success(request, "You have successfully logged out.")
    return redirect("login")


@login_required
def change_password_view(request):
    form = UserPasswordChangeForm(request.user, request.POST or None)

    if request.method == "POST":
        if form.is_valid():
            user = form.save()
            user.must_change_password = False
            user.save(update_fields=["must_change_password"])

            update_session_auth_hash(request, user)
            messages.success(request, "Your password has been changed successfully.")
            return redirect("dashboard")

        messages.error(request, "Please correct the errors below.")

    return render(request, "accounts/change_password.html", {"form": form})



@login_required
@admin_required
def staff_dashboard(request):
    query = request.GET.get("q", "").strip()
    role = request.GET.get("role", "").strip()
    status = request.GET.get("status", "").strip()

    users = User.objects.all().order_by("role", "first_name", "last_name")

    if query:
        users = users.filter(
            Q(username__icontains=query)
            | Q(first_name__icontains=query)
            | Q(last_name__icontains=query)
            | Q(email__icontains=query)
            | Q(phone_number__icontains=query)
            | Q(staff_id__icontains=query)
            | Q(department__icontains=query)
        )

    if role:
        users = users.filter(role=role)

    if status == "active":
        users = users.filter(is_active=True)
    elif status == "inactive":
        users = users.filter(is_active=False)

    total_staff = User.objects.count()
    active_staff = User.objects.filter(is_active=True).count()
    inactive_staff = User.objects.filter(is_active=False).count()
    admin_staff = User.objects.filter(is_staff=True).count()

    role_summary = User.objects.values("role").annotate(
        count=Count("id")
    ).order_by("role")

    return render(request, "accounts/staff_dashboard.html", {
        "users": users,
        "query": query,
        "role": role,
        "status": status,
        "role_choices": User.Role.choices,
        "total_staff": total_staff,
        "active_staff": active_staff,
        "inactive_staff": inactive_staff,
        "admin_staff": admin_staff,
        "role_summary": role_summary,
    })


@login_required
@admin_required
def staff_create(request):
    form = CustomUserCreationForm(request.POST or None)

    if request.method == "POST":
        if form.is_valid():
            user = form.save()

            log_activity(
                request,
                AuditLog.ActionType.CREATE,
                "Staff Management",
                f"Created staff account: {user.username}.",
                object_id=user.pk,
                object_repr=user.username,
            )

            messages.success(request, "Staff account created successfully.")
            return redirect("staff_dashboard")

        messages.error(request, "Please correct the errors below.")

    return render(request, "accounts/staff_form.html", {
        "form": form,
        "title": "Create Staff Account",
        "button_text": "Create Staff",
    })


@login_required
@admin_required
def staff_update(request, pk):
    user_obj = get_object_or_404(User, pk=pk)
    form = CustomUserChangeForm(request.POST or None, instance=user_obj)

    if request.method == "POST":
        if form.is_valid():
            form.save()

            log_activity(
                request,
                AuditLog.ActionType.UPDATE,
                "Staff Management",
                f"Updated staff account: {user_obj.username}.",
                object_id=user_obj.pk,
                object_repr=user_obj.username,
            )

            messages.success(request, "Staff account updated successfully.")
            return redirect("staff_dashboard")

        messages.error(request, "Please correct the errors below.")

    return render(request, "accounts/staff_form.html", {
        "form": form,
        "staff": user_obj,
        "title": "Update Staff Account",
        "button_text": "Save Changes",
    })


@login_required
@admin_required
def staff_toggle_active(request, pk):
    user_obj = get_object_or_404(User, pk=pk)

    if user_obj == request.user:
        messages.error(request, "You cannot deactivate your own account.")
        return redirect("staff_dashboard")

    user_obj.is_active = not user_obj.is_active
    user_obj.save(update_fields=["is_active"])

    action_word = "activated" if user_obj.is_active else "deactivated"

    log_activity(
        request,
        AuditLog.ActionType.UPDATE,
        "Staff Management",
        f"{action_word.title()} staff account: {user_obj.username}.",
        object_id=user_obj.pk,
        object_repr=user_obj.username,
    )

    messages.success(request, f"Staff account {action_word} successfully.")
    return redirect("staff_dashboard")


@login_required
@admin_required
def staff_detail(request, pk):
    user_obj = get_object_or_404(User, pk=pk)
    recent_logs = user_obj.audit_logs.all()[:20]

    return render(request, "accounts/staff_detail.html", {
        "staff": user_obj,
        "recent_logs": recent_logs,
    })


@login_required
def change_own_password(request):
    form = OwnPasswordChangeForm(request.user, request.POST or None)

    if request.method == "POST":
        if form.is_valid():
            user = form.save()
            user.must_change_password = False
            user.save(update_fields=["must_change_password"])

            update_session_auth_hash(request, user)

            log_activity(
                request,
                AuditLog.ActionType.UPDATE,
                "Security",
                "Changed own password.",
                object_id=request.user.pk,
                object_repr=request.user.username,
            )

            messages.success(request, "Your password was changed successfully.")
            return redirect("dashboard")

        messages.error(request, "Please correct the errors below.")

    return render(request, "accounts/change_password.html", {
        "form": form,
        "title": "Change My Password",
        "button_text": "Change Password",
    })


@login_required
@admin_required
def staff_password_reset(request, pk):
    user_obj = get_object_or_404(User, pk=pk)
    form = StaffPasswordResetForm(user_obj, request.POST or None)

    if request.method == "POST":
        if form.is_valid():
            form.save()
            user_obj.must_change_password = True
            user_obj.save(update_fields=["must_change_password"])

            log_activity(
                request,
                AuditLog.ActionType.UPDATE,
                "Security",
                f"Admin reset password for staff account: {user_obj.username}.",
                object_id=user_obj.pk,
                object_repr=user_obj.username,
            )

            messages.success(
                request,
                "Password reset successfully. Staff will be required to change password on next login."
            )
            return redirect("staff_detail", pk=user_obj.pk)

        messages.error(request, "Please correct the errors below.")

    return render(request, "accounts/staff_password_reset.html", {
        "form": form,
        "staff": user_obj,
        "title": "Reset Staff Password",
        "button_text": "Reset Password",
    })


@login_required
@admin_required
def staff_force_password_change(request, pk):
    user_obj = get_object_or_404(User, pk=pk)

    user_obj.must_change_password = True
    user_obj.save(update_fields=["must_change_password"])

    log_activity(
        request,
        AuditLog.ActionType.UPDATE,
        "Security",
        f"Forced password change for staff account: {user_obj.username}.",
        object_id=user_obj.pk,
        object_repr=user_obj.username,
    )

    messages.success(request, "Staff will be required to change password on next login.")
    return redirect("staff_detail", pk=user_obj.pk)