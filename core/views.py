import sys
from pathlib import Path

import django
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.db.models import Sum
from django.shortcuts import render, redirect
from django.utils import timezone

from patients.models import (
    Patient,
    PatientVisit,
    Appointment,
    SurgeryProcedure,
    Bill,
    Payment,
)

try:
    from audit_logs.models import AuditLog
except Exception:
    AuditLog = None


def home(request):
    if request.user.is_authenticated:
        return redirect("dashboard")
    return redirect("login")


@login_required
def dashboard(request):
    today = timezone.localdate()

    total_patients = Patient.objects.count()

    visits_today = PatientVisit.objects.filter(
        visit_date__date=today
    ).count()

    appointments_today = Appointment.objects.filter(
        appointment_date=today
    ).count()

    today_payments = Payment.objects.filter(
        payment_date__date=today
    ).aggregate(total=Sum("amount"))["total"] or 0

    pending_bills = Bill.objects.exclude(
        status=Bill.BillStatus.PAID
    ).exclude(
        status=Bill.BillStatus.CANCELLED
    ).count()

    upcoming_surgeries = SurgeryProcedure.objects.filter(
        status__in=[
            SurgeryProcedure.ProcedureStatus.PLANNED,
            SurgeryProcedure.ProcedureStatus.POSTPONED,
        ]
    ).count()

    recent_patients = Patient.objects.select_related("registered_by")[:5]
    recent_visits = PatientVisit.objects.select_related("patient", "created_by")[:5]
    upcoming_appointments = Appointment.objects.select_related("patient", "assigned_to").filter(
        appointment_date__gte=today
    )[:5]

    recent_logs = []
    if AuditLog:
        recent_logs = AuditLog.objects.select_related("user")[:8]

    backup_dir = Path(settings.BACKUP_ROOT)
    backup_dir.mkdir(exist_ok=True)

    latest_backup = None
    backup_files = sorted(
        backup_dir.glob("*.zip"),
        key=lambda x: x.stat().st_mtime,
        reverse=True,
    )

    if backup_files:
        latest_backup = backup_files[0]

    system_health = {
        "database": "Connected",
        "lan_mode": "Ready",
        "backup": "Available" if latest_backup else "No Backup Yet",
        "storage": "OK",
    }

    context = {
        "total_patients": total_patients,
        "visits_today": visits_today,
        "appointments_today": appointments_today,
        "today_payments": today_payments,
        "pending_bills": pending_bills,
        "upcoming_surgeries": upcoming_surgeries,
        "recent_patients": recent_patients,
        "recent_visits": recent_visits,
        "upcoming_appointments": upcoming_appointments,
        "recent_logs": recent_logs,
        "latest_backup": latest_backup,
        "system_health": system_health,
    }

    return render(request, "core/dashboard.html", context)



@login_required
def about_system(request):
    context = {
        "python_version": sys.version.split()[0],
        "django_version": django.get_version(),
        "system_version": "1.0.0",
        "edition": "Enterprise Edition",
        "developer": "Mutafs Global Technology",
        "license_type": "Commercial",
    }

    return render(request, "core/about_system.html", context)
