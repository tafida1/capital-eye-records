import os
import uuid

from decimal import Decimal, InvalidOperation

from django.conf import settings
from django.core.validators import (
    FileExtensionValidator,
    MaxValueValidator,
    MinValueValidator,
)
from django.db import models
from django.utils import timezone


def clinical_attachment_upload_path(instance, filename):
    """
    Store clinical files in a structured directory without exposing
    the original filename as the physical storage name.

    Example:
    clinical_attachments/
        CEH-2026-00001/
            VIS-20260802-0001/
                2026/
                    08/
                        8cbf...f9.pdf
    """

    original_extension = os.path.splitext(filename)[1].lower()

    safe_extension = original_extension[:10]

    generated_filename = (
        f"{uuid.uuid4().hex}{safe_extension}"
    )

    patient_file_number = "unknown-patient"
    visit_number = "unknown-visit"

    if instance.patient_id and instance.patient:
        patient_file_number = (
            instance.patient.file_number or "unknown-patient"
        )

    if instance.visit_id and instance.visit:
        visit_number = (
            instance.visit.visit_number or "unknown-visit"
        )

    now = timezone.now()

    return (
        "clinical_attachments/"
        f"{patient_file_number}/"
        f"{visit_number}/"
        f"{now:%Y}/"
        f"{now:%m}/"
        f"{generated_filename}"
    )


class FamilyGroup(models.Model):
    family_code = models.CharField(max_length=30, unique=True, editable=False)
    family_name = models.CharField(max_length=150)
    head_of_family = models.CharField(max_length=150, blank=True)
    primary_phone = models.CharField(max_length=20, blank=True)
    address = models.TextField(blank=True)
    notes = models.TextField(blank=True)

    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="created_family_groups",
    )

    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["family_name"]
        indexes = [
            models.Index(fields=["family_code"]),
            models.Index(fields=["family_name"]),
            models.Index(fields=["primary_phone"]),
        ]

    def __str__(self):
        return f"{self.family_code} - {self.family_name}"

    def save(self, *args, **kwargs):
        if not self.family_code:
            self.family_code = self.generate_family_code()
        super().save(*args, **kwargs)

    @classmethod
    def generate_family_code(cls):
        year = timezone.now().year
        prefix = f"FAM-{year}-"

        last_group = (
            cls.objects.filter(family_code__startswith=prefix)
            .order_by("-id")
            .first()
        )

        if last_group:
            try:
                last_number = int(last_group.family_code.split("-")[-1])
            except ValueError:
                last_number = 0
        else:
            last_number = 0

        return f"{prefix}{last_number + 1:05d}"


class Patient(models.Model):
    class Gender(models.TextChoices):
        MALE = "MALE", "Male"
        FEMALE = "FEMALE", "Female"

    class PaymentStatus(models.TextChoices):
        PAID = "PAID", "Paid"
        UNPAID = "UNPAID", "Unpaid"
        PART_PAYMENT = "PART_PAYMENT", "Part Payment"
        NOT_APPLICABLE = "NOT_APPLICABLE", "Not Applicable"

    file_number = models.CharField(max_length=30, unique=True, editable=False)

    full_name = models.CharField(max_length=150)
    gender = models.CharField(max_length=10, choices=Gender.choices)
    date_of_birth = models.DateField(blank=True, null=True)
    age = models.PositiveIntegerField(blank=True, null=True)

    phone_number = models.CharField(max_length=20, blank=True)
    address = models.TextField(blank=True)
    occupation = models.CharField(max_length=100, blank=True)

    next_of_kin_name = models.CharField(max_length=150, blank=True)
    next_of_kin_phone = models.CharField(max_length=20, blank=True)
    next_of_kin_relationship = models.CharField(max_length=100, blank=True)

    family_group = models.ForeignKey(
        FamilyGroup,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="members",
    )
    family_group_name = models.CharField(max_length=150, blank=True)
    family_relationship = models.CharField(max_length=100, blank=True)

    medical_history = models.TextField(blank=True)
    allergy_history = models.TextField(blank=True)
    eye_complaint = models.TextField(blank=True)
    diagnosis = models.TextField(blank=True)
    treatment = models.TextField(blank=True)
    surgery_procedure_details = models.TextField(blank=True)

    payment_status = models.CharField(
        max_length=20,
        choices=PaymentStatus.choices,
        default=PaymentStatus.NOT_APPLICABLE,
    )

    notes = models.TextField(blank=True)

    registered_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="registered_patients",
    )

    registration_date = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-registration_date"]
        indexes = [
            models.Index(fields=["file_number"]),
            models.Index(fields=["full_name"]),
            models.Index(fields=["phone_number"]),
            models.Index(fields=["registration_date"]),
        ]

    def __str__(self):
        return f"{self.file_number} - {self.full_name}"

    def save(self, *args, **kwargs):
        if not self.file_number:
            self.file_number = self.generate_file_number()
        super().save(*args, **kwargs)

    @classmethod
    def generate_file_number(cls):
        year = timezone.now().year
        prefix = f"CEH-{year}-"

        last_patient = (
            cls.objects.filter(file_number__startswith=prefix)
            .order_by("-id")
            .first()
        )

        if last_patient:
            try:
                last_number = int(last_patient.file_number.split("-")[-1])
            except ValueError:
                last_number = 0
        else:
            last_number = 0

        new_number = last_number + 1
        return f"{prefix}{new_number:05d}"

    @property
    def display_age(self):
        if self.age:
            return self.age

        if self.date_of_birth:
            today = timezone.now().date()
            return (
                today.year
                - self.date_of_birth.year
                - ((today.month, today.day) < (self.date_of_birth.month, self.date_of_birth.day))
            )

        return None



class PatientVisit(models.Model):
    class VisitType(models.TextChoices):
        NEW_CONSULTATION = "NEW_CONSULTATION", "New Consultation"
        FOLLOW_UP = "FOLLOW_UP", "Follow Up"
        EMERGENCY = "EMERGENCY", "Emergency"
        SURGERY_REVIEW = "SURGERY_REVIEW", "Surgery Review"
        PROCEDURE = "PROCEDURE", "Procedure"
        OTHER = "OTHER", "Other"

    class VisitStatus(models.TextChoices):
        WAITING = "WAITING", "Waiting"
        WITH_NURSE = "WITH_NURSE", "With Nurse"
        WITH_DOCTOR = "WITH_DOCTOR", "With Doctor"
        COMPLETED = "COMPLETED", "Completed"
        CANCELLED = "CANCELLED", "Cancelled"

    patient = models.ForeignKey(
        Patient,
        on_delete=models.CASCADE,
        related_name="visits",
    )

    visit_number = models.CharField(max_length=40, unique=True, editable=False)
    visit_date = models.DateTimeField(default=timezone.now)

    visit_type = models.CharField(
        max_length=30,
        choices=VisitType.choices,
        default=VisitType.NEW_CONSULTATION,
    )

    status = models.CharField(
        max_length=30,
        choices=VisitStatus.choices,
        default=VisitStatus.WAITING,
    )

    chief_complaint = models.TextField(blank=True)
    brief_history = models.TextField(blank=True)
    temperature = models.CharField(max_length=20, blank=True)
    blood_pressure = models.CharField(max_length=20, blank=True)
    pulse = models.CharField(max_length=20, blank=True)
    weight = models.CharField(max_length=20, blank=True)

    notes = models.TextField(blank=True)

    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="created_patient_visits",
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-visit_date"]
        indexes = [
            models.Index(fields=["visit_number"]),
            models.Index(fields=["visit_date"]),
            models.Index(fields=["status"]),
            models.Index(fields=["visit_type"]),
        ]

    def __str__(self):
        return f"{self.visit_number} - {self.patient.full_name}"

    def save(self, *args, **kwargs):
        if not self.visit_number:
            self.visit_number = self.generate_visit_number()
        super().save(*args, **kwargs)

    @classmethod
    def generate_visit_number(cls):
        today = timezone.now()
        prefix = f"VIS-{today.strftime('%Y%m%d')}-"

        last_visit = (
            cls.objects.filter(visit_number__startswith=prefix)
            .order_by("-id")
            .first()
        )

        if last_visit:
            try:
                last_number = int(last_visit.visit_number.split("-")[-1])
            except ValueError:
                last_number = 0
        else:
            last_number = 0

        return f"{prefix}{last_number + 1:04d}"



class Consultation(models.Model):
    visit = models.OneToOneField(
        PatientVisit,
        on_delete=models.CASCADE,
        related_name="consultation",
    )

    presenting_complaint = models.TextField(blank=True)
    history_of_presenting_complaint = models.TextField(blank=True)
    past_ocular_history = models.TextField(blank=True)
    past_medical_history = models.TextField(blank=True)
    drug_history = models.TextField(blank=True)
    family_history = models.TextField(blank=True)

    provisional_diagnosis = models.TextField(blank=True)
    final_diagnosis = models.TextField(blank=True)
    treatment_plan = models.TextField(blank=True)
    doctor_notes = models.TextField(blank=True)

    doctor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="consultations_done",
    )

    consultation_date = models.DateTimeField(default=timezone.now)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-consultation_date"]

    def __str__(self):
        return f"Consultation - {self.visit.visit_number}"




