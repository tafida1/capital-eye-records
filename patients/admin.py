from django.contrib import admin
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


@admin.register(FamilyGroup)
class FamilyGroupAdmin(admin.ModelAdmin):
    list_display = (
        "family_code",
        "family_name",
        "head_of_family",
        "primary_phone",
        "created_at",
        "created_by",
    )
    search_fields = ("family_code", "family_name", "head_of_family", "primary_phone")
    readonly_fields = ("family_code", "created_at", "updated_at")
    list_per_page = 25

    def save_model(self, request, obj, form, change):
        if not obj.created_by:
            obj.created_by = request.user
        super().save_model(request, obj, form, change)


@admin.register(Patient)
class PatientAdmin(admin.ModelAdmin):
    list_display = (
        "file_number",
        "full_name",
        "gender",
        "display_age",
        "phone_number",
        "payment_status",
        "registration_date",
        "registered_by",
    )

    list_filter = (
        "gender",
        "payment_status",
        "registration_date",
        "registered_by",
    )

    search_fields = (
        "file_number",
        "full_name",
        "phone_number",
        "diagnosis",
        "eye_complaint",
        "surgery_procedure_details",
    )

    readonly_fields = (
        "file_number",
        "registration_date",
        "updated_at",
    )

    date_hierarchy = "registration_date"
    list_per_page = 25

    fieldsets = (
        ("File Information", {
            "fields": ("file_number", "registration_date", "registered_by")
        }),
        ("Personal Information", {
            "fields": (
                "full_name",
                "gender",
                "date_of_birth",
                "age",
                "phone_number",
                "address",
                "occupation",
            )
        }),
        ("Next of Kin", {
            "fields": (
                "next_of_kin_name",
                "next_of_kin_phone",
                "next_of_kin_relationship",
            )
        }),
        ("Family / Group Record", {
            "fields": (
                "family_group",
                "family_group_name",
                "family_relationship",
            )
        }),
        ("Medical Information", {
            "fields": (
                "medical_history",
                "allergy_history",
                "eye_complaint",
                "diagnosis",
                "treatment",
                "surgery_procedure_details",
            )
        }),
        ("Payment / Notes", {
            "fields": ("payment_status", "notes")
        }),
        ("System Information", {
            "fields": ("updated_at",)
        }),
    )

    def save_model(self, request, obj, form, change):
        if not obj.registered_by:
            obj.registered_by = request.user
        super().save_model(request, obj, form, change)


@admin.register(PatientVisit)
class PatientVisitAdmin(admin.ModelAdmin):
    list_display = (
        "visit_number",
        "patient",
        "visit_type",
        "status",
        "visit_date",
        "created_by",
    )
    list_filter = ("visit_type", "status", "visit_date", "created_by")
    search_fields = (
        "visit_number",
        "patient__file_number",
        "patient__full_name",
        "chief_complaint",
        "brief_history",
    )
    readonly_fields = ("visit_number", "visit_date", "created_at", "updated_at")
    date_hierarchy = "visit_date"
    list_per_page = 25

    def save_model(self, request, obj, form, change):
        if not obj.created_by:
            obj.created_by = request.user
        super().save_model(request, obj, form, change)


@admin.register(Consultation)
class ConsultationAdmin(admin.ModelAdmin):
    list_display = ("visit", "get_patient", "doctor", "consultation_date")
    search_fields = (
        "visit__visit_number",
        "visit__patient__file_number",
        "visit__patient__full_name",
        "presenting_complaint",
        "final_diagnosis",
    )
    list_filter = ("consultation_date", "doctor")
    readonly_fields = ("consultation_date", "created_at", "updated_at")
    date_hierarchy = "consultation_date"
    list_per_page = 25

    def get_patient(self, obj):
        return obj.visit.patient.full_name

    get_patient.short_description = "Patient"


@admin.register(EyeExamination)
class EyeExaminationAdmin(admin.ModelAdmin):
    list_display = ("visit", "get_patient", "examined_by", "examination_date")
    search_fields = (
        "visit__visit_number",
        "visit__patient__file_number",
        "visit__patient__full_name",
        "impression",
        "recommendation",
    )
    list_filter = ("examination_date", "examined_by")
    readonly_fields = ("examination_date", "created_at", "updated_at")
    date_hierarchy = "examination_date"
    list_per_page = 25

    def get_patient(self, obj):
        return obj.visit.patient.full_name

    get_patient.short_description = "Patient"


