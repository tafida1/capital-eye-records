import os

from datetime import timedelta
from decimal import Decimal, InvalidOperation

from django import forms
from django.utils import timezone

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
    ClinicalAttachment,
    ContactLensAssessment,
    ContactLensTrial,
    ContactLensPrescription,
    ContactLensFollowUp,
)



# ============================================================
# CLINICAL ATTACHMENT SECURITY SETTINGS
# ============================================================

CLINICAL_ATTACHMENT_MAX_SIZE = 10 * 1024 * 1024
# 10 MB per file

CLINICAL_ATTACHMENT_ALLOWED_EXTENSIONS = {
    ".jpg",
    ".jpeg",
    ".png",
    ".pdf",
    ".doc",
    ".docx",
}

CLINICAL_ATTACHMENT_ALLOWED_CONTENT_TYPES = {
    ".jpg": {
        "image/jpeg",
        "image/jpg",
        "application/octet-stream",
    },
    ".jpeg": {
        "image/jpeg",
        "image/jpg",
        "application/octet-stream",
    },
    ".png": {
        "image/png",
        "application/octet-stream",
    },
    ".pdf": {
        "application/pdf",
        "application/octet-stream",
    },
    ".doc": {
        "application/msword",
        "application/vnd.ms-office",
        "application/octet-stream",
    },
    ".docx": {
        (
            "application/vnd.openxmlformats-officedocument."
            "wordprocessingml.document"
        ),
        "application/zip",
        "application/octet-stream",
    },
}


def read_uploaded_file_header(uploaded_file, length=16):
    """
    Read the beginning of an uploaded file without leaving its file
    pointer in the wrong position.

    Django must still be able to save the complete file after validation.
    """

    if uploaded_file is None:
        return b""

    original_position = None

    try:
        original_position = uploaded_file.tell()
    except (AttributeError, OSError):
        original_position = None

    try:
        uploaded_file.seek(0)
        return uploaded_file.read(length)
    finally:
        try:
            if original_position is None:
                uploaded_file.seek(0)
            else:
                uploaded_file.seek(original_position)
        except (AttributeError, OSError):
            pass


def uploaded_file_signature_matches(uploaded_file, extension):
    """
    Perform a basic signature check for supported clinical files.

    This is not antivirus scanning. It helps detect common cases where
    an unsafe or unrelated file is renamed with an allowed extension.
    """

    header = read_uploaded_file_header(uploaded_file, length=16)

    if not header:
        return False

    extension = extension.lower()

    if extension in {".jpg", ".jpeg"}:
        # JPEG files begin with FF D8 FF.
        return header.startswith(b"\xff\xd8\xff")

    if extension == ".png":
        # PNG standard signature.
        return header.startswith(
            b"\x89PNG\r\n\x1a\n"
        )

    if extension == ".pdf":
        # Most valid PDFs begin with %PDF-.
        return header.startswith(b"%PDF-")

    if extension == ".doc":
        # Legacy Microsoft Office Compound File Binary format.
        return header.startswith(
            b"\xd0\xcf\x11\xe0\xa1\xb1\x1a\xe1"
        )

    if extension == ".docx":
        # DOCX is an Open XML ZIP package.
        return header.startswith(
            (
                b"PK\x03\x04",
                b"PK\x05\x06",
                b"PK\x07\x08",
            )
        )

    return False


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

        

VCDR_CHOICES = [
    ("", "Select VCDR"),
    ("0.00", "0.00"),
    ("0.05", "0.05"),
    ("0.10", "0.10"),
    ("0.15", "0.15"),
    ("0.20", "0.20"),
    ("0.25", "0.25"),
    ("0.30", "0.30"),
    ("0.35", "0.35"),
    ("0.40", "0.40"),
    ("0.45", "0.45"),
    ("0.50", "0.50"),
    ("0.55", "0.55"),
    ("0.60", "0.60"),
    ("0.65", "0.65"),
    ("0.70", "0.70"),
    ("0.75", "0.75"),
    ("0.80", "0.80"),
    ("0.85", "0.85"),
    ("0.90", "0.90"),
    ("0.95", "0.95"),
    ("1.00", "1.00"),
]


VISUAL_ACUITY_CHOICES = [
    ("", "Select visual acuity"),
    ("6/4", "6/4"),
    ("6/5", "6/5"),
    ("6/6", "6/6"),
    ("6/9", "6/9"),
    ("6/12", "6/12"),
    ("6/18", "6/18"),
    ("6/24", "6/24"),
    ("6/36", "6/36"),
    ("6/60", "6/60"),
    ("CF", "Counting Fingers (CF)"),
    ("HM", "Hand Movement (HM)"),
    ("PL", "Perception of Light (PL)"),
    ("NPL", "No Perception of Light (NPL)"),
    ("OTHER", "Others (Specify)"),
]


NEAR_VISION_CHOICES = [
    ("", "Select near vision"),
    ("N4", "N4"),
    ("N5", "N5"),
    ("N6", "N6"),
    ("N8", "N8"),
    ("N10", "N10"),
    ("N12", "N12"),
    ("N18", "N18"),
    ("N24", "N24"),
    ("N36", "N36"),
    ("OTHER", "Others (Specify)"),
]


SUBJECTIVE_ADD_POWER_CHOICES = [
    ("", "Select Add Power"),
    ("0.50", "+0.50"),
    ("0.75", "+0.75"),
    ("1.00", "+1.00"),
    ("1.25", "+1.25"),
    ("1.50", "+1.50"),
    ("1.75", "+1.75"),
    ("2.00", "+2.00"),
    ("2.25", "+2.25"),
    ("2.50", "+2.50"),
    ("2.75", "+2.75"),
    ("3.00", "+3.00"),
    ("3.25", "+3.25"),
    ("3.50", "+3.50"),
]


