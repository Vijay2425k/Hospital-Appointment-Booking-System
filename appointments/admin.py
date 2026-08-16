from django.contrib import admin

from .models import Appointment, Doctor


@admin.register(Doctor)
class DoctorAdmin(admin.ModelAdmin):
    list_display = ['user', 'specialization', 'consultation_fee', 'is_active']
    list_filter = ['specialization', 'is_active']
    search_fields = ['user__first_name', 'user__last_name', 'specialization']


@admin.register(Appointment)
class AppointmentAdmin(admin.ModelAdmin):
    list_display = ['patient', 'doctor', 'appointment_date', 'time_slot', 'status']
    list_filter = ['status', 'appointment_date', 'doctor']
    search_fields = ['patient__username', 'doctor__user__username']
    date_hierarchy = 'appointment_date'