class EyeExamination(models.Model):
    """
    Stores one comprehensive eye examination for a patient visit.

    Existing fields have been preserved so that old records, templates,
    reports and views continue to work. New structured Slit Lamp and
    Fundoscopy fields are additive and optional.
    """

    class ConjunctivaFinding(models.TextChoices):
        QUIET = "QUIET", "Quiet"
        INJECTION = "INJECTION", "Injection"
        HYPERAEMIA = "HYPERAEMIA", "Hyperaemia"
        OTHER = "OTHER", "Others (Specify)"

    class CorneaFinding(models.TextChoices):
        CLEAR = "CLEAR", "Clear"
        HAZY = "HAZY", "Hazy"
        OTHER = "OTHER", "Others (Specify)"

    class AnteriorChamberFinding(models.TextChoices):
        FORMED_CLEAR = "FORMED_CLEAR", "Formed, Clear Media"
        OTHER = "OTHER", "Others (Specify)"

    class IrisFinding(models.TextChoices):
        NORMAL = "NORMAL", "Normal"
        OTHER = "OTHER", "Others (Specify)"

    class PupilFinding(models.TextChoices):
        ROUND_REGULAR_REACTIVE = (
            "ROUND_REGULAR_REACTIVE",
            "Round, Regular, Reactive",
        )
        RAPD = "RAPD", "RAPD"
        OTHER = "OTHER", "Others (Specify)"

    class LensFinding(models.TextChoices):
        TRANSPARENT = "TRANSPARENT", "Transparent"
        OTHER = "OTHER", "Others (Specify)"

    class VitreousFinding(models.TextChoices):
        CLEAR_MEDIA = "CLEAR_MEDIA", "Clear media"
        OTHER = "OTHER", "Others (Specify)"

    class DiscColourFinding(models.TextChoices):
        PINK_NRR = "PINK_NRR", "Pink NRR"
        PALE_NRR = "PALE_NRR", "Pale NRR"
        OTHER = "OTHER", "Others (Specify)"

    class DiscMarginFinding(models.TextChoices):
        DISTINCT = "DISTINCT", "Distinct"
        OTHER = "OTHER", "Others (Specify)"

    class VesselFinding(models.TextChoices):
        NORMAL = "NORMAL", "Normal"
        OTHER = "OTHER", "Others (Specify)"

    class RetinaFinding(models.TextChoices):
        PINK_FLAT = "PINK_FLAT", "Pink, Flat"
        OTHER = "OTHER", "Others (Specify)"

    class MaculaFinding(models.TextChoices):
        BRIGHT_REFLEX = "BRIGHT_REFLEX", "Bright reflex"
        DULL_REFLEX = "DULL_REFLEX", "Dull reflex"
        OTHER = "OTHER", "Others (Specify)"

    class CycloplegicAgent(models.TextChoices):
        NONE = "NONE", "None"
        CYCLOPENTOLATE = "CYCLOPENTOLATE", "Cyclopentolate"
        TROPICAMIDE = "TROPICAMIDE", "Tropicamide"
        ATROPINE = "ATROPINE", "Atropine"
        PHENYLEPHRINE = "PHENYLEPHRINE", "Phenylephrine"
        OTHER = "OTHER", "Others (Specify)"

    # =========================================================
    # SUBJECTIVE REFRACTION CHOICES
    # =========================================================

    class OpticalLensType(models.TextChoices):
        WHITE = "WHITE", "White"
        WHITE_AR = "WHITE_AR", "White A/R"
        PHOTO_AR = "PHOTO_AR", "Photo A/R"
        VARILUX = "VARILUX", "Varilux"
        REGULAR_BLUE_COAT = (
            "REGULAR_BLUE_COAT",
            "Regular Blue Coat",
        )
        ORIGINAL_BLUE_COAT = (
            "ORIGINAL_BLUE_COAT",
            "Original Blue Coat",
        )
        OTHER = "OTHER", "Others (Specify)"

    class BifocalType(models.TextChoices):
        D_TOP = "D_TOP", "D-Top"
        EXECUTIVE = "EXECUTIVE", "Executive"
        FUSED = "FUSED", "Fused"
        VARILUX = "VARILUX", "Varilux"
        OTHER = "OTHER", "Others (Specify)"

    class WearingInstruction(models.TextChoices):
        DISTANCE_ONLY = "DISTANCE_ONLY", "Distance Only"
        NEAR_ONLY = "NEAR_ONLY", "Near Only"
        REGULAR_WEAR = "REGULAR_WEAR", "Regular Wear"
        OTHER = "OTHER", "Others (Specify)"

    class DispensaryInstruction(models.TextChoices):
        BIFOCAL = "BIFOCAL", "Bifocal"
        SEPARATE = "SEPARATE", "Separate"
        DISTANCE_ONLY = "DISTANCE_ONLY", "Distance Only"
        NEAR_ONLY = "NEAR_ONLY", "Near Only"
        OTHER = "OTHER", "Others (Specify)"

    visit = models.OneToOneField(
        PatientVisit,
        on_delete=models.CASCADE,
        related_name="eye_examination",
    )

    # =========================================================
    # EXISTING VISUAL ACUITY FIELDS — DO NOT REMOVE
    # =========================================================

    right_visual_acuity = models.CharField(max_length=50, blank=True)
    left_visual_acuity = models.CharField(max_length=50, blank=True)

    right_pinhole = models.CharField(max_length=50, blank=True)
    left_pinhole = models.CharField(max_length=50, blank=True)

    right_near_vision = models.CharField(max_length=50, blank=True)
    left_near_vision = models.CharField(max_length=50, blank=True)

    # Manual values used when "Others (Specify)" is selected
    right_visual_acuity_other = models.CharField(
        max_length=100,
        blank=True,
    )
    left_visual_acuity_other = models.CharField(
        max_length=100,
        blank=True,
    )

    right_pinhole_other = models.CharField(
        max_length=100,
        blank=True,
    )
    left_pinhole_other = models.CharField(
        max_length=100,
        blank=True,
    )

    right_near_vision_other = models.CharField(
        max_length=100,
        blank=True,
    )
    left_near_vision_other = models.CharField(
        max_length=100,
        blank=True,
    )

    # =========================================================
    # EXISTING REFRACTION FIELDS — DO NOT REMOVE
    # =========================================================

    right_sphere = models.CharField(max_length=30, blank=True)
    right_cylinder = models.CharField(max_length=30, blank=True)
    right_axis = models.CharField(max_length=30, blank=True)

    left_sphere = models.CharField(max_length=30, blank=True)
    left_cylinder = models.CharField(max_length=30, blank=True)
    left_axis = models.CharField(max_length=30, blank=True)

    # =========================================================
    # EXISTING IOP FIELDS — DO NOT REMOVE
    # =========================================================

    right_iop = models.CharField(max_length=30, blank=True)
    left_iop = models.CharField(max_length=30, blank=True)

    # New corrected GAT IOP fields
    right_corrected_iop = models.CharField(max_length=30, blank=True)
    left_corrected_iop = models.CharField(max_length=30, blank=True)

    # =========================================================
    # STRUCTURED SLIT LAMP EXAMINATION — RIGHT EYE
    # =========================================================

    right_lids_adnexa = models.CharField(max_length=150, blank=True)

    right_conjunctiva = models.CharField(
        max_length=30,
        choices=ConjunctivaFinding.choices,
        blank=True,
    )
    right_conjunctiva_other = models.CharField(max_length=255, blank=True)

    right_cornea = models.CharField(
        max_length=30,
        choices=CorneaFinding.choices,
        blank=True,
    )
    right_cornea_other = models.CharField(max_length=255, blank=True)

    right_anterior_chamber = models.CharField(
        max_length=30,
        choices=AnteriorChamberFinding.choices,
        blank=True,
    )
    right_anterior_chamber_other = models.CharField(
        max_length=255,
        blank=True,
    )

    right_iris = models.CharField(
        max_length=30,
        choices=IrisFinding.choices,
        blank=True,
    )
    right_iris_other = models.CharField(max_length=255, blank=True)

    right_pupil = models.CharField(
        max_length=40,
        choices=PupilFinding.choices,
        blank=True,
    )
    right_pupil_other = models.CharField(max_length=255, blank=True)

    right_lens = models.CharField(
        max_length=30,
        choices=LensFinding.choices,
        blank=True,
    )
    right_lens_other = models.CharField(max_length=255, blank=True)

    right_gonioscopy_findings = models.TextField(blank=True)

    # =========================================================
    # STRUCTURED SLIT LAMP EXAMINATION — LEFT EYE
    # =========================================================

    left_lids_adnexa = models.CharField(max_length=150, blank=True)

    left_conjunctiva = models.CharField(
        max_length=30,
        choices=ConjunctivaFinding.choices,
        blank=True,
    )
    left_conjunctiva_other = models.CharField(max_length=255, blank=True)

    left_cornea = models.CharField(
        max_length=30,
        choices=CorneaFinding.choices,
        blank=True,
    )
    left_cornea_other = models.CharField(max_length=255, blank=True)

    left_anterior_chamber = models.CharField(
        max_length=30,
        choices=AnteriorChamberFinding.choices,
        blank=True,
    )
    left_anterior_chamber_other = models.CharField(
        max_length=255,
        blank=True,
    )

    left_iris = models.CharField(
        max_length=30,
        choices=IrisFinding.choices,
        blank=True,
    )
    left_iris_other = models.CharField(max_length=255, blank=True)

    left_pupil = models.CharField(
        max_length=40,
        choices=PupilFinding.choices,
        blank=True,
    )
    left_pupil_other = models.CharField(max_length=255, blank=True)

    left_lens = models.CharField(
        max_length=30,
        choices=LensFinding.choices,
        blank=True,
    )
    left_lens_other = models.CharField(max_length=255, blank=True)

    left_gonioscopy_findings = models.TextField(blank=True)

    # =========================================================
    # STRUCTURED FUNDOSCOPY — RIGHT EYE
    # =========================================================

    right_vitreous = models.CharField(
        max_length=30,
        choices=VitreousFinding.choices,
        blank=True,
    )
    right_vitreous_other = models.CharField(max_length=255, blank=True)

    right_disc_colour = models.CharField(
        max_length=30,
        choices=DiscColourFinding.choices,
        blank=True,
    )
    right_disc_colour_other = models.CharField(max_length=255, blank=True)

    right_estimated_vcdr = models.DecimalField(
        max_digits=3,
        decimal_places=2,
        blank=True,
        null=True,
    )

    right_disc_margin = models.CharField(
        max_length=30,
        choices=DiscMarginFinding.choices,
        blank=True,
    )
    right_disc_margin_other = models.CharField(max_length=255, blank=True)

    right_vessels = models.CharField(
        max_length=30,
        choices=VesselFinding.choices,
        blank=True,
    )
    right_vessels_other = models.CharField(max_length=255, blank=True)

    right_retina = models.CharField(
        max_length=30,
        choices=RetinaFinding.choices,
        blank=True,
    )
    right_retina_other = models.CharField(max_length=255, blank=True)

    right_macula = models.CharField(
        max_length=30,
        choices=MaculaFinding.choices,
        blank=True,
    )
    right_macula_other = models.CharField(max_length=255, blank=True)

    right_other_fundus_findings = models.TextField(blank=True)

    # =========================================================
    # STRUCTURED FUNDOSCOPY — LEFT EYE
    # =========================================================

    left_vitreous = models.CharField(
        max_length=30,
        choices=VitreousFinding.choices,
        blank=True,
    )
    left_vitreous_other = models.CharField(max_length=255, blank=True)

    left_disc_colour = models.CharField(
        max_length=30,
        choices=DiscColourFinding.choices,
        blank=True,
    )
    left_disc_colour_other = models.CharField(max_length=255, blank=True)

    left_estimated_vcdr = models.DecimalField(
        max_digits=3,
        decimal_places=2,
        blank=True,
        null=True,
    )

    left_disc_margin = models.CharField(
        max_length=30,
        choices=DiscMarginFinding.choices,
        blank=True,
    )
    left_disc_margin_other = models.CharField(max_length=255, blank=True)

    left_vessels = models.CharField(
        max_length=30,
        choices=VesselFinding.choices,
        blank=True,
    )
    left_vessels_other = models.CharField(max_length=255, blank=True)

    left_retina = models.CharField(
        max_length=30,
        choices=RetinaFinding.choices,
        blank=True,
    )
    left_retina_other = models.CharField(max_length=255, blank=True)

    left_macula = models.CharField(
        max_length=30,
        choices=MaculaFinding.choices,
        blank=True,
    )
    left_macula_other = models.CharField(max_length=255, blank=True)

    left_other_fundus_findings = models.TextField(blank=True)

    # =========================================================
    # AUTO REFRACTION
    #
    # Existing fields reused:
    # right_visual_acuity / left_visual_acuity = Unaided VA
    # right_pinhole / left_pinhole             = Pinhole VA
    # right_near_vision / left_near_vision     = Near Vision
    # examined_by                              = Doctor / Optometrist
    # =========================================================

    # Visual acuity fields missing from the original model
    right_with_glasses = models.CharField(
        max_length=50,
        blank=True,
        verbose_name="Right Eye With Glasses",
    )
    left_with_glasses = models.CharField(
        max_length=50,
        blank=True,
        verbose_name="Left Eye With Glasses",
    )

    right_with_glasses_other = models.CharField(
        max_length=100,
        blank=True,
    )
    left_with_glasses_other = models.CharField(
        max_length=100,
        blank=True,
    )

    # ---------------------------------------------------------
    # Dry Auto Refraction — Right Eye
    # ---------------------------------------------------------

    right_dry_sphere = models.DecimalField(
        max_digits=6,
        decimal_places=2,
        blank=True,
        null=True,
        verbose_name="Right Dry Sphere",
    )
    right_dry_cylinder = models.DecimalField(
        max_digits=6,
        decimal_places=2,
        blank=True,
        null=True,
        verbose_name="Right Dry Cylinder",
    )
    right_dry_axis = models.PositiveSmallIntegerField(
        blank=True,
        null=True,
        verbose_name="Right Dry Axis",
    )
    right_dry_spherical_equivalent = models.DecimalField(
        max_digits=6,
        decimal_places=2,
        blank=True,
        null=True,
        editable=False,
        verbose_name="Right Dry Spherical Equivalent",
    )

    # ---------------------------------------------------------
    # Dry Auto Refraction — Left Eye
    # ---------------------------------------------------------

    left_dry_sphere = models.DecimalField(
        max_digits=6,
        decimal_places=2,
        blank=True,
        null=True,
        verbose_name="Left Dry Sphere",
    )
    left_dry_cylinder = models.DecimalField(
        max_digits=6,
        decimal_places=2,
        blank=True,
        null=True,
        verbose_name="Left Dry Cylinder",
    )
    left_dry_axis = models.PositiveSmallIntegerField(
        blank=True,
        null=True,
        verbose_name="Left Dry Axis",
    )
    left_dry_spherical_equivalent = models.DecimalField(
        max_digits=6,
        decimal_places=2,
        blank=True,
        null=True,
        editable=False,
        verbose_name="Left Dry Spherical Equivalent",
    )

    # ---------------------------------------------------------
    # Wet Auto Refraction — Right Eye
    # ---------------------------------------------------------

    right_wet_sphere = models.DecimalField(
        max_digits=6,
        decimal_places=2,
        blank=True,
        null=True,
        verbose_name="Right Wet Sphere",
    )
    right_wet_cylinder = models.DecimalField(
        max_digits=6,
        decimal_places=2,
        blank=True,
        null=True,
        verbose_name="Right Wet Cylinder",
    )
    right_wet_axis = models.PositiveSmallIntegerField(
        blank=True,
        null=True,
        verbose_name="Right Wet Axis",
    )
    right_wet_spherical_equivalent = models.DecimalField(
        max_digits=6,
        decimal_places=2,
        blank=True,
        null=True,
        editable=False,
        verbose_name="Right Wet Spherical Equivalent",
    )

    # ---------------------------------------------------------
    # Wet Auto Refraction — Left Eye
    # ---------------------------------------------------------

    left_wet_sphere = models.DecimalField(
        max_digits=6,
        decimal_places=2,
        blank=True,
        null=True,
        verbose_name="Left Wet Sphere",
    )
    left_wet_cylinder = models.DecimalField(
        max_digits=6,
        decimal_places=2,
        blank=True,
        null=True,
        verbose_name="Left Wet Cylinder",
    )
    left_wet_axis = models.PositiveSmallIntegerField(
        blank=True,
        null=True,
        verbose_name="Left Wet Axis",
    )
    left_wet_spherical_equivalent = models.DecimalField(
        max_digits=6,
        decimal_places=2,
        blank=True,
        null=True,
        editable=False,
        verbose_name="Left Wet Spherical Equivalent",
    )

    # ---------------------------------------------------------
    # Lensometry, Cycloplegia and Remarks
    # ---------------------------------------------------------

    right_lensometry = models.CharField(
        max_length=150,
        blank=True,
        verbose_name="Lensometry — Right Eye",
    )
    left_lensometry = models.CharField(
        max_length=150,
        blank=True,
        verbose_name="Lensometry — Left Eye",
    )

    cycloplegic_agent = models.CharField(
        max_length=30,
        choices=CycloplegicAgent.choices,
        blank=True,
        verbose_name="Cycloplegic Agent",
    )
    cycloplegic_agent_other = models.CharField(
        max_length=150,
        blank=True,
        verbose_name="Other Cycloplegic Agent",
    )

    auto_refraction_remarks = models.TextField(
        blank=True,
        verbose_name="Auto Refraction Remarks",
    )

    # =========================================================
    # SUBJECTIVE REFRACTION / OPTICAL LENS PRESCRIPTION
    #
    # This is an optical refraction record. It is separate from
    # the existing medication Prescription model.
    # =========================================================

    subjective_refraction_history = models.TextField(
        blank=True,
        verbose_name="Subjective Refraction History",
    )

    subjective_refraction_diagnosis = models.TextField(
        blank=True,
        verbose_name="Subjective Refraction Diagnosis",
    )

    # ---------------------------------------------------------
    # RIGHT EYE SUBJECTIVE REFRACTION
    # ---------------------------------------------------------

    right_subjective_sphere = models.DecimalField(
        max_digits=6,
        decimal_places=2,
        blank=True,
        null=True,
        verbose_name="Right Subjective Sphere",
    )

    right_subjective_cylinder = models.DecimalField(
        max_digits=6,
        decimal_places=2,
        blank=True,
        null=True,
        verbose_name="Right Subjective Cylinder",
    )

    right_subjective_axis = models.PositiveSmallIntegerField(
        blank=True,
        null=True,
        verbose_name="Right Subjective Axis",
    )

    right_subjective_aided_va = models.CharField(
        max_length=50,
        blank=True,
        verbose_name="Right Aided Visual Acuity",
    )

    right_subjective_aided_va_other = models.CharField(
        max_length=100,
        blank=True,
        verbose_name="Other Right Aided Visual Acuity",
    )

    right_subjective_add_power = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        blank=True,
        null=True,
        verbose_name="Right Add Power",
    )

    right_subjective_near_vision = models.CharField(
        max_length=50,
        blank=True,
        verbose_name="Right Subjective Near Vision",
    )

    right_subjective_near_vision_other = models.CharField(
        max_length=100,
        blank=True,
        verbose_name="Other Right Subjective Near Vision",
    )

    # ---------------------------------------------------------
    # LEFT EYE SUBJECTIVE REFRACTION
    # ---------------------------------------------------------

    left_subjective_sphere = models.DecimalField(
        max_digits=6,
        decimal_places=2,
        blank=True,
        null=True,
        verbose_name="Left Subjective Sphere",
    )

    left_subjective_cylinder = models.DecimalField(
        max_digits=6,
        decimal_places=2,
        blank=True,
        null=True,
        verbose_name="Left Subjective Cylinder",
    )

    left_subjective_axis = models.PositiveSmallIntegerField(
        blank=True,
        null=True,
        verbose_name="Left Subjective Axis",
    )

    left_subjective_aided_va = models.CharField(
        max_length=50,
        blank=True,
        verbose_name="Left Aided Visual Acuity",
    )

    left_subjective_aided_va_other = models.CharField(
        max_length=100,
        blank=True,
        verbose_name="Other Left Aided Visual Acuity",
    )

    left_subjective_add_power = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        blank=True,
        null=True,
        verbose_name="Left Add Power",
    )

    left_subjective_near_vision = models.CharField(
        max_length=50,
        blank=True,
        verbose_name="Left Subjective Near Vision",
    )

    left_subjective_near_vision_other = models.CharField(
        max_length=100,
        blank=True,
        verbose_name="Other Left Subjective Near Vision",
    )

    # ---------------------------------------------------------
    # PUPILLARY DISTANCE
    # ---------------------------------------------------------

    subjective_distance_pd = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        blank=True,
        null=True,
        verbose_name="Distance PD",
        help_text="Distance pupillary distance in millimetres.",
    )

    subjective_near_pd = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        blank=True,
        null=True,
        verbose_name="Near PD",
        help_text="Near pupillary distance in millimetres.",
    )

    # ---------------------------------------------------------
    # LENS AND DISPENSING DETAILS
    # ---------------------------------------------------------

    subjective_lens_type = models.CharField(
        max_length=40,
        choices=OpticalLensType.choices,
        blank=True,
        verbose_name="Lens Type",
    )

    subjective_lens_type_other = models.CharField(
        max_length=150,
        blank=True,
        verbose_name="Other Lens Type",
    )

    subjective_bifocal_type = models.CharField(
        max_length=30,
        choices=BifocalType.choices,
        blank=True,
        verbose_name="Bifocal Type",
    )

    subjective_bifocal_type_other = models.CharField(
        max_length=150,
        blank=True,
        verbose_name="Other Bifocal Type",
    )

    subjective_wearing_instruction = models.CharField(
        max_length=30,
        choices=WearingInstruction.choices,
        blank=True,
        verbose_name="Wearing Instruction",
    )

    subjective_wearing_instruction_other = models.CharField(
        max_length=150,
        blank=True,
        verbose_name="Other Wearing Instruction",
    )

    subjective_dispensary_instruction = models.CharField(
        max_length=30,
        choices=DispensaryInstruction.choices,
        blank=True,
        verbose_name="Dispensary Instruction",
    )

    subjective_dispensary_instruction_other = models.CharField(
        max_length=150,
        blank=True,
        verbose_name="Other Dispensary Instruction",
    )

    subjective_refraction_remarks = models.TextField(
        blank=True,
        verbose_name="Subjective Refraction Remarks",
    )

    # ---------------------------------------------------------
    # APPROVAL AND AUDIT INFORMATION
    # ---------------------------------------------------------

    subjective_refraction_approved = models.BooleanField(
        default=False,
        verbose_name="Subjective Refraction Approved",
    )

    subjective_refraction_approved_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="approved_subjective_refractions",
        verbose_name="Approved By",
    )

    subjective_refraction_approved_at = models.DateTimeField(
        blank=True,
        null=True,
        verbose_name="Approved At",
    )

    # =========================================================
    # EXISTING GENERAL FREE-TEXT FINDINGS — DO NOT REMOVE
    # =========================================================

    external_exam = models.TextField(blank=True)
    anterior_segment = models.TextField(blank=True)
    posterior_segment = models.TextField(blank=True)
    fundus_exam = models.TextField(blank=True)
    slit_lamp_exam = models.TextField(blank=True)

    right_eye_findings = models.TextField(blank=True)
    left_eye_findings = models.TextField(blank=True)

    impression = models.TextField(blank=True)
    recommendation = models.TextField(blank=True)

    examined_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="eye_examinations_done",
    )

    examination_date = models.DateTimeField(default=timezone.now)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-examination_date"]

    @staticmethod
    def calculate_spherical_equivalent(sphere, cylinder):
        """
        Calculate spherical equivalent:

            S/E = Sphere + (Cylinder / 2)

        Returns None when both measurements are absent.
        """

        if sphere is None and cylinder is None:
            return None

        try:
            sphere_value = (
                Decimal(str(sphere))
                if sphere is not None
                else Decimal("0.00")
            )
            cylinder_value = (
                Decimal(str(cylinder))
                if cylinder is not None
                else Decimal("0.00")
            )

            return (
                sphere_value + (cylinder_value / Decimal("2"))
            ).quantize(Decimal("0.01"))

        except (InvalidOperation, TypeError, ValueError):
            return None

    def save(self, *args, **kwargs):
        self.right_dry_spherical_equivalent = (
            self.calculate_spherical_equivalent(
                self.right_dry_sphere,
                self.right_dry_cylinder,
            )
        )

        self.left_dry_spherical_equivalent = (
            self.calculate_spherical_equivalent(
                self.left_dry_sphere,
                self.left_dry_cylinder,
            )
        )

        self.right_wet_spherical_equivalent = (
            self.calculate_spherical_equivalent(
                self.right_wet_sphere,
                self.right_wet_cylinder,
            )
        )

        self.left_wet_spherical_equivalent = (
            self.calculate_spherical_equivalent(
                self.left_wet_sphere,
                self.left_wet_cylinder,
            )
        )

        # Set or clear the Subjective Refraction approval time.
        if (
            self.subjective_refraction_approved
            and self.subjective_refraction_approved_at is None
        ):
            self.subjective_refraction_approved_at = timezone.now()

        if not self.subjective_refraction_approved:
            self.subjective_refraction_approved_at = None
            self.subjective_refraction_approved_by = None

        super().save(*args, **kwargs)

    def __str__(self):
        return f"Eye Exam - {self.visit.visit_number}"