class EyeExaminationForm(forms.ModelForm):
    right_dry_se_display = forms.DecimalField(
        required=False,
        disabled=True,
        label="Right Dry S/E",
        decimal_places=2,
        max_digits=6,
        widget=forms.NumberInput(
            attrs={
                "class": "form-control spherical-equivalent-display",
                "placeholder": "Auto-calculated",
                "step": "0.01",
                "readonly": "readonly",
            }
        ),
    )

    left_dry_se_display = forms.DecimalField(
        required=False,
        disabled=True,
        label="Left Dry S/E",
        decimal_places=2,
        max_digits=6,
        widget=forms.NumberInput(
            attrs={
                "class": "form-control spherical-equivalent-display",
                "placeholder": "Auto-calculated",
                "step": "0.01",
                "readonly": "readonly",
            }
        ),
    )

    right_wet_se_display = forms.DecimalField(
        required=False,
        disabled=True,
        label="Right Wet S/E",
        decimal_places=2,
        max_digits=6,
        widget=forms.NumberInput(
            attrs={
                "class": "form-control spherical-equivalent-display",
                "placeholder": "Auto-calculated",
                "step": "0.01",
                "readonly": "readonly",
            }
        ),
    )

    left_wet_se_display = forms.DecimalField(
        required=False,
        disabled=True,
        label="Left Wet S/E",
        decimal_places=2,
        max_digits=6,
        widget=forms.NumberInput(
            attrs={
                "class": "form-control spherical-equivalent-display",
                "placeholder": "Auto-calculated",
                "step": "0.01",
                "readonly": "readonly",
            }
        ),
    )

    SUBJECTIVE_APPROVAL_ROLES = {
        "SUPER_ADMIN",
        "HOSPITAL_ADMIN",
        "DOCTOR",
        "OPHTHALMOLOGIST",
        "OPTOMETRIST",
    }

    class Meta:
        model = EyeExamination
        fields = [
            # Existing visual-acuity fields
            "right_visual_acuity",
            "right_visual_acuity_other",
            "left_visual_acuity",
            "left_visual_acuity_other",

            "right_pinhole",
            "right_pinhole_other",
            "left_pinhole",
            "left_pinhole_other",

            "right_near_vision",
            "right_near_vision_other",
            "left_near_vision",
            "left_near_vision_other",

            # Existing refraction fields
            "right_sphere",
            "right_cylinder",
            "right_axis",
            "left_sphere",
            "left_cylinder",
            "left_axis",

            # Auto Refraction — additional visual acuity
            "right_with_glasses",
            "right_with_glasses_other",
            "left_with_glasses",
            "left_with_glasses_other",

            # Dry Auto Refraction
            "right_dry_sphere",
            "right_dry_cylinder",
            "right_dry_axis",
            "left_dry_sphere",
            "left_dry_cylinder",
            "left_dry_axis",

            # Wet Auto Refraction
            "right_wet_sphere",
            "right_wet_cylinder",
            "right_wet_axis",
            "left_wet_sphere",
            "left_wet_cylinder",
            "left_wet_axis",

            # Lensometry, cycloplegia and remarks
            "right_lensometry",
            "left_lensometry",
            "cycloplegic_agent",
            "cycloplegic_agent_other",
            "auto_refraction_remarks",

            # =====================================================
            # SUBJECTIVE REFRACTION
            # =====================================================

            # Clinical history and diagnosis
            "subjective_refraction_history",
            "subjective_refraction_diagnosis",

            # Right eye subjective refraction
            "right_subjective_sphere",
            "right_subjective_cylinder",
            "right_subjective_axis",
            "right_subjective_aided_va",
            "right_subjective_aided_va_other",
            "right_subjective_add_power",
            "right_subjective_near_vision",
            "right_subjective_near_vision_other",

            # Left eye subjective refraction
            "left_subjective_sphere",
            "left_subjective_cylinder",
            "left_subjective_axis",
            "left_subjective_aided_va",
            "left_subjective_aided_va_other",
            "left_subjective_add_power",
            "left_subjective_near_vision",
            "left_subjective_near_vision_other",

            # PD measurements
            "subjective_distance_pd",
            "subjective_near_pd",

            # Lens and dispensing details
            "subjective_lens_type",
            "subjective_lens_type_other",
            "subjective_bifocal_type",
            "subjective_bifocal_type_other",
            "subjective_wearing_instruction",
            "subjective_wearing_instruction_other",
            "subjective_dispensary_instruction",
            "subjective_dispensary_instruction_other",

            # Remarks and approval
            "subjective_refraction_remarks",
            "subjective_refraction_approved",

            # IOP
            "right_iop",
            "left_iop",
            "right_corrected_iop",
            "left_corrected_iop",

            # Slit Lamp — Right
            "right_lids_adnexa",
            "right_conjunctiva",
            "right_conjunctiva_other",
            "right_cornea",
            "right_cornea_other",
            "right_anterior_chamber",
            "right_anterior_chamber_other",
            "right_iris",
            "right_iris_other",
            "right_pupil",
            "right_pupil_other",
            "right_lens",
            "right_lens_other",
            "right_gonioscopy_findings",

            # Slit Lamp — Left
            "left_lids_adnexa",
            "left_conjunctiva",
            "left_conjunctiva_other",
            "left_cornea",
            "left_cornea_other",
            "left_anterior_chamber",
            "left_anterior_chamber_other",
            "left_iris",
            "left_iris_other",
            "left_pupil",
            "left_pupil_other",
            "left_lens",
            "left_lens_other",
            "left_gonioscopy_findings",

            # Fundoscopy — Right
            "right_vitreous",
            "right_vitreous_other",
            "right_disc_colour",
            "right_disc_colour_other",
            "right_estimated_vcdr",
            "right_disc_margin",
            "right_disc_margin_other",
            "right_vessels",
            "right_vessels_other",
            "right_retina",
            "right_retina_other",
            "right_macula",
            "right_macula_other",
            "right_other_fundus_findings",

            # Fundoscopy — Left
            "left_vitreous",
            "left_vitreous_other",
            "left_disc_colour",
            "left_disc_colour_other",
            "left_estimated_vcdr",
            "left_disc_margin",
            "left_disc_margin_other",
            "left_vessels",
            "left_vessels_other",
            "left_retina",
            "left_retina_other",
            "left_macula",
            "left_macula_other",
            "left_other_fundus_findings",

            # Existing free-text findings
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
            # Visual acuity
            "right_visual_acuity": forms.Select(
                choices=VISUAL_ACUITY_CHOICES,
                attrs={"class": "form-select"},
            ),
            "left_visual_acuity": forms.Select(
                choices=VISUAL_ACUITY_CHOICES,
                attrs={"class": "form-select"},
            ),
            "right_pinhole": forms.Select(
                choices=VISUAL_ACUITY_CHOICES,
                attrs={"class": "form-select"},
            ),
            "left_pinhole": forms.Select(
                choices=VISUAL_ACUITY_CHOICES,
                attrs={"class": "form-select"},
            ),
            "right_near_vision": forms.Select(
                choices=NEAR_VISION_CHOICES,
                attrs={"class": "form-select"},
            ),
            "left_near_vision": forms.Select(
                choices=NEAR_VISION_CHOICES,
                attrs={"class": "form-select"},
            ),

            "right_visual_acuity_other": forms.TextInput(
                attrs={
                    "class": "form-control other-detail",
                    "placeholder": "Specify right visual acuity",
                }
            ),
            "left_visual_acuity_other": forms.TextInput(
                attrs={
                    "class": "form-control other-detail",
                    "placeholder": "Specify left visual acuity",
                }
            ),

            "right_pinhole_other": forms.TextInput(
                attrs={
                    "class": "form-control other-detail",
                    "placeholder": "Specify right pinhole value",
                }
            ),
            "left_pinhole_other": forms.TextInput(
                attrs={
                    "class": "form-control other-detail",
                    "placeholder": "Specify left pinhole value",
                }
            ),

            "right_near_vision_other": forms.TextInput(
                attrs={
                    "class": "form-control other-detail",
                    "placeholder": "Specify right near-vision value",
                }
            ),
            "left_near_vision_other": forms.TextInput(
                attrs={
                    "class": "form-control other-detail",
                    "placeholder": "Specify left near-vision value",
                }
            ),

            # Refraction
            "right_sphere": forms.TextInput(attrs={"class": "form-control"}),
            "right_cylinder": forms.TextInput(attrs={"class": "form-control"}),
            "right_axis": forms.TextInput(attrs={"class": "form-control"}),
            "left_sphere": forms.TextInput(attrs={"class": "form-control"}),
            "left_cylinder": forms.TextInput(attrs={"class": "form-control"}),
            "left_axis": forms.TextInput(attrs={"class": "form-control"}),

            # =====================================================
            # AUTO REFRACTION
            # =====================================================

            "right_with_glasses": forms.Select(
                choices=VISUAL_ACUITY_CHOICES,
                attrs={
                    "class": "form-select",
                },
            ),
            "left_with_glasses": forms.Select(
                choices=VISUAL_ACUITY_CHOICES,
                attrs={
                    "class": "form-select",
                },
            ),

            "right_with_glasses_other": forms.TextInput(
                attrs={
                    "class": "form-control other-detail",
                    "placeholder": "Specify right with-glasses value",
                }
            ),
            "left_with_glasses_other": forms.TextInput(
                attrs={
                    "class": "form-control other-detail",
                    "placeholder": "Specify left with-glasses value",
                }
            ),

            # Dry Auto Refraction — Right
            "right_dry_sphere": forms.NumberInput(
                attrs={
                    "class": "form-control se-source",
                    "placeholder": "e.g. -1.00",
                    "step": "0.25",
                    "data-se-pair": "right-dry",
                    "data-se-component": "sphere",
                }
            ),
            "right_dry_cylinder": forms.NumberInput(
                attrs={
                    "class": "form-control se-source",
                    "placeholder": "e.g. -0.50",
                    "step": "0.25",
                    "data-se-pair": "right-dry",
                    "data-se-component": "cylinder",
                }
            ),
            "right_dry_axis": forms.NumberInput(
                attrs={
                    "class": "form-control axis-input",
                    "placeholder": "0–180",
                    "min": "0",
                    "max": "180",
                    "step": "1",
                }
            ),

            # Dry Auto Refraction — Left
            "left_dry_sphere": forms.NumberInput(
                attrs={
                    "class": "form-control se-source",
                    "placeholder": "e.g. -1.00",
                    "step": "0.25",
                    "data-se-pair": "left-dry",
                    "data-se-component": "sphere",
                }
            ),
            "left_dry_cylinder": forms.NumberInput(
                attrs={
                    "class": "form-control se-source",
                    "placeholder": "e.g. -0.50",
                    "step": "0.25",
                    "data-se-pair": "left-dry",
                    "data-se-component": "cylinder",
                }
            ),
            "left_dry_axis": forms.NumberInput(
                attrs={
                    "class": "form-control axis-input",
                    "placeholder": "0–180",
                    "min": "0",
                    "max": "180",
                    "step": "1",
                }
            ),

            # Wet Auto Refraction — Right
            "right_wet_sphere": forms.NumberInput(
                attrs={
                    "class": "form-control se-source",
                    "placeholder": "e.g. +1.00",
                    "step": "0.25",
                    "data-se-pair": "right-wet",
                    "data-se-component": "sphere",
                }
            ),
            "right_wet_cylinder": forms.NumberInput(
                attrs={
                    "class": "form-control se-source",
                    "placeholder": "e.g. -0.50",
                    "step": "0.25",
                    "data-se-pair": "right-wet",
                    "data-se-component": "cylinder",
                }
            ),
            "right_wet_axis": forms.NumberInput(
                attrs={
                    "class": "form-control axis-input",
                    "placeholder": "0–180",
                    "min": "0",
                    "max": "180",
                    "step": "1",
                }
            ),

            # Wet Auto Refraction — Left
            "left_wet_sphere": forms.NumberInput(
                attrs={
                    "class": "form-control se-source",
                    "placeholder": "e.g. +1.00",
                    "step": "0.25",
                    "data-se-pair": "left-wet",
                    "data-se-component": "sphere",
                }
            ),
            "left_wet_cylinder": forms.NumberInput(
                attrs={
                    "class": "form-control se-source",
                    "placeholder": "e.g. -0.50",
                    "step": "0.25",
                    "data-se-pair": "left-wet",
                    "data-se-component": "cylinder",
                }
            ),
            "left_wet_axis": forms.NumberInput(
                attrs={
                    "class": "form-control axis-input",
                    "placeholder": "0–180",
                    "min": "0",
                    "max": "180",
                    "step": "1",
                }
            ),

            # Additional Auto Refraction fields
            "right_lensometry": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Enter right-eye lensometry",
                }
            ),
            "left_lensometry": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Enter left-eye lensometry",
                }
            ),
            "cycloplegic_agent": forms.Select(
                attrs={
                    "class": "form-select other-toggle",
                }
            ),
            "cycloplegic_agent_other": forms.TextInput(
                attrs={
                    "class": "form-control other-detail",
                    "placeholder": "Specify cycloplegic agent",
                }
            ),
            "auto_refraction_remarks": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 4,
                    "placeholder": "Enter Auto Refraction remarks",
                }
            ),

            # =====================================================
            # SUBJECTIVE REFRACTION
            # =====================================================

            "subjective_refraction_history": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 4,
                    "placeholder": (
                        "Enter relevant refractive history, spectacle use, "
                        "visual complaints and previous optical correction"
                    ),
                }
            ),

            "subjective_refraction_diagnosis": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 4,
                    "placeholder": "Enter optical or refractive diagnosis",
                }
            ),

            # -----------------------------------------------------
            # Right eye
            # -----------------------------------------------------

            "right_subjective_sphere": forms.NumberInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "e.g. -1.00",
                    "step": "0.25",
                }
            ),

            "right_subjective_cylinder": forms.NumberInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "e.g. -0.50",
                    "step": "0.25",
                }
            ),

            "right_subjective_axis": forms.NumberInput(
                attrs={
                    "class": "form-control subjective-axis-input",
                    "placeholder": "0–180",
                    "min": "0",
                    "max": "180",
                    "step": "1",
                }
            ),

            "right_subjective_aided_va": forms.Select(
                choices=VISUAL_ACUITY_CHOICES,
                attrs={
                    "class": "form-select",
                },
            ),

            "right_subjective_aided_va_other": forms.TextInput(
                attrs={
                    "class": "form-control other-detail",
                    "placeholder": "Specify right aided visual acuity",
                }
            ),

            "right_subjective_add_power": forms.Select(
                choices=SUBJECTIVE_ADD_POWER_CHOICES,
                attrs={
                    "class": "form-select",
                },
            ),

            "right_subjective_near_vision": forms.Select(
                choices=NEAR_VISION_CHOICES,
                attrs={
                    "class": "form-select",
                },
            ),

            "right_subjective_near_vision_other": forms.TextInput(
                attrs={
                    "class": "form-control other-detail",
                    "placeholder": "Specify right subjective near vision",
                }
            ),

            # -----------------------------------------------------
            # Left eye
            # -----------------------------------------------------

            "left_subjective_sphere": forms.NumberInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "e.g. -1.00",
                    "step": "0.25",
                }
            ),

            "left_subjective_cylinder": forms.NumberInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "e.g. -0.50",
                    "step": "0.25",
                }
            ),

            "left_subjective_axis": forms.NumberInput(
                attrs={
                    "class": "form-control subjective-axis-input",
                    "placeholder": "0–180",
                    "min": "0",
                    "max": "180",
                    "step": "1",
                }
            ),

            "left_subjective_aided_va": forms.Select(
                choices=VISUAL_ACUITY_CHOICES,
                attrs={
                    "class": "form-select",
                },
            ),

            "left_subjective_aided_va_other": forms.TextInput(
                attrs={
                    "class": "form-control other-detail",
                    "placeholder": "Specify left aided visual acuity",
                }
            ),

            "left_subjective_add_power": forms.Select(
                choices=SUBJECTIVE_ADD_POWER_CHOICES,
                attrs={
                    "class": "form-select",
                },
            ),

            "left_subjective_near_vision": forms.Select(
                choices=NEAR_VISION_CHOICES,
                attrs={
                    "class": "form-select",
                },
            ),

            "left_subjective_near_vision_other": forms.TextInput(
                attrs={
                    "class": "form-control other-detail",
                    "placeholder": "Specify left subjective near vision",
                }
            ),

            # -----------------------------------------------------
            # Pupillary distance
            # -----------------------------------------------------

            "subjective_distance_pd": forms.NumberInput(
                attrs={
                    "class": "form-control pd-input",
                    "placeholder": "e.g. 62",
                    "min": "30",
                    "max": "90",
                    "step": "0.50",
                }
            ),

            "subjective_near_pd": forms.NumberInput(
                attrs={
                    "class": "form-control pd-input",
                    "placeholder": "e.g. 58",
                    "min": "25",
                    "max": "85",
                    "step": "0.50",
                }
            ),

            # -----------------------------------------------------
            # Lens and dispensing
            # -----------------------------------------------------

            "subjective_lens_type": forms.Select(
                attrs={
                    "class": "form-select other-toggle",
                }
            ),

            "subjective_lens_type_other": forms.TextInput(
                attrs={
                    "class": "form-control other-detail",
                    "placeholder": "Specify lens type",
                }
            ),

            "subjective_bifocal_type": forms.Select(
                attrs={
                    "class": "form-select other-toggle",
                }
            ),

            "subjective_bifocal_type_other": forms.TextInput(
                attrs={
                    "class": "form-control other-detail",
                    "placeholder": "Specify bifocal type",
                }
            ),

            "subjective_wearing_instruction": forms.Select(
                attrs={
                    "class": "form-select other-toggle",
                }
            ),

            "subjective_wearing_instruction_other": forms.TextInput(
                attrs={
                    "class": "form-control other-detail",
                    "placeholder": "Specify wearing instruction",
                }
            ),

            "subjective_dispensary_instruction": forms.Select(
                attrs={
                    "class": "form-select other-toggle",
                }
            ),

            "subjective_dispensary_instruction_other": forms.TextInput(
                attrs={
                    "class": "form-control other-detail",
                    "placeholder": "Specify dispensary instruction",
                }
            ),

            "subjective_refraction_remarks": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 4,
                    "placeholder": (
                        "Enter additional optical prescription remarks"
                    ),
                }
            ),

            "subjective_refraction_approved": forms.CheckboxInput(
                attrs={
                    "class": "form-check-input",
                    "role": "switch",
                }
            ),

            # IOP
            "right_iop": forms.TextInput(
                attrs={"class": "form-control", "placeholder": "e.g. 16"}
            ),
            "left_iop": forms.TextInput(
                attrs={"class": "form-control", "placeholder": "e.g. 17"}
            ),
            "right_corrected_iop": forms.TextInput(
                attrs={"class": "form-control", "placeholder": "Corrected GAT IOP"}
            ),
            "left_corrected_iop": forms.TextInput(
                attrs={"class": "form-control", "placeholder": "Corrected GAT IOP"}
            ),

            # Slit Lamp — Right
            "right_lids_adnexa": forms.TextInput(attrs={"class": "form-control"}),
            "right_conjunctiva": forms.Select(attrs={"class": "form-select other-toggle"}),
            "right_conjunctiva_other": forms.TextInput(
                attrs={"class": "form-control other-detail", "placeholder": "Specify right conjunctiva finding"}
            ),
            "right_cornea": forms.Select(attrs={"class": "form-select other-toggle"}),
            "right_cornea_other": forms.TextInput(
                attrs={"class": "form-control other-detail", "placeholder": "Specify right cornea finding"}
            ),
            "right_anterior_chamber": forms.Select(attrs={"class": "form-select other-toggle"}),
            "right_anterior_chamber_other": forms.TextInput(
                attrs={"class": "form-control other-detail", "placeholder": "Specify right anterior chamber finding"}
            ),
            "right_iris": forms.Select(attrs={"class": "form-select other-toggle"}),
            "right_iris_other": forms.TextInput(
                attrs={"class": "form-control other-detail", "placeholder": "Specify right iris finding"}
            ),
            "right_pupil": forms.Select(attrs={"class": "form-select other-toggle"}),
            "right_pupil_other": forms.TextInput(
                attrs={"class": "form-control other-detail", "placeholder": "Specify right pupil finding"}
            ),
            "right_lens": forms.Select(attrs={"class": "form-select other-toggle"}),
            "right_lens_other": forms.TextInput(
                attrs={"class": "form-control other-detail", "placeholder": "Specify right lens finding"}
            ),
            "right_gonioscopy_findings": forms.Textarea(
                attrs={"class": "form-control", "rows": 3}
            ),

            # Slit Lamp — Left
            "left_lids_adnexa": forms.TextInput(attrs={"class": "form-control"}),
            "left_conjunctiva": forms.Select(attrs={"class": "form-select other-toggle"}),
            "left_conjunctiva_other": forms.TextInput(
                attrs={"class": "form-control other-detail", "placeholder": "Specify left conjunctiva finding"}
            ),
            "left_cornea": forms.Select(attrs={"class": "form-select other-toggle"}),
            "left_cornea_other": forms.TextInput(
                attrs={"class": "form-control other-detail", "placeholder": "Specify left cornea finding"}
            ),
            "left_anterior_chamber": forms.Select(attrs={"class": "form-select other-toggle"}),
            "left_anterior_chamber_other": forms.TextInput(
                attrs={"class": "form-control other-detail", "placeholder": "Specify left anterior chamber finding"}
            ),
            "left_iris": forms.Select(attrs={"class": "form-select other-toggle"}),
            "left_iris_other": forms.TextInput(
                attrs={"class": "form-control other-detail", "placeholder": "Specify left iris finding"}
            ),
            "left_pupil": forms.Select(attrs={"class": "form-select other-toggle"}),
            "left_pupil_other": forms.TextInput(
                attrs={"class": "form-control other-detail", "placeholder": "Specify left pupil finding"}
            ),
            "left_lens": forms.Select(attrs={"class": "form-select other-toggle"}),
            "left_lens_other": forms.TextInput(
                attrs={"class": "form-control other-detail", "placeholder": "Specify left lens finding"}
            ),
            "left_gonioscopy_findings": forms.Textarea(
                attrs={"class": "form-control", "rows": 3}
            ),

            # Fundoscopy — Right
            "right_vitreous": forms.Select(attrs={"class": "form-select other-toggle"}),
            "right_vitreous_other": forms.TextInput(
                attrs={"class": "form-control other-detail", "placeholder": "Specify right vitreous finding"}
            ),
            "right_disc_colour": forms.Select(attrs={"class": "form-select other-toggle"}),
            "right_disc_colour_other": forms.TextInput(
                attrs={"class": "form-control other-detail", "placeholder": "Specify right disc colour"}
            ),
            "right_estimated_vcdr": forms.Select(
                choices=VCDR_CHOICES,
                attrs={"class": "form-select"}
            ),
            "right_disc_margin": forms.Select(attrs={"class": "form-select other-toggle"}),
            "right_disc_margin_other": forms.TextInput(
                attrs={"class": "form-control other-detail", "placeholder": "Specify right disc margin"}
            ),
            "right_vessels": forms.Select(attrs={"class": "form-select other-toggle"}),
            "right_vessels_other": forms.TextInput(
                attrs={"class": "form-control other-detail", "placeholder": "Specify right vessel finding"}
            ),
            "right_retina": forms.Select(attrs={"class": "form-select other-toggle"}),
            "right_retina_other": forms.TextInput(
                attrs={"class": "form-control other-detail", "placeholder": "Specify right retina finding"}
            ),
            "right_macula": forms.Select(attrs={"class": "form-select other-toggle"}),
            "right_macula_other": forms.TextInput(
                attrs={"class": "form-control other-detail", "placeholder": "Specify right macula finding"}
            ),
            "right_other_fundus_findings": forms.Textarea(
                attrs={"class": "form-control", "rows": 3}
            ),

            # Fundoscopy — Left
            "left_vitreous": forms.Select(attrs={"class": "form-select other-toggle"}),
            "left_vitreous_other": forms.TextInput(
                attrs={"class": "form-control other-detail", "placeholder": "Specify left vitreous finding"}
            ),
            "left_disc_colour": forms.Select(attrs={"class": "form-select other-toggle"}),
            "left_disc_colour_other": forms.TextInput(
                attrs={"class": "form-control other-detail", "placeholder": "Specify left disc colour"}
            ),
            "left_estimated_vcdr": forms.Select(
                choices=VCDR_CHOICES,
                attrs={"class": "form-select"}
            ),
            "left_disc_margin": forms.Select(attrs={"class": "form-select other-toggle"}),
            "left_disc_margin_other": forms.TextInput(
                attrs={"class": "form-control other-detail", "placeholder": "Specify left disc margin"}
            ),
            "left_vessels": forms.Select(attrs={"class": "form-select other-toggle"}),
            "left_vessels_other": forms.TextInput(
                attrs={"class": "form-control other-detail", "placeholder": "Specify left vessel finding"}
            ),
            "left_retina": forms.Select(attrs={"class": "form-select other-toggle"}),
            "left_retina_other": forms.TextInput(
                attrs={"class": "form-control other-detail", "placeholder": "Specify left retina finding"}
            ),
            "left_macula": forms.Select(attrs={"class": "form-select other-toggle"}),
            "left_macula_other": forms.TextInput(
                attrs={"class": "form-control other-detail", "placeholder": "Specify left macula finding"}
            ),
            "left_other_fundus_findings": forms.Textarea(
                attrs={"class": "form-control", "rows": 3}
            ),

            # Existing free-text findings
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

    OTHER_FIELD_PAIRS = [
        ("right_conjunctiva", "right_conjunctiva_other"),
        ("right_cornea", "right_cornea_other"),
        ("right_anterior_chamber", "right_anterior_chamber_other"),
        ("right_iris", "right_iris_other"),
        ("right_pupil", "right_pupil_other"),
        ("right_lens", "right_lens_other"),
        ("left_conjunctiva", "left_conjunctiva_other"),
        ("left_cornea", "left_cornea_other"),
        ("left_anterior_chamber", "left_anterior_chamber_other"),
        ("left_iris", "left_iris_other"),
        ("left_pupil", "left_pupil_other"),
        ("left_lens", "left_lens_other"),
        ("right_vitreous", "right_vitreous_other"),
        ("right_disc_colour", "right_disc_colour_other"),
        ("right_disc_margin", "right_disc_margin_other"),
        ("right_vessels", "right_vessels_other"),
        ("right_retina", "right_retina_other"),
        ("right_macula", "right_macula_other"),
        ("left_vitreous", "left_vitreous_other"),
        ("left_disc_colour", "left_disc_colour_other"),
        ("left_disc_margin", "left_disc_margin_other"),
        ("left_vessels", "left_vessels_other"),
        ("left_retina", "left_retina_other"),
        ("left_macula", "left_macula_other"),
        ("cycloplegic_agent", "cycloplegic_agent_other"),

        ("right_visual_acuity", "right_visual_acuity_other"),
        ("left_visual_acuity", "left_visual_acuity_other"),

        ("right_pinhole", "right_pinhole_other"),
        ("left_pinhole", "left_pinhole_other"),

        ("right_near_vision", "right_near_vision_other"),
        ("left_near_vision", "left_near_vision_other"),

        ("right_with_glasses", "right_with_glasses_other"),
        ("left_with_glasses", "left_with_glasses_other"),

        # Subjective Refraction — visual measurements
        (
            "right_subjective_aided_va",
            "right_subjective_aided_va_other",
        ),
        (
            "left_subjective_aided_va",
            "left_subjective_aided_va_other",
        ),
        (
            "right_subjective_near_vision",
            "right_subjective_near_vision_other",
        ),
        (
            "left_subjective_near_vision",
            "left_subjective_near_vision_other",
        ),

        # Subjective Refraction — lens and dispensing
        (
            "subjective_lens_type",
            "subjective_lens_type_other",
        ),
        (
            "subjective_bifocal_type",
            "subjective_bifocal_type_other",
        ),
        (
            "subjective_wearing_instruction",
            "subjective_wearing_instruction_other",
        ),
        (
            "subjective_dispensary_instruction",
            "subjective_dispensary_instruction_other",
        ),
    ]

    def __init__(self, *args, **kwargs):
        self.request_user = kwargs.pop("request_user", None)

        super().__init__(*args, **kwargs)
        apply_enterprise_form_style(self)

        # Connect every "Others (Specify)" dropdown to its detail field.
        for select_name, other_name in self.OTHER_FIELD_PAIRS:
            if select_name in self.fields and other_name in self.fields:
                self.fields[select_name].widget.attrs["data-other-target"] = (
                    f"id_{other_name}"
                )

        # Display the server-calculated S/E values when editing a record.
        if self.instance and self.instance.pk:
            self.fields["right_dry_se_display"].initial = (
                self.instance.right_dry_spherical_equivalent
            )
            self.fields["left_dry_se_display"].initial = (
                self.instance.left_dry_spherical_equivalent
            )
            self.fields["right_wet_se_display"].initial = (
                self.instance.right_wet_spherical_equivalent
            )
            self.fields["left_wet_se_display"].initial = (
                self.instance.left_wet_spherical_equivalent
            )

        # Attach browser-calculation targets to the S/E source fields.
        se_target_map = {
            "right_dry_sphere": "id_right_dry_se_display",
            "right_dry_cylinder": "id_right_dry_se_display",

            "left_dry_sphere": "id_left_dry_se_display",
            "left_dry_cylinder": "id_left_dry_se_display",

            "right_wet_sphere": "id_right_wet_se_display",
            "right_wet_cylinder": "id_right_wet_se_display",

            "left_wet_sphere": "id_left_wet_se_display",
            "left_wet_cylinder": "id_left_wet_se_display",
        }

        for source_name, target_id in se_target_map.items():
            if source_name in self.fields:
                self.fields[source_name].widget.attrs["data-se-target"] = (
                    target_id
                )

        # Preserve old free-text visual-acuity values that may not yet
        # exist in the new dropdown lists.
        #
        # These model fields are CharFields using Select widgets.
        # Therefore, their choices belong to field.widget.choices,
        # not directly to field.choices.
        select_fields_to_preserve = [
            "right_visual_acuity",
            "left_visual_acuity",
            "right_pinhole",
            "left_pinhole",
            "right_near_vision",
            "left_near_vision",
            "right_with_glasses",
            "left_with_glasses",

            "right_subjective_aided_va",
            "left_subjective_aided_va",
            "right_subjective_near_vision",
            "left_subjective_near_vision",
        ]

        for field_name in select_fields_to_preserve:
            field = self.fields.get(field_name)

            if field is None:
                continue

            widget_choices = getattr(
                field.widget,
                "choices",
                None,
            )

            # Skip any field whose widget is not a Select widget.
            if widget_choices is None:
                continue

            if self.is_bound:
                current_value = self.data.get(
                    self.add_prefix(field_name),
                    "",
                )
            elif self.instance and self.instance.pk:
                current_value = getattr(
                    self.instance,
                    field_name,
                    "",
                )
            else:
                current_value = ""

            current_value = str(current_value or "").strip()

            existing_choices = list(widget_choices)

            existing_values = {
                str(value)
                for value, _label in existing_choices
            }

            if current_value and current_value not in existing_values:
                existing_choices.append(
                    (
                        current_value,
                        f"{current_value} — existing value",
                    )
                )

                field.widget.choices = existing_choices

        # =====================================================
        # SUBJECTIVE REFRACTION APPROVAL PERMISSION
        # =====================================================

        approval_field = self.fields.get(
            "subjective_refraction_approved"
        )

        if approval_field is not None:
            approval_field.label = (
                "Approve Subjective Refraction / Lens Prescription"
            )

            user_can_approve = self._user_can_approve_subjective_refraction()

            if not user_can_approve:
                approval_field.disabled = True
                approval_field.help_text = (
                    "Only an authorized clinician or administrator "
                    "may approve this optical prescription."
                )
            else:
                approval_field.help_text = (
                    "Approval records your user account and the "
                    "approval date automatically."
                )

    def _user_can_approve_subjective_refraction(self):
        """
        Return True only when the authenticated user is authorized
        to approve an optical prescription.

        The server remains the authority. The checkbox state in the
        browser cannot grant approval privileges.
        """

        user = self.request_user

        if user is None or not user.is_authenticated:
            return False

        if user.is_superuser:
            return True

        if getattr(user, "is_staff", False):
            return True

        role_value = str(
            getattr(user, "role", "") or ""
        ).upper()

        return role_value in self.SUBJECTIVE_APPROVAL_ROLES

    def clean(self):
        cleaned_data = super().clean()

        # =====================================================
        # "OTHERS (SPECIFY)" VALIDATION
        # =====================================================

        for select_name, other_name in self.OTHER_FIELD_PAIRS:
            selected_value = cleaned_data.get(select_name)
            other_value = (cleaned_data.get(other_name) or "").strip()

            if selected_value == "OTHER" and not other_value:
                self.add_error(
                    other_name,
                    (
                        "Please specify the finding or value because "
                        "'Others (Specify)' was selected."
                    ),
                )

            if selected_value != "OTHER":
                cleaned_data[other_name] = ""

        # =====================================================
        # AXIS VALIDATION
        # =====================================================

        axis_fields = [
            ("right_dry_axis", "Right Dry Axis"),
            ("left_dry_axis", "Left Dry Axis"),
            ("right_wet_axis", "Right Wet Axis"),
            ("left_wet_axis", "Left Wet Axis"),

            (
                "right_subjective_axis",
                "Right Subjective Axis",
            ),
            (
                "left_subjective_axis",
                "Left Subjective Axis",
            ),
        ]

        for field_name, label in axis_fields:
            value = cleaned_data.get(field_name)

            if value is not None and not 0 <= value <= 180:
                self.add_error(
                    field_name,
                    f"{label} must be between 0 and 180 degrees.",
                )

        # =====================================================
        # CYLINDER / AXIS CONSISTENCY
        # =====================================================

        refraction_groups = [
            (
                "right_dry_cylinder",
                "right_dry_axis",
                "Right Dry Refraction",
            ),
            (
                "left_dry_cylinder",
                "left_dry_axis",
                "Left Dry Refraction",
            ),
            (
                "right_wet_cylinder",
                "right_wet_axis",
                "Right Wet Refraction",
            ),
            (
                "left_wet_cylinder",
                "left_wet_axis",
                "Left Wet Refraction",
            ),

            (
                "right_subjective_cylinder",
                "right_subjective_axis",
                "Right Subjective Refraction",
            ),
            (
                "left_subjective_cylinder",
                "left_subjective_axis",
                "Left Subjective Refraction",
            ),
        ]

        for cylinder_name, axis_name, label in refraction_groups:
            cylinder = cleaned_data.get(cylinder_name)
            axis = cleaned_data.get(axis_name)

            if cylinder not in (None, Decimal("0.00")) and axis is None:
                self.add_error(
                    axis_name,
                    (
                        f"Enter the axis for {label} because a cylinder "
                        "value has been entered."
                    ),
                )

        # =====================================================
        # PUPILLARY DISTANCE VALIDATION
        # =====================================================

        distance_pd = cleaned_data.get("subjective_distance_pd")
        near_pd = cleaned_data.get("subjective_near_pd")

        if distance_pd is not None:
            if not Decimal("30.00") <= distance_pd <= Decimal("90.00"):
                self.add_error(
                    "subjective_distance_pd",
                    (
                        "Distance PD must be between 30 mm and 90 mm. "
                        "Confirm the measurement before saving."
                    ),
                )

        if near_pd is not None:
            if not Decimal("25.00") <= near_pd <= Decimal("85.00"):
                self.add_error(
                    "subjective_near_pd",
                    (
                        "Near PD must be between 25 mm and 85 mm. "
                        "Confirm the measurement before saving."
                    ),
                )

        if (
            distance_pd is not None
            and near_pd is not None
            and near_pd > distance_pd
        ):
            self.add_error(
                "subjective_near_pd",
                (
                    "Near PD should not be greater than Distance PD. "
                    "Please verify both measurements."
                ),
            )

        # =====================================================
        # SUBJECTIVE REFRACTION APPROVAL VALIDATION
        # =====================================================

        approval_requested = cleaned_data.get(
            "subjective_refraction_approved",
            False,
        )

        previously_approved = bool(
            self.instance
            and self.instance.pk
            and self.instance.subjective_refraction_approved
        )

        user_can_approve = (
            self._user_can_approve_subjective_refraction()
        )

        # Unauthorized users cannot create a new approval or
        # remove an existing approval.
        if not user_can_approve:
            cleaned_data[
                "subjective_refraction_approved"
            ] = previously_approved

        if approval_requested and user_can_approve:
            required_for_approval = [
                (
                    "right_subjective_sphere",
                    "Enter the right-eye sphere before approval.",
                ),
                (
                    "left_subjective_sphere",
                    "Enter the left-eye sphere before approval.",
                ),
                (
                    "right_subjective_aided_va",
                    (
                        "Enter the right-eye aided visual acuity "
                        "before approval."
                    ),
                ),
                (
                    "left_subjective_aided_va",
                    (
                        "Enter the left-eye aided visual acuity "
                        "before approval."
                    ),
                ),
                (
                    "subjective_lens_type",
                    "Select the lens type before approval.",
                ),
            ]

            for field_name, error_message in required_for_approval:
                if cleaned_data.get(field_name) in (
                    None,
                    "",
                ):
                    self.add_error(
                        field_name,
                        error_message,
                    )

        # =====================================================
        # SERVER-SIDE S/E PREVIEW VALUES
        #
        # The model remains the source of truth and recalculates
        # these values again during save().
        # =====================================================

        se_groups = [
            (
                "right_dry_sphere",
                "right_dry_cylinder",
                "right_dry_se_display",
            ),
            (
                "left_dry_sphere",
                "left_dry_cylinder",
                "left_dry_se_display",
            ),
            (
                "right_wet_sphere",
                "right_wet_cylinder",
                "right_wet_se_display",
            ),
            (
                "left_wet_sphere",
                "left_wet_cylinder",
                "left_wet_se_display",
            ),
        ]

        for sphere_name, cylinder_name, display_name in se_groups:
            sphere = cleaned_data.get(sphere_name)
            cylinder = cleaned_data.get(cylinder_name)

            calculated_value = (
                EyeExamination.calculate_spherical_equivalent(
                    sphere,
                    cylinder,
                )
            )

            cleaned_data[display_name] = calculated_value

        return cleaned_data

    def save(self, commit=True):
        """
        Save Subjective Refraction approval safely.

        The approving account always comes from request_user and can
        never be forged through submitted form data.
        """

        original_approved = False
        original_approved_by = None
        original_approved_at = None

        if self.instance and self.instance.pk:
            original_approved = bool(
                self.instance.subjective_refraction_approved
            )
            original_approved_by = (
                self.instance.subjective_refraction_approved_by
            )
            original_approved_at = (
                self.instance.subjective_refraction_approved_at
            )

        exam = super().save(commit=False)

        user_can_approve = (
            self._user_can_approve_subjective_refraction()
        )

        approval_requested = bool(
            self.cleaned_data.get(
                "subjective_refraction_approved",
                False,
            )
        )

        if user_can_approve:
            exam.subjective_refraction_approved = (
                approval_requested
            )

            if approval_requested:
                if (
                    not original_approved
                    or original_approved_by is None
                ):
                    exam.subjective_refraction_approved_by = (
                        self.request_user
                    )
            else:
                exam.subjective_refraction_approved_by = None
                exam.subjective_refraction_approved_at = None

        else:
            exam.subjective_refraction_approved = original_approved
            exam.subjective_refraction_approved_by = (
                original_approved_by
            )
            exam.subjective_refraction_approved_at = (
                original_approved_at
            )

        if commit:
            exam.save()
            self.save_m2m()

        return exam


