from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models


class Doctor(models.Model):
    """
    Extends a User (role=DOCTOR) with hospital-specific profile fields.
    Kept as a separate model rather than piling fields onto User, since
    only doctors need a specialization/consultation fee/bio.
    """

    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='doctor_profile')
    specialization = models.CharField(max_length=100)
    bio = models.TextField(blank=True)
    consultation_fee = models.DecimalField(max_digits=8, decimal_places=2, default=0)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"Dr. {self.user.get_full_name() or self.user.username} — {self.specialization}"


class TimeSlot(models.TextChoices):
    SLOT_09_10 = '09:00-10:00', '09:00 AM - 10:00 AM'
    SLOT_10_11 = '10:00-11:00', '10:00 AM - 11:00 AM'
    SLOT_11_12 = '11:00-12:00', '11:00 AM - 12:00 PM'
    SLOT_14_15 = '14:00-15:00', '02:00 PM - 03:00 PM'
    SLOT_15_16 = '15:00-16:00', '03:00 PM - 04:00 PM'
    SLOT_16_17 = '16:00-17:00', '04:00 PM - 05:00 PM'


class Appointment(models.Model):

    class Status(models.TextChoices):
        PENDING = 'PENDING', 'Pending'
        CONFIRMED = 'CONFIRMED', 'Confirmed'
        COMPLETED = 'COMPLETED', 'Completed'
        CANCELLED = 'CANCELLED', 'Cancelled'

    patient = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='appointments_as_patient'
    )
    doctor = models.ForeignKey(Doctor, on_delete=models.CASCADE, related_name='appointments')
    appointment_date = models.DateField()
    time_slot = models.CharField(max_length=20, choices=TimeSlot.choices)
    reason = models.CharField(max_length=255, blank=True)
    status = models.CharField(max_length=10, choices=Status.choices, default=Status.PENDING)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-appointment_date', '-time_slot']
        constraints = [
            models.UniqueConstraint(
                fields=['doctor', 'appointment_date', 'time_slot'],
                condition=models.Q(status__in=['PENDING', 'CONFIRMED']),
                name='unique_active_doctor_slot',
            )
        ]

    def clean(self):
        """
        Defense-in-depth alongside the DB constraint: also block double-booking
        at the form/model level so the error surfaces as a clean validation
        message instead of a raw IntegrityError.
        """
        if self.status in (self.Status.PENDING, self.Status.CONFIRMED):
            clashing = Appointment.objects.filter(
                doctor=self.doctor,
                appointment_date=self.appointment_date,
                time_slot=self.time_slot,
                status__in=[self.Status.PENDING, self.Status.CONFIRMED],
            ).exclude(pk=self.pk)
            if clashing.exists():
                raise ValidationError('This time slot is already booked for the selected doctor.')

    def __str__(self):
        return f"{self.patient} with {self.doctor} on {self.appointment_date} [{self.time_slot}]"