class DiagnosisTreatment(models.Model):
    visit = models.OneToOneField(
        PatientVisit,
        on_delete=models.CASCADE,
        related_name="diagnosis_treatment",
    )

    primary_diagnosis = models.TextField()
    secondary_diagnosis = models.TextField(blank=True)
    differential_diagnosis = models.TextField(blank=True)

    treatment_plan = models.TextField(blank=True)
    advice_given = models.TextField(blank=True)
    follow_up_instruction = models.TextField(blank=True)

    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="diagnosis_treatments_created",
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"Diagnosis/Treatment - {self.visit.visit_number}"


class Prescription(models.Model):
    visit = models.ForeignKey(
        PatientVisit,
        on_delete=models.CASCADE,
        related_name="prescriptions",
    )

    drug_name = models.CharField(max_length=150)
    dosage = models.CharField(max_length=100, blank=True)
    frequency = models.CharField(max_length=100, blank=True)
    duration = models.CharField(max_length=100, blank=True)
    instructions = models.TextField(blank=True)

    prescribed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="prescriptions_given",
    )

    prescribed_at = models.DateTimeField(default=timezone.now)

    class Meta:
        ordering = ["-prescribed_at"]

    def __str__(self):
        return f"{self.drug_name} - {self.visit.visit_number}"