class ClinicalAttachmentForm(forms.ModelForm):
    """
    Upload form for clinical investigation images and documents.

    Patient, visit, uploader, file metadata and review audit fields are
    intentionally excluded. They are assigned by trusted server-side
    view logic.
    """

    class Meta:
        model = ClinicalAttachment

        fields = [
            "category",
            "category_other",
            "eye_side",
            "title",
            "description",
            "investigation_date",
            "attachment_file",
        ]

        widgets = {
            "category": forms.Select(
                attrs={
                    "class": "form-select",
                    "data-other-target": (
                        "id_category_other"
                    ),
                }
            ),

            "category_other": forms.TextInput(
                attrs={
                    "class": "form-control other-detail",
                    "placeholder": (
                        "Specify the investigation or document category"
                    ),
                }
            ),

            "eye_side": forms.Select(
                attrs={
                    "class": "form-select",
                }
            ),

            "title": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": (
                        "e.g. OCT Macula — Right Eye"
                    ),
                    "maxlength": "200",
                    "autocomplete": "off",
                }
            ),

            "description": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 4,
                    "placeholder": (
                        "Enter a comment, clinical note or description "
                        "of this investigation result"
                    ),
                    "maxlength": "2000",
                }
            ),

            "investigation_date": forms.DateInput(
                attrs={
                    "class": "form-control",
                    "type": "date",
                }
            ),

            "attachment_file": forms.ClearableFileInput(
                attrs={
                    "class": "form-control",
                    "accept": (
                        ".jpg,.jpeg,.png,.pdf,.doc,.docx,"
                        "image/jpeg,image/png,application/pdf,"
                        "application/msword,"
                        "application/vnd.openxmlformats-officedocument."
                        "wordprocessingml.document"
                    ),
                }
            ),
        }

        labels = {
            "category": "Investigation / Document Category",
            "category_other": "Other Category",
            "eye_side": "Eye",
            "title": "File Title",
            "description": "Comment / Description",
            "investigation_date": "Investigation Date",
            "attachment_file": "Select Clinical File",
        }

        help_texts = {
            "attachment_file": (
                "Allowed types: JPG, JPEG, PNG, PDF, DOC and DOCX. "
                "Maximum file size: 10 MB."
            ),
            "investigation_date": (
                "Enter the date the test or investigation was performed."
            ),
            "eye_side": (
                "Select Not Applicable for documents that are not "
                "specific to an eye."
            ),
        }

    def __init__(self, *args, **kwargs):
        self.visit = kwargs.pop("visit", None)
        self.request_user = kwargs.pop("request_user", None)

        super().__init__(*args, **kwargs)
        apply_enterprise_form_style(self)

        self.fields["category"].widget.attrs[
            "data-other-target"
        ] = "id_category_other"

        # A file is required when creating a new record.
        # During a future edit operation, the existing file may remain.
        if self.instance and self.instance.pk:
            self.fields["attachment_file"].required = False
            self.fields["attachment_file"].help_text = (
                "Leave this field empty to retain the existing file. "
                "Allowed types: JPG, JPEG, PNG, PDF, DOC and DOCX. "
                "Maximum size: 10 MB."
            )
        else:
            self.fields["attachment_file"].required = True

        # Do not permit browser-side manipulation of the date maximum.
        # The clean method below remains the final authority.
        self.fields["investigation_date"].widget.attrs["max"] = (
            timezone.localdate().isoformat()
        )

    def clean_title(self):
        title = (self.cleaned_data.get("title") or "").strip()

        if not title:
            raise forms.ValidationError(
                "Enter a clear title for the clinical file."
            )

        # Prevent titles containing only punctuation or whitespace.
        if not any(character.isalnum() for character in title):
            raise forms.ValidationError(
                "The file title must contain letters or numbers."
            )

        return title

    def clean_description(self):
        description = (
            self.cleaned_data.get("description") or ""
        ).strip()

        if len(description) > 2000:
            raise forms.ValidationError(
                "The comment or description must not exceed "
                "2,000 characters."
            )

        return description

    def clean_investigation_date(self):
        investigation_date = self.cleaned_data.get(
            "investigation_date"
        )

        if (
            investigation_date
            and investigation_date > timezone.localdate()
        ):
            raise forms.ValidationError(
                "The investigation date cannot be in the future."
            )

        return investigation_date

    def clean_attachment_file(self):
        uploaded_file = self.cleaned_data.get(
            "attachment_file"
        )

        # During edit, retaining the existing file is allowed.
        if uploaded_file is None:
            if self.instance and self.instance.pk:
                return uploaded_file

            raise forms.ValidationError(
                "Select a clinical image or document to upload."
            )

        original_name = os.path.basename(
            str(uploaded_file.name or "")
        )

        if not original_name:
            raise forms.ValidationError(
                "The uploaded file has no valid filename."
            )

        if len(original_name) > 255:
            raise forms.ValidationError(
                "The filename is too long. Rename the file to fewer "
                "than 255 characters and try again."
            )

        extension = os.path.splitext(
            original_name
        )[1].lower()

        if extension not in CLINICAL_ATTACHMENT_ALLOWED_EXTENSIONS:
            raise forms.ValidationError(
                "Unsupported file type. Upload only JPG, JPEG, PNG, "
                "PDF, DOC or DOCX files."
            )

        file_size = getattr(
            uploaded_file,
            "size",
            0,
        ) or 0

        if file_size <= 0:
            raise forms.ValidationError(
                "The selected file is empty or could not be read."
            )

        if file_size > CLINICAL_ATTACHMENT_MAX_SIZE:
            raise forms.ValidationError(
                "The selected file is larger than 10 MB. Reduce the "
                "file size and try again."
            )

        reported_content_type = str(
            getattr(
                uploaded_file,
                "content_type",
                "",
            )
            or ""
        ).lower()

        allowed_content_types = (
            CLINICAL_ATTACHMENT_ALLOWED_CONTENT_TYPES.get(
                extension,
                set(),
            )
        )

        if (
            reported_content_type
            and reported_content_type
            not in allowed_content_types
        ):
            raise forms.ValidationError(
                (
                    "The file content type does not match the selected "
                    "file extension. Please upload the original clinical "
                    "file without renaming its extension."
                )
            )

        if not uploaded_file_signature_matches(
            uploaded_file,
            extension,
        ):
            raise forms.ValidationError(
                (
                    "The uploaded file does not appear to be a valid "
                    f"{extension.lstrip('.').upper()} file. The file "
                    "may be damaged or may have been renamed incorrectly."
                )
            )

        # Reset the pointer before Django storage reads the file.
        try:
            uploaded_file.seek(0)
        except (AttributeError, OSError):
            pass

        return uploaded_file

    def clean(self):
        cleaned_data = super().clean()

        category = cleaned_data.get("category")
        category_other = (
            cleaned_data.get("category_other") or ""
        ).strip()

        if (
            category == ClinicalAttachment.Category.OTHER
            and not category_other
        ):
            self.add_error(
                "category_other",
                (
                    "Specify the investigation or document category "
                    "because 'Others (Specify)' was selected."
                ),
            )

        if category != ClinicalAttachment.Category.OTHER:
            cleaned_data["category_other"] = ""

        visit = self.visit

        if visit is not None:
            # Defensive verification for a visit passed by the view.
            if not getattr(visit, "pk", None):
                raise forms.ValidationError(
                    "The selected patient visit is invalid."
                )

            if not getattr(visit, "patient_id", None):
                raise forms.ValidationError(
                    "The selected visit is not linked to a patient."
                )

        return cleaned_data

    def save(self, commit=True):
        """
        Assign trusted visit, patient, uploader and file metadata.

        These values are not accepted from browser POST data.
        """

        attachment = super().save(commit=False)

        if self.visit is not None:
            attachment.visit = self.visit
            attachment.patient = self.visit.patient

        if (
            self.request_user is not None
            and self.request_user.is_authenticated
            and not attachment.uploaded_by_id
        ):
            attachment.uploaded_by = self.request_user

        uploaded_file = self.cleaned_data.get(
            "attachment_file"
        )

        if uploaded_file:
            attachment.original_filename = os.path.basename(
                str(uploaded_file.name)
            )[:255]

            attachment.file_extension = os.path.splitext(
                attachment.original_filename
            )[1].lower()[:20]

            attachment.file_size = (
                getattr(uploaded_file, "size", 0) or 0
            )

        if commit:
            attachment.save()
            self.save_m2m()

        return attachment


