from django.urls import path
from . import views

urlpatterns = [
    path("search/", views.global_search, name="global_search"),

    path("excel/import/", views.patient_excel_import, name="patient_excel_import"),
    path("excel/export/", views.patient_excel_export, name="patient_excel_export"),
    path("excel/template/", views.patient_excel_template, name="patient_excel_template"),

    # PDF URLs
    path("<int:pk>/pdf/card/", views.patient_card_pdf, name="patient_card_pdf"),
    path("<int:pk>/pdf/report/", views.patient_report_pdf, name="patient_report_pdf"),
    path("visits/<int:pk>/pdf/report/", views.visit_report_pdf, name="visit_report_pdf"),
    path("billing/<int:pk>/pdf/receipt/", views.bill_receipt_pdf, name="bill_receipt_pdf"),

    path("reports/", views.reports_dashboard, name="reports_dashboard"),
    path("reports/financial/", views.financial_report, name="financial_report"),
    path("reports/clinical/", views.clinical_report, name="clinical_report"),
    path("reports/appointments/", views.appointment_report, name="appointment_report"),
    path("reports/surgeries/", views.surgery_report, name="surgery_report"),

    path("reports/financial/pdf/", views.financial_report_pdf, name="financial_report_pdf"),
    path("reports/financial/excel/", views.financial_report_excel, name="financial_report_excel"),

    path("reports/clinical/pdf/", views.clinical_report_pdf, name="clinical_report_pdf"),
    path("reports/clinical/excel/", views.clinical_report_excel, name="clinical_report_excel"),

    path("reports/appointments/pdf/", views.appointment_report_pdf, name="appointment_report_pdf"),
    path("reports/appointments/excel/", views.appointment_report_excel, name="appointment_report_excel"),

    path("reports/surgeries/pdf/", views.surgery_report_pdf, name="surgery_report_pdf"),
    path("reports/surgeries/excel/", views.surgery_report_excel, name="surgery_report_excel"),

    path("", views.patient_list, name="patient_list"),
    path("register/", views.patient_create, name="patient_create"),
    path(
        "ophthalmology-dashboard/",
        views.ophthalmology_dashboard,
        name="ophthalmology_dashboard",
    ),
    path("<int:pk>/", views.patient_detail, name="patient_detail"),
    path("<int:pk>/edit/", views.patient_update, name="patient_update"),

    path("families/", views.family_group_list, name="family_group_list"),
    path("families/create/", views.family_group_create, name="family_group_create"),
    path("families/<int:pk>/", views.family_group_detail, name="family_group_detail"),
    path("families/<int:pk>/edit/", views.family_group_update, name="family_group_update"),

    path("visits/", views.visit_list, name="visit_list"),
    path("visits/create/", views.visit_create, name="visit_create"),
    path("visits/<int:pk>/", views.visit_detail, name="visit_detail"),
    path("visits/<int:pk>/edit/", views.visit_update, name="visit_update"),

    path("<int:patient_pk>/visits/", views.patient_visit_history, name="patient_visit_history"),
    path("<int:patient_pk>/visits/create/", views.patient_visit_create, name="patient_visit_create"),

    path("visits/<int:visit_pk>/consultation/create/", views.consultation_create, name="consultation_create"),
    path("consultations/<int:pk>/edit/", views.consultation_update, name="consultation_update"),

    path("visits/<int:visit_pk>/eye-exam/create/", views.eye_examination_create, name="eye_examination_create"),
    path("eye-exams/<int:pk>/edit/", views.eye_examination_update, name="eye_examination_update"),

    # =====================================================
    # CLINICAL ATTACHMENTS / INVESTIGATION RESULTS
    # =====================================================

    path(
        "visits/<int:visit_pk>/attachments/",
        views.visit_clinical_attachment_list,
        name="visit_clinical_attachment_list",
    ),

    path(
        "visits/<int:visit_pk>/attachments/upload/",
        views.clinical_attachment_create,
        name="clinical_attachment_create",
    ),

    path(
        "patients/<int:patient_pk>/attachments/",
        views.patient_clinical_attachment_list,
        name="patient_clinical_attachment_list",
    ),

    path(
        "patients/<int:patient_pk>/ophthalmology-timeline/",
        views.patient_ophthalmology_timeline,
        name="patient_ophthalmology_timeline",
    ),

    path(
        "clinical-attachments/<int:pk>/",
        views.clinical_attachment_detail,
        name="clinical_attachment_detail",
    ),

    path(
        "clinical-attachments/<int:pk>/viewer/",
        views.clinical_attachment_viewer,
        name="clinical_attachment_viewer",
    ),

    path(
        "clinical-attachments/<int:pk>/edit/",
        views.clinical_attachment_update,
        name="clinical_attachment_update",
    ),

    path(
        "clinical-attachments/<int:pk>/preview/",
        views.clinical_attachment_preview,
        name="clinical_attachment_preview",
    ),

    path(
        "clinical-attachments/<int:pk>/download/",
        views.clinical_attachment_download,
        name="clinical_attachment_download",
    ),

    path(
        "clinical-attachments/<int:pk>/review/",
        views.clinical_attachment_review,
        name="clinical_attachment_review",
    ),

    path(
        "clinical-attachments/<int:pk>/deactivate/",
        views.clinical_attachment_deactivate,
        name="clinical_attachment_deactivate",
    ),

    path(
        "clinical-attachments/<int:pk>/restore/",
        views.clinical_attachment_restore,
        name="clinical_attachment_restore",
    ),

    path(
        "clinical-attachments/<int:pk>/permanent-delete/",
        views.clinical_attachment_permanent_delete,
        name="clinical_attachment_permanent_delete",
    ),

    path(
        "clinical-attachments/<int:pk>/compare/select/",
        views.clinical_attachment_compare_select,
        name="clinical_attachment_compare_select",
    ),

    path(
        (
            "clinical-attachments/compare/"
            "<int:left_pk>/<int:right_pk>/"
        ),
        views.clinical_attachment_compare,
        name="clinical_attachment_compare",
    ),

    path(
        "clinical-attachments/<int:pk>/annotate/",
        views.clinical_attachment_annotation_workspace,
        name="clinical_attachment_annotation_workspace",
    ),

    path(
        "clinical-attachments/<int:pk>/annotations/save/",
        views.clinical_attachment_annotation_save,
        name="clinical_attachment_annotation_save",
    ),

    path(
        "clinical-image-annotations/<int:annotation_pk>/deactivate/",
        views.clinical_image_annotation_deactivate,
        name="clinical_image_annotation_deactivate",
    ),

    # ============================================================
    # CONTACT LENS MODULE
    # ============================================================

    path(
        "visits/<int:visit_pk>/contact-lens/assessment/create/",
        views.contact_lens_assessment_create,
        name="contact_lens_assessment_create",
    ),

    path(
        "contact-lens/assessments/<int:pk>/",
        views.contact_lens_assessment_detail,
        name="contact_lens_assessment_detail",
    ),

    path(
        "contact-lens/assessments/<int:pk>/edit/",
        views.contact_lens_assessment_update,
        name="contact_lens_assessment_update",
    ),

    path(
        "contact-lens/assessments/<int:assessment_pk>/trials/create/",
        views.contact_lens_trial_create,
        name="contact_lens_trial_create",
    ),

    path(
        "contact-lens/trials/<int:pk>/edit/",
        views.contact_lens_trial_update,
        name="contact_lens_trial_update",
    ),

    path(
        "contact-lens/assessments/<int:assessment_pk>/prescriptions/create/",
        views.contact_lens_prescription_create,
        name="contact_lens_prescription_create",
    ),

    path(
        "contact-lens/prescriptions/<int:pk>/",
        views.contact_lens_prescription_detail,
        name="contact_lens_prescription_detail",
    ),

    path(
        "contact-lens/prescriptions/<int:pk>/edit/",
        views.contact_lens_prescription_update,
        name="contact_lens_prescription_update",
    ),

    path(
        "contact-lens/prescriptions/<int:pk>/submit/",
        views.contact_lens_prescription_submit,
        name="contact_lens_prescription_submit",
    ),

    path(
        "contact-lens/prescriptions/<int:pk>/approve/",
        views.contact_lens_prescription_approve,
        name="contact_lens_prescription_approve",
    ),

    path(
        "contact-lens/prescriptions/<int:pk>/dispense/",
        views.contact_lens_prescription_dispense,
        name="contact_lens_prescription_dispense",
    ),

    path(
        "contact-lens/prescriptions/<int:pk>/new-version/",
        views.contact_lens_prescription_new_version,
        name="contact_lens_prescription_new_version",
    ),

    path(
        "contact-lens/prescriptions/<int:pk>/print/",
        views.contact_lens_prescription_print,
        name="contact_lens_prescription_print",
    ),

    path(
        "contact-lens/prescriptions/<int:pk>/pdf/",
        views.contact_lens_prescription_pdf,
        name="contact_lens_prescription_pdf",
    ),

    path(
        "contact-lens/follow-up-queue/",
        views.contact_lens_follow_up_queue,
        name="contact_lens_follow_up_queue",
    ),

    path(
        "contact-lens/prescriptions/<int:prescription_pk>/follow-ups/create/",
        views.contact_lens_follow_up_create,
        name="contact_lens_follow_up_create",
    ),

    path(
        "contact-lens/follow-ups/<int:pk>/",
        views.contact_lens_follow_up_detail,
        name="contact_lens_follow_up_detail",
    ),

    path(
        "contact-lens/follow-ups/<int:pk>/edit/",
        views.contact_lens_follow_up_update,
        name="contact_lens_follow_up_update",
    ),

    path(
        "patients/<int:patient_pk>/contact-lens-history/",
        views.patient_contact_lens_history,
        name="patient_contact_lens_history",
    ),

    path("visits/<int:visit_pk>/diagnosis-treatment/create/", views.diagnosis_treatment_create, name="diagnosis_treatment_create"),
    path("diagnosis-treatment/<int:pk>/edit/", views.diagnosis_treatment_update, name="diagnosis_treatment_update"),

    path("visits/<int:visit_pk>/prescriptions/create/", views.prescription_create, name="prescription_create"),
    path("prescriptions/<int:pk>/edit/", views.prescription_update, name="prescription_update"),

    path("surgeries/theatre/", views.surgery_theatre_dashboard, name="surgery_theatre_dashboard"),

    path("surgeries/<int:pk>/mark-in-progress/", views.surgery_mark_in_progress, name="surgery_mark_in_progress"),
    path("surgeries/<int:pk>/mark-completed/", views.surgery_mark_completed, name="surgery_mark_completed"),
    path("surgeries/<int:pk>/mark-postponed/", views.surgery_mark_postponed, name="surgery_mark_postponed"),
    path("surgeries/<int:pk>/mark-cancelled/", views.surgery_mark_cancelled, name="surgery_mark_cancelled"),

    path("surgeries/", views.surgery_list, name="surgery_list"),
    path("surgeries/create/", views.surgery_create, name="surgery_create"),
    path("surgeries/<int:pk>/", views.surgery_detail, name="surgery_detail"),
    path("surgeries/<int:pk>/edit/", views.surgery_update, name="surgery_update"),

    path("<int:patient_pk>/surgeries/", views.patient_surgery_history, name="patient_surgery_history"),
    path("<int:patient_pk>/surgeries/create/", views.patient_surgery_create, name="patient_surgery_create"),

    path("visits/<int:visit_pk>/surgeries/create/", views.visit_surgery_create, name="visit_surgery_create"),

    path("appointments/", views.appointment_list, name="appointment_list"),
    path("appointments/create/", views.appointment_create, name="appointment_create"),
    path("appointments/calendar/", views.appointment_calendar, name="appointment_calendar"),
    path("appointments/<int:pk>/mark-arrived/", views.appointment_mark_arrived, name="appointment_mark_arrived"),
    path("appointments/<int:pk>/mark-completed/", views.appointment_mark_completed, name="appointment_mark_completed"),
    path("appointments/<int:pk>/", views.appointment_detail, name="appointment_detail"),
    path("appointments/<int:pk>/edit/", views.appointment_update, name="appointment_update"),

    path("<int:patient_pk>/appointments/", views.patient_appointment_history, name="patient_appointment_history"),
    path("<int:patient_pk>/appointments/create/", views.patient_appointment_create, name="patient_appointment_create"),

    path("clinic-queue/", views.clinic_queue, name="clinic_queue"),
    path("doctor-worklist/", views.doctor_worklist, name="doctor_worklist"),

    path("visits/<int:pk>/mark-completed/", views.visit_mark_completed, name="visit_mark_completed"),

    path("billing/", views.bill_list, name="bill_list"),
    path("billing/create/", views.bill_create, name="bill_create"),
    path("billing/<int:pk>/", views.bill_detail, name="bill_detail"),
    path("billing/<int:pk>/edit/", views.bill_update, name="bill_update"),
    path("billing/<int:bill_pk>/payment/create/", views.payment_create, name="payment_create"),

    path("<int:patient_pk>/billing/", views.patient_bill_history, name="patient_bill_history"),
    path("<int:patient_pk>/billing/create/", views.patient_bill_create, name="patient_bill_create"),
]