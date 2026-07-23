from django import forms
from .models import SystemSetting


class SystemSettingForm(forms.ModelForm):
    class Meta:
        model = SystemSetting
        fields = [
            "hospital_name",
            "system_name",
            "hospital_address",
            "hospital_phone",
            "hospital_email",
            "receipt_footer",
            "report_footer",
            "backup_reminder_text",
            "default_currency",
            "allow_duplicate_warning",
            "enable_audit_logs",
        ]

        widgets = {
            "hospital_name": forms.TextInput(attrs={"class": "form-control"}),
            "system_name": forms.TextInput(attrs={"class": "form-control"}),
            "hospital_address": forms.Textarea(attrs={"class": "form-control", "rows": 3}),
            "hospital_phone": forms.TextInput(attrs={"class": "form-control"}),
            "hospital_email": forms.EmailInput(attrs={"class": "form-control"}),
            "receipt_footer": forms.Textarea(attrs={"class": "form-control", "rows": 3}),
            "report_footer": forms.Textarea(attrs={"class": "form-control", "rows": 3}),
            "backup_reminder_text": forms.TextInput(attrs={"class": "form-control"}),
            "default_currency": forms.TextInput(attrs={"class": "form-control"}),
            "allow_duplicate_warning": forms.CheckboxInput(attrs={"class": "form-check-input"}),
            "enable_audit_logs": forms.CheckboxInput(attrs={"class": "form-check-input"}),
        }