class ClinicalAttachmentReviewForm(forms.ModelForm):
    """
    Clinical review form for an existing attachment.

    reviewed_by and reviewed_at are assigned by the server-side view.
    """

    class Meta:
        model = ClinicalAttachment

        fields = [
            "review_status",
            "review_notes",
        ]

        widgets = {
            "review_status": forms.Select(
                attrs={
                    "class": "form-select",
                }
            ),

            "review_notes": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 4,
                    "placeholder": (
                        "Enter the clinician's review findings or notes"
                    ),
                    "maxlength": "2000",
                }
            ),
        }

        labels = {
            "review_status": "Review Status",
            "review_notes": "Clinical Review Notes",
        }

    def __init__(self, *args, **kwargs):
        self.request_user = kwargs.pop(
            "request_user",
            None,
        )

        super().__init__(*args, **kwargs)
        apply_enterprise_form_style(self)

    def clean_review_notes(self):
        review_notes = (
            self.cleaned_data.get("review_notes") or ""
        ).strip()

        if len(review_notes) > 2000:
            raise forms.ValidationError(
                "Review notes must not exceed 2,000 characters."
            )

        return review_notes

    def clean(self):
        cleaned_data = super().clean()

        review_status = cleaned_data.get(
            "review_status"
        )

        review_notes = (
            cleaned_data.get("review_notes") or ""
        ).strip()

        if (
            review_status
            == ClinicalAttachment.ReviewStatus.NEEDS_ATTENTION
            and not review_notes
        ):
            self.add_error(
                "review_notes",
                (
                    "Enter a review note explaining why this result "
                    "needs attention."
                ),
            )

        return cleaned_data

    def save(self, commit=True):
        attachment = super().save(commit=False)

        review_status = self.cleaned_data.get(
            "review_status"
        )

        if (
            self.request_user is not None
            and self.request_user.is_authenticated
            and review_status
            in {
                ClinicalAttachment.ReviewStatus.REVIEWED,
                ClinicalAttachment.ReviewStatus.NEEDS_ATTENTION,
            }
        ):
            attachment.reviewed_by = self.request_user
            attachment.reviewed_at = timezone.now()

        if (
            review_status
            == ClinicalAttachment.ReviewStatus.PENDING
        ):
            attachment.reviewed_by = None
            attachment.reviewed_at = None

        if commit:
            attachment.save()
            self.save_m2m()

        return attachment


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


