from django.urls import path
from . import views

urlpatterns = [
    path("login/", views.login_view, name="login"),
    path("logout/", views.logout_view, name="logout"),
    path("change-password/", views.change_password_view, name="change_password"),

    path("password/change/", views.change_own_password, name="change_own_password"),

    path("staff/", views.staff_dashboard, name="staff_dashboard"),
    path("staff/create/", views.staff_create, name="staff_create"),

    path("staff/<int:pk>/reset-password/", views.staff_password_reset, name="staff_password_reset"),
    path("staff/<int:pk>/force-password-change/", views.staff_force_password_change, name="staff_force_password_change"),
    path("staff/<int:pk>/toggle-active/", views.staff_toggle_active, name="staff_toggle_active"),
    path("staff/<int:pk>/edit/", views.staff_update, name="staff_update"),
    path("staff/<int:pk>/", views.staff_detail, name="staff_detail"),
]