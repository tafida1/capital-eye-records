from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect

from accounts.decorators import admin_required
from audit_logs.models import AuditLog
from audit_logs.utils import log_activity

from .forms import SystemSettingForm
from .models import SystemSetting


@login_required
@admin_required
def system_setting_update(request):
    setting = SystemSetting.get_settings()
    form = SystemSettingForm(request.POST or None, instance=setting)

    if request.method == "POST":
        if form.is_valid():
            form.save()

            log_activity(
                request,
                AuditLog.ActionType.UPDATE,
                "System Settings",
                "Updated system settings.",
                object_id=setting.pk,
                object_repr=setting.system_name,
            )

            messages.success(request, "System settings updated successfully.")
            return redirect("system_setting_update")

        messages.error(request, "Please correct the errors below.")

    return render(request, "settings_app/system_setting_form.html", {
        "form": form,
        "setting": setting,
    })