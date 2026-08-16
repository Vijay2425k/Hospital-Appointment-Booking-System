from datetime import date, timedelta

from django.test import TestCase
from django.urls import reverse

from accounts.models import User
from .models import Appointment, Doctor, TimeSlot


class AppointmentModelTests(TestCase):

    def setUp(self):
        self.doctor_user = User.objects.create_user(username='drsmith', password='pass', role=User.Role.DOCTOR)
        self.doctor = Doctor.objects.create(user=self.doctor_user, specialization='Cardiology', consultation_fee=500)
        self.patient1 = User.objects.create_user(username='patient1', password='pass', role=User.Role.PATIENT)
        self.patient2 = User.objects.create_user(username='patient2', password='pass', role=User.Role.PATIENT)
        self.tomorrow = date.today() + timedelta(days=1)

    def test_appointment_can_be_created(self):
        appt = Appointment.objects.create(
            patient=self.patient1, doctor=self.doctor,
            appointment_date=self.tomorrow, time_slot=TimeSlot.SLOT_09_10,
        )
        self.assertEqual(appt.status, Appointment.Status.PENDING)

    def test_double_booking_same_slot_is_rejected(self):
        Appointment.objects.create(
            patient=self.patient1, doctor=self.doctor,
            appointment_date=self.tomorrow, time_slot=TimeSlot.SLOT_09_10,
        )
        clashing = Appointment(
            patient=self.patient2, doctor=self.doctor,
            appointment_date=self.tomorrow, time_slot=TimeSlot.SLOT_09_10,
        )
        with self.assertRaises(Exception):
            clashing.full_clean()

    def test_cancelled_appointment_frees_up_the_slot(self):
        first = Appointment.objects.create(
            patient=self.patient1, doctor=self.doctor,
            appointment_date=self.tomorrow, time_slot=TimeSlot.SLOT_09_10,
            status=Appointment.Status.CANCELLED,
        )
        second = Appointment(
            patient=self.patient2, doctor=self.doctor,
            appointment_date=self.tomorrow, time_slot=TimeSlot.SLOT_09_10,
        )
        second.full_clean()  # should not raise
        second.save()
        self.assertEqual(Appointment.objects.filter(doctor=self.doctor, appointment_date=self.tomorrow).count(), 2)

    def test_different_time_slots_same_day_allowed(self):
        Appointment.objects.create(
            patient=self.patient1, doctor=self.doctor,
            appointment_date=self.tomorrow, time_slot=TimeSlot.SLOT_09_10,
        )
        second = Appointment(
            patient=self.patient2, doctor=self.doctor,
            appointment_date=self.tomorrow, time_slot=TimeSlot.SLOT_10_11,
        )
        second.full_clean()  # should not raise
        second.save()
        self.assertEqual(Appointment.objects.filter(doctor=self.doctor, appointment_date=self.tomorrow).count(), 2)