class SurgeryProcedure(models.Model):
    class ProcedureStatus(models.TextChoices):
        PLANNED = "PLANNED", "Planned"
        IN_PROGRESS = "IN_PROGRESS", "In Progress"
        COMPLETED = "COMPLETED", "Completed"
        CANCELLED = "CANCELLED", "Cancelled"
        POSTPONED = "POSTPONED", "Postponed"

    class EyeSide(models.TextChoices):
        RIGHT = "RIGHT", "Right Eye"
        LEFT = "LEFT", "Left Eye"
        BOTH = "BOTH", "Both Eyes"
        NOT_APPLICABLE = "NOT_APPLICABLE", "Not Applicable"

    patient = models.ForeignKey(
        Patient,
        on_delete=models.CASCADE,
        related_name="surgeries",
    )

    visit = models.ForeignKey(
        PatientVisit,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="surgeries",
    )

    procedure_number = models.CharField(max_length=40, unique=True, editable=False)
    procedure_name = models.CharField(max_length=200)
    procedure_type = models.CharField(max_length=150, blank=True)
    eye_side = models.CharField(
        max_length=20,
        choices=EyeSide.choices,
        default=EyeSide.NOT_APPLICABLE,
    )

    scheduled_date = models.DateTimeField(blank=True, null=True)
    procedure_date = models.DateTimeField(blank=True, null=True)

    status = models.CharField(
        max_length=30,
        choices=ProcedureStatus.choices,
        default=ProcedureStatus.PLANNED,
    )

    pre_op_diagnosis = models.TextField(blank=True)
    post_op_diagnosis = models.TextField(blank=True)
    procedure_notes = models.TextField(blank=True)
    anesthesia_type = models.CharField(max_length=100, blank=True)
    complications = models.TextField(blank=True)
    outcome = models.TextField(blank=True)
    post_op_instructions = models.TextField(blank=True)

    surgeon = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="surgeries_as_surgeon",
    )

    assistant = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="surgeries_as_assistant",
    )

    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="surgery_records_created",
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-scheduled_date", "-created_at"]
        indexes = [
            models.Index(fields=["procedure_number"]),
            models.Index(fields=["procedure_name"]),
            models.Index(fields=["procedure_type"]),
            models.Index(fields=["status"]),
            models.Index(fields=["scheduled_date"]),
        ]

    def __str__(self):
        return f"{self.procedure_number} - {self.patient.full_name}"

    def save(self, *args, **kwargs):
        if not self.procedure_number:
            self.procedure_number = self.generate_procedure_number()
        super().save(*args, **kwargs)

    @classmethod
    def generate_procedure_number(cls):
        today = timezone.now()
        prefix = f"PROC-{today.strftime('%Y%m%d')}-"

        last_record = (
            cls.objects.filter(procedure_number__startswith=prefix)
            .order_by("-id")
            .first()
        )

        if last_record:
            try:
                last_number = int(last_record.procedure_number.split("-")[-1])
            except ValueError:
                last_number = 0
        else:
            last_number = 0

        return f"{prefix}{last_number + 1:04d}"


class Appointment(models.Model):
    class AppointmentStatus(models.TextChoices):
        SCHEDULED = "SCHEDULED", "Scheduled"
        CONFIRMED = "CONFIRMED", "Confirmed"
        ARRIVED = "ARRIVED", "Arrived"
        COMPLETED = "COMPLETED", "Completed"
        CANCELLED = "CANCELLED", "Cancelled"
        MISSED = "MISSED", "Missed"

    class AppointmentType(models.TextChoices):
        CONSULTATION = "CONSULTATION", "Consultation"
        FOLLOW_UP = "FOLLOW_UP", "Follow Up"
        SURGERY = "SURGERY", "Surgery"
        PROCEDURE = "PROCEDURE", "Procedure"
        EYE_TEST = "EYE_TEST", "Eye Test"
        OTHER = "OTHER", "Other"

    patient = models.ForeignKey(
        Patient,
        on_delete=models.CASCADE,
        related_name="appointments",
    )

    appointment_number = models.CharField(max_length=40, unique=True, editable=False)

    appointment_type = models.CharField(
        max_length=30,
        choices=AppointmentType.choices,
        default=AppointmentType.CONSULTATION,
    )

    status = models.CharField(
        max_length=30,
        choices=AppointmentStatus.choices,
        default=AppointmentStatus.SCHEDULED,
    )

    appointment_date = models.DateField()
    appointment_time = models.TimeField()

    reason = models.TextField(blank=True)
    notes = models.TextField(blank=True)

    assigned_to = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="assigned_appointments",
    )

    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="appointments_created",
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["appointment_date", "appointment_time"]
        indexes = [
            models.Index(fields=["appointment_number"]),
            models.Index(fields=["appointment_date"]),
            models.Index(fields=["status"]),
            models.Index(fields=["appointment_type"]),
        ]

    def __str__(self):
        return f"{self.appointment_number} - {self.patient.full_name}"

    def save(self, *args, **kwargs):
        if not self.appointment_number:
            self.appointment_number = self.generate_appointment_number()
        super().save(*args, **kwargs)

    @classmethod
    def generate_appointment_number(cls):
        today = timezone.now()
        prefix = f"APT-{today.strftime('%Y%m%d')}-"

        last_record = (
            cls.objects.filter(appointment_number__startswith=prefix)
            .order_by("-id")
            .first()
        )

        if last_record:
            try:
                last_number = int(last_record.appointment_number.split("-")[-1])
            except ValueError:
                last_number = 0
        else:
            last_number = 0

        return f"{prefix}{last_number + 1:04d}"


class Bill(models.Model):
    class BillStatus(models.TextChoices):
        UNPAID = "UNPAID", "Unpaid"
        PART_PAID = "PART_PAID", "Part Paid"
        PAID = "PAID", "Paid"
        CANCELLED = "CANCELLED", "Cancelled"

    patient = models.ForeignKey(
        Patient,
        on_delete=models.CASCADE,
        related_name="bills",
    )

    visit = models.ForeignKey(
        PatientVisit,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="bills",
    )

    surgery = models.ForeignKey(
        SurgeryProcedure,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="bills",
    )

    appointment = models.ForeignKey(
        Appointment,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="bills",
    )

    bill_number = models.CharField(max_length=40, unique=True, editable=False)
    bill_title = models.CharField(max_length=200)

    total_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    discount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    amount_paid = models.DecimalField(max_digits=12, decimal_places=2, default=0)

    status = models.CharField(
        max_length=20,
        choices=BillStatus.choices,
        default=BillStatus.UNPAID,
    )

    notes = models.TextField(blank=True)

    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="bills_created",
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["bill_number"]),
            models.Index(fields=["status"]),
            models.Index(fields=["created_at"]),
        ]

    def __str__(self):
        return f"{self.bill_number} - {self.patient.full_name}"

    @property
    def net_amount(self):
        return self.total_amount - self.discount

    @property
    def balance(self):
        return self.net_amount - self.amount_paid

    def update_status(self):
        if self.status == self.BillStatus.CANCELLED:
            return

        if self.amount_paid <= 0:
            self.status = self.BillStatus.UNPAID
        elif self.amount_paid < self.net_amount:
            self.status = self.BillStatus.PART_PAID
        else:
            self.status = self.BillStatus.PAID

    def save(self, *args, **kwargs):
        if not self.bill_number:
            self.bill_number = self.generate_bill_number()

        self.update_status()
        super().save(*args, **kwargs)

    @classmethod
    def generate_bill_number(cls):
        today = timezone.now()
        prefix = f"BILL-{today.strftime('%Y%m%d')}-"

        last_record = (
            cls.objects.filter(bill_number__startswith=prefix)
            .order_by("-id")
            .first()
        )

        if last_record:
            try:
                last_number = int(last_record.bill_number.split("-")[-1])
            except ValueError:
                last_number = 0
        else:
            last_number = 0

        return f"{prefix}{last_number + 1:04d}"


class Payment(models.Model):
    class PaymentMethod(models.TextChoices):
        CASH = "CASH", "Cash"
        POS = "POS", "POS"
        TRANSFER = "TRANSFER", "Bank Transfer"
        CHEQUE = "CHEQUE", "Cheque"
        OTHER = "OTHER", "Other"

    bill = models.ForeignKey(
        Bill,
        on_delete=models.CASCADE,
        related_name="payments",
    )

    receipt_number = models.CharField(max_length=40, unique=True, editable=False)
    amount = models.DecimalField(max_digits=12, decimal_places=2)

    payment_method = models.CharField(
        max_length=20,
        choices=PaymentMethod.choices,
        default=PaymentMethod.CASH,
    )

    reference_number = models.CharField(max_length=100, blank=True)
    payment_date = models.DateTimeField(default=timezone.now)
    notes = models.TextField(blank=True)

    received_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="payments_received",
    )

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-payment_date"]
        indexes = [
            models.Index(fields=["receipt_number"]),
            models.Index(fields=["payment_date"]),
            models.Index(fields=["payment_method"]),
        ]

    def __str__(self):
        return f"{self.receipt_number} - {self.amount}"

    def save(self, *args, **kwargs):
        is_new = self.pk is None

        if not self.receipt_number:
            self.receipt_number = self.generate_receipt_number()

        super().save(*args, **kwargs)

        if is_new:
            bill = self.bill
            bill.amount_paid = sum(payment.amount for payment in bill.payments.all())
            bill.save(update_fields=["amount_paid", "status", "updated_at"])

    @classmethod
    def generate_receipt_number(cls):
        today = timezone.now()
        prefix = f"RCT-{today.strftime('%Y%m%d')}-"

        last_record = (
            cls.objects.filter(receipt_number__startswith=prefix)
            .order_by("-id")
            .first()
        )

        if last_record:
            try:
                last_number = int(last_record.receipt_number.split("-")[-1])
            except ValueError:
                last_number = 0
        else:
            last_number = 0

        return f"{prefix}{last_number + 1:04d}"

