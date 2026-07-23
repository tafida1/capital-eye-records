from django.conf import settings
from django.db import models
from django.utils import timezone



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
    visit = models.OneToOneField(
        PatientVisit,
        on_delete=models.CASCADE,
        related_name="eye_examination",
    )

    # Visual acuity
    right_visual_acuity = models.CharField(max_length=50, blank=True)
    left_visual_acuity = models.CharField(max_length=50, blank=True)

    right_pinhole = models.CharField(max_length=50, blank=True)
    left_pinhole = models.CharField(max_length=50, blank=True)

    right_near_vision = models.CharField(max_length=50, blank=True)
    left_near_vision = models.CharField(max_length=50, blank=True)

    # Refraction
    right_sphere = models.CharField(max_length=30, blank=True)
    right_cylinder = models.CharField(max_length=30, blank=True)
    right_axis = models.CharField(max_length=30, blank=True)

    left_sphere = models.CharField(max_length=30, blank=True)
    left_cylinder = models.CharField(max_length=30, blank=True)
    left_axis = models.CharField(max_length=30, blank=True)

    # Eye pressure
    right_iop = models.CharField(max_length=30, blank=True)
    left_iop = models.CharField(max_length=30, blank=True)

    # Examination findings
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