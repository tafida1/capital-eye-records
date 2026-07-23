from django import forms
from .models import (
    Patient,
    FamilyGroup,
    PatientVisit,
    Consultation,
    EyeExamination,
    DiagnosisTreatment,
    Prescription,
    SurgeryProcedure,
    Appointment,
    Bill,
    Payment,
)


def apply_enterprise_form_style(form):
    for field_name, field in form.fields.items():
        existing_class = field.widget.attrs.get("class", "")

        if field.widget.__class__.__name__ == "Select":
            field.widget.attrs["class"] = f"{existing_class} form-select".strip()
        else:
            field.widget.attrs["class"] = f"{existing_class} form-control".strip()

        field.widget.attrs.setdefault("placeholder", field.label)


class FamilyGroupForm(forms.ModelForm):
    class Meta:
        model = FamilyGroup
        fields = [
            "family_name",
            "head_of_family",
            "primary_phone",
            "address",
            "notes",
        ]

        widgets = {
            "family_name": forms.TextInput(attrs={"class": "form-control"}),
            "head_of_family": forms.TextInput(attrs={"class": "form-control"}),
            "primary_phone": forms.TextInput(attrs={"class": "form-control"}),
            "address": forms.Textarea(attrs={"class": "form-control", "rows": 2}),
            "notes": forms.Textarea(attrs={"class": "form-control", "rows": 3}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        apply_enterprise_form_style(self)


class PatientForm(forms.ModelForm):
    class Meta:
        model = Patient
        fields = [
            "full_name",
            "gender",
            "date_of_birth",
            "age",
            "phone_number",
            "address",
            "occupation",
            "next_of_kin_name",
            "next_of_kin_phone",
            "next_of_kin_relationship",
            "family_group",
            "family_group_name",
            "family_relationship",
            "medical_history",
            "allergy_history",
            "eye_complaint",
            "diagnosis",
            "treatment",
            "surgery_procedure_details",
            "payment_status",
            "notes",
        ]

        widgets = {
            "full_name": forms.TextInput(attrs={"class": "form-control"}),
            "gender": forms.Select(attrs={"class": "form-select"}),
            "date_of_birth": forms.DateInput(attrs={"class": "form-control", "type": "date"}),
            "age": forms.NumberInput(attrs={"class": "form-control", "min": "0"}),
            "phone_number": forms.TextInput(attrs={"class": "form-control"}),
            "address": forms.Textarea(attrs={"class": "form-control", "rows": 2}),
            "occupation": forms.TextInput(attrs={"class": "form-control"}),
            "next_of_kin_name": forms.TextInput(attrs={"class": "form-control"}),
            "next_of_kin_phone": forms.TextInput(attrs={"class": "form-control"}),
            "next_of_kin_relationship": forms.TextInput(attrs={"class": "form-control"}),
            "family_group": forms.Select(attrs={"class": "form-select"}),
            "family_group_name": forms.TextInput(attrs={"class": "form-control"}),
            "family_relationship": forms.TextInput(attrs={"class": "form-control"}),
            "medical_history": forms.Textarea(attrs={"class": "form-control", "rows": 3}),
            "allergy_history": forms.Textarea(attrs={"class": "form-control", "rows": 3}),
            "eye_complaint": forms.Textarea(attrs={"class": "form-control", "rows": 3}),
            "diagnosis": forms.Textarea(attrs={"class": "form-control", "rows": 3}),
            "treatment": forms.Textarea(attrs={"class": "form-control", "rows": 3}),
            "surgery_procedure_details": forms.Textarea(attrs={"class": "form-control", "rows": 3}),
            "payment_status": forms.Select(attrs={"class": "form-select"}),
            "notes": forms.Textarea(attrs={"class": "form-control", "rows": 3}),
        }

    def clean(self):
        cleaned_data = super().clean()

        full_name = cleaned_data.get("full_name")
        phone_number = cleaned_data.get("phone_number")
        date_of_birth = cleaned_data.get("date_of_birth")

        qs = Patient.objects.all()

        if self.instance.pk:
            qs = qs.exclude(pk=self.instance.pk)

        if full_name and phone_number:
            duplicate = qs.filter(
                full_name__iexact=full_name.strip(),
                phone_number__iexact=phone_number.strip(),
            ).exists()

            if duplicate:
                raise forms.ValidationError(
                    "Possible duplicate patient detected: a patient with this full name and phone number already exists."
                )

        if full_name and date_of_birth:
            duplicate = qs.filter(
                full_name__iexact=full_name.strip(),
                date_of_birth=date_of_birth,
            ).exists()

            if duplicate:
                raise forms.ValidationError(
                    "Possible duplicate patient detected: a patient with this full name and date of birth already exists."
                )

        return cleaned_data

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        apply_enterprise_form_style(self)


class PatientVisitForm(forms.ModelForm):
    class Meta:
        model = PatientVisit
        fields = [
            "patient",
            "visit_type",
            "status",
            "chief_complaint",
            "brief_history",
            "temperature",
            "blood_pressure",
            "pulse",
            "weight",
            "notes",
        ]

        widgets = {
            "patient": forms.Select(attrs={"class": "form-select"}),
            "visit_type": forms.Select(attrs={"class": "form-select"}),
            "status": forms.Select(attrs={"class": "form-select"}),
            "chief_complaint": forms.Textarea(attrs={"class": "form-control", "rows": 3}),
            "brief_history": forms.Textarea(attrs={"class": "form-control", "rows": 3}),
            "temperature": forms.TextInput(attrs={"class": "form-control", "placeholder": "e.g. 36.8°C"}),
            "blood_pressure": forms.TextInput(attrs={"class": "form-control", "placeholder": "e.g. 120/80"}),
            "pulse": forms.TextInput(attrs={"class": "form-control", "placeholder": "e.g. 78 bpm"}),
            "weight": forms.TextInput(attrs={"class": "form-control", "placeholder": "e.g. 65 kg"}),
            "notes": forms.Textarea(attrs={"class": "form-control", "rows": 3}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        apply_enterprise_form_style(self)


class PatientVisitQuickForm(forms.ModelForm):
    class Meta:
        model = PatientVisit
        fields = [
            "visit_type",
            "chief_complaint",
            "brief_history",
            "temperature",
            "blood_pressure",
            "pulse",
            "weight",
            "notes",
        ]

        widgets = {
            "visit_type": forms.Select(attrs={"class": "form-select"}),
            "chief_complaint": forms.Textarea(attrs={"class": "form-control", "rows": 3}),
            "brief_history": forms.Textarea(attrs={"class": "form-control", "rows": 3}),
            "temperature": forms.TextInput(attrs={"class": "form-control"}),
            "blood_pressure": forms.TextInput(attrs={"class": "form-control"}),
            "pulse": forms.TextInput(attrs={"class": "form-control"}),
            "weight": forms.TextInput(attrs={"class": "form-control"}),
            "notes": forms.Textarea(attrs={"class": "form-control", "rows": 3}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        apply_enterprise_form_style(self)


class ConsultationForm(forms.ModelForm):
    class Meta:
        model = Consultation
        fields = [
            "presenting_complaint",
            "history_of_presenting_complaint",
            "past_ocular_history",
            "past_medical_history",
            "drug_history",
            "family_history",
            "provisional_diagnosis",
            "final_diagnosis",
            "treatment_plan",
            "doctor_notes",
        ]

        widgets = {
            "presenting_complaint": forms.Textarea(attrs={"class": "form-control", "rows": 3}),
            "history_of_presenting_complaint": forms.Textarea(attrs={"class": "form-control", "rows": 3}),
            "past_ocular_history": forms.Textarea(attrs={"class": "form-control", "rows": 3}),
            "past_medical_history": forms.Textarea(attrs={"class": "form-control", "rows": 3}),
            "drug_history": forms.Textarea(attrs={"class": "form-control", "rows": 3}),
            "family_history": forms.Textarea(attrs={"class": "form-control", "rows": 3}),
            "provisional_diagnosis": forms.Textarea(attrs={"class": "form-control", "rows": 3}),
            "final_diagnosis": forms.Textarea(attrs={"class": "form-control", "rows": 3}),
            "treatment_plan": forms.Textarea(attrs={"class": "form-control", "rows": 3}),
            "doctor_notes": forms.Textarea(attrs={"class": "form-control", "rows": 3}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        apply_enterprise_form_style(self)


class EyeExaminationForm(forms.ModelForm):
    class Meta:
        model = EyeExamination
        fields = [
            "right_visual_acuity",
            "left_visual_acuity",
            "right_pinhole",
            "left_pinhole",
            "right_near_vision",
            "left_near_vision",
            "right_sphere",
            "right_cylinder",
            "right_axis",
            "left_sphere",
            "left_cylinder",
            "left_axis",
            "right_iop",
            "left_iop",
            "external_exam",
            "anterior_segment",
            "posterior_segment",
            "fundus_exam",
            "slit_lamp_exam",
            "right_eye_findings",
            "left_eye_findings",
            "impression",
            "recommendation",
        ]

        widgets = {
            "right_visual_acuity": forms.TextInput(attrs={"class": "form-control", "placeholder": "e.g. 6/6"}),
            "left_visual_acuity": forms.TextInput(attrs={"class": "form-control", "placeholder": "e.g. 6/9"}),
            "right_pinhole": forms.TextInput(attrs={"class": "form-control"}),
            "left_pinhole": forms.TextInput(attrs={"class": "form-control"}),
            "right_near_vision": forms.TextInput(attrs={"class": "form-control"}),
            "left_near_vision": forms.TextInput(attrs={"class": "form-control"}),

            "right_sphere": forms.TextInput(attrs={"class": "form-control", "placeholder": "SPH"}),
            "right_cylinder": forms.TextInput(attrs={"class": "form-control", "placeholder": "CYL"}),
            "right_axis": forms.TextInput(attrs={"class": "form-control", "placeholder": "AXIS"}),

            "left_sphere": forms.TextInput(attrs={"class": "form-control", "placeholder": "SPH"}),
            "left_cylinder": forms.TextInput(attrs={"class": "form-control", "placeholder": "CYL"}),
            "left_axis": forms.TextInput(attrs={"class": "form-control", "placeholder": "AXIS"}),

            "right_iop": forms.TextInput(attrs={"class": "form-control", "placeholder": "mmHg"}),
            "left_iop": forms.TextInput(attrs={"class": "form-control", "placeholder": "mmHg"}),

            "external_exam": forms.Textarea(attrs={"class": "form-control", "rows": 3}),
            "anterior_segment": forms.Textarea(attrs={"class": "form-control", "rows": 3}),
            "posterior_segment": forms.Textarea(attrs={"class": "form-control", "rows": 3}),
            "fundus_exam": forms.Textarea(attrs={"class": "form-control", "rows": 3}),
            "slit_lamp_exam": forms.Textarea(attrs={"class": "form-control", "rows": 3}),
            "right_eye_findings": forms.Textarea(attrs={"class": "form-control", "rows": 3}),
            "left_eye_findings": forms.Textarea(attrs={"class": "form-control", "rows": 3}),
            "impression": forms.Textarea(attrs={"class": "form-control", "rows": 3}),
            "recommendation": forms.Textarea(attrs={"class": "form-control", "rows": 3}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        apply_enterprise_form_style(self)


class DiagnosisTreatmentForm(forms.ModelForm):
    class Meta:
        model = DiagnosisTreatment
        fields = [
            "primary_diagnosis",
            "secondary_diagnosis",
            "differential_diagnosis",
            "treatment_plan",
            "advice_given",
            "follow_up_instruction",
        ]

        widgets = {
            "primary_diagnosis": forms.Textarea(attrs={"class": "form-control", "rows": 3}),
            "secondary_diagnosis": forms.Textarea(attrs={"class": "form-control", "rows": 3}),
            "differential_diagnosis": forms.Textarea(attrs={"class": "form-control", "rows": 3}),
            "treatment_plan": forms.Textarea(attrs={"class": "form-control", "rows": 3}),
            "advice_given": forms.Textarea(attrs={"class": "form-control", "rows": 3}),
            "follow_up_instruction": forms.Textarea(attrs={"class": "form-control", "rows": 3}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        apply_enterprise_form_style(self)


class PrescriptionForm(forms.ModelForm):
    class Meta:
        model = Prescription
        fields = [
            "drug_name",
            "dosage",
            "frequency",
            "duration",
            "instructions",
        ]

        widgets = {
            "drug_name": forms.TextInput(attrs={"class": "form-control"}),
            "dosage": forms.TextInput(attrs={"class": "form-control", "placeholder": "e.g. 1 drop / 500mg"}),
            "frequency": forms.TextInput(attrs={"class": "form-control", "placeholder": "e.g. twice daily"}),
            "duration": forms.TextInput(attrs={"class": "form-control", "placeholder": "e.g. 7 days"}),
            "instructions": forms.Textarea(attrs={"class": "form-control", "rows": 3}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        apply_enterprise_form_style(self)


class SurgeryProcedureForm(forms.ModelForm):
    class Meta:
        model = SurgeryProcedure
        fields = [
            "patient",
            "visit",
            "procedure_name",
            "procedure_type",
            "eye_side",
            "scheduled_date",
            "procedure_date",
            "status",
            "pre_op_diagnosis",
            "post_op_diagnosis",
            "procedure_notes",
            "anesthesia_type",
            "complications",
            "outcome",
            "post_op_instructions",
            "surgeon",
            "assistant",
        ]

        widgets = {
            "patient": forms.Select(attrs={"class": "form-select"}),
            "visit": forms.Select(attrs={"class": "form-select"}),
            "procedure_name": forms.TextInput(attrs={"class": "form-control"}),
            "procedure_type": forms.TextInput(attrs={"class": "form-control", "placeholder": "e.g. Cataract surgery"}),
            "eye_side": forms.Select(attrs={"class": "form-select"}),
            "scheduled_date": forms.DateTimeInput(attrs={"class": "form-control", "type": "datetime-local"}),
            "procedure_date": forms.DateTimeInput(attrs={"class": "form-control", "type": "datetime-local"}),
            "status": forms.Select(attrs={"class": "form-select"}),
            "pre_op_diagnosis": forms.Textarea(attrs={"class": "form-control", "rows": 3}),
            "post_op_diagnosis": forms.Textarea(attrs={"class": "form-control", "rows": 3}),
            "procedure_notes": forms.Textarea(attrs={"class": "form-control", "rows": 3}),
            "anesthesia_type": forms.TextInput(attrs={"class": "form-control"}),
            "complications": forms.Textarea(attrs={"class": "form-control", "rows": 3}),
            "outcome": forms.Textarea(attrs={"class": "form-control", "rows": 3}),
            "post_op_instructions": forms.Textarea(attrs={"class": "form-control", "rows": 3}),
            "surgeon": forms.Select(attrs={"class": "form-select"}),
            "assistant": forms.Select(attrs={"class": "form-select"}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        apply_enterprise_form_style(self)


class SurgeryProcedureQuickForm(forms.ModelForm):
    class Meta:
        model = SurgeryProcedure
        fields = [
            "procedure_name",
            "procedure_type",
            "eye_side",
            "scheduled_date",
            "procedure_date",
            "status",
            "pre_op_diagnosis",
            "post_op_diagnosis",
            "procedure_notes",
            "anesthesia_type",
            "complications",
            "outcome",
            "post_op_instructions",
            "surgeon",
            "assistant",
        ]

        widgets = {
            "procedure_name": forms.TextInput(attrs={"class": "form-control"}),
            "procedure_type": forms.TextInput(attrs={"class": "form-control"}),
            "eye_side": forms.Select(attrs={"class": "form-select"}),
            "scheduled_date": forms.DateTimeInput(attrs={"class": "form-control", "type": "datetime-local"}),
            "procedure_date": forms.DateTimeInput(attrs={"class": "form-control", "type": "datetime-local"}),
            "status": forms.Select(attrs={"class": "form-select"}),
            "pre_op_diagnosis": forms.Textarea(attrs={"class": "form-control", "rows": 3}),
            "post_op_diagnosis": forms.Textarea(attrs={"class": "form-control", "rows": 3}),
            "procedure_notes": forms.Textarea(attrs={"class": "form-control", "rows": 3}),
            "anesthesia_type": forms.TextInput(attrs={"class": "form-control"}),
            "complications": forms.Textarea(attrs={"class": "form-control", "rows": 3}),
            "outcome": forms.Textarea(attrs={"class": "form-control", "rows": 3}),
            "post_op_instructions": forms.Textarea(attrs={"class": "form-control", "rows": 3}),
            "surgeon": forms.Select(attrs={"class": "form-select"}),
            "assistant": forms.Select(attrs={"class": "form-select"}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        apply_enterprise_form_style(self)


class AppointmentForm(forms.ModelForm):
    class Meta:
        model = Appointment
        fields = [
            "patient",
            "appointment_type",
            "status",
            "appointment_date",
            "appointment_time",
            "reason",
            "notes",
            "assigned_to",
        ]

        widgets = {
            "patient": forms.Select(attrs={"class": "form-select"}),
            "appointment_type": forms.Select(attrs={"class": "form-select"}),
            "status": forms.Select(attrs={"class": "form-select"}),
            "appointment_date": forms.DateInput(attrs={"class": "form-control", "type": "date"}),
            "appointment_time": forms.TimeInput(attrs={"class": "form-control", "type": "time"}),
            "reason": forms.Textarea(attrs={"class": "form-control", "rows": 3}),
            "notes": forms.Textarea(attrs={"class": "form-control", "rows": 3}),
            "assigned_to": forms.Select(attrs={"class": "form-select"}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        apply_enterprise_form_style(self)


class AppointmentQuickForm(forms.ModelForm):
    class Meta:
        model = Appointment
        fields = [
            "appointment_type",
            "status",
            "appointment_date",
            "appointment_time",
            "reason",
            "notes",
            "assigned_to",
        ]

        widgets = {
            "appointment_type": forms.Select(attrs={"class": "form-select"}),
            "status": forms.Select(attrs={"class": "form-select"}),
            "appointment_date": forms.DateInput(attrs={"class": "form-control", "type": "date"}),
            "appointment_time": forms.TimeInput(attrs={"class": "form-control", "type": "time"}),
            "reason": forms.Textarea(attrs={"class": "form-control", "rows": 3}),
            "notes": forms.Textarea(attrs={"class": "form-control", "rows": 3}),
            "assigned_to": forms.Select(attrs={"class": "form-select"}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        apply_enterprise_form_style(self)


class BillForm(forms.ModelForm):
    class Meta:
        model = Bill
        fields = [
            "patient",
            "visit",
            "surgery",
            "appointment",
            "bill_title",
            "total_amount",
            "discount",
            "notes",
        ]

        widgets = {
            "patient": forms.Select(attrs={"class": "form-select"}),
            "visit": forms.Select(attrs={"class": "form-select"}),
            "surgery": forms.Select(attrs={"class": "form-select"}),
            "appointment": forms.Select(attrs={"class": "form-select"}),
            "bill_title": forms.TextInput(attrs={"class": "form-control"}),
            "total_amount": forms.NumberInput(attrs={"class": "form-control", "step": "0.01"}),
            "discount": forms.NumberInput(attrs={"class": "form-control", "step": "0.01"}),
            "notes": forms.Textarea(attrs={"class": "form-control", "rows": 3}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        apply_enterprise_form_style(self)


class BillQuickForm(forms.ModelForm):
    class Meta:
        model = Bill
        fields = [
            "bill_title",
            "total_amount",
            "discount",
            "notes",
        ]

        widgets = {
            "bill_title": forms.TextInput(attrs={"class": "form-control"}),
            "total_amount": forms.NumberInput(attrs={"class": "form-control", "step": "0.01"}),
            "discount": forms.NumberInput(attrs={"class": "form-control", "step": "0.01"}),
            "notes": forms.Textarea(attrs={"class": "form-control", "rows": 3}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        apply_enterprise_form_style(self)


class PaymentForm(forms.ModelForm):
    class Meta:
        model = Payment
        fields = [
            "amount",
            "payment_method",
            "reference_number",
            "payment_date",
            "notes",
        ]

        widgets = {
            "amount": forms.NumberInput(attrs={
                "class": "form-control",
                "step": "0.01",
                "min": "0",
            }),
            "payment_method": forms.Select(attrs={"class": "form-select"}),
            "reference_number": forms.TextInput(attrs={"class": "form-control"}),
            "payment_date": forms.DateTimeInput(attrs={"class": "form-control", "type": "datetime-local"}),
            "notes": forms.Textarea(attrs={"class": "form-control", "rows": 3}),
        }

    def __init__(self, *args, **kwargs):
        self.bill = kwargs.pop("bill", None)
        super().__init__(*args, **kwargs)
        apply_enterprise_form_style(self)

    def clean_amount(self):
        amount = self.cleaned_data.get("amount")

        if amount <= 0:
            raise forms.ValidationError("Payment amount must be greater than zero.")

        if self.bill and amount > self.bill.balance:
            raise forms.ValidationError(
                f"Payment amount cannot exceed outstanding balance of ₦{self.bill.balance}."
            )

        return amount