class ClinicalAttachment(models.Model):
    """
    Stores investigation images and clinical documents associated
    with a patient visit.

    A visit may contain multiple attachments. This model is separate
    from EyeExamination so files can be uploaded, reviewed and managed
    independently without duplicating the examination record.
    """

    class Category(models.TextChoices):
        OCT = "OCT", "OCT Scan"
        FUNDUS_PHOTO = "FUNDUS_PHOTO", "Fundus Photograph"
        VISUAL_FIELD = "VISUAL_FIELD", "Visual Field Test"
        B_SCAN = "B_SCAN", "B-Scan Ultrasound"
        CORNEAL_TOPOGRAPHY = (
            "CORNEAL_TOPOGRAPHY",
            "Corneal Topography",
        )
        OPTICAL_BIOMETRY = (
            "OPTICAL_BIOMETRY",
            "Optical Biometry",
        )
        FLUORESCEIN_ANGIOGRAPHY = (
            "FLUORESCEIN_ANGIOGRAPHY",
            "Fluorescein Angiography",
        )
        LENSOMETRY = "LENSOMETRY", "Lensometry Report"
        LAB_RESULT = "LAB_RESULT", "Laboratory Result"
        RADIOLOGY = "RADIOLOGY", "Radiology Report"
        REFERRAL_LETTER = (
            "REFERRAL_LETTER",
            "Referral Letter",
        )
        OPERATION_NOTE = (
            "OPERATION_NOTE",
            "Operation Note",
        )
        MEDICAL_CERTIFICATE = (
            "MEDICAL_CERTIFICATE",
            "Medical Certificate",
        )
        INSURANCE_DOCUMENT = (
            "INSURANCE_DOCUMENT",
            "Insurance Document",
        )
        CONSENT_FORM = "CONSENT_FORM", "Consent Form"
        EXTERNAL_REPORT = (
            "EXTERNAL_REPORT",
            "External Medical Report",
        )
        OTHER = "OTHER", "Others (Specify)"

    class EyeSide(models.TextChoices):
        RIGHT = "RIGHT", "Right Eye"
        LEFT = "LEFT", "Left Eye"
        BOTH = "BOTH", "Both Eyes"
        NOT_APPLICABLE = (
            "NOT_APPLICABLE",
            "Not Applicable",
        )

    class ReviewStatus(models.TextChoices):
        PENDING = "PENDING", "Pending Review"
        REVIEWED = "REVIEWED", "Reviewed"
        NEEDS_ATTENTION = (
            "NEEDS_ATTENTION",
            "Needs Attention",
        )

    patient = models.ForeignKey(
        Patient,
        on_delete=models.CASCADE,
        related_name="clinical_attachments",
    )

    visit = models.ForeignKey(
        PatientVisit,
        on_delete=models.CASCADE,
        related_name="clinical_attachments",
    )

    category = models.CharField(
        max_length=40,
        choices=Category.choices,
    )

    category_other = models.CharField(
        max_length=150,
        blank=True,
        verbose_name="Other Category",
    )

    eye_side = models.CharField(
        max_length=20,
        choices=EyeSide.choices,
        default=EyeSide.NOT_APPLICABLE,
    )

    title = models.CharField(
        max_length=200,
        verbose_name="File Title",
    )

    description = models.TextField(
        blank=True,
        verbose_name="Comment / Description",
    )

    investigation_date = models.DateField(
        blank=True,
        null=True,
        verbose_name="Investigation Date",
    )

    attachment_file = models.FileField(
        upload_to=clinical_attachment_upload_path,
        validators=[
            FileExtensionValidator(
                allowed_extensions=[
                    "jpg",
                    "jpeg",
                    "png",
                    "pdf",
                    "doc",
                    "docx",
                ]
            )
        ],
        verbose_name="Clinical File",
    )

    original_filename = models.CharField(
        max_length=255,
        blank=True,
        editable=False,
    )

    file_extension = models.CharField(
        max_length=20,
        blank=True,
        editable=False,
    )

    file_size = models.PositiveBigIntegerField(
        default=0,
        editable=False,
        help_text="File size in bytes.",
    )

    uploaded_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="uploaded_clinical_attachments",
    )

    uploaded_at = models.DateTimeField(
        auto_now_add=True,
    )

    updated_at = models.DateTimeField(
        auto_now=True,
    )

    review_status = models.CharField(
        max_length=30,
        choices=ReviewStatus.choices,
        default=ReviewStatus.PENDING,
    )

    reviewed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="reviewed_clinical_attachments",
    )

    reviewed_at = models.DateTimeField(
        blank=True,
        null=True,
    )

    review_notes = models.TextField(
        blank=True,
    )

    is_active = models.BooleanField(
        default=True,
        help_text=(
            "Inactive attachments remain recorded for audit purposes "
            "but are hidden from normal clinical lists."
        ),
    )

    class Meta:
        ordering = [
            "-investigation_date",
            "-uploaded_at",
        ]

        indexes = [
            models.Index(
                fields=["patient", "uploaded_at"],
                name="clinical_att_patient_date_idx",
            ),
            models.Index(
                fields=["visit", "category"],
                name="clinical_att_visit_cat_idx",
            ),
            models.Index(
                fields=["review_status"],
                name="clinical_att_review_idx",
            ),
            models.Index(
                fields=["is_active"],
                name="clinical_att_active_idx",
            ),
        ]

        verbose_name = "Clinical Attachment"
        verbose_name_plural = "Clinical Attachments"

    def __str__(self):
        return (
            f"{self.title} - "
            f"{self.patient.file_number} - "
            f"{self.visit.visit_number}"
        )

    @property
    def file_size_display(self):
        """
        Return a readable file size.
        """

        size = self.file_size or 0

        if size < 1024:
            return f"{size} bytes"

        if size < 1024 * 1024:
            return f"{size / 1024:.1f} KB"

        return f"{size / (1024 * 1024):.1f} MB"

    @property
    def is_image(self):
        return self.file_extension.lower() in {
            ".jpg",
            ".jpeg",
            ".png",
        }

    @property
    def is_pdf(self):
        return self.file_extension.lower() == ".pdf"

    def save(self, *args, **kwargs):
        """
        Capture non-editable file metadata and maintain review
        timestamps safely.
        """

        if self.attachment_file:
            uploaded_name = os.path.basename(
                self.attachment_file.name
            )

            # Preserve the original name only when it has not already
            # been captured. This avoids replacing it with the generated
            # storage name during later updates.
            if not self.original_filename:
                self.original_filename = uploaded_name[:255]

            extension = os.path.splitext(uploaded_name)[1].lower()
            self.file_extension = extension[:20]

            try:
                self.file_size = self.attachment_file.size
            except (OSError, ValueError, AttributeError):
                if not self.file_size:
                    self.file_size = 0

        if (
            self.review_status == self.ReviewStatus.REVIEWED
            and self.reviewed_at is None
        ):
            self.reviewed_at = timezone.now()

        if self.review_status == self.ReviewStatus.PENDING:
            self.reviewed_by = None
            self.reviewed_at = None

        super().save(*args, **kwargs)


class ClinicalImageAnnotation(models.Model):
    """
    Stores non-destructive vector annotations for a clinical image.

    The original investigation image is never modified. Drawing
    instructions are stored as normalized JSON coordinates so they
    remain correctly positioned on different screen sizes.
    """

    class AnnotationStatus(models.TextChoices):
        DRAFT = "DRAFT", "Draft"
        FINAL = "FINAL", "Finalized"

    attachment = models.ForeignKey(
        ClinicalAttachment,
        on_delete=models.CASCADE,
        related_name="image_annotations",
    )

    title = models.CharField(
        max_length=200,
        default="Clinical Annotation",
    )

    clinical_note = models.TextField(
        blank=True,
        verbose_name="Clinical Annotation Note",
    )

    annotation_data = models.JSONField(
        default=dict,
        blank=True,
        help_text=(
            "Normalized vector drawing instructions. "
            "The original clinical image remains unchanged."
        ),
    )

    status = models.CharField(
        max_length=20,
        choices=AnnotationStatus.choices,
        default=AnnotationStatus.DRAFT,
    )

    version = models.PositiveIntegerField(
        default=1,
    )

    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="created_clinical_annotations",
    )

    updated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="updated_clinical_annotations",
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
    )

    updated_at = models.DateTimeField(
        auto_now=True,
    )

    finalized_at = models.DateTimeField(
        null=True,
        blank=True,
    )

    is_active = models.BooleanField(
        default=True,
    )

    class Meta:
        ordering = [
            "-updated_at",
            "-pk",
        ]

        indexes = [
            models.Index(
                fields=[
                    "attachment",
                    "is_active",
                ],
                name="img_ann_attach_active_idx",
            ),
            models.Index(
                fields=[
                    "status",
                    "updated_at",
                ],
                name="img_ann_status_date_idx",
            ),
        ]

        verbose_name = "Clinical Image Annotation"
        verbose_name_plural = "Clinical Image Annotations"

    def __str__(self):
        return (
            f"{self.title} — "
            f"{self.attachment.title}"
        )

    def save(self, *args, **kwargs):
        if (
            self.status == self.AnnotationStatus.FINAL
            and self.finalized_at is None
        ):
            self.finalized_at = timezone.now()

        if self.status == self.AnnotationStatus.DRAFT:
            self.finalized_at = None

        super().save(*args, **kwargs)


