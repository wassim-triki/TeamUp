# Generated migration for availability field update

from django.db import migrations, models
import json


def safe_text_to_json_conversion(apps, schema_editor):
    """Safely convert text availability to JSON list format."""
    UserProfile = apps.get_model('users', 'UserProfile')
    
    keyword_mapping = {
        'weekday morning': 'weekday_mornings',
        'weekday afternoon': 'weekday_afternoons',
        'weekday evening': 'weekday_evenings',
        'weekend morning': 'weekend_mornings',
        'weekend afternoon': 'weekend_afternoons',
        'weekend evening': 'weekend_evenings',
        'flexible': 'flexible',
        'any time': 'flexible',
        'anytime': 'flexible',
        'most times': 'flexible',
    }
    
    for profile in UserProfile.objects.all():
        old_value = profile.availability
        
        if not old_value or old_value == '':
            profile.availability = '[]'
        elif old_value.startswith('['):
            continue
        else:
            text = old_value.lower()
            patterns = []
            
            for keyword, pattern in keyword_mapping.items():
                if keyword in text:
                    if pattern not in patterns:
                        patterns.append(pattern)
            
            if not patterns:
                patterns = ['flexible']
            
            profile.availability = json.dumps(patterns)
        
        profile.save()


def reverse_json_to_text(apps, schema_editor):
    """Convert JSON patterns back to readable text."""
    UserProfile = apps.get_model('users', 'UserProfile')
    
    pattern_names = {
        'weekday_mornings': 'Weekday Mornings',
        'weekday_afternoons': 'Weekday Afternoons',
        'weekday_evenings': 'Weekday Evenings',
        'weekend_mornings': 'Weekend Mornings',
        'weekend_afternoons': 'Weekend Afternoons',
        'weekend_evenings': 'Weekend Evenings',
        'flexible': 'Flexible Schedule',
    }
    
    for profile in UserProfile.objects.all():
        old_value = profile.availability
        
        if not old_value:
            profile.availability = ''
        elif isinstance(old_value, str) and old_value.startswith('['):
            try:
                patterns = json.loads(old_value)
                if isinstance(patterns, list):
                    text_parts = [pattern_names.get(code, code) for code in patterns]
                    profile.availability = ', '.join(text_parts)
            except json.JSONDecodeError:
                profile.availability = 'Flexible Schedule'
        
        profile.save()


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0007_userprofile_interested_sports_and_more'),
    ]

    operations = [
        migrations.RunPython(safe_text_to_json_conversion, reverse_json_to_text),
        migrations.AlterField(
            model_name='userprofile',
            name='availability',
            field=models.JSONField(
                blank=True,
                default=list,
                help_text="User's availability patterns",
                null=True
            ),
        ),
    ]
