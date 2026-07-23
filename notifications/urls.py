from django.urls import path
from . import views

urlpatterns = [
    path("", views.notification_list, name="notification_list"),
    path("<int:pk>/read/", views.notification_mark_read, name="notification_mark_read"),
    path("read-all/", views.notification_mark_all_read, name="notification_mark_all_read"),
]