class ContactLensAssessment(models.Model):
    """
    Stores the principal contact-lens suitability assessment for a
    patient visit.

    The assessment remains separate from EyeExamination so it can be
    completed, reviewed and followed up independently without changing
    the original ophthalmology examination.
    """

    class LensPurpose(models.TextChoices):
        DISTANCE = "DISTANCE", "Distance Correction"
        NEAR = "NEAR", "Near Correction"
        MULTIFOCAL = "MULTIFOCAL", "Multifocal Correction"
        TORIC = "TORIC", "Astigmatism / Toric Correction"
        COSMETIC = "COSMETIC", "Cosmetic / Coloured Lens"
        THERAPEUTIC = "THERAPEUTIC", "Therapeutic / Bandage Lens"
        ORTHOKERATOLOGY = (
            "ORTHOKERATOLOGY",
            "Orthokeratology",
        )
        MYOPIA_CONTROL = (
            "MYOPIA_CONTROL",
            "Myopia Control",
        )
        APHAKIC = "APHAKIC", "Aphakic Correction"
        PROSTHETIC = "PROSTHETIC", "Prosthetic Lens"
        OTHER = "OTHER", "Others (Specify)"

    class WearingExperience(models.TextChoices):
        NEVER = "NEVER", "Never Worn Contact Lenses"
        PREVIOUS = "PREVIOUS", "Previous Wearer"
        CURRENT = "CURRENT", "Current Wearer"
        DISCONTINUED = (
            "DISCONTINUED",
            "Previously Discontinued",
        )

    class SuitabilityStatus(models.TextChoices):
        PENDING = "PENDING", "Assessment Pending"
        SUITABLE = "SUITABLE", "Suitable"
        SUITABLE_WITH_CAUTION = (
            "SUITABLE_WITH_CAUTION",
            "Suitable With Caution",
        )
        TEMPORARILY_UNSUITABLE = (
            "TEMPORARILY_UNSUITABLE",
            "Temporarily Unsuitable",
        )
        UNSUITABLE = "UNSUITABLE", "Unsuitable"

    class TearFilmStatus(models.TextChoices):
        NORMAL = "NORMAL", "Normal"
        BORDERLINE = "BORDERLINE", "Borderline"
        REDUCED = "REDUCED", "Reduced"
        SEVERE_DRY_EYE = (
            "SEVERE_DRY_EYE",
            "Severe Dry Eye",
        )
        NOT_ASSESSED = (
            "NOT_ASSESSED",
            "Not Assessed",
        )

    class CornealStatus(models.TextChoices):
        CLEAR = "CLEAR", "Clear / Normal"
        SCAR = "SCAR", "Corneal Scar"
        ECTASIA = "ECTASIA", "Corneal Ectasia"
        KERATOCONUS = "KERATOCONUS", "Keratoconus"
        EDEMA = "EDEMA", "Corneal Oedema"
        DYSTROPHY = "DYSTROPHY", "Corneal Dystrophy"
        IRREGULAR = "IRREGULAR", "Irregular Cornea"
        OTHER = "OTHER", "Others (Specify)"

    class HygieneAssessment(models.TextChoices):
        GOOD = "GOOD", "Good"
        ACCEPTABLE = "ACCEPTABLE", "Acceptable"
        NEEDS_EDUCATION = (
            "NEEDS_EDUCATION",
            "Needs Additional Education",
        )
        POOR = "POOR", "Poor"

    patient = models.ForeignKey(
        Patient,
        on_delete=models.CASCADE,
        related_name="contact_lens_assessments",
    )

    visit = models.OneToOneField(
        PatientVisit,
        on_delete=models.CASCADE,
        related_name="contact_lens_assessment",
    )

    eye_examination = models.ForeignKey(
        EyeExamination,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="contact_lens_assessments",
        help_text=(
            "Optional Eye Examination record used as the clinical "
            "basis for this assessment."
        ),
    )

    assessment_date = models.DateTimeField(
        default=timezone.now,
    )

    assessed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="contact_lens_assessments_completed",
    )

    lens_purpose = models.CharField(
        max_length=30,
        choices=LensPurpose.choices,
        blank=True,
    )

    lens_purpose_other = models.CharField(
        max_length=150,
        blank=True,
        verbose_name="Other Lens Purpose",
    )

    wearing_experience = models.CharField(
        max_length=20,
        choices=WearingExperience.choices,
        default=WearingExperience.NEVER,
    )

    previous_lens_brand = models.CharField(
        max_length=150,
        blank=True,
    )

    previous_lens_type = models.CharField(
        max_length=150,
        blank=True,
    )

    previous_wearing_schedule = models.CharField(
        max_length=150,
        blank=True,
    )

    previous_lens_problems = models.TextField(
        blank=True,
        help_text=(
            "Record discomfort, redness, infection, poor vision, "
            "handling problems or other previous complications."
        ),
    )

    occupation = models.CharField(
        max_length=150,
        blank=True,
    )

    environmental_exposure = models.TextField(
        blank=True,
        help_text=(
            "Record dust, smoke, air-conditioning, chemical exposure, "
            "screen use or other relevant environmental factors."
        ),
    )

    average_daily_wear_hours_requested = models.DecimalField(
        max_digits=4,
        decimal_places=1,
        null=True,
        blank=True,
        validators=[
            MinValueValidator(Decimal("0.0")),
            MaxValueValidator(Decimal("24.0")),
        ],
    )

    allergies = models.TextField(
        blank=True,
    )

    systemic_conditions = models.TextField(
        blank=True,
    )

    current_medications = models.TextField(
        blank=True,
    )

    ocular_history = models.TextField(
        blank=True,
    )

    previous_contact_lens_infection = models.BooleanField(
        default=False,
    )

    previous_contact_lens_infection_details = models.TextField(
        blank=True,
    )

    right_horizontal_visible_iris_diameter = models.DecimalField(
        max_digits=4,
        decimal_places=1,
        null=True,
        blank=True,
        verbose_name="Right HVID (mm)",
        validators=[
            MinValueValidator(Decimal("8.0")),
            MaxValueValidator(Decimal("15.0")),
        ],
    )

    left_horizontal_visible_iris_diameter = models.DecimalField(
        max_digits=4,
        decimal_places=1,
        null=True,
        blank=True,
        verbose_name="Left HVID (mm)",
        validators=[
            MinValueValidator(Decimal("8.0")),
            MaxValueValidator(Decimal("15.0")),
        ],
    )

    right_pupil_diameter = models.DecimalField(
        max_digits=4,
        decimal_places=1,
        null=True,
        blank=True,
        verbose_name="Right Pupil Diameter (mm)",
        validators=[
            MinValueValidator(Decimal("1.0")),
            MaxValueValidator(Decimal("12.0")),
        ],
    )

    left_pupil_diameter = models.DecimalField(
        max_digits=4,
        decimal_places=1,
        null=True,
        blank=True,
        verbose_name="Left Pupil Diameter (mm)",
        validators=[
            MinValueValidator(Decimal("1.0")),
            MaxValueValidator(Decimal("12.0")),
        ],
    )

    right_palpebral_aperture = models.DecimalField(
        max_digits=4,
        decimal_places=1,
        null=True,
        blank=True,
        verbose_name="Right Palpebral Aperture (mm)",
        validators=[
            MinValueValidator(Decimal("3.0")),
            MaxValueValidator(Decimal("20.0")),
        ],
    )

    left_palpebral_aperture = models.DecimalField(
        max_digits=4,
        decimal_places=1,
        null=True,
        blank=True,
        verbose_name="Left Palpebral Aperture (mm)",
        validators=[
            MinValueValidator(Decimal("3.0")),
            MaxValueValidator(Decimal("20.0")),
        ],
    )

    right_k1 = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name="Right K1 (D)",
        validators=[
            MinValueValidator(Decimal("30.00")),
            MaxValueValidator(Decimal("60.00")),
        ],
    )

    right_k1_axis = models.PositiveSmallIntegerField(
        null=True,
        blank=True,
        verbose_name="Right K1 Axis",
        validators=[
            MinValueValidator(0),
            MaxValueValidator(180),
        ],
    )

    right_k2 = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name="Right K2 (D)",
        validators=[
            MinValueValidator(Decimal("30.00")),
            MaxValueValidator(Decimal("60.00")),
        ],
    )

    right_k2_axis = models.PositiveSmallIntegerField(
        null=True,
        blank=True,
        verbose_name="Right K2 Axis",
        validators=[
            MinValueValidator(0),
            MaxValueValidator(180),
        ],
    )

    left_k1 = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name="Left K1 (D)",
        validators=[
            MinValueValidator(Decimal("30.00")),
            MaxValueValidator(Decimal("60.00")),
        ],
    )

    left_k1_axis = models.PositiveSmallIntegerField(
        null=True,
        blank=True,
        verbose_name="Left K1 Axis",
        validators=[
            MinValueValidator(0),
            MaxValueValidator(180),
        ],
    )

    left_k2 = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name="Left K2 (D)",
        validators=[
            MinValueValidator(Decimal("30.00")),
            MaxValueValidator(Decimal("60.00")),
        ],
    )

    left_k2_axis = models.PositiveSmallIntegerField(
        null=True,
        blank=True,
        verbose_name="Left K2 Axis",
        validators=[
            MinValueValidator(0),
            MaxValueValidator(180),
        ],
    )

    tear_film_status = models.CharField(
        max_length=30,
        choices=TearFilmStatus.choices,
        default=TearFilmStatus.NOT_ASSESSED,
    )

    tear_break_up_time_right = models.DecimalField(
        max_digits=4,
        decimal_places=1,
        null=True,
        blank=True,
        verbose_name="Right TBUT (seconds)",
        validators=[
            MinValueValidator(Decimal("0.0")),
            MaxValueValidator(Decimal("60.0")),
        ],
    )

    tear_break_up_time_left = models.DecimalField(
        max_digits=4,
        decimal_places=1,
        null=True,
        blank=True,
        verbose_name="Left TBUT (seconds)",
        validators=[
            MinValueValidator(Decimal("0.0")),
            MaxValueValidator(Decimal("60.0")),
        ],
    )

    schirmer_right = models.DecimalField(
        max_digits=5,
        decimal_places=1,
        null=True,
        blank=True,
        verbose_name="Right Schirmer Test (mm)",
        validators=[
            MinValueValidator(Decimal("0.0")),
            MaxValueValidator(Decimal("50.0")),
        ],
    )

    schirmer_left = models.DecimalField(
        max_digits=5,
        decimal_places=1,
        null=True,
        blank=True,
        verbose_name="Left Schirmer Test (mm)",
        validators=[
            MinValueValidator(Decimal("0.0")),
            MaxValueValidator(Decimal("50.0")),
        ],
    )

    corneal_status = models.CharField(
        max_length=30,
        choices=CornealStatus.choices,
        default=CornealStatus.CLEAR,
    )

    corneal_status_other = models.CharField(
        max_length=150,
        blank=True,
    )

    right_cornea_notes = models.TextField(
        blank=True,
    )

    left_cornea_notes = models.TextField(
        blank=True,
    )

    right_lid_notes = models.TextField(
        blank=True,
    )

    left_lid_notes = models.TextField(
        blank=True,
    )

    conjunctival_findings = models.TextField(
        blank=True,
    )

    hygiene_assessment = models.CharField(
        max_length=30,
        choices=HygieneAssessment.choices,
        default=HygieneAssessment.ACCEPTABLE,
    )

    handling_ability = models.CharField(
        max_length=150,
        blank=True,
    )

    motivation_and_expectations = models.TextField(
        blank=True,
    )

    contraindications = models.TextField(
        blank=True,
    )

    suitability_status = models.CharField(
        max_length=40,
        choices=SuitabilityStatus.choices,
        default=SuitabilityStatus.PENDING,
    )

    suitability_reason = models.TextField(
        blank=True,
    )

    assessment_notes = models.TextField(
        blank=True,
    )

    patient_education_provided = models.BooleanField(
        default=False,
    )

    patient_education_notes = models.TextField(
        blank=True,
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
    )

    updated_at = models.DateTimeField(
        auto_now=True,
    )

    class Meta:
        ordering = [
            "-assessment_date",
            "-pk",
        ]

        indexes = [
            models.Index(
                fields=["patient", "assessment_date"],
                name="cl_assess_patient_date_idx",
            ),
            models.Index(
                fields=["suitability_status"],
                name="cl_assess_suitability_idx",
            ),
        ]

        verbose_name = "Contact Lens Assessment"
        verbose_name_plural = "Contact Lens Assessments"

    def __str__(self):
        return (
            f"Contact Lens Assessment — "
            f"{self.patient.file_number} — "
            f"{self.visit.visit_number}"
        )

    def save(self, *args, **kwargs):
        if self.visit_id:
            self.patient = self.visit.patient

        super().save(*args, **kwargs)


