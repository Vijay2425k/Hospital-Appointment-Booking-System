from django.test import TestCase
from django.urls import reverse

from .models import User


class PatientRegistrationTests(TestCase):

    def test_patient_can_register(self):
        response = self.client.post(reverse('accounts:register'), {
            'username': 'johndoe',
            'first_name': 'John',
            'last_name': 'Doe',
            'email': 'john@example.com',
            'phone_number': '9876543210',
            'password1': 'StrongPass123!',
            'password2': 'StrongPass123!',
        })
        self.assertEqual(response.status_code, 302)
        user = User.objects.get(username='johndoe')
        self.assertEqual(user.role, User.Role.PATIENT)
        self.assertEqual(user.email, 'john@example.com')

    def test_registration_fails_with_mismatched_passwords(self):
        response = self.client.post(reverse('accounts:register'), {
            'username': 'janedoe',
            'first_name': 'Jane',
            'last_name': 'Doe',
            'email': 'jane@example.com',
            'phone_number': '9876543211',
            'password1': 'StrongPass123!',
            'password2': 'DifferentPass456!',
        })
        self.assertEqual(response.status_code, 200)
        self.assertFalse(User.objects.filter(username='janedoe').exists())

    def test_registered_user_is_logged_in_automatically(self):
        self.client.post(reverse('accounts:register'), {
            'username': 'autologin',
            'first_name': 'Auto',
            'last_name': 'Login',
            'email': 'auto@example.com',
            'phone_number': '9876543212',
            'password1': 'StrongPass123!',
            'password2': 'StrongPass123!',
        })
        response = self.client.get(reverse('appointments:dashboard'))
        self.assertEqual(response.status_code, 200)


class LoginTests(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(username='testpatient', password='TestPass123!', role=User.Role.PATIENT)

    def test_valid_login_succeeds(self):
        response = self.client.post(reverse('accounts:login'), {
            'username': 'testpatient',
            'password': 'TestPass123!',
        })
        self.assertEqual(response.status_code, 302)

    def test_invalid_password_fails(self):
        response = self.client.post(reverse('accounts:login'), {
            'username': 'testpatient',
            'password': 'WrongPassword',
        })
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'correct')

    def test_dashboard_requires_login(self):
        response = self.client.get(reverse('appointments:dashboard'))
        self.assertEqual(response.status_code, 302)
        self.assertIn('/accounts/login/', response.url)
