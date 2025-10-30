from django.core.management.base import BaseCommand
from apps.users.models import User
from apps.search.ai_matching import generate_recommendations_for_user, refresh_recommendations_for_user


class Command(BaseCommand):
    help = 'Generate AI-based partner recommendations for users'

    def add_arguments(self, parser):
        parser.add_argument(
            '--user-email',
            type=str,
            help='Generate recommendations for specific user email',
        )
        parser.add_argument(
            '--refresh',
            action='store_true',
            help='Delete existing recommendations and regenerate',
        )
        parser.add_argument(
            '--all',
            action='store_true',
            help='Generate for all users',
        )

    def handle(self, *args, **options):
        user_email = options.get('user_email')
        refresh = options.get('refresh')
        generate_all = options.get('all')

        if user_email:
            # Generate for specific user
            try:
                user = User.objects.get(email=user_email)
                self.stdout.write(f'Generating recommendations for {user.email}...')
                
                if refresh:
                    count = refresh_recommendations_for_user(user)
                    self.stdout.write(self.style.SUCCESS(
                        f'✓ Refreshed {count} recommendations for {user.email}'
                    ))
                else:
                    count = generate_recommendations_for_user(user)
                    self.stdout.write(self.style.SUCCESS(
                        f'✓ Generated {count} new recommendations for {user.email}'
                    ))
                    
            except User.DoesNotExist:
                self.stdout.write(self.style.ERROR(f'✗ User not found: {user_email}'))
                
        elif generate_all:
            # Generate for all users
            users = User.objects.filter(is_active=True)
            total_count = 0
            success_count = 0
            
            self.stdout.write(f'Generating recommendations for {users.count()} users...\n')
            
            for user in users:
                try:
                    if refresh:
                        count = refresh_recommendations_for_user(user)
                    else:
                        count = generate_recommendations_for_user(user)
                    
                    if count > 0:
                        self.stdout.write(self.style.SUCCESS(
                            f'✓ {user.email}: {count} recommendations'
                        ))
                        success_count += 1
                    else:
                        self.stdout.write(self.style.WARNING(
                            f'⚠ {user.email}: No compatible partners found'
                        ))
                    total_count += count
                    
                except Exception as e:
                    self.stdout.write(self.style.ERROR(
                        f'✗ {user.email}: Error - {str(e)}'
                    ))
            
            self.stdout.write(self.style.SUCCESS(
                f'\n🎉 Generated {total_count} recommendations for {success_count} users'
            ))
            
        else:
            self.stdout.write(self.style.WARNING(
                'Please specify --user-email or --all'
            ))
            self.stdout.write('\nExamples:')
            self.stdout.write('  python manage.py generate_ai_recommendations --user-email testuser1@teamup.com')
            self.stdout.write('  python manage.py generate_ai_recommendations --all')
            self.stdout.write('  python manage.py generate_ai_recommendations --all --refresh')