class ContactLensTrial(models.Model):
    """
    Stores each trial lens fitted during a contact-lens assessment.

    Several trial records may belong to one assessment.
    """

    class EyeSide(models.TextChoices):
        RIGHT = "RIGHT", "Right Eye"
        LEFT = "LEFT", "Left Eye"

    class LensDesign(models.TextChoices):
        SPHERICAL = "SPHERICAL", "Spherical Soft Lens"
        TORIC = "TORIC", "Toric Soft Lens"
        MULTIFOCAL = "MULTIFOCAL", "Multifocal Soft Lens"
        RGP = "RGP", "Rigid Gas Permeable"
        SCLERAL = "SCLERAL", "Scleral Lens"
        HYBRID = "HYBRID", "Hybrid Lens"
        ORTHOKERATOLOGY = (
            "ORTHOKERATOLOGY",
            "Orthokeratology Lens",
        )
        BANDAGE = "BANDAGE", "Bandage / Therapeutic Lens"
        COSMETIC = "COSMETIC", "Cosmetic / Coloured Lens"
        PROSTHETIC = "PROSTHETIC", "Prosthetic Lens"
        OTHER = "OTHER", "Others (Specify)"

    class MovementAssessment(models.TextChoices):
        INSUFFICIENT = "INSUFFICIENT", "Insufficient Movement"
        ACCEPTABLE = "ACCEPTABLE", "Acceptable Movement"
        EXCESSIVE = "EXCESSIVE", "Excessive Movement"
        NOT_ASSESSED = "NOT_ASSESSED", "Not Assessed"

    class CentrationAssessment(models.TextChoices):
        CENTRAL = "CENTRAL", "Central"
        SLIGHT_DECENTRATION = (
            "SLIGHT_DECENTRATION",
            "Slight Decentration",
        )
        SIGNIFICANT_DECENTRATION = (
            "SIGNIFICANT_DECENTRATION",
            "Significant Decentration",
        )
        NOT_ASSESSED = "NOT_ASSESSED", "Not Assessed"

    class FitAssessment(models.TextChoices):
        OPTIMAL = "OPTIMAL", "Optimal Fit"
        ACCEPTABLE = "ACCEPTABLE", "Acceptable Fit"
        TIGHT = "TIGHT", "Tight Fit"
        LOOSE = "LOOSE", "Loose Fit"
        STEEP = "STEEP", "Steep Fit"
        FLAT = "FLAT", "Flat Fit"
        UNACCEPTABLE = "UNACCEPTABLE", "Unacceptable Fit"

    assessment = models.ForeignKey(
        ContactLensAssessment,
        on_delete=models.CASCADE,
        related_name="trial_lenses",
    )

    eye_side = models.CharField(
        max_length=10,
        choices=EyeSide.choices,
    )

    trial_number = models.PositiveSmallIntegerField(
        default=1,
    )

    trial_date = models.DateTimeField(
        default=timezone.now,
    )

    lens_design = models.CharField(
        max_length=30,
        choices=LensDesign.choices,
    )

    lens_design_other = models.CharField(
        max_length=150,
        blank=True,
    )

    manufacturer = models.CharField(
        max_length=150,
        blank=True,
    )

    brand_name = models.CharField(
        max_length=150,
        blank=True,
    )

    material = models.CharField(
        max_length=150,
        blank=True,
    )

    base_curve = models.DecimalField(
        max_digits=4,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name="Base Curve (mm)",
        validators=[
            MinValueValidator(Decimal("5.00")),
            MaxValueValidator(Decimal("12.00")),
        ],
    )

    diameter = models.DecimalField(
        max_digits=4,
        decimal_places=1,
        null=True,
        blank=True,
        verbose_name="Diameter (mm)",
        validators=[
            MinValueValidator(Decimal("7.0")),
            MaxValueValidator(Decimal("25.0")),
        ],
    )

    sphere = models.DecimalField(
        max_digits=6,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name="Sphere (D)",
        validators=[
            MinValueValidator(Decimal("-40.00")),
            MaxValueValidator(Decimal("40.00")),
        ],
    )

    cylinder = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name="Cylinder (D)",
        validators=[
            MinValueValidator(Decimal("-15.00")),
            MaxValueValidator(Decimal("15.00")),
        ],
    )

    axis = models.PositiveSmallIntegerField(
        null=True,
        blank=True,
        validators=[
            MinValueValidator(0),
            MaxValueValidator(180),
        ],
    )

    add_power = models.DecimalField(
        max_digits=4,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name="Add Power (D)",
        validators=[
            MinValueValidator(Decimal("0.00")),
            MaxValueValidator(Decimal("6.00")),
        ],
    )

    peripheral_curve = models.CharField(
        max_length=100,
        blank=True,
    )

    optical_zone = models.DecimalField(
        max_digits=4,
        decimal_places=1,
        null=True,
        blank=True,
        verbose_name="Optical Zone (mm)",
    )

    sagittal_depth = models.DecimalField(
        max_digits=6,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name="Sagittal Depth (microns)",
    )

    tint_or_colour = models.CharField(
        max_length=100,
        blank=True,
    )

    right_or_left_visual_acuity = models.CharField(
        max_length=50,
        blank=True,
        verbose_name="Visual Acuity With Trial Lens",
    )

    over_refraction_sphere = models.DecimalField(
        max_digits=6,
        decimal_places=2,
        null=True,
        blank=True,
        validators=[
            MinValueValidator(Decimal("-20.00")),
            MaxValueValidator(Decimal("20.00")),
        ],
    )

    over_refraction_cylinder = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        null=True,
        blank=True,
        validators=[
            MinValueValidator(Decimal("-10.00")),
            MaxValueValidator(Decimal("10.00")),
        ],
    )

    over_refraction_axis = models.PositiveSmallIntegerField(
        null=True,
        blank=True,
        validators=[
            MinValueValidator(0),
            MaxValueValidator(180),
        ],
    )

    final_visual_acuity = models.CharField(
        max_length=50,
        blank=True,
    )

    centration = models.CharField(
        max_length=30,
        choices=CentrationAssessment.choices,
        default=CentrationAssessment.NOT_ASSESSED,
    )

    movement = models.CharField(
        max_length=30,
        choices=MovementAssessment.choices,
        default=MovementAssessment.NOT_ASSESSED,
    )

    fit_assessment = models.CharField(
        max_length=30,
        choices=FitAssessment.choices,
        default=FitAssessment.ACCEPTABLE,
    )

    rotation_degrees = models.SmallIntegerField(
        null=True,
        blank=True,
        verbose_name="Toric Rotation (degrees)",
        validators=[
            MinValueValidator(-180),
            MaxValueValidator(180),
        ],
    )

    push_up_test = models.CharField(
        max_length=150,
        blank=True,
    )

    fluorescein_pattern = models.TextField(
        blank=True,
    )

    comfort_score = models.PositiveSmallIntegerField(
        null=True,
        blank=True,
        validators=[
            MinValueValidator(0),
            MaxValueValidator(10),
        ],
        help_text="Patient-reported comfort score from 0 to 10.",
    )

    fit_notes = models.TextField(
        blank=True,
    )

    accepted_for_prescription = models.BooleanField(
        default=False,
    )

    fitted_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="contact_lens_trials_fitted",
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
    )

    updated_at = models.DateTimeField(
        auto_now=True,
    )

    class Meta:
        ordering = [
            "eye_side",
            "trial_number",
            "pk",
        ]

        constraints = [
            models.UniqueConstraint(
                fields=[
                    "assessment",
                    "eye_side",
                    "trial_number",
                ],
                name="unique_cl_trial_eye_number",
            ),
        ]

        indexes = [
            models.Index(
                fields=[
                    "assessment",
                    "eye_side",
                ],
                name="cl_trial_assess_eye_idx",
            ),
            models.Index(
                fields=["accepted_for_prescription"],
                name="cl_trial_accepted_idx",
            ),
        ]

        verbose_name = "Contact Lens Trial"
        verbose_name_plural = "Contact Lens Trials"

    def __str__(self):
        return (
            f"Trial {self.trial_number} — "
            f"{self.get_eye_side_display()} — "
            f"{self.assessment.patient.file_number}"
        )