class BookingViewTests(TestCase):

    def setUp(self):
        self.doctor_user = User.objects.create_user(username='drjones', password='pass', role=User.Role.DOCTOR)
        self.doctor = Doctor.objects.create(user=self.doctor_user, specialization='Dermatology', consultation_fee=400)
        self.patient = User.objects.create_user(username='patientx', password='TestPass123!', role=User.Role.PATIENT)
        self.tomorrow = date.today() + timedelta(days=1)

    def test_anonymous_user_redirected_from_booking_page(self):
        response = self.client.get(reverse('appointments:book_appointment'))
        self.assertEqual(response.status_code, 302)

    def test_logged_in_patient_can_book_appointment(self):
        self.client.login(username='patientx', password='TestPass123!')
        response = self.client.post(reverse('appointments:book_appointment'), {
            'doctor': self.doctor.id,
            'appointment_date': self.tomorrow.isoformat(),
            'time_slot': TimeSlot.SLOT_11_12,
            'reason': 'Routine checkup',
        })
        self.assertEqual(response.status_code, 302)
        self.assertTrue(Appointment.objects.filter(patient=self.patient, doctor=self.doctor).exists())

    def test_booking_same_slot_twice_shows_form_error_not_crash(self):
        self.client.login(username='patientx', password='TestPass123!')
        self.client.post(reverse('appointments:book_appointment'), {
            'doctor': self.doctor.id,
            'appointment_date': self.tomorrow.isoformat(),
            'time_slot': TimeSlot.SLOT_14_15,
        })
        other_patient = User.objects.create_user(username='patienty', password='TestPass123!', role=User.Role.PATIENT)
        self.client.login(username='patienty', password='TestPass123!')
        response = self.client.post(reverse('appointments:book_appointment'), {
            'doctor': self.doctor.id,
            'appointment_date': self.tomorrow.isoformat(),
            'time_slot': TimeSlot.SLOT_14_15,
        })
        self.assertEqual(response.status_code, 200)  # re-rendered with error, not a crash
        self.assertEqual(
            Appointment.objects.filter(doctor=self.doctor, appointment_date=self.tomorrow, time_slot=TimeSlot.SLOT_14_15).count(),
            1,
        )

    def test_cannot_book_appointment_in_the_past(self):
        self.client.login(username='patientx', password='TestPass123!')
        yesterday = date.today() - timedelta(days=1)
        response = self.client.post(reverse('appointments:book_appointment'), {
            'doctor': self.doctor.id,
            'appointment_date': yesterday.isoformat(),
            'time_slot': TimeSlot.SLOT_09_10,
        })
        self.assertEqual(response.status_code, 200)
        self.assertFalse(Appointment.objects.filter(appointment_date=yesterday).exists())

    def test_patient_can_cancel_own_appointment(self):
        self.client.login(username='patientx', password='TestPass123!')
        appt = Appointment.objects.create(
            patient=self.patient, doctor=self.doctor,
            appointment_date=self.tomorrow, time_slot=TimeSlot.SLOT_15_16,
        )
        response = self.client.post(reverse('appointments:cancel_appointment', args=[appt.pk]))
        self.assertEqual(response.status_code, 302)
        appt.refresh_from_db()
        self.assertEqual(appt.status, Appointment.Status.CANCELLED)

    def test_patient_cannot_cancel_someone_elses_appointment(self):
        other_patient = User.objects.create_user(username='otherpatient', password='TestPass123!', role=User.Role.PATIENT)
        appt = Appointment.objects.create(
            patient=other_patient, doctor=self.doctor,
            appointment_date=self.tomorrow, time_slot=TimeSlot.SLOT_16_17,
        )
        self.client.login(username='patientx', password='TestPass123!')
        self.client.post(reverse('appointments:cancel_appointment', args=[appt.pk]))
        appt.refresh_from_db()
        self.assertNotEqual(appt.status, Appointment.Status.CANCELLED)


class DoctorListViewTests(TestCase):

    def setUp(self):
        cardio_user = User.objects.create_user(username='drcardio', password='pass', role=User.Role.DOCTOR)
        Doctor.objects.create(user=cardio_user, specialization='Cardiology', consultation_fee=600, is_active=True)
        derm_user = User.objects.create_user(username='drderm', password='pass', role=User.Role.DOCTOR)
        Doctor.objects.create(user=derm_user, specialization='Dermatology', consultation_fee=400, is_active=True)
        inactive_user = User.objects.create_user(username='drold', password='pass', role=User.Role.DOCTOR)
        Doctor.objects.create(user=inactive_user, specialization='Cardiology', consultation_fee=550, is_active=False)

    def test_doctor_list_shows_only_active_doctors(self):
        response = self.client.get(reverse('appointments:doctor_list'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context['doctors']), 2)

    def test_filter_by_specialization(self):
        response = self.client.get(reverse('appointments:doctor_list'), {'specialization': 'Cardiology'})
        doctors = response.context['doctors']
        self.assertEqual(len(doctors), 1)
        self.assertEqual(doctors[0].specialization, 'Cardiology')
