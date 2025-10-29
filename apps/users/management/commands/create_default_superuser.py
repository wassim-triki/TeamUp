from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.db import IntegrityError


class Command(BaseCommand):
    help = 'Creates a superuser automatically if it does not exist'

    def handle(self, *args, **options):
        User = get_user_model()
        
        # Admin credentials
        email = 'admin@teamup.com'
        password = 'password'
        
        try:
            # Check if user already exists
            if User.objects.filter(email=email).exists():
                self.stdout.write(
                    self.style.WARNING(f'Admin user with email {email} already exists.')
                )
                return
            
            # Create superuser
            User.objects.create_superuser(
                email=email,
                password=password,
                first_name='Admin',
                last_name='User'
            )
            
            self.stdout.write(
                self.style.SUCCESS(f'Successfully created superuser: {email}')
            )
            
        except IntegrityError as e:
            self.stdout.write(
                self.style.ERROR(f'Error creating superuser: {str(e)}')
            )
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Unexpected error: {str(e)}')
            )