# ============================================================
# CONTACT LENS FORM HELPERS
# ============================================================


def contact_lens_decimal_is_nonzero(value):
    """
    Return True when a decimal-compatible value is not zero.
    """

    if value in {
        None,
        "",
    }:
        return False

    try:
        return Decimal(str(value)) != Decimal("0")
    except (
        InvalidOperation,
        TypeError,
        ValueError,
    ):
        return False


def contact_lens_axis_required(
    cleaned_data,
    *,
    cylinder_field,
    axis_field,
    form,
    eye_label,
):
    """
    Require an axis when cylinder power is not zero.

    The axis may remain empty when the cylinder is empty or exactly zero.
    """

    cylinder = cleaned_data.get(
        cylinder_field
    )

    axis = cleaned_data.get(
        axis_field
    )

    if (
        contact_lens_decimal_is_nonzero(cylinder)
        and axis is None
    ):
        form.add_error(
            axis_field,
            (
                f"Enter the {eye_label} axis because a cylinder "
                "power has been entered."
            ),
        )


def contact_lens_other_required(
    cleaned_data,
    *,
    choice_field,
    other_field,
    other_value,
    form,
    message,
):
    """
    Require the corresponding Other field when an Other option is selected.
    Clear stale Other values when another choice is selected.
    """

    selected_value = cleaned_data.get(
        choice_field
    )

    other_text = (
        cleaned_data.get(other_field)
        or ""
    ).strip()

    if (
        selected_value == other_value
        and not other_text
    ):
        form.add_error(
            other_field,
            message,
        )

    if selected_value != other_value:
        cleaned_data[other_field] = ""


def contact_lens_datetime_not_future(
    value,
    *,
    field_name,
    form,
    label,
):
    """
    Reject clinical activity timestamps that are in the future.
    """

    if value and value > timezone.now():
        form.add_error(
            field_name,
            f"{label} cannot be in the future.",
        )


def contact_lens_date_not_future(
    value,
    *,
    field_name,
    form,
    label,
):
    if value and value > timezone.localdate():
        form.add_error(
            field_name,
            f"{label} cannot be in the future.",
        )

class ContactLensAssessmentForm(forms.ModelForm):
    """
    Contact lens suitability assessment.

    Patient, visit and assessing clinician are assigned by the server-side
    view and are therefore not exposed as editable browser fields.
    """

    class Meta:
        model = ContactLensAssessment

        fields = [
            "assessment_date",
            "eye_examination",

            "lens_purpose",
            "lens_purpose_other",
            "wearing_experience",

            "previous_lens_brand",
            "previous_lens_type",
            "previous_wearing_schedule",
            "previous_lens_problems",

            "occupation",
            "environmental_exposure",
            "average_daily_wear_hours_requested",

            "allergies",
            "systemic_conditions",
            "current_medications",
            "ocular_history",

            "previous_contact_lens_infection",
            "previous_contact_lens_infection_details",

            "right_horizontal_visible_iris_diameter",
            "left_horizontal_visible_iris_diameter",

            "right_pupil_diameter",
            "left_pupil_diameter",

            "right_palpebral_aperture",
            "left_palpebral_aperture",

            "right_k1",
            "right_k1_axis",
            "right_k2",
            "right_k2_axis",

            "left_k1",
            "left_k1_axis",
            "left_k2",
            "left_k2_axis",

            "tear_film_status",
            "tear_break_up_time_right",
            "tear_break_up_time_left",
            "schirmer_right",
            "schirmer_left",

            "corneal_status",
            "corneal_status_other",

            "right_cornea_notes",
            "left_cornea_notes",
            "right_lid_notes",
            "left_lid_notes",
            "conjunctival_findings",

            "hygiene_assessment",
            "handling_ability",
            "motivation_and_expectations",
            "contraindications",

            "suitability_status",
            "suitability_reason",
            "assessment_notes",

            "patient_education_provided",
            "patient_education_notes",
        ]

        widgets = {
            "assessment_date": forms.DateTimeInput(
                attrs={
                    "type": "datetime-local",
                    "class": "form-control",
                },
                format="%Y-%m-%dT%H:%M",
            ),

            "eye_examination": forms.Select(
                attrs={
                    "class": "form-select",
                }
            ),

            "lens_purpose": forms.Select(
                attrs={
                    "class": "form-select",
                    "data-other-target": "id_lens_purpose_other",
                }
            ),

            "lens_purpose_other": forms.TextInput(
                attrs={
                    "class": "form-control other-detail",
                    "placeholder": "Specify the contact lens purpose",
                    "maxlength": "150",
                }
            ),

            "wearing_experience": forms.Select(
                attrs={
                    "class": "form-select",
                }
            ),

            "previous_lens_brand": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Previous brand, if applicable",
                }
            ),

            "previous_lens_type": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Previous lens type",
                }
            ),

            "previous_wearing_schedule": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "e.g. Monthly daily wear",
                }
            ),

            "previous_lens_problems": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 3,
                }
            ),

            "occupation": forms.TextInput(
                attrs={
                    "class": "form-control",
                }
            ),

            "environmental_exposure": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 3,
                }
            ),

            "average_daily_wear_hours_requested": forms.NumberInput(
                attrs={
                    "class": "form-control",
                    "min": "0",
                    "max": "24",
                    "step": "0.5",
                }
            ),

            "allergies": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 2,
                }
            ),

            "systemic_conditions": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 2,
                }
            ),

            "current_medications": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 2,
                }
            ),

            "ocular_history": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 3,
                }
            ),

            "previous_contact_lens_infection": forms.CheckboxInput(
                attrs={
                    "class": "form-check-input",
                    "data-detail-target": (
                        "id_previous_contact_lens_infection_details"
                    ),
                }
            ),

            "previous_contact_lens_infection_details": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 3,
                    "placeholder": (
                        "Describe the infection, treatment and outcome"
                    ),
                }
            ),

            "right_horizontal_visible_iris_diameter": forms.NumberInput(
                attrs={
                    "class": "form-control",
                    "step": "0.1",
                    "min": "8",
                    "max": "15",
                }
            ),

            "left_horizontal_visible_iris_diameter": forms.NumberInput(
                attrs={
                    "class": "form-control",
                    "step": "0.1",
                    "min": "8",
                    "max": "15",
                }
            ),

            "right_pupil_diameter": forms.NumberInput(
                attrs={
                    "class": "form-control",
                    "step": "0.1",
                    "min": "1",
                    "max": "12",
                }
            ),

            "left_pupil_diameter": forms.NumberInput(
                attrs={
                    "class": "form-control",
                    "step": "0.1",
                    "min": "1",
                    "max": "12",
                }
            ),

            "right_palpebral_aperture": forms.NumberInput(
                attrs={
                    "class": "form-control",
                    "step": "0.1",
                    "min": "3",
                    "max": "20",
                }
            ),

            "left_palpebral_aperture": forms.NumberInput(
                attrs={
                    "class": "form-control",
                    "step": "0.1",
                    "min": "3",
                    "max": "20",
                }
            ),

            "right_k1": forms.NumberInput(
                attrs={
                    "class": "form-control",
                    "step": "0.01",
                    "min": "30",
                    "max": "60",
                }
            ),

            "right_k1_axis": forms.NumberInput(
                attrs={
                    "class": "form-control",
                    "min": "0",
                    "max": "180",
                    "step": "1",
                }
            ),

            "right_k2": forms.NumberInput(
                attrs={
                    "class": "form-control",
                    "step": "0.01",
                    "min": "30",
                    "max": "60",
                }
            ),

            "right_k2_axis": forms.NumberInput(
                attrs={
                    "class": "form-control",
                    "min": "0",
                    "max": "180",
                    "step": "1",
                }
            ),

            "left_k1": forms.NumberInput(
                attrs={
                    "class": "form-control",
                    "step": "0.01",
                    "min": "30",
                    "max": "60",
                }
            ),

            "left_k1_axis": forms.NumberInput(
                attrs={
                    "class": "form-control",
                    "min": "0",
                    "max": "180",
                    "step": "1",
                }
            ),

            "left_k2": forms.NumberInput(
                attrs={
                    "class": "form-control",
                    "step": "0.01",
                    "min": "30",
                    "max": "60",
                }
            ),

            "left_k2_axis": forms.NumberInput(
                attrs={
                    "class": "form-control",
                    "min": "0",
                    "max": "180",
                    "step": "1",
                }
            ),

            "tear_film_status": forms.Select(
                attrs={
                    "class": "form-select",
                }
            ),

            "tear_break_up_time_right": forms.NumberInput(
                attrs={
                    "class": "form-control",
                    "step": "0.1",
                    "min": "0",
                    "max": "60",
                }
            ),

            "tear_break_up_time_left": forms.NumberInput(
                attrs={
                    "class": "form-control",
                    "step": "0.1",
                    "min": "0",
                    "max": "60",
                }
            ),

            "schirmer_right": forms.NumberInput(
                attrs={
                    "class": "form-control",
                    "step": "0.1",
                    "min": "0",
                    "max": "50",
                }
            ),

            "schirmer_left": forms.NumberInput(
                attrs={
                    "class": "form-control",
                    "step": "0.1",
                    "min": "0",
                    "max": "50",
                }
            ),

            "corneal_status": forms.Select(
                attrs={
                    "class": "form-select",
                    "data-other-target": "id_corneal_status_other",
                }
            ),

            "corneal_status_other": forms.TextInput(
                attrs={
                    "class": "form-control other-detail",
                    "placeholder": "Specify the corneal status",
                    "maxlength": "150",
                }
            ),

            "right_cornea_notes": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 3,
                }
            ),

            "left_cornea_notes": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 3,
                }
            ),

            "right_lid_notes": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 2,
                }
            ),

            "left_lid_notes": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 2,
                }
            ),

            "conjunctival_findings": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 3,
                }
            ),

            "hygiene_assessment": forms.Select(
                attrs={
                    "class": "form-select",
                }
            ),

            "handling_ability": forms.TextInput(
                attrs={
                    "class": "form-control",
                }
            ),

            "motivation_and_expectations": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 3,
                }
            ),

            "contraindications": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 3,
                }
            ),

            "suitability_status": forms.Select(
                attrs={
                    "class": "form-select",
                }
            ),

            "suitability_reason": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 3,
                }
            ),

            "assessment_notes": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 4,
                }
            ),

            "patient_education_provided": forms.CheckboxInput(
                attrs={
                    "class": "form-check-input",
                    "data-detail-target": "id_patient_education_notes",
                }
            ),

            "patient_education_notes": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 3,
                }
            ),
        }

    def __init__(self, *args, **kwargs):
        self.visit = kwargs.pop(
            "visit",
            None,
        )

        self.request_user = kwargs.pop(
            "request_user",
            None,
        )

        super().__init__(*args, **kwargs)
        apply_enterprise_form_style(self)

        self.fields[
            "assessment_date"
        ].input_formats = [
            "%Y-%m-%dT%H:%M",
            "%Y-%m-%d %H:%M:%S",
            "%Y-%m-%d %H:%M",
        ]

        if not self.is_bound and not self.instance.pk:
            self.initial["assessment_date"] = (
                timezone.localtime()
                .strftime("%Y-%m-%dT%H:%M")
            )

        if self.visit is not None:
            self.fields[
                "eye_examination"
            ].queryset = EyeExamination.objects.filter(
                visit=self.visit
            )

            existing_examination = (
                EyeExamination.objects.filter(
                    visit=self.visit
                ).first()
            )

            if (
                existing_examination
                and not self.instance.pk
            ):
                self.initial[
                    "eye_examination"
                ] = existing_examination.pk
        else:
            self.fields[
                "eye_examination"
            ].queryset = EyeExamination.objects.none()

    def clean(self):
        cleaned_data = super().clean()

        contact_lens_other_required(
            cleaned_data,
            choice_field="lens_purpose",
            other_field="lens_purpose_other",
            other_value=(
                ContactLensAssessment
                .LensPurpose
                .OTHER
            ),
            form=self,
            message=(
                "Specify the contact lens purpose because "
                "'Others (Specify)' was selected."
            ),
        )

        contact_lens_other_required(
            cleaned_data,
            choice_field="corneal_status",
            other_field="corneal_status_other",
            other_value=(
                ContactLensAssessment
                .CornealStatus
                .OTHER
            ),
            form=self,
            message=(
                "Specify the corneal status because "
                "'Others (Specify)' was selected."
            ),
        )

        assessment_date = cleaned_data.get(
            "assessment_date"
        )

        contact_lens_datetime_not_future(
            assessment_date,
            field_name="assessment_date",
            form=self,
            label="Assessment date",
        )

        wearing_experience = cleaned_data.get(
            "wearing_experience"
        )

        previous_history_fields = [
            cleaned_data.get("previous_lens_brand"),
            cleaned_data.get("previous_lens_type"),
            cleaned_data.get("previous_wearing_schedule"),
            cleaned_data.get("previous_lens_problems"),
        ]

        if (
            wearing_experience
            == ContactLensAssessment.WearingExperience.NEVER
            and any(previous_history_fields)
        ):
            self.add_error(
                "wearing_experience",
                (
                    "Previous contact lens details were entered, but "
                    "'Never Worn Contact Lenses' was selected."
                ),
            )

        previous_infection = cleaned_data.get(
            "previous_contact_lens_infection"
        )

        infection_details = (
            cleaned_data.get(
                "previous_contact_lens_infection_details"
            )
            or ""
        ).strip()

        if previous_infection and not infection_details:
            self.add_error(
                "previous_contact_lens_infection_details",
                (
                    "Describe the previous contact lens infection, "
                    "its treatment and outcome."
                ),
            )

        if not previous_infection:
            cleaned_data[
                "previous_contact_lens_infection_details"
            ] = ""

        education_provided = cleaned_data.get(
            "patient_education_provided"
        )

        education_notes = (
            cleaned_data.get(
                "patient_education_notes"
            )
            or ""
        ).strip()

        if education_provided and not education_notes:
            self.add_error(
                "patient_education_notes",
                (
                    "Briefly record the contact lens education "
                    "provided to the patient."
                ),
            )

        suitability_status = cleaned_data.get(
            "suitability_status"
        )

        suitability_reason = (
            cleaned_data.get(
                "suitability_reason"
            )
            or ""
        ).strip()

        if (
            suitability_status
            in {
                ContactLensAssessment
                .SuitabilityStatus
                .SUITABLE_WITH_CAUTION,

                ContactLensAssessment
                .SuitabilityStatus
                .TEMPORARILY_UNSUITABLE,

                ContactLensAssessment
                .SuitabilityStatus
                .UNSUITABLE,
            }
            and not suitability_reason
        ):
            self.add_error(
                "suitability_reason",
                (
                    "Explain the clinical reason for the selected "
                    "suitability status."
                ),
            )

        # Keratometry axes must accompany the corresponding K reading.
        keratometry_pairs = [
            (
                "right_k1",
                "right_k1_axis",
                "right K1",
            ),
            (
                "right_k2",
                "right_k2_axis",
                "right K2",
            ),
            (
                "left_k1",
                "left_k1_axis",
                "left K1",
            ),
            (
                "left_k2",
                "left_k2_axis",
                "left K2",
            ),
        ]

        for power_field, axis_field, label in keratometry_pairs:
            power = cleaned_data.get(
                power_field
            )

            axis = cleaned_data.get(
                axis_field
            )

            if power is not None and axis is None:
                self.add_error(
                    axis_field,
                    f"Enter the axis for {label}.",
                )

            if power is None and axis is not None:
                self.add_error(
                    power_field,
                    (
                        f"Enter the keratometry power for {label} "
                        "because an axis was supplied."
                    ),
                )

        right_k1 = cleaned_data.get("right_k1")
        right_k2 = cleaned_data.get("right_k2")
        left_k1 = cleaned_data.get("left_k1")
        left_k2 = cleaned_data.get("left_k2")

        if (
            right_k1 is not None
            and right_k2 is not None
            and abs(right_k1 - right_k2) > Decimal("15.00")
        ):
            self.add_error(
                "right_k2",
                (
                    "The difference between right K1 and K2 appears "
                    "unusually large. Verify the keratometry values."
                ),
            )

        if (
            left_k1 is not None
            and left_k2 is not None
            and abs(left_k1 - left_k2) > Decimal("15.00")
        ):
            self.add_error(
                "left_k2",
                (
                    "The difference between left K1 and K2 appears "
                    "unusually large. Verify the keratometry values."
                ),
            )

        selected_examination = cleaned_data.get(
            "eye_examination"
        )

        if (
            selected_examination
            and self.visit is not None
            and selected_examination.visit_id
            != self.visit.pk
        ):
            self.add_error(
                "eye_examination",
                (
                    "The selected Eye Examination does not belong "
                    "to this patient visit."
                ),
            )

        return cleaned_data

    def save(self, commit=True):
        assessment = super().save(
            commit=False
        )

        if self.visit is not None:
            assessment.visit = self.visit
            assessment.patient = self.visit.patient

        if (
            self.request_user is not None
            and self.request_user.is_authenticated
            and not assessment.assessed_by_id
        ):
            assessment.assessed_by = (
                self.request_user
            )

        if commit:
            assessment.save()
            self.save_m2m()

        return assessment


