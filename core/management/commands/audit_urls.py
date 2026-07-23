from django.core.management.base import BaseCommand
from django.urls import reverse


class Command(BaseCommand):
    help = "Audit important named URLs."

    URL_NAMES = [
        "dashboard",
        "login",
        "logout",
        "change_own_password",
        "staff_dashboard",
        "patient_list",
        "patient_create",
        "visit_list",
        "appointment_list",
        "appointment_calendar",
        "clinic_queue",
        "doctor_worklist",
        "surgery_list",
        "surgery_theatre_dashboard",
        "bill_list",
        "global_search",
        "reports_dashboard",
        "financial_report",
        "clinical_report",
        "appointment_report",
        "surgery_report",
        "financial_report_pdf",
        "financial_report_excel",
        "clinical_report_pdf",
        "clinical_report_excel",
        "appointment_report_pdf",
        "appointment_report_excel",
        "surgery_report_pdf",
        "surgery_report_excel",
        "notification_list",
        "backup_dashboard",
        "system_setting_update",
        "audit_log_list",
    ]

    def handle(self, *args, **options):
        failed = []

        for name in self.URL_NAMES:
            try:
                reverse(name)
            except Exception as e:
                failed.append((name, str(e)))

        if failed:
            self.stdout.write(self.style.ERROR("Broken URL names:"))
            for name, error in failed:
                self.stdout.write(f" - {name}: {error}")
        else:
            self.stdout.write(self.style.SUCCESS("All important URL names resolved."))