@admin.register(DiagnosisTreatment)
class DiagnosisTreatmentAdmin(admin.ModelAdmin):
    list_display = ("visit", "get_patient", "created_by", "created_at")
    search_fields = (
        "visit__visit_number",
        "visit__patient__file_number",
        "visit__patient__full_name",
        "primary_diagnosis",
        "secondary_diagnosis",
    )
    list_filter = ("created_at", "created_by")
    date_hierarchy = "created_at"
    list_per_page = 25

    def get_patient(self, obj):
        return obj.visit.patient.full_name

    get_patient.short_description = "Patient"


@admin.register(Prescription)
class PrescriptionAdmin(admin.ModelAdmin):
    list_display = (
        "drug_name",
        "visit",
        "get_patient",
        "dosage",
        "frequency",
        "duration",
        "prescribed_by",
        "prescribed_at",
    )
    search_fields = (
        "drug_name",
        "visit__visit_number",
        "visit__patient__file_number",
        "visit__patient__full_name",
    )
    list_filter = ("prescribed_at", "prescribed_by")
    date_hierarchy = "prescribed_at"
    list_per_page = 25

    def get_patient(self, obj):
        return obj.visit.patient.full_name

    get_patient.short_description = "Patient"


@admin.register(SurgeryProcedure)
class SurgeryProcedureAdmin(admin.ModelAdmin):
    list_display = (
        "procedure_number",
        "patient",
        "procedure_name",
        "procedure_type",
        "eye_side",
        "status",
        "scheduled_date",
        "surgeon",
    )
    list_filter = (
        "status",
        "eye_side",
        "procedure_type",
        "scheduled_date",
        "procedure_date",
        "surgeon",
    )
    search_fields = (
        "procedure_number",
        "patient__file_number",
        "patient__full_name",
        "patient__phone_number",
        "procedure_name",
        "procedure_type",
        "pre_op_diagnosis",
        "post_op_diagnosis",
    )
    readonly_fields = ("procedure_number", "created_at", "updated_at")
    date_hierarchy = "scheduled_date"
    list_per_page = 25

    def save_model(self, request, obj, form, change):
        if not obj.created_by:
            obj.created_by = request.user
        super().save_model(request, obj, form, change)


@admin.register(Appointment)
class AppointmentAdmin(admin.ModelAdmin):
    list_display = (
        "appointment_number",
        "patient",
        "appointment_type",
        "status",
        "appointment_date",
        "appointment_time",
        "assigned_to",
        "created_by",
    )
    list_filter = ("appointment_type", "status", "appointment_date", "assigned_to")
    search_fields = (
        "appointment_number",
        "patient__file_number",
        "patient__full_name",
        "patient__phone_number",
        "reason",
    )
    readonly_fields = ("appointment_number", "created_at", "updated_at")
    date_hierarchy = "appointment_date"
    list_per_page = 25

    def save_model(self, request, obj, form, change):
        if not obj.created_by:
            obj.created_by = request.user
        super().save_model(request, obj, form, change)


@admin.register(Bill)
class BillAdmin(admin.ModelAdmin):
    list_display = (
        "bill_number",
        "patient",
        "bill_title",
        "total_amount",
        "discount",
        "amount_paid",
        "balance",
        "status",
        "created_at",
        "created_by",
    )
    list_filter = ("status", "created_at", "created_by")
    search_fields = (
        "bill_number",
        "patient__file_number",
        "patient__full_name",
        "patient__phone_number",
        "bill_title",
    )
    readonly_fields = ("bill_number", "amount_paid", "created_at", "updated_at")
    date_hierarchy = "created_at"
    list_per_page = 25

    def save_model(self, request, obj, form, change):
        if not obj.created_by:
            obj.created_by = request.user
        super().save_model(request, obj, form, change)


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = (
        "receipt_number",
        "bill",
        "amount",
        "payment_method",
        "payment_date",
        "received_by",
    )
    list_filter = ("payment_method", "payment_date", "received_by")
    search_fields = (
        "receipt_number",
        "bill__bill_number",
        "bill__patient__file_number",
        "bill__patient__full_name",
        "reference_number",
    )
    readonly_fields = ("receipt_number", "created_at")
    date_hierarchy = "payment_date"
    list_per_page = 25

    def save_model(self, request, obj, form, change):
        if not obj.received_by:
            obj.received_by = request.user
        super().save_model(request, obj, form, change)