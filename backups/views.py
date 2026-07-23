import zipfile
from pathlib import Path

from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.management import call_command
from django.http import FileResponse
from django.shortcuts import render, redirect
from django.utils import timezone

from accounts.decorators import admin_required
from audit_logs.models import AuditLog
from audit_logs.utils import log_activity

from .forms import RestoreBackupForm
from .utils import create_system_backup

from notifications.utils import create_notification
from notifications.models import Notification


@login_required
@admin_required
def backup_dashboard(request):
    backup_dir = Path(settings.BACKUP_ROOT)
    backup_dir.mkdir(exist_ok=True)

    backups = sorted(
        backup_dir.glob("*.zip"),
        key=lambda x: x.stat().st_mtime,
        reverse=True,
    )

    return render(request, "backups/backup_dashboard.html", {
        "backups": backups,
    })


@login_required
@admin_required
def create_backup(request):
    backup_path = create_system_backup()

    log_activity(
        request,
        AuditLog.ActionType.BACKUP,
        "Backup",
        f"Created system backup: {backup_path.name}",
        object_repr=backup_path.name,
    )

    create_notification(
        title="Backup Created",
        message=f"System backup was created successfully: {backup_path.name}",
        notification_type=Notification.NotificationType.BACKUP,
        is_global=True,
        link="/backups/",
    )

    messages.success(request, f"Backup created successfully: {backup_path.name}")
    return redirect("backup_dashboard")


@login_required
@admin_required
def download_backup(request, filename):
    backup_path = Path(settings.BACKUP_ROOT) / filename

    if not backup_path.exists():
        messages.error(request, "Backup file not found.")
        return redirect("backup_dashboard")

    return FileResponse(
        open(backup_path, "rb"),
        as_attachment=True,
        filename=filename,
    )


@login_required
@admin_required
def restore_backup(request):
    form = RestoreBackupForm(request.POST or None, request.FILES or None)

    if request.method == "POST":
        if form.is_valid():
            backup_file = request.FILES["backup_file"]

            restore_dir = Path(settings.BACKUP_ROOT) / "restore_temp"
            restore_dir.mkdir(parents=True, exist_ok=True)

            zip_path = restore_dir / backup_file.name

            with open(zip_path, "wb+") as destination:
                for chunk in backup_file.chunks():
                    destination.write(chunk)

            try:
                with zipfile.ZipFile(zip_path, "r") as backup_zip:
                    backup_zip.extractall(restore_dir)

                json_files = list(restore_dir.glob("*.json"))

                if not json_files:
                    messages.error(request, "Invalid backup file. No database JSON found.")
                    return redirect("restore_backup")

                call_command("loaddata", str(json_files[0]))

                log_activity(
                    request,
                    AuditLog.ActionType.RESTORE,
                    "Backup",
                    f"Restored system backup: {backup_file.name}",
                    object_repr=backup_file.name,
                )

                messages.success(request, "Backup restored successfully.")
                return redirect("backup_dashboard")

            except Exception as e:
                messages.error(request, f"Restore failed: {e}")
                return redirect("restore_backup")

        messages.error(request, "Please correct the errors below.")

    return render(request, "backups/restore_backup.html", {
        "form": form,
    })