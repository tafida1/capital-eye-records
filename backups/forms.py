from django import forms


class RestoreBackupForm(forms.Form):
    backup_file = forms.FileField(
        widget=forms.FileInput(attrs={
            "class": "form-control",
            "accept": ".zip",
        })
    )

    confirm_restore = forms.BooleanField(
        required=True,
        label="I understand this will restore data into the system.",
        widget=forms.CheckboxInput(attrs={"class": "form-check-input"})
    )