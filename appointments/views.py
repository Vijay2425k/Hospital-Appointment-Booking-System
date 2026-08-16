from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ValidationError
from django.db import IntegrityError, transaction
from django.shortcuts import get_object_or_404, redirect, render

from .forms import AppointmentBookingForm
from .models import Appointment, Doctor


def doctor_list(request):
    specialization = request.GET.get('specialization', '').strip()
    doctors = Doctor.objects.filter(is_active=True).select_related('user')
    if specialization:
        doctors = doctors.filter(specialization__icontains=specialization)

    specializations = Doctor.objects.filter(is_active=True).values_list(
        'specialization', flat=True
    ).distinct().order_by('specialization')

    return render(request, 'appointments/doctor_list.html', {
        'doctors': doctors,
        'specializations': specializations,
        'selected_specialization': specialization,
    })


@login_required
def book_appointment(request):
    initial = {}
    doctor_id = request.GET.get('doctor')
    if doctor_id:
        initial['doctor'] = doctor_id

    if request.method == 'POST':
        form = AppointmentBookingForm(request.POST)
        if form.is_valid():
            appointment = form.save(commit=False)
            appointment.patient = request.user
            try:
                appointment.full_clean()
                with transaction.atomic():
                    appointment.save()
                messages.success(request, 'Appointment booked successfully. It is pending confirmation.')
                return redirect('appointments:dashboard')
            except (ValidationError, IntegrityError):
                form.add_error(None, 'This slot was just booked by someone else. Please pick another slot.')
    else:
        form = AppointmentBookingForm(initial=initial)

    return render(request, 'appointments/book_appointment.html', {'form': form})


@login_required
def dashboard(request):
    user = request.user

    if user.is_doctor():
        doctor_profile = getattr(user, 'doctor_profile', None)
        appointments = (
            Appointment.objects.filter(doctor=doctor_profile).select_related('patient')
            if doctor_profile else Appointment.objects.none()
        )
        return render(request, 'appointments/doctor_dashboard.html', {'appointments': appointments})

    appointments = Appointment.objects.filter(patient=user).select_related('doctor', 'doctor__user')
    return render(request, 'appointments/patient_dashboard.html', {'appointments': appointments})


@login_required
def cancel_appointment(request, pk):
    appointment = get_object_or_404(Appointment, pk=pk)

    is_owner_patient = appointment.patient_id == request.user.id
    is_assigned_doctor = request.user.is_doctor() and getattr(request.user, 'doctor_profile', None) == appointment.doctor
    if not (is_owner_patient or is_assigned_doctor):
        messages.error(request, "You don't have permission to cancel this appointment.")
        return redirect('appointments:dashboard')

    if request.method == 'POST':
        appointment.status = Appointment.Status.CANCELLED
        appointment.save()
        messages.success(request, 'Appointment cancelled.')
        return redirect('appointments:dashboard')

    return render(request, 'appointments/cancel_confirm.html', {'appointment': appointment})


@login_required
def mark_completed(request, pk):
    appointment = get_object_or_404(Appointment, pk=pk)
    if not (request.user.is_doctor() and getattr(request.user, 'doctor_profile', None) == appointment.doctor):
        messages.error(request, "You don't have permission to update this appointment.")
        return redirect('appointments:dashboard')

    appointment.status = Appointment.Status.COMPLETED
    appointment.save()
    messages.success(request, 'Appointment marked as completed.')
    return redirect('appointments:dashboard')
