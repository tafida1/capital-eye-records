from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User
from .forms import CustomUserCreationForm, CustomUserChangeForm



@admin.register(User)
class CustomUserAdmin(UserAdmin):
    model = User
    add_form = CustomUserCreationForm
    form = CustomUserChangeForm

    list_display = (
        "username",
        "first_name",
        "last_name",
        "role",
        "department",
        "phone_number",
        "is_active",
        "is_staff",
    )

    list_filter = (
        "role",
        "department",
        "is_active",
        "is_staff",
        "is_superuser",
    )

    search_fields = (
        "username",
        "first_name",
        "last_name",
        "email",
        "phone_number",
        "staff_id",
        "department",
    )

    ordering = ("role", "first_name", "last_name")

    fieldsets = (
        ("Login Information", {
            "fields": ("username", "password")
        }),
        ("Personal Information", {
            "fields": (
                "first_name",
                "last_name",
                "email",
                "phone_number",
                "staff_id",
                "department",
            )
        }),
        ("Hospital Role", {
            "fields": (
                "role",
                "must_change_password",
                "is_active_staff",
            )
        }),
        ("Permissions", {
            "fields": (
                "is_active",
                "is_staff",
                "is_superuser",
                "groups",
                "user_permissions",
            )
        }),
        ("Important Dates", {
            "fields": (
                "last_login",
                "date_joined",
            )
        }),
    )

    add_fieldsets = (
        ("Create User Account", {
            "classes": ("wide",),
            "fields": (
                "username",
                "password1",
                "password2",
                "first_name",
                "last_name",
                "email",
                "phone_number",
                "staff_id",
                "department",
                "role",
                "is_active",
                "is_staff",
            ),
        }),
    )
