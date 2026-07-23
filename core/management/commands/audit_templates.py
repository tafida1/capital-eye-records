from pathlib import Path

from django.core.management.base import BaseCommand
from django.conf import settings


class Command(BaseCommand):
    help = "Audit important project templates."

    REQUIRED_TEMPLATES = [
        "base.html",
        "accounts/login.html",
        "accounts/change_password.html",
        "accounts/staff_dashboard.html",
        "accounts/staff_form.html",
        "accounts/staff_detail.html",
        "patients/patient_list.html",
        "patients/patient_detail.html",
        "patients/visit_detail.html",
        "patients/bill_detail.html",
        "patients/surgery_detail.html",
        "patients/appointment_calendar.html",
        "patients/clinic_queue.html",
        "patients/doctor_worklist.html",
        "patients/surgery_theatre_dashboard.html",
        "patients/reports_dashboard.html",
        "patients/reports/financial_report.html",
        "patients/reports/clinical_report.html",
        "patients/reports/appointment_report.html",
        "patients/reports/surgery_report.html",
        "patients/reports/pdf/report_pdf_base.html",
        "patients/reports/pdf/financial_report_pdf.html",
        "patients/reports/pdf/clinical_report_pdf.html",
        "patients/reports/pdf/appointment_report_pdf.html",
        "patients/reports/pdf/surgery_report_pdf.html",
        "notifications/notification_list.html",
        "backups/backup_dashboard.html",
        "settings_app/system_setting_form.html",
        "audit_logs/audit_log_list.html",
    ]

    def handle(self, *args, **options):
        template_root = Path(settings.BASE_DIR) / "templates"
        missing = []

        for template in self.REQUIRED_TEMPLATES:
            path = template_root / template
            if not path.exists():
                missing.append(template)

        if missing:
            self.stdout.write(self.style.ERROR("Missing templates:"))
            for item in missing:
                self.stdout.write(f" - {item}")
        else:
            self.stdout.write(self.style.SUCCESS("All required templates exist."))