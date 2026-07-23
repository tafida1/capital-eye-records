from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from core import views as core_views



admin.site.site_header = "CAPITAL EYE HOSPITAL RECORDS SYSTEM"
admin.site.site_title = "Capital Eye Admin"
admin.site.index_title = "Enterprise Administration Portal"



urlpatterns = [
    path("admin/", admin.site.urls),

    path("accounts/", include("accounts.urls")),
    path("patients/", include("patients.urls")),
    path("audit-logs/", include("audit_logs.urls")),
    path("backups/", include("backups.urls")),
    path("settings/", include("settings_app.urls")),
    path("notifications/", include("notifications.urls")),
    path("system/about/", core_views.about_system, name="about_system"),

    path("", core_views.home, name="home"),
    path("dashboard/", core_views.dashboard, name="dashboard"),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)