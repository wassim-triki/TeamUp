# User Availability System

## Overview

The availability system allows users to select predefined time patterns that work best for them. This makes it easy to match users with similar schedules without requiring tedious manual input.

## Available Patterns

Users can select from the following availability patterns:

1. **Weekday Mornings** - 6 AM - 12 PM on weekdays
2. **Weekday Afternoons** - 12 PM - 6 PM on weekdays
3. **Weekday Evenings** - 6 PM - 10 PM on weekdays
4. **Weekend Mornings** - 6 AM - 12 PM on weekends
5. **Weekend Afternoons** - 12 PM - 6 PM on weekends
6. **Weekend Evenings** - 6 PM - 10 PM on weekends
7. **Flexible Schedule** - Available most times

## Features

### User-Friendly Selection
- Clean checkbox-based interface
- Select multiple patterns
- Visual cards with descriptions
- Mobile-friendly design

### Data Structure

Availability is stored as a JSON array in the database:

```python
# Example
user_profile.availability = ['weekday_evenings', 'weekend_mornings', 'flexible']
```

### Matching Algorithm

The system includes a matching algorithm to find users with compatible schedules:

```python
from apps.users.utils import calculate_availability_match, get_compatible_users

# Calculate match score between two users (0-100)
score = calculate_availability_match(user1.availability, user2.availability)

# Find compatible users for a given user
matches = get_compatible_users(user_profile, min_score=30, limit=10)
# Returns: [(user_profile, score), ...]
```

### Matching Logic

- **Direct Overlap**: Users with common patterns get higher scores
- **Flexible Priority**: Users with "Flexible Schedule" match well with everyone (score: 90)
- **Jaccard Similarity**: Uses intersection over union to calculate match percentage
- **Minimum Score**: Default minimum match score is 30%

## Usage Examples

### Display Availability

```python
# In a template
{{ user.userprofile.get_availability_display }}

# In Python
from apps.users.utils import format_availability_for_display
display_text = format_availability_for_display(user.userprofile.availability)
```

### Find Compatible Users

```python
from apps.users.utils import get_compatible_users

# Get top 10 compatible users with at least 30% match
compatible_users = get_compatible_users(request.user.userprofile, min_score=30, limit=10)

for user_profile, match_score in compatible_users:
    print(f"{user_profile.full_name}: {match_score}% match")
```

### Manual Match Calculation

```python
from apps.users.utils import calculate_availability_match

user1_availability = ['weekday_evenings', 'weekend_mornings']
user2_availability = ['weekday_evenings', 'weekday_afternoons']

score = calculate_availability_match(user1_availability, user2_availability)
# Returns: 33 (1 out of 3 unique patterns match)
```

## Integration Points

### Signup Flow

- **Step 4** of the signup process now uses checkbox-based availability selection
- Template: `templates/users/signup_step4_minimal.html`
- View: `apps/users/views.py` - `signup_step4_availability()`

### User Profile

- Availability patterns are stored in `UserProfile.availability`
- Access patterns via `UserProfile.get_availability_choices()`
- Display formatted text via `UserProfile.get_availability_display()`

### Session Matching

When creating sports sessions, you can now match users based on:
1. Sport interest (existing feature)
2. Availability patterns (new feature)
3. Location/proximity (if implemented)

## Migration

The system includes automatic migration from text-based availability to pattern-based:

```bash
python manage.py migrate users
```

The migration (`0008_change_availability_to_jsonfield.py`) will:
- Convert existing text availability to patterns based on keywords
- Default to 'flexible' if no patterns are detected
- Support rollback if needed

## Extending the System

### Adding New Patterns

To add new availability patterns:

1. Update `UserProfile.AVAILABILITY_PATTERNS` in `apps/users/models.py`
2. Create a new migration
3. Update templates if needed

```python
AVAILABILITY_PATTERNS = [
    # ... existing patterns ...
    ('late_night', 'Late Night', '10 PM - 2 AM'),  # New pattern
]
```

### Custom Matching Logic

You can customize the matching algorithm in `apps/users/utils.py`:

- Adjust weights for different patterns
- Add time zone considerations
- Include additional factors (location, skill level, etc.)

## Benefits

✅ **Simple for users** - Takes 5-10 seconds to complete  
✅ **Structured data** - Easy to query and filter  
✅ **Scalable** - Can add more patterns without breaking existing data  
✅ **Match-friendly** - Enables intelligent user matching  
✅ **Flexible** - Users can select multiple time slots  

## Future Enhancements

Potential improvements:
- Time zone support
- Recurring availability (e.g., "Every Tuesday evening")
- Temporary availability updates
- Availability calendar view
- Push notifications for matches
