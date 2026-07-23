from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    class Role(models.TextChoices):
        SUPER_ADMIN = "SUPER_ADMIN", "Super Admin"
        HOSPITAL_ADMIN = "HOSPITAL_ADMIN", "Hospital Admin"
        RECEPTIONIST = "RECEPTIONIST", "Receptionist"
        DOCTOR = "DOCTOR", "Doctor/Ophthalmologist"
        NURSE = "NURSE", "Nurse"
        CASHIER = "CASHIER", "Cashier/Accountant"
        RECORDS_OFFICER = "RECORDS_OFFICER", "Records Officer"
        LAB_STAFF = "LAB_STAFF", "Lab/Procedure Staff"
        VIEWER = "VIEWER", "Viewer/Auditor"

    role = models.CharField(
        max_length=30,
        choices=Role.choices,
        default=Role.VIEWER,
    )

    phone_number = models.CharField(max_length=20, blank=True)
    staff_id = models.CharField(max_length=30, blank=True, unique=True, null=True)
    department = models.CharField(max_length=100, blank=True)
    must_change_password = models.BooleanField(default=False)
    is_active_staff = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["first_name", "last_name", "username"]

    def __str__(self):
        full_name = self.get_full_name()
        return full_name if full_name else self.username

    @property
    def is_super_admin(self):
        return self.role == self.Role.SUPER_ADMIN or self.is_superuser

    @property
    def is_hospital_admin(self):
        return self.role == self.Role.HOSPITAL_ADMIN

    @property
    def is_receptionist(self):
        return self.role == self.Role.RECEPTIONIST

    @property
    def is_doctor(self):
        return self.role == self.Role.DOCTOR

    @property
    def is_nurse(self):
        return self.role == self.Role.NURSE

    @property
    def is_cashier(self):
        return self.role == self.Role.CASHIER

    @property
    def is_records_officer(self):
        return self.role == self.Role.RECORDS_OFFICER

    @property
    def is_lab_staff(self):
        return self.role == self.Role.LAB_STAFF

    @property
    def is_viewer(self):
        return self.role == self.Role.VIEWER