"""
Management command to generate or regenerate AI profile tags for users.
Usage: python manage.py generate_profile_tags [--user-id USER_ID] [--all]
"""

from django.core.management.base import BaseCommand
from django.db import transaction
from apps.users.models import UserProfile
from apps.users.utils import generate_profile_tags


class Command(BaseCommand):
    help = 'Generate or regenerate AI profile tags for user profiles'

    def add_arguments(self, parser):
        parser.add_argument(
            '--user-id',
            type=int,
            help='Generate tags for a specific user ID',
        )
        parser.add_argument(
            '--all',
            action='store_true',
            help='Generate tags for all users without tags',
        )
        parser.add_argument(
            '--force',
            action='store_true',
            help='Regenerate tags even if they already exist',
        )

    def handle(self, *args, **options):
        user_id = options.get('user_id')
        process_all = options.get('all')
        force = options.get('force')

        if user_id:
            # Process specific user
            try:
                profile = UserProfile.objects.get(user_id=user_id)
                self._generate_tags_for_profile(profile, force)
            except UserProfile.DoesNotExist:
                self.stdout.write(
                    self.style.ERROR(f'User profile with ID {user_id} not found')
                )
        elif process_all:
            # Process all users
            if force:
                profiles = UserProfile.objects.filter(user__is_active=True)
                self.stdout.write(f'Regenerating tags for {profiles.count()} active users...')
            else:
                profiles = UserProfile.objects.filter(
                    user__is_active=True,
                    profile_tags__isnull=True
                ) | UserProfile.objects.filter(
                    user__is_active=True,
                    profile_tags=[]
                )
                self.stdout.write(f'Generating tags for {profiles.count()} users without tags...')

            success_count = 0
            error_count = 0

            for profile in profiles:
                try:
                    self._generate_tags_for_profile(profile, force, verbose=False)
                    success_count += 1
                except Exception as e:
                    error_count += 1
                    self.stdout.write(
                        self.style.WARNING(
                            f'Failed for user {profile.user.id}: {str(e)[:50]}'
                        )
                    )

            self.stdout.write(
                self.style.SUCCESS(
                    f'Completed: {success_count} successful, {error_count} failed'
                )
            )
        else:
            self.stdout.write(
                self.style.WARNING(
                    'Please specify --user-id USER_ID or --all'
                )
            )

    def _generate_tags_for_profile(self, profile, force=False, verbose=True):
        """Generate tags for a single profile."""
        user = profile.user
        
        if profile.profile_tags and not force:
            if verbose:
                self.stdout.write(
                    self.style.WARNING(
                        f'User {user.id} ({user.email}) already has tags. Use --force to regenerate.'
                    )
                )
            return

        if verbose:
            self.stdout.write(f'Generating tags for user {user.id} ({user.email})...')

        tags = generate_profile_tags(profile)
        
        if tags:
            profile.profile_tags = tags
            profile.save(update_fields=['profile_tags'])
            
            if verbose:
                self.stdout.write(
                    self.style.SUCCESS(
                        f'✓ Generated tags: {" · ".join(tags)}'
                    )
                )
        else:
            if verbose:
                self.stdout.write(
                    self.style.WARNING(
                        f'✗ No tags generated for user {user.id}'
                    )
                )