class ContactLensTrialForm(forms.ModelForm):
    """
    Records a single right-eye or left-eye contact lens trial.
    """

    class Meta:
        model = ContactLensTrial

        fields = [
            "eye_side",
            "trial_number",
            "trial_date",

            "lens_design",
            "lens_design_other",

            "manufacturer",
            "brand_name",
            "material",

            "base_curve",
            "diameter",
            "sphere",
            "cylinder",
            "axis",
            "add_power",

            "peripheral_curve",
            "optical_zone",
            "sagittal_depth",
            "tint_or_colour",

            "right_or_left_visual_acuity",

            "over_refraction_sphere",
            "over_refraction_cylinder",
            "over_refraction_axis",
            "final_visual_acuity",

            "centration",
            "movement",
            "fit_assessment",
            "rotation_degrees",
            "push_up_test",
            "fluorescein_pattern",

            "comfort_score",
            "fit_notes",
            "accepted_for_prescription",
        ]

        widgets = {
            "eye_side": forms.Select(
                attrs={
                    "class": "form-select",
                }
            ),

            "trial_number": forms.NumberInput(
                attrs={
                    "class": "form-control",
                    "min": "1",
                    "step": "1",
                }
            ),

            "trial_date": forms.DateTimeInput(
                attrs={
                    "class": "form-control",
                    "type": "datetime-local",
                },
                format="%Y-%m-%dT%H:%M",
            ),

            "lens_design": forms.Select(
                attrs={
                    "class": "form-select",
                    "data-other-target": (
                        "id_lens_design_other"
                    ),
                }
            ),

            "lens_design_other": forms.TextInput(
                attrs={
                    "class": "form-control other-detail",
                    "placeholder": "Specify the trial lens design",
                }
            ),

            "manufacturer": forms.TextInput(
                attrs={
                    "class": "form-control",
                }
            ),

            "brand_name": forms.TextInput(
                attrs={
                    "class": "form-control",
                }
            ),

            "material": forms.TextInput(
                attrs={
                    "class": "form-control",
                }
            ),

            "base_curve": forms.NumberInput(
                attrs={
                    "class": "form-control",
                    "min": "5",
                    "max": "12",
                    "step": "0.01",
                }
            ),

            "diameter": forms.NumberInput(
                attrs={
                    "class": "form-control",
                    "min": "7",
                    "max": "25",
                    "step": "0.1",
                }
            ),

            "sphere": forms.NumberInput(
                attrs={
                    "class": "form-control",
                    "min": "-40",
                    "max": "40",
                    "step": "0.25",
                }
            ),

            "cylinder": forms.NumberInput(
                attrs={
                    "class": "form-control",
                    "min": "-15",
                    "max": "15",
                    "step": "0.25",
                }
            ),

            "axis": forms.NumberInput(
                attrs={
                    "class": "form-control",
                    "min": "0",
                    "max": "180",
                    "step": "1",
                }
            ),

            "add_power": forms.NumberInput(
                attrs={
                    "class": "form-control",
                    "min": "0",
                    "max": "6",
                    "step": "0.25",
                }
            ),

            "peripheral_curve": forms.TextInput(
                attrs={
                    "class": "form-control",
                }
            ),

            "optical_zone": forms.NumberInput(
                attrs={
                    "class": "form-control",
                    "step": "0.1",
                }
            ),

            "sagittal_depth": forms.NumberInput(
                attrs={
                    "class": "form-control",
                    "step": "1",
                }
            ),

            "tint_or_colour": forms.TextInput(
                attrs={
                    "class": "form-control",
                }
            ),

            "right_or_left_visual_acuity": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "e.g. 6/6",
                }
            ),

            "over_refraction_sphere": forms.NumberInput(
                attrs={
                    "class": "form-control",
                    "step": "0.25",
                }
            ),

            "over_refraction_cylinder": forms.NumberInput(
                attrs={
                    "class": "form-control",
                    "step": "0.25",
                }
            ),

            "over_refraction_axis": forms.NumberInput(
                attrs={
                    "class": "form-control",
                    "min": "0",
                    "max": "180",
                    "step": "1",
                }
            ),

            "final_visual_acuity": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "e.g. 6/6",
                }
            ),

            "centration": forms.Select(
                attrs={
                    "class": "form-select",
                }
            ),

            "movement": forms.Select(
                attrs={
                    "class": "form-select",
                }
            ),

            "fit_assessment": forms.Select(
                attrs={
                    "class": "form-select",
                }
            ),

            "rotation_degrees": forms.NumberInput(
                attrs={
                    "class": "form-control",
                    "min": "-180",
                    "max": "180",
                    "step": "1",
                }
            ),

            "push_up_test": forms.TextInput(
                attrs={
                    "class": "form-control",
                }
            ),

            "fluorescein_pattern": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 3,
                }
            ),

            "comfort_score": forms.NumberInput(
                attrs={
                    "class": "form-control",
                    "min": "0",
                    "max": "10",
                    "step": "1",
                }
            ),

            "fit_notes": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 4,
                }
            ),

            "accepted_for_prescription": forms.CheckboxInput(
                attrs={
                    "class": "form-check-input",
                }
            ),
        }

    def __init__(self, *args, **kwargs):
        self.assessment = kwargs.pop(
            "assessment",
            None,
        )

        self.request_user = kwargs.pop(
            "request_user",
            None,
        )

        super().__init__(*args, **kwargs)
        apply_enterprise_form_style(self)

        self.fields[
            "trial_date"
        ].input_formats = [
            "%Y-%m-%dT%H:%M",
            "%Y-%m-%d %H:%M:%S",
            "%Y-%m-%d %H:%M",
        ]

        if not self.is_bound and not self.instance.pk:
            self.initial["trial_date"] = (
                timezone.localtime()
                .strftime("%Y-%m-%dT%H:%M")
            )

            if self.assessment is not None:
                last_trial = (
                    self.assessment
                    .trial_lenses
                    .order_by("-trial_number")
                    .first()
                )

                self.initial["trial_number"] = (
                    last_trial.trial_number + 1
                    if last_trial
                    else 1
                )

    def clean(self):
        cleaned_data = super().clean()

        contact_lens_other_required(
            cleaned_data,
            choice_field="lens_design",
            other_field="lens_design_other",
            other_value=(
                ContactLensTrial
                .LensDesign
                .OTHER
            ),
            form=self,
            message=(
                "Specify the trial lens design because "
                "'Others (Specify)' was selected."
            ),
        )

        contact_lens_datetime_not_future(
            cleaned_data.get("trial_date"),
            field_name="trial_date",
            form=self,
            label="Trial date",
        )

        contact_lens_axis_required(
            cleaned_data,
            cylinder_field="cylinder",
            axis_field="axis",
            form=self,
            eye_label="trial-lens",
        )

        contact_lens_axis_required(
            cleaned_data,
            cylinder_field=(
                "over_refraction_cylinder"
            ),
            axis_field=(
                "over_refraction_axis"
            ),
            form=self,
            eye_label="over-refraction",
        )

        lens_design = cleaned_data.get(
            "lens_design"
        )

        cylinder = cleaned_data.get(
            "cylinder"
        )

        axis = cleaned_data.get(
            "axis"
        )

        if (
            lens_design
            == ContactLensTrial.LensDesign.TORIC
            and not contact_lens_decimal_is_nonzero(
                cylinder
            )
        ):
            self.add_error(
                "cylinder",
                (
                    "Enter a non-zero cylinder power for a toric "
                    "trial lens."
                ),
            )

        if (
            lens_design
            == ContactLensTrial.LensDesign.TORIC
            and axis is None
        ):
            self.add_error(
                "axis",
                (
                    "Enter the trial lens axis for the toric lens."
                ),
            )

        if (
            lens_design
            == ContactLensTrial.LensDesign.MULTIFOCAL
            and cleaned_data.get("add_power") is None
        ):
            self.add_error(
                "add_power",
                (
                    "Enter the addition power for a multifocal "
                    "trial lens."
                ),
            )

        if (
            lens_design
            in {
                ContactLensTrial.LensDesign.RGP,
                ContactLensTrial.LensDesign.SCLERAL,
                ContactLensTrial.LensDesign.HYBRID,
            }
            and cleaned_data.get("base_curve") is None
        ):
            self.add_error(
                "base_curve",
                (
                    "Enter the base curve for the selected rigid "
                    "or specialty trial lens."
                ),
            )

        fit_assessment = cleaned_data.get(
            "fit_assessment"
        )

        accepted = cleaned_data.get(
            "accepted_for_prescription"
        )

        if (
            accepted
            and fit_assessment
            in {
                ContactLensTrial
                .FitAssessment
                .UNACCEPTABLE,

                ContactLensTrial
                .FitAssessment
                .TIGHT,

                ContactLensTrial
                .FitAssessment
                .LOOSE,
            }
        ):
            self.add_error(
                "accepted_for_prescription",
                (
                    "A trial with an unacceptable, tight or loose fit "
                    "cannot be accepted for the final prescription."
                ),
            )

        if (
            accepted
            and not cleaned_data.get(
                "final_visual_acuity"
            )
        ):
            self.add_error(
                "final_visual_acuity",
                (
                    "Record the final visual acuity before accepting "
                    "the trial for prescription."
                ),
            )

        if self.assessment is not None:
            trial_number = cleaned_data.get(
                "trial_number"
            )

            eye_side = cleaned_data.get(
                "eye_side"
            )

            duplicate_query = (
                ContactLensTrial.objects.filter(
                    assessment=self.assessment,
                    trial_number=trial_number,
                    eye_side=eye_side,
                )
            )

            if self.instance.pk:
                duplicate_query = (
                    duplicate_query.exclude(
                        pk=self.instance.pk
                    )
                )

            if (
                trial_number
                and eye_side
                and duplicate_query.exists()
            ):
                self.add_error(
                    "trial_number",
                    (
                        "This trial number already exists for the "
                        "selected eye."
                    ),
                )

        return cleaned_data

    def save(self, commit=True):
        trial = super().save(
            commit=False
        )

        if self.assessment is not None:
            trial.assessment = self.assessment

        if (
            self.request_user is not None
            and self.request_user.is_authenticated
            and not trial.fitted_by_id
        ):
            trial.fitted_by = self.request_user

        if commit:
            trial.save()
            self.save_m2m()

        return trial


