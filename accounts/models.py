from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    """
    Extends Django's built-in user with a role field. Role determines
    which dashboard and permissions a logged-in user gets — patients book
    appointments, doctors manage their schedule, admins use /admin/.
    """

    class Role(models.TextChoices):
        PATIENT = 'PATIENT', 'Patient'
        DOCTOR = 'DOCTOR', 'Doctor'
        ADMIN = 'ADMIN', 'Admin'

    role = models.CharField(max_length=10, choices=Role.choices, default=Role.PATIENT)
    phone_number = models.CharField(max_length=20, blank=True)

    def is_patient(self):
        return self.role == self.Role.PATIENT

    def is_doctor(self):
        return self.role == self.Role.DOCTOR

    def __str__(self):
        return f"{self.get_full_name() or self.username} ({self.get_role_display()})"
