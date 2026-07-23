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