from django.core.management.base import BaseCommand

from accounts.models import User
from appointments.models import Doctor


class Command(BaseCommand):
    help = 'Creates demo doctor accounts for local testing/screenshots.'

    def handle(self, *args, **options):
        demo_doctors = [
            ('drpriya', 'Priya', 'Sharma', 'Cardiology', 600),
            ('drarjun', 'Arjun', 'Mehta', 'Dermatology', 400),
            ('drkavya', 'Kavya', 'Reddy', 'Pediatrics', 350),
            ('drrohan', 'Rohan', 'Iyer', 'Orthopedics', 500),
        ]

        for username, first, last, spec, fee in demo_doctors:
            user, created = User.objects.get_or_create(
                username=username,
                defaults={
                    'first_name': first, 'last_name': last,
                    'email': f'{username}@medicare.example',
                    'role': User.Role.DOCTOR,
                },
            )
            if created:
                user.set_password('DemoPass123!')
                user.save()

            Doctor.objects.get_or_create(
                user=user,
                defaults={
                    'specialization': spec,
                    'consultation_fee': fee,
                    'bio': f'{spec} specialist with a patient-first approach to care.',
                },
            )

        self.stdout.write(self.style.SUCCESS('Demo doctors created.'))