class ContactLensPrescriptionForm(forms.ModelForm):
    """
    Contact lens prescription content form.

    Status approval, approved_by, approved_at, dispensed_by and
    dispensed_at are controlled by separate server-side workflows.
    """

    class Meta:
        model = ContactLensPrescription

        fields = [
            "prescription_date",
            "valid_until",

            "right_lens_design",
            "right_lens_design_other",
            "right_manufacturer",
            "right_brand_name",
            "right_material",
            "right_base_curve",
            "right_diameter",
            "right_sphere",
            "right_cylinder",
            "right_axis",
            "right_add_power",
            "right_colour",

            "left_lens_design",
            "left_lens_design_other",
            "left_manufacturer",
            "left_brand_name",
            "left_material",
            "left_base_curve",
            "left_diameter",
            "left_sphere",
            "left_cylinder",
            "left_axis",
            "left_add_power",
            "left_colour",

            "replacement_schedule",
            "replacement_schedule_other",
            "wearing_schedule",
            "maximum_daily_wear_hours",

            "cleaning_solution",
            "cleaning_instructions",

            "insertion_removal_training_completed",
            "hygiene_training_completed",
            "emergency_warning_signs_explained",

            "clinical_notes",
            "dispensing_instructions",
        ]

        widgets = {
            "prescription_date": forms.DateInput(
                attrs={
                    "class": "form-control",
                    "type": "date",
                }
            ),

            "valid_until": forms.DateInput(
                attrs={
                    "class": "form-control",
                    "type": "date",
                }
            ),

            "right_lens_design": forms.Select(
                attrs={
                    "class": "form-select",
                    "data-other-target": (
                        "id_right_lens_design_other"
                    ),
                }
            ),

            "right_lens_design_other": forms.TextInput(
                attrs={
                    "class": "form-control other-detail",
                    "placeholder": "Specify right lens design",
                }
            ),

            "left_lens_design": forms.Select(
                attrs={
                    "class": "form-select",
                    "data-other-target": (
                        "id_left_lens_design_other"
                    ),
                }
            ),

            "left_lens_design_other": forms.TextInput(
                attrs={
                    "class": "form-control other-detail",
                    "placeholder": "Specify left lens design",
                }
            ),

            "replacement_schedule": forms.Select(
                attrs={
                    "class": "form-select",
                    "data-other-target": (
                        "id_replacement_schedule_other"
                    ),
                }
            ),

            "replacement_schedule_other": forms.TextInput(
                attrs={
                    "class": "form-control other-detail",
                    "placeholder": (
                        "Specify the replacement schedule"
                    ),
                }
            ),

            "wearing_schedule": forms.Select(
                attrs={
                    "class": "form-select",
                }
            ),

            "maximum_daily_wear_hours": forms.NumberInput(
                attrs={
                    "class": "form-control",
                    "min": "0",
                    "max": "24",
                    "step": "0.5",
                }
            ),

            "cleaning_solution": forms.TextInput(
                attrs={
                    "class": "form-control",
                }
            ),

            "cleaning_instructions": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 3,
                }
            ),

            "clinical_notes": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 4,
                }
            ),

            "dispensing_instructions": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 4,
                }
            ),

            "insertion_removal_training_completed": (
                forms.CheckboxInput(
                    attrs={
                        "class": "form-check-input",
                    }
                )
            ),

            "hygiene_training_completed": forms.CheckboxInput(
                attrs={
                    "class": "form-check-input",
                }
            ),

            "emergency_warning_signs_explained": (
                forms.CheckboxInput(
                    attrs={
                        "class": "form-check-input",
                    }
                )
            ),
        }

    def __init__(self, *args, **kwargs):
        self.assessment = kwargs.pop(
            "assessment",
            None,
        )

        self.visit = kwargs.pop(
            "visit",
            None,
        )

        self.request_user = kwargs.pop(
            "request_user",
            None,
        )

        super().__init__(*args, **kwargs)
        apply_enterprise_form_style(self)

        numeric_configuration = {
            "right_base_curve": (
                "5",
                "12",
                "0.01",
            ),
            "left_base_curve": (
                "5",
                "12",
                "0.01",
            ),
            "right_diameter": (
                "7",
                "25",
                "0.1",
            ),
            "left_diameter": (
                "7",
                "25",
                "0.1",
            ),
            "right_sphere": (
                "-40",
                "40",
                "0.25",
            ),
            "left_sphere": (
                "-40",
                "40",
                "0.25",
            ),
            "right_cylinder": (
                "-15",
                "15",
                "0.25",
            ),
            "left_cylinder": (
                "-15",
                "15",
                "0.25",
            ),
            "right_axis": (
                "0",
                "180",
                "1",
            ),
            "left_axis": (
                "0",
                "180",
                "1",
            ),
            "right_add_power": (
                "0",
                "6",
                "0.25",
            ),
            "left_add_power": (
                "0",
                "6",
                "0.25",
            ),
        }

        for field_name, settings in numeric_configuration.items():
            field = self.fields[field_name]

            field.widget = forms.NumberInput(
                attrs={
                    "class": "form-control",
                    "min": settings[0],
                    "max": settings[1],
                    "step": settings[2],
                }
            )

        text_fields = [
            "right_manufacturer",
            "right_brand_name",
            "right_material",
            "right_colour",
            "left_manufacturer",
            "left_brand_name",
            "left_material",
            "left_colour",
        ]

        for field_name in text_fields:
            self.fields[
                field_name
            ].widget.attrs.update(
                {
                    "class": "form-control",
                }
            )

        if not self.is_bound and not self.instance.pk:
            today = timezone.localdate()

            self.initial[
                "prescription_date"
            ] = today

            self.initial[
                "valid_until"
            ] = today + timedelta(days=365)

            self._populate_from_accepted_trials()

    def _populate_from_accepted_trials(self):
        """
        Populate right and left parameters from the most recent accepted
        trial lenses. This only supplies initial values and does not alter
        existing records.
        """

        if self.assessment is None:
            return

        accepted_trials = (
            self.assessment
            .trial_lenses
            .filter(
                accepted_for_prescription=True
            )
            .order_by(
                "eye_side",
                "-trial_number",
            )
        )

        right_trial = accepted_trials.filter(
            eye_side=(
                ContactLensTrial
                .EyeSide
                .RIGHT
            )
        ).first()

        left_trial = accepted_trials.filter(
            eye_side=(
                ContactLensTrial
                .EyeSide
                .LEFT
            )
        ).first()

        self._apply_trial_initials(
            right_trial,
            prefix="right",
        )

        self._apply_trial_initials(
            left_trial,
            prefix="left",
        )

    def _apply_trial_initials(
        self,
        trial,
        *,
        prefix,
    ):
        if trial is None:
            return

        trial_values = {
            f"{prefix}_lens_design": (
                trial.lens_design
            ),
            f"{prefix}_lens_design_other": (
                trial.lens_design_other
            ),
            f"{prefix}_manufacturer": (
                trial.manufacturer
            ),
            f"{prefix}_brand_name": (
                trial.brand_name
            ),
            f"{prefix}_material": (
                trial.material
            ),
            f"{prefix}_base_curve": (
                trial.base_curve
            ),
            f"{prefix}_diameter": (
                trial.diameter
            ),
            f"{prefix}_sphere": (
                (
                    trial.sphere
                    or Decimal("0.00")
                )
                + (
                    trial.over_refraction_sphere
                    or Decimal("0.00")
                )
            ),
            f"{prefix}_cylinder": (
                trial.cylinder
            ),
            f"{prefix}_axis": (
                trial.axis
            ),
            f"{prefix}_add_power": (
                trial.add_power
            ),
            f"{prefix}_colour": (
                trial.tint_or_colour
            ),
        }

        for field_name, value in trial_values.items():
            if value not in {
                None,
                "",
            }:
                self.initial[field_name] = value

    def clean(self):
        cleaned_data = super().clean()

        contact_lens_other_required(
            cleaned_data,
            choice_field="right_lens_design",
            other_field="right_lens_design_other",
            other_value=(
                ContactLensPrescription
                .LensDesign
                .OTHER
            ),
            form=self,
            message=(
                "Specify the right-eye lens design."
            ),
        )

        contact_lens_other_required(
            cleaned_data,
            choice_field="left_lens_design",
            other_field="left_lens_design_other",
            other_value=(
                ContactLensPrescription
                .LensDesign
                .OTHER
            ),
            form=self,
            message=(
                "Specify the left-eye lens design."
            ),
        )

        contact_lens_other_required(
            cleaned_data,
            choice_field="replacement_schedule",
            other_field="replacement_schedule_other",
            other_value=(
                ContactLensPrescription
                .ReplacementSchedule
                .OTHER
            ),
            form=self,
            message=(
                "Specify the replacement schedule."
            ),
        )

        prescription_date = cleaned_data.get(
            "prescription_date"
        )

        valid_until = cleaned_data.get(
            "valid_until"
        )

        contact_lens_date_not_future(
            prescription_date,
            field_name="prescription_date",
            form=self,
            label="Prescription date",
        )

        if (
            prescription_date
            and valid_until
            and valid_until <= prescription_date
        ):
            self.add_error(
                "valid_until",
                (
                    "The expiry date must be after the "
                    "prescription date."
                ),
            )

        contact_lens_axis_required(
            cleaned_data,
            cylinder_field="right_cylinder",
            axis_field="right_axis",
            form=self,
            eye_label="right-eye",
        )

        contact_lens_axis_required(
            cleaned_data,
            cylinder_field="left_cylinder",
            axis_field="left_axis",
            form=self,
            eye_label="left-eye",
        )

        for prefix, eye_label in [
            ("right", "right eye"),
            ("left", "left eye"),
        ]:
            design = cleaned_data.get(
                f"{prefix}_lens_design"
            )

            cylinder = cleaned_data.get(
                f"{prefix}_cylinder"
            )

            axis = cleaned_data.get(
                f"{prefix}_axis"
            )

            add_power = cleaned_data.get(
                f"{prefix}_add_power"
            )

            if (
                design
                == ContactLensPrescription
                .LensDesign
                .TORIC
            ):
                if not contact_lens_decimal_is_nonzero(
                    cylinder
                ):
                    self.add_error(
                        f"{prefix}_cylinder",
                        (
                            f"Enter a non-zero cylinder for the "
                            f"{eye_label} toric lens."
                        ),
                    )

                if axis is None:
                    self.add_error(
                        f"{prefix}_axis",
                        (
                            f"Enter the axis for the "
                            f"{eye_label} toric lens."
                        ),
                    )

            if (
                design
                == ContactLensPrescription
                .LensDesign
                .MULTIFOCAL
                and add_power is None
            ):
                self.add_error(
                    f"{prefix}_add_power",
                    (
                        f"Enter the addition power for the "
                        f"{eye_label} multifocal lens."
                    ),
                )

            if (
                design
                in {
                    ContactLensPrescription
                    .LensDesign
                    .RGP,

                    ContactLensPrescription
                    .LensDesign
                    .SCLERAL,

                    ContactLensPrescription
                    .LensDesign
                    .HYBRID,
                }
                and cleaned_data.get(
                    f"{prefix}_base_curve"
                ) is None
            ):
                self.add_error(
                    f"{prefix}_base_curve",
                    (
                        f"Enter the base curve for the "
                        f"{eye_label} specialty lens."
                    ),
                )

        right_has_data = any(
            cleaned_data.get(field_name)
            not in {
                None,
                "",
            }
            for field_name in [
                "right_lens_design",
                "right_brand_name",
                "right_sphere",
                "right_cylinder",
                "right_base_curve",
                "right_diameter",
            ]
        )

        left_has_data = any(
            cleaned_data.get(field_name)
            not in {
                None,
                "",
            }
            for field_name in [
                "left_lens_design",
                "left_brand_name",
                "left_sphere",
                "left_cylinder",
                "left_base_curve",
                "left_diameter",
            ]
        )

        if not right_has_data and not left_has_data:
            raise forms.ValidationError(
                (
                    "Enter prescription parameters for at least "
                    "one eye."
                )
            )

        return cleaned_data

    def save(self, commit=True):
        prescription = super().save(
            commit=False
        )

        if self.assessment is not None:
            prescription.assessment = (
                self.assessment
            )

        if self.visit is not None:
            prescription.visit = self.visit
            prescription.patient = (
                self.visit.patient
            )
        elif self.assessment is not None:
            prescription.visit = (
                self.assessment.visit
            )

            prescription.patient = (
                self.assessment.patient
            )

        if (
            self.request_user is not None
            and self.request_user.is_authenticated
            and not prescription.prescribed_by_id
        ):
            prescription.prescribed_by = (
                self.request_user
            )

        if not prescription.pk:
            prescription.status = (
                ContactLensPrescription
                .PrescriptionStatus
                .DRAFT
            )

        if commit:
            prescription.save()
            self.save_m2m()

        return prescription


