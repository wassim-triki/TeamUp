from django.core.management.base import BaseCommand
from apps.core.models import Sport


class Command(BaseCommand):
    help = 'Populate the database with a comprehensive list of sports'

    def handle(self, *args, **options):
        sports_data = [
            # Team Sports
            {'name': 'Football', 'emoji': '⚽', 'category': 'team', 'popularity_score': 100},
            {'name': 'Basketball', 'emoji': '🏀', 'category': 'team', 'popularity_score': 95},
            {'name': 'Volleyball', 'emoji': '🏐', 'category': 'team', 'popularity_score': 85},
            {'name': 'Baseball', 'emoji': '⚾', 'category': 'team', 'popularity_score': 80},
            {'name': 'American Football', 'emoji': '🏈', 'category': 'team', 'popularity_score': 75},
            {'name': 'Rugby', 'emoji': '🏉', 'category': 'team', 'popularity_score': 70},
            {'name': 'Hockey', 'emoji': '🏒', 'category': 'team', 'popularity_score': 65},
            {'name': 'Ice Hockey', 'emoji': '🏒', 'category': 'team', 'popularity_score': 60},
            {'name': 'Handball', 'emoji': '🤾', 'category': 'team', 'popularity_score': 55},
            {'name': 'Water Polo', 'emoji': '🤽', 'category': 'team', 'popularity_score': 45},
            
            # Racket Sports
            {'name': 'Tennis', 'emoji': '🎾', 'category': 'racket', 'popularity_score': 90},
            {'name': 'Badminton', 'emoji': '🏸', 'category': 'racket', 'popularity_score': 85},
            {'name': 'Table Tennis', 'emoji': '🏓', 'category': 'racket', 'popularity_score': 80},
            {'name': 'Squash', 'emoji': '🎾', 'category': 'racket', 'popularity_score': 60},
            {'name': 'Racquetball', 'emoji': '🎾', 'category': 'racket', 'popularity_score': 50},
            {'name': 'Padel', 'emoji': '🎾', 'category': 'racket', 'popularity_score': 70},
            {'name': 'Pickleball', 'emoji': '🏓', 'category': 'racket', 'popularity_score': 65},
            
            # Water Sports
            {'name': 'Swimming', 'emoji': '🏊', 'category': 'water', 'popularity_score': 90},
            {'name': 'Surfing', 'emoji': '🏄', 'category': 'water', 'popularity_score': 75},
            {'name': 'Diving', 'emoji': '🤿', 'category': 'water', 'popularity_score': 60},
            {'name': 'Sailing', 'emoji': '⛵', 'category': 'water', 'popularity_score': 55},
            {'name': 'Rowing', 'emoji': '🚣', 'category': 'water', 'popularity_score': 65},
            {'name': 'Kayaking', 'emoji': '🛶', 'category': 'water', 'popularity_score': 70},
            {'name': 'Canoeing', 'emoji': '🛶', 'category': 'water', 'popularity_score': 65},
            {'name': 'Windsurfing', 'emoji': '🏄', 'category': 'water', 'popularity_score': 50},
            {'name': 'Kitesurfing', 'emoji': '🪁', 'category': 'water', 'popularity_score': 55},
            {'name': 'Waterskiing', 'emoji': '🎿', 'category': 'water', 'popularity_score': 50},
            
            # Combat Sports
            {'name': 'Boxing', 'emoji': '🥊', 'category': 'combat', 'popularity_score': 80},
            {'name': 'Karate', 'emoji': '🥋', 'category': 'combat', 'popularity_score': 75},
            {'name': 'Judo', 'emoji': '🥋', 'category': 'combat', 'popularity_score': 70},
            {'name': 'Taekwondo', 'emoji': '🥋', 'category': 'combat', 'popularity_score': 70},
            {'name': 'MMA', 'emoji': '🥊', 'category': 'combat', 'popularity_score': 75},
            {'name': 'Wrestling', 'emoji': '🤼', 'category': 'combat', 'popularity_score': 65},
            {'name': 'Kickboxing', 'emoji': '🥊', 'category': 'combat', 'popularity_score': 70},
            {'name': 'Muay Thai', 'emoji': '🥊', 'category': 'combat', 'popularity_score': 65},
            {'name': 'Brazilian Jiu-Jitsu', 'emoji': '🥋', 'category': 'combat', 'popularity_score': 70},
            {'name': 'Fencing', 'emoji': '🤺', 'category': 'combat', 'popularity_score': 55},
            
            # Individual Sports
            {'name': 'Running', 'emoji': '🏃', 'category': 'individual', 'popularity_score': 95},
            {'name': 'Cycling', 'emoji': '🚴', 'category': 'individual', 'popularity_score': 90},
            {'name': 'Athletics', 'emoji': '🏃', 'category': 'individual', 'popularity_score': 85},
            {'name': 'Marathon', 'emoji': '🏃', 'category': 'individual', 'popularity_score': 75},
            {'name': 'Triathlon', 'emoji': '🏊', 'category': 'individual', 'popularity_score': 70},
            {'name': 'Track and Field', 'emoji': '🏃', 'category': 'individual', 'popularity_score': 70},
            {'name': 'Golf', 'emoji': '⛳', 'category': 'individual', 'popularity_score': 80},
            {'name': 'Bowling', 'emoji': '🎳', 'category': 'individual', 'popularity_score': 70},
            {'name': 'Archery', 'emoji': '🏹', 'category': 'individual', 'popularity_score': 60},
            {'name': 'Shooting', 'emoji': '🔫', 'category': 'individual', 'popularity_score': 55},
            {'name': 'Darts', 'emoji': '🎯', 'category': 'individual', 'popularity_score': 60},
            {'name': 'Billiards', 'emoji': '🎱', 'category': 'individual', 'popularity_score': 65},
            {'name': 'Snooker', 'emoji': '🎱', 'category': 'individual', 'popularity_score': 55},
            {'name': 'Pool', 'emoji': '🎱', 'category': 'individual', 'popularity_score': 60},
            
            # Fitness & Gym
            {'name': 'Gym', 'emoji': '💪', 'category': 'fitness', 'popularity_score': 95},
            {'name': 'Yoga', 'emoji': '🧘', 'category': 'fitness', 'popularity_score': 90},
            {'name': 'Pilates', 'emoji': '🧘', 'category': 'fitness', 'popularity_score': 80},
            {'name': 'CrossFit', 'emoji': '🏋️', 'category': 'fitness', 'popularity_score': 85},
            {'name': 'Weightlifting', 'emoji': '🏋️', 'category': 'fitness', 'popularity_score': 80},
            {'name': 'Bodybuilding', 'emoji': '💪', 'category': 'fitness', 'popularity_score': 75},
            {'name': 'Powerlifting', 'emoji': '🏋️', 'category': 'fitness', 'popularity_score': 70},
            {'name': 'Aerobics', 'emoji': '🤸', 'category': 'fitness', 'popularity_score': 75},
            {'name': 'Zumba', 'emoji': '💃', 'category': 'fitness', 'popularity_score': 80},
            {'name': 'Spinning', 'emoji': '🚴', 'category': 'fitness', 'popularity_score': 75},
            {'name': 'HIIT', 'emoji': '🏃', 'category': 'fitness', 'popularity_score': 80},
            {'name': 'Calisthenics', 'emoji': '🤸', 'category': 'fitness', 'popularity_score': 75},
            
            # Outdoor Activities
            {'name': 'Hiking', 'emoji': '🥾', 'category': 'outdoor', 'popularity_score': 85},
            {'name': 'Mountain Biking', 'emoji': '🚵', 'category': 'outdoor', 'popularity_score': 80},
            {'name': 'Rock Climbing', 'emoji': '🧗', 'category': 'outdoor', 'popularity_score': 75},
            {'name': 'Bouldering', 'emoji': '🧗', 'category': 'outdoor', 'popularity_score': 70},
            {'name': 'Skiing', 'emoji': '⛷️', 'category': 'outdoor', 'popularity_score': 75},
            {'name': 'Snowboarding', 'emoji': '🏂', 'category': 'outdoor', 'popularity_score': 75},
            {'name': 'Skateboarding', 'emoji': '🛹', 'category': 'outdoor', 'popularity_score': 70},
            {'name': 'Rollerblading', 'emoji': '⛸️', 'category': 'outdoor', 'popularity_score': 65},
            {'name': 'Ice Skating', 'emoji': '⛸️', 'category': 'outdoor', 'popularity_score': 70},
            {'name': 'Parkour', 'emoji': '🤸', 'category': 'outdoor', 'popularity_score': 65},
            {'name': 'Trail Running', 'emoji': '🏃', 'category': 'outdoor', 'popularity_score': 75},
            {'name': 'Camping', 'emoji': '🏕️', 'category': 'outdoor', 'popularity_score': 70},
            
            # Other Sports
            {'name': 'Gymnastics', 'emoji': '🤸', 'category': 'other', 'popularity_score': 75},
            {'name': 'Cheerleading', 'emoji': '📣', 'category': 'other', 'popularity_score': 65},
            {'name': 'Dance', 'emoji': '💃', 'category': 'other', 'popularity_score': 80},
            {'name': 'Figure Skating', 'emoji': '⛸️', 'category': 'other', 'popularity_score': 70},
            {'name': 'Horse Riding', 'emoji': '🏇', 'category': 'other', 'popularity_score': 65},
            {'name': 'Polo', 'emoji': '🏇', 'category': 'other', 'popularity_score': 50},
            {'name': 'Skateboarding', 'emoji': '🛹', 'category': 'other', 'popularity_score': 70},
            {'name': 'BMX', 'emoji': '🚴', 'category': 'other', 'popularity_score': 65},
            {'name': 'Parkour', 'emoji': '🤸', 'category': 'other', 'popularity_score': 65},
            {'name': 'Cricket', 'emoji': '🏏', 'category': 'team', 'popularity_score': 85},
            {'name': 'Other', 'emoji': '🎯', 'category': 'other', 'popularity_score': 50},
        ]

        created_count = 0
        updated_count = 0
        
        for sport_data in sports_data:
            sport, created = Sport.objects.get_or_create(
                name=sport_data['name'],
                defaults={
                    'emoji': sport_data['emoji'],
                    'category': sport_data['category'],
                    'popularity_score': sport_data['popularity_score'],
                }
            )
            
            if created:
                created_count += 1
                self.stdout.write(
                    self.style.SUCCESS(f'✓ Created: {sport}')
                )
            else:
                # Update existing sport
                sport.emoji = sport_data['emoji']
                sport.category = sport_data['category']
                sport.popularity_score = sport_data['popularity_score']
                sport.save()
                updated_count += 1
                self.stdout.write(
                    self.style.WARNING(f'↻ Updated: {sport}')
                )
        
        self.stdout.write(
            self.style.SUCCESS(
                f'\n✓ Successfully populated sports database!'
                f'\n  Created: {created_count}'
                f'\n  Updated: {updated_count}'
                f'\n  Total: {Sport.objects.count()}'
            )
        )