class ContactLensPrescription(models.Model):
    """
    Stores the final contact-lens prescription resulting from an
    assessment and its accepted trial lenses.

    Every new prescription is a new historical record. Existing
    prescriptions are not overwritten.
    """

    class PrescriptionStatus(models.TextChoices):
        DRAFT = "DRAFT", "Draft"
        PENDING_APPROVAL = (
            "PENDING_APPROVAL",
            "Pending Approval",
        )
        APPROVED = "APPROVED", "Approved"
        DISPENSED = "DISPENSED", "Dispensed"
        EXPIRED = "EXPIRED", "Expired"
        CANCELLED = "CANCELLED", "Cancelled"

    class LensDesign(models.TextChoices):
        SPHERICAL = "SPHERICAL", "Spherical Soft Lens"
        TORIC = "TORIC", "Toric Soft Lens"
        MULTIFOCAL = "MULTIFOCAL", "Multifocal Soft Lens"
        RGP = "RGP", "Rigid Gas Permeable"
        SCLERAL = "SCLERAL", "Scleral Lens"
        HYBRID = "HYBRID", "Hybrid Lens"
        ORTHOKERATOLOGY = (
            "ORTHOKERATOLOGY",
            "Orthokeratology Lens",
        )
        BANDAGE = "BANDAGE", "Bandage / Therapeutic Lens"
        COSMETIC = "COSMETIC", "Cosmetic / Coloured Lens"
        PROSTHETIC = "PROSTHETIC", "Prosthetic Lens"
        OTHER = "OTHER", "Others (Specify)"

    class ReplacementSchedule(models.TextChoices):
        DAILY = "DAILY", "Daily Disposable"
        TWO_WEEKLY = "TWO_WEEKLY", "Two-Weekly"
        MONTHLY = "MONTHLY", "Monthly"
        QUARTERLY = "QUARTERLY", "Three-Monthly"
        SIX_MONTHLY = "SIX_MONTHLY", "Six-Monthly"
        ANNUAL = "ANNUAL", "Annual"
        CONVENTIONAL = "CONVENTIONAL", "Conventional"
        AS_DIRECTED = "AS_DIRECTED", "As Directed"
        OTHER = "OTHER", "Others (Specify)"

    class WearingSchedule(models.TextChoices):
        DAILY_WEAR = "DAILY_WEAR", "Daily Wear"
        EXTENDED_WEAR = "EXTENDED_WEAR", "Extended Wear"
        OCCASIONAL = "OCCASIONAL", "Occasional Wear"
        NIGHT_WEAR = "NIGHT_WEAR", "Night Wear"
        THERAPEUTIC = "THERAPEUTIC", "Therapeutic Wear"
        AS_DIRECTED = "AS_DIRECTED", "As Directed"

    assessment = models.ForeignKey(
        ContactLensAssessment,
        on_delete=models.PROTECT,
        related_name="prescriptions",
    )

    patient = models.ForeignKey(
        Patient,
        on_delete=models.CASCADE,
        related_name="contact_lens_prescriptions",
    )

    visit = models.ForeignKey(
        PatientVisit,
        on_delete=models.PROTECT,
        related_name="contact_lens_prescriptions",
    )

    prescription_number = models.CharField(
        max_length=40,
        unique=True,
        editable=False,
    )

    version = models.PositiveIntegerField(
        default=1,
    )

    prescription_date = models.DateField(
        default=timezone.localdate,
    )

    valid_until = models.DateField(
        null=True,
        blank=True,
    )

    status = models.CharField(
        max_length=30,
        choices=PrescriptionStatus.choices,
        default=PrescriptionStatus.DRAFT,
    )

    right_lens_design = models.CharField(
        max_length=30,
        choices=LensDesign.choices,
        blank=True,
    )

    right_lens_design_other = models.CharField(
        max_length=150,
        blank=True,
    )

    right_manufacturer = models.CharField(
        max_length=150,
        blank=True,
    )

    right_brand_name = models.CharField(
        max_length=150,
        blank=True,
    )

    right_material = models.CharField(
        max_length=150,
        blank=True,
    )

    right_base_curve = models.DecimalField(
        max_digits=4,
        decimal_places=2,
        null=True,
        blank=True,
        validators=[
            MinValueValidator(Decimal("5.00")),
            MaxValueValidator(Decimal("12.00")),
        ],
    )

    right_diameter = models.DecimalField(
        max_digits=4,
        decimal_places=1,
        null=True,
        blank=True,
        validators=[
            MinValueValidator(Decimal("7.0")),
            MaxValueValidator(Decimal("25.0")),
        ],
    )

    right_sphere = models.DecimalField(
        max_digits=6,
        decimal_places=2,
        null=True,
        blank=True,
    )

    right_cylinder = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        null=True,
        blank=True,
    )

    right_axis = models.PositiveSmallIntegerField(
        null=True,
        blank=True,
        validators=[
            MinValueValidator(0),
            MaxValueValidator(180),
        ],
    )

    right_add_power = models.DecimalField(
        max_digits=4,
        decimal_places=2,
        null=True,
        blank=True,
    )

    right_colour = models.CharField(
        max_length=100,
        blank=True,
    )

    left_lens_design = models.CharField(
        max_length=30,
        choices=LensDesign.choices,
        blank=True,
    )

    left_lens_design_other = models.CharField(
        max_length=150,
        blank=True,
    )

    left_manufacturer = models.CharField(
        max_length=150,
        blank=True,
    )

    left_brand_name = models.CharField(
        max_length=150,
        blank=True,
    )

    left_material = models.CharField(
        max_length=150,
        blank=True,
    )

    left_base_curve = models.DecimalField(
        max_digits=4,
        decimal_places=2,
        null=True,
        blank=True,
        validators=[
            MinValueValidator(Decimal("5.00")),
            MaxValueValidator(Decimal("12.00")),
        ],
    )

    left_diameter = models.DecimalField(
        max_digits=4,
        decimal_places=1,
        null=True,
        blank=True,
        validators=[
            MinValueValidator(Decimal("7.0")),
            MaxValueValidator(Decimal("25.0")),
        ],
    )

    left_sphere = models.DecimalField(
        max_digits=6,
        decimal_places=2,
        null=True,
        blank=True,
    )

    left_cylinder = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        null=True,
        blank=True,
    )

    left_axis = models.PositiveSmallIntegerField(
        null=True,
        blank=True,
        validators=[
            MinValueValidator(0),
            MaxValueValidator(180),
        ],
    )

    left_add_power = models.DecimalField(
        max_digits=4,
        decimal_places=2,
        null=True,
        blank=True,
    )

    left_colour = models.CharField(
        max_length=100,
        blank=True,
    )

    replacement_schedule = models.CharField(
        max_length=30,
        choices=ReplacementSchedule.choices,
        default=ReplacementSchedule.MONTHLY,
    )

    replacement_schedule_other = models.CharField(
        max_length=150,
        blank=True,
    )

    wearing_schedule = models.CharField(
        max_length=30,
        choices=WearingSchedule.choices,
        default=WearingSchedule.DAILY_WEAR,
    )

    maximum_daily_wear_hours = models.DecimalField(
        max_digits=4,
        decimal_places=1,
        null=True,
        blank=True,
        validators=[
            MinValueValidator(Decimal("0.0")),
            MaxValueValidator(Decimal("24.0")),
        ],
    )

    cleaning_solution = models.CharField(
        max_length=200,
        blank=True,
    )

    cleaning_instructions = models.TextField(
        blank=True,
    )

    insertion_removal_training_completed = models.BooleanField(
        default=False,
    )

    hygiene_training_completed = models.BooleanField(
        default=False,
    )

    emergency_warning_signs_explained = models.BooleanField(
        default=False,
    )

    clinical_notes = models.TextField(
        blank=True,
    )

    dispensing_instructions = models.TextField(
        blank=True,
    )

    prescribed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="contact_lens_prescriptions_created",
    )

    approved_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="contact_lens_prescriptions_approved",
    )

    approved_at = models.DateTimeField(
        null=True,
        blank=True,
    )

    dispensed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="contact_lens_prescriptions_dispensed",
    )

    dispensed_at = models.DateTimeField(
        null=True,
        blank=True,
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
    )

    updated_at = models.DateTimeField(
        auto_now=True,
    )

    is_active = models.BooleanField(
        default=True,
    )

    class Meta:
        ordering = [
            "-prescription_date",
            "-pk",
        ]

        indexes = [
            models.Index(
                fields=["patient", "prescription_date"],
                name="cl_rx_patient_date_idx",
            ),
            models.Index(
                fields=["status"],
                name="cl_rx_status_idx",
            ),
            models.Index(
                fields=["is_active"],
                name="cl_rx_active_idx",
            ),
        ]

        verbose_name = "Contact Lens Prescription"
        verbose_name_plural = "Contact Lens Prescriptions"

    def __str__(self):
        return (
            f"{self.prescription_number} — "
            f"{self.patient.file_number}"
        )

    def save(self, *args, **kwargs):
        if self.visit_id:
            self.patient = self.visit.patient

        if not self.prescription_number:
            year = timezone.localdate().year

            last_prescription = (
                ContactLensPrescription.objects
                .filter(
                    prescription_number__startswith=(
                        f"CL-{year}-"
                    )
                )
                .order_by("-pk")
                .first()
            )

            next_number = 1

            if last_prescription:
                try:
                    next_number = (
                        int(
                            last_prescription
                            .prescription_number
                            .split("-")[-1]
                        )
                        + 1
                    )
                except (TypeError, ValueError):
                    next_number = (
                        last_prescription.pk + 1
                    )

            self.prescription_number = (
                f"CL-{year}-{next_number:05d}"
            )

        if (
            self.status
            == self.PrescriptionStatus.APPROVED
            and self.approved_at is None
        ):
            self.approved_at = timezone.now()

        if (
            self.status
            not in {
                self.PrescriptionStatus.APPROVED,
                self.PrescriptionStatus.DISPENSED,
            }
        ):
            self.approved_at = None
            self.approved_by = None

        super().save(*args, **kwargs)


class ContactLensFollowUp(models.Model):
    """
    Stores scheduled and completed follow-up reviews for a contact-lens
    prescription.
    """

    class FollowUpStatus(models.TextChoices):
        SCHEDULED = "SCHEDULED", "Scheduled"
        COMPLETED = "COMPLETED", "Completed"
        MISSED = "MISSED", "Missed"
        CANCELLED = "CANCELLED", "Cancelled"

    class LensCondition(models.TextChoices):
        GOOD = "GOOD", "Good"
        DEPOSITS = "DEPOSITS", "Deposits Present"
        DAMAGED = "DAMAGED", "Damaged"
        POOR_HYGIENE = "POOR_HYGIENE", "Poor Hygiene"
        REPLACEMENT_REQUIRED = (
            "REPLACEMENT_REQUIRED",
            "Replacement Required",
        )
        NOT_ASSESSED = "NOT_ASSESSED", "Not Assessed"

    prescription = models.ForeignKey(
        ContactLensPrescription,
        on_delete=models.CASCADE,
        related_name="follow_ups",
    )

    patient = models.ForeignKey(
        Patient,
        on_delete=models.CASCADE,
        related_name="contact_lens_follow_ups",
    )

    follow_up_date = models.DateTimeField()

    status = models.CharField(
        max_length=20,
        choices=FollowUpStatus.choices,
        default=FollowUpStatus.SCHEDULED,
    )

    attended_at = models.DateTimeField(
        null=True,
        blank=True,
    )

    reviewed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="contact_lens_follow_ups_reviewed",
    )

    wearing_time_per_day = models.DecimalField(
        max_digits=4,
        decimal_places=1,
        null=True,
        blank=True,
        validators=[
            MinValueValidator(Decimal("0.0")),
            MaxValueValidator(Decimal("24.0")),
        ],
    )

    comfort_score_right = models.PositiveSmallIntegerField(
        null=True,
        blank=True,
        validators=[
            MinValueValidator(0),
            MaxValueValidator(10),
        ],
    )

    comfort_score_left = models.PositiveSmallIntegerField(
        null=True,
        blank=True,
        validators=[
            MinValueValidator(0),
            MaxValueValidator(10),
        ],
    )

    right_visual_acuity = models.CharField(
        max_length=50,
        blank=True,
    )

    left_visual_acuity = models.CharField(
        max_length=50,
        blank=True,
    )

    right_fit_assessment = models.CharField(
        max_length=150,
        blank=True,
    )

    left_fit_assessment = models.CharField(
        max_length=150,
        blank=True,
    )

    right_cornea_findings = models.TextField(
        blank=True,
    )

    left_cornea_findings = models.TextField(
        blank=True,
    )

    conjunctival_findings = models.TextField(
        blank=True,
    )

    lens_condition = models.CharField(
        max_length=30,
        choices=LensCondition.choices,
        default=LensCondition.NOT_ASSESSED,
    )

    compliance_assessment = models.TextField(
        blank=True,
    )

    complications = models.TextField(
        blank=True,
    )

    management_plan = models.TextField(
        blank=True,
    )

    lens_parameters_changed = models.BooleanField(
        default=False,
    )

    revised_parameters = models.TextField(
        blank=True,
    )

    next_follow_up_date = models.DateTimeField(
        null=True,
        blank=True,
    )

    clinical_notes = models.TextField(
        blank=True,
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
    )

    updated_at = models.DateTimeField(
        auto_now=True,
    )

    class Meta:
        ordering = [
            "-follow_up_date",
            "-pk",
        ]

        indexes = [
            models.Index(
                fields=[
                    "patient",
                    "follow_up_date",
                ],
                name="cl_follow_patient_date_idx",
            ),
            models.Index(
                fields=["status"],
                name="cl_follow_status_idx",
            ),
        ]

        verbose_name = "Contact Lens Follow-up"
        verbose_name_plural = "Contact Lens Follow-ups"

    def __str__(self):
        return (
            f"Contact Lens Follow-up — "
            f"{self.patient.file_number} — "
            f"{self.follow_up_date:%d %b %Y}"
        )

    def save(self, *args, **kwargs):
        if self.prescription_id:
            self.patient = self.prescription.patient

        if (
            self.status == self.FollowUpStatus.COMPLETED
            and self.attended_at is None
        ):
            self.attended_at = timezone.now()

        super().save(*args, **kwargs)