class ContactLensPrescriptionApprovalForm(forms.Form):
    """
    Separate approval action so approved_by and approved_at are never
    accepted directly from browser fields.
    """

    confirm_approval = forms.BooleanField(
        required=True,
        label=(
            "I have reviewed the contact lens parameters "
            "and approve this prescription."
        ),
        widget=forms.CheckboxInput(
            attrs={
                "class": "form-check-input",
            }
        ),
    )

    approval_note = forms.CharField(
        required=False,
        max_length=2000,
        label="Approval Note",
        widget=forms.Textarea(
            attrs={
                "class": "form-control",
                "rows": 4,
                "placeholder": (
                    "Optional approval note or clinical instruction"
                ),
            }
        ),
    )

    def __init__(
        self,
        *args,
        prescription=None,
        request_user=None,
        **kwargs,
    ):
        self.prescription = prescription
        self.request_user = request_user

        super().__init__(
            *args,
            **kwargs,
        )

    def clean(self):
        cleaned_data = super().clean()

        if self.prescription is None:
            raise forms.ValidationError(
                "The contact lens prescription is unavailable."
            )

        if not self.prescription.is_active:
            raise forms.ValidationError(
                "An inactive prescription cannot be approved."
            )

        if (
            self.prescription.status
            == ContactLensPrescription
            .PrescriptionStatus
            .CANCELLED
        ):
            raise forms.ValidationError(
                "A cancelled prescription cannot be approved."
            )

        if (
            not self.prescription
            .insertion_removal_training_completed
        ):
            self.add_error(
                "confirm_approval",
                (
                    "Insertion and removal training must be completed "
                    "before approval."
                ),
            )

        if (
            not self.prescription
            .hygiene_training_completed
        ):
            self.add_error(
                "confirm_approval",
                (
                    "Hygiene training must be completed before approval."
                ),
            )

        if (
            not self.prescription
            .emergency_warning_signs_explained
        ):
            self.add_error(
                "confirm_approval",
                (
                    "Emergency warning signs must be explained before "
                    "approval."
                ),
            )

        return cleaned_data


class ContactLensPrescriptionDispensingForm(forms.Form):
    confirm_dispensing = forms.BooleanField(
        required=True,
        label=(
            "I confirm that the prescribed contact lenses "
            "have been dispensed."
        ),
        widget=forms.CheckboxInput(
            attrs={
                "class": "form-check-input",
            }
        ),
    )

    dispensing_note = forms.CharField(
        required=False,
        max_length=2000,
        label="Dispensing Note",
        widget=forms.Textarea(
            attrs={
                "class": "form-control",
                "rows": 4,
            }
        ),
    )

    def __init__(
        self,
        *args,
        prescription=None,
        request_user=None,
        **kwargs,
    ):
        self.prescription = prescription
        self.request_user = request_user

        super().__init__(
            *args,
            **kwargs,
        )

    def clean(self):
        cleaned_data = super().clean()

        if self.prescription is None:
            raise forms.ValidationError(
                "The contact lens prescription is unavailable."
            )

        if (
            self.prescription.status
            != ContactLensPrescription
            .PrescriptionStatus
            .APPROVED
        ):
            raise forms.ValidationError(
                (
                    "Only an approved contact lens prescription "
                    "can be marked as dispensed."
                )
            )

        return cleaned_data


class ContactLensFollowUpForm(forms.ModelForm):
    """
    Contact lens follow-up form.

    Prescription, patient and reviewing clinician are assigned by the view.
    """

    class Meta:
        model = ContactLensFollowUp

        fields = [
            "follow_up_date",
            "status",

            "wearing_time_per_day",
            "comfort_score_right",
            "comfort_score_left",

            "right_visual_acuity",
            "left_visual_acuity",

            "right_fit_assessment",
            "left_fit_assessment",

            "right_cornea_findings",
            "left_cornea_findings",
            "conjunctival_findings",

            "lens_condition",
            "compliance_assessment",
            "complications",
            "management_plan",

            "lens_parameters_changed",
            "revised_parameters",

            "next_follow_up_date",
            "clinical_notes",
        ]

        widgets = {
            "follow_up_date": forms.DateTimeInput(
                attrs={
                    "class": "form-control",
                    "type": "datetime-local",
                },
                format="%Y-%m-%dT%H:%M",
            ),

            "status": forms.Select(
                attrs={
                    "class": "form-select",
                }
            ),

            "wearing_time_per_day": forms.NumberInput(
                attrs={
                    "class": "form-control",
                    "min": "0",
                    "max": "24",
                    "step": "0.5",
                }
            ),

            "comfort_score_right": forms.NumberInput(
                attrs={
                    "class": "form-control",
                    "min": "0",
                    "max": "10",
                    "step": "1",
                }
            ),

            "comfort_score_left": forms.NumberInput(
                attrs={
                    "class": "form-control",
                    "min": "0",
                    "max": "10",
                    "step": "1",
                }
            ),

            "right_visual_acuity": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "e.g. 6/6",
                }
            ),

            "left_visual_acuity": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "e.g. 6/6",
                }
            ),

            "right_fit_assessment": forms.TextInput(
                attrs={
                    "class": "form-control",
                }
            ),

            "left_fit_assessment": forms.TextInput(
                attrs={
                    "class": "form-control",
                }
            ),

            "right_cornea_findings": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 3,
                }
            ),

            "left_cornea_findings": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 3,
                }
            ),

            "conjunctival_findings": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 3,
                }
            ),

            "lens_condition": forms.Select(
                attrs={
                    "class": "form-select",
                }
            ),

            "compliance_assessment": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 3,
                }
            ),

            "complications": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 3,
                }
            ),

            "management_plan": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 4,
                }
            ),

            "lens_parameters_changed": forms.CheckboxInput(
                attrs={
                    "class": "form-check-input",
                    "data-detail-target": (
                        "id_revised_parameters"
                    ),
                }
            ),

            "revised_parameters": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 3,
                    "placeholder": (
                        "Record the revised right and/or left lens "
                        "parameters"
                    ),
                }
            ),

            "next_follow_up_date": forms.DateTimeInput(
                attrs={
                    "class": "form-control",
                    "type": "datetime-local",
                },
                format="%Y-%m-%dT%H:%M",
            ),

            "clinical_notes": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 4,
                }
            ),
        }

    def __init__(self, *args, **kwargs):
        self.prescription = kwargs.pop(
            "prescription",
            None,
        )

        self.request_user = kwargs.pop(
            "request_user",
            None,
        )

        super().__init__(*args, **kwargs)
        apply_enterprise_form_style(self)

        datetime_fields = [
            "follow_up_date",
            "next_follow_up_date",
        ]

        for field_name in datetime_fields:
            self.fields[
                field_name
            ].input_formats = [
                "%Y-%m-%dT%H:%M",
                "%Y-%m-%d %H:%M:%S",
                "%Y-%m-%d %H:%M",
            ]

        if not self.is_bound and not self.instance.pk:
            self.initial[
                "follow_up_date"
            ] = (
                timezone.localtime()
                .strftime("%Y-%m-%dT%H:%M")
            )

    def clean(self):
        cleaned_data = super().clean()

        follow_up_date = cleaned_data.get(
            "follow_up_date"
        )

        status = cleaned_data.get(
            "status"
        )

        next_follow_up_date = cleaned_data.get(
            "next_follow_up_date"
        )

        if (
            status
            == ContactLensFollowUp
            .FollowUpStatus
            .COMPLETED
        ):
            contact_lens_datetime_not_future(
                follow_up_date,
                field_name="follow_up_date",
                form=self,
                label="Completed follow-up date",
            )

        if (
            next_follow_up_date
            and follow_up_date
            and next_follow_up_date
            <= follow_up_date
        ):
            self.add_error(
                "next_follow_up_date",
                (
                    "The next follow-up must be later than the "
                    "current follow-up."
                ),
            )

        parameters_changed = cleaned_data.get(
            "lens_parameters_changed"
        )

        revised_parameters = (
            cleaned_data.get(
                "revised_parameters"
            )
            or ""
        ).strip()

        if (
            parameters_changed
            and not revised_parameters
        ):
            self.add_error(
                "revised_parameters",
                (
                    "Record the revised lens parameters because "
                    "a parameter change was selected."
                ),
            )

        if not parameters_changed:
            cleaned_data[
                "revised_parameters"
            ] = ""

        complications = (
            cleaned_data.get(
                "complications"
            )
            or ""
        ).strip()

        management_plan = (
            cleaned_data.get(
                "management_plan"
            )
            or ""
        ).strip()

        if complications and not management_plan:
            self.add_error(
                "management_plan",
                (
                    "Enter a management plan for the recorded "
                    "contact lens complication."
                ),
            )

        if (
            status
            == ContactLensFollowUp
            .FollowUpStatus
            .COMPLETED
        ):
            clinical_fields = [
                cleaned_data.get(
                    "right_visual_acuity"
                ),
                cleaned_data.get(
                    "left_visual_acuity"
                ),
                cleaned_data.get(
                    "right_fit_assessment"
                ),
                cleaned_data.get(
                    "left_fit_assessment"
                ),
                cleaned_data.get(
                    "clinical_notes"
                ),
            ]

            if not any(clinical_fields):
                raise forms.ValidationError(
                    (
                        "Record at least one clinical follow-up "
                        "finding before marking the review completed."
                    )
                )

        return cleaned_data

    def save(self, commit=True):
        follow_up = super().save(
            commit=False
        )

        if self.prescription is not None:
            follow_up.prescription = (
                self.prescription
            )

            follow_up.patient = (
                self.prescription.patient
            )

        if (
            self.request_user is not None
            and self.request_user.is_authenticated
            and follow_up.status
            == ContactLensFollowUp
            .FollowUpStatus
            .COMPLETED
        ):
            follow_up.reviewed_by = (
                self.request_user
            )

        if commit:
            follow_up.save()
            self.save_m2m()

        return follow_up
