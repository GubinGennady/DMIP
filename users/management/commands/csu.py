from django.core.management import BaseCommand
from app.models import User

class Command(BaseCommand):
    def handle(self, *args, **options):
        superuser, created = User.objects.get_or_create(
            username='admin1',
            defaults={
                'first_name': 'Super',
                'last_name': 'User',
                'is_staff': True,
                'is_superuser': True,
                'is_active': True
            }
        )

        if created:
            superuser.set_password('12345')
            superuser.save()
            self.stdout.write(self.style.SUCCESS('Superuser created successfully.'))
        else:
            self.stdout.write(self.style.WARNING('Superuser with this email already exists.'))

