from django.core.management.base import BaseCommand
from apps.users.models import User, UserProfile
from apps.search.models import PartnerRecommendation
import random
import json


class Command(BaseCommand):
    help = 'Generates test data for search functionality'

    def handle(self, *args, **kwargs):
        self.stdout.write('Generating test data...')
        
        # Sample data
        sports_list = ['Football', 'Basketball', 'Tennis', 'Running', 'Cycling', 'Swimming', 'Volleyball', 'Badminton', 'Gym/Fitness', 'Yoga']
        genders = ['male', 'female']
        countries = ['TN', 'FR', 'DE', 'US', 'GB', 'ES', 'IT', 'MA', 'DZ', 'EG']
        cities = {
            'TN': ['Tunis', 'Sfax', 'Sousse', 'Bizerte', 'Gabès'],
            'FR': ['Paris', 'Lyon', 'Marseille', 'Toulouse', 'Nice'],
            'DE': ['Berlin', 'Munich', 'Hamburg', 'Frankfurt', 'Cologne'],
            'US': ['New York', 'Los Angeles', 'Chicago', 'Houston', 'Miami'],
            'GB': ['London', 'Manchester', 'Birmingham', 'Liverpool', 'Leeds'],
            'ES': ['Madrid', 'Barcelona', 'Valencia', 'Seville', 'Bilbao'],
            'IT': ['Rome', 'Milan', 'Naples', 'Turin', 'Florence'],
            'MA': ['Casablanca', 'Rabat', 'Marrakech', 'Fes', 'Tangier'],
            'DZ': ['Algiers', 'Oran', 'Constantine', 'Annaba', 'Blida'],
            'EG': ['Cairo', 'Alexandria', 'Giza', 'Sharm El-Sheikh', 'Luxor']
        }
        
        availabilities = [
            'Mornings (6am-12pm)',
            'Afternoons (12pm-6pm)', 
            'Evenings (6pm-10pm)',
            'Weekends',
            'Flexible - All times',
            'Weekday mornings',
            'Weekday evenings',
            'Weekend mornings'
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
            "Looking for workout buddies to stay accountable.",
            "Fitness is my passion, let's train together!",
            "New to the area, excited to meet sports partners.",
            "Love team sports and outdoor activities.",
        ]
        
        first_names_male = ['Ahmed', 'Mohamed', 'Ali', 'Omar', 'Youssef', 'Karim', 'Hassan', 'Tarek', 'Rami', 'Fadi', 'John', 'Michael', 'David', 'James', 'Robert']
        first_names_female = ['Fatima', 'Aisha', 'Mariam', 'Nour', 'Lina', 'Sara', 'Yasmine', 'Amira', 'Hiba', 'Salma', 'Emma', 'Olivia', 'Sophie', 'Emily', 'Isabella']
        last_names = ['Ben Ali', 'Kassem', 'Mansour', 'Khalil', 'Saad', 'Mustafa', 'Ibrahim', 'Hassan', 'Smith', 'Johnson', 'Williams', 'Brown', 'Garcia', 'Martinez', 'Lopez']
        
        # Create test users
        created_count = 0
        for i in range(1, 26):  # Create 25 test users
            email = f'testuser{i}@teamup.com'
            
            # Check if user exists
            if User.objects.filter(email=email).exists():
                self.stdout.write(self.style.WARNING(f'User already exists: {email}'))
                continue
            
            try:
                # Random gender
                gender = random.choice(genders)
                
                # Select first name based on gender
                if gender == 'male':
                    first_name = random.choice(first_names_male)
                else:
                    first_name = random.choice(first_names_female)
                
                last_name = random.choice(last_names)
                
                # Create user (will auto-generate username)
                user = User.objects.create_user(
                    email=email,
                    password='testpass123'
                )
                
                # Activate user (skip email verification for test users)
                user.is_active = True
                user.save()
                
                # Select random country and matching city
                country = random.choice(countries)
                city = random.choice(cities[country])
                
                # Select random sports (1-4 sports per person)
                selected_sports = random.sample(sports_list, k=random.randint(1, 4))
                
                # Create profile
                profile = UserProfile.objects.create(
                    user=user,
                    first_name=first_name,
                    last_name=last_name,
                    gender=gender,
                    country=country,
                    city=city,
                    sports=json.dumps(selected_sports),
                    availability=random.choice(availabilities),
                    bio=random.choice(bios),
                    age=random.randint(18, 55)
                )
                
                created_count += 1
                self.stdout.write(self.style.SUCCESS(f'✓ Created: {email} - {first_name} {last_name} ({gender}, {country}, {len(selected_sports)} sports)'))
                
            except Exception as e:
                self.stdout.write(self.style.ERROR(f'✗ Error creating {email}: {str(e)}'))
        
        self.stdout.write(self.style.SUCCESS(f'\n{created_count} users created successfully!'))
        
        # Generate recommendations for first 3 users
        self.stdout.write('\nGenerating AI recommendations...')
        
        try:
            # Get first 3 users
            main_users = User.objects.filter(email__in=[
                'testuser1@teamup.com',
                'testuser2@teamup.com',
                'testuser3@teamup.com'
            ])
            
            for main_user in main_users:
                # Get other users to recommend
                other_users = User.objects.exclude(email=main_user.email)[:8]
                
                for other_user in other_users:
                    # Check if recommendation already exists
                    if PartnerRecommendation.objects.filter(
                        user=main_user, 
                        recommended_user=other_user
                    ).exists():
                        continue
                    
                    # Generate random match score
                    match_score = random.randint(65, 95)
                    
                    # Create recommendation
                    PartnerRecommendation.objects.create(
                        user=main_user,
                        recommended_user=other_user,
                        match_score=match_score,
                        explanation={
                            'sport_match': random.choice([True, False]),
                            'level_compatible': random.choice([True, False]),
                            'distance_km': round(random.uniform(0.5, 15), 1)
                        },
                        reasons=random.sample([
                            'Same sport practiced',
                            'Compatible level',
                            'Similar availability',
                            'Common goals',
                            'Lives nearby',
                            'Similar age group'
                        ], k=random.randint(2, 4))
                    )
            
            self.stdout.write(self.style.SUCCESS('✓ Recommendations generated'))
        except Exception as e:
            self.stdout.write(self.style.WARNING(f'Could not generate recommendations: {str(e)}'))
        
        # Summary
        self.stdout.write(self.style.SUCCESS('\n' + '='*60))
        self.stdout.write(self.style.SUCCESS('🎉 TEST DATA GENERATION COMPLETE!'))
        self.stdout.write(self.style.SUCCESS('='*60))
        self.stdout.write('\n📧 Test Login Credentials:')
        self.stdout.write('   Email: testuser1@teamup.com (or testuser2, testuser3, etc.)')
        self.stdout.write('   Password: testpass123')
        self.stdout.write('\n🔗 URLs to test:')
        self.stdout.write('   Search Partners: http://127.0.0.1:8000/search/')
        self.stdout.write('   Recommendations: http://127.0.0.1:8000/search/recommendations/')
        self.stdout.write('   Search History:  http://127.0.0.1:8000/search/history/')
        self.stdout.write('\n💡 Tip: Login first at /accounts/login/ to see full features!\n')