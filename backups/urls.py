from django.urls import path
from . import views

urlpatterns = [
    path("", views.backup_dashboard, name="backup_dashboard"),
    path("create/", views.create_backup, name="create_backup"),
    path("download/<str:filename>/", views.download_backup, name="download_backup"),
    path("restore/", views.restore_backup, name="restore_backup"),
]