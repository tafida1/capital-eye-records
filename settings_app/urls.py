from django.urls import path
from . import views

urlpatterns = [
    path("", views.system_setting_update, name="system_setting_update"),
]