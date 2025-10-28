from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from search.models import UserProfile, PartnerRecommendation
import random

class Command(BaseCommand):
    help = 'Generates test data for search functionality'

    def handle(self, *args, **kwargs):
        self.stdout.write('Generating test data...')
        
        # Sample data
        sports_list = ['Football', 'Basketball', 'Tennis', 'Running', 'Cycling', 'Swimming', 'Volleyball', 'Badminton']
        levels = ['beginner', 'intermediate', 'advanced', 'expert']
        goals = ['weight loss', 'competition', 'muscle building', 'wellness', 'social']
        locations = [
            ('Paris', 48.8566, 2.3522),
            ('Lyon', 45.7640, 4.8357),
            ('Marseille', 43.2965, 5.3698),
            ('Toulouse', 43.6047, 1.4442),
            ('Nice', 43.7102, 7.2620),
        ]
        
        bios = [
            "Sports enthusiast looking to improve and meet new people!",
            "I love sports and making new connections.",
            "Available for regular sessions.",
            "Casual athlete ready to get more involved.",
            "Competitive spirit, always up for challenges.",
            "Sports = wellness for me. Always motivated!",
            "Beginner but very motivated to learn.",
            "I've been practicing for years, happy to coach.",
        ]
        
        # Create test users
        for i in range(1, 21):
            username = f'user{i}'
            
            # Check if user exists
            if not User.objects.filter(username=username).exists():
                user = User.objects.create_user(
                    username=username,
                    email=f'user{i}@teamup.com',
                    password='testpass123',
                    first_name=f'User{i}',
                    last_name='Test'
                )
                
                # Create profile
                location = random.choice(locations)
                selected_sports = random.sample(sports_list, k=random.randint(1, 4))
                selected_goals = random.sample(goals, k=random.randint(1, 3))
                
                profile = UserProfile.objects.create(
                    user=user,
                    sports=selected_sports,
                    level=random.choice(levels),
                    location=location[0],
                    latitude=location[1] + random.uniform(-0.1, 0.1),
                    longitude=location[2] + random.uniform(-0.1, 0.1),
                    goals=selected_goals,
                    bio=random.choice(bios),
                    availability={
                        'monday': ['08:00-10:00', '18:00-20:00'],
                        'wednesday': ['18:00-20:00'],
                        'saturday': ['09:00-12:00']
                    }
                )
                
                self.stdout.write(self.style.SUCCESS(f'Created user: {username}'))
        
        # Generate recommendations for first user if exists
        try:
            main_user = User.objects.get(username='user1')
            other_users = User.objects.exclude(username='user1')[:10]
            
            for other_user in other_users:
                if not PartnerRecommendation.objects.filter(
                    user=main_user, 
                    recommended_user=other_user
                ).exists():
                    match_score = random.randint(60, 95)
                    
                    PartnerRecommendation.objects.create(
                        user=main_user,
                        recommended_user=other_user,
                        match_score=match_score,
                        explanation={
                            'sport_match': random.choice([True, False]),
                            'level_compatible': random.choice([True, False]),
                            'distance_km': round(random.uniform(1, 10), 1)
                        },
                        reasons=[
                            'Same sport practiced',
                            'Compatible level',
                            'Similar availability',
                            'Common goals'
                        ][:random.randint(2, 4)]
                    )
            
            self.stdout.write(self.style.SUCCESS('Generated recommendations'))
        except User.DoesNotExist:
            pass
        
        self.stdout.write(self.style.SUCCESS('Test data generation complete!'))
        self.stdout.write(self.style.WARNING('Test credentials: username=user1, password=testpass123'))