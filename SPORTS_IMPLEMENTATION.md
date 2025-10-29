# Sports Management System - Implementation Guide

## Overview

We've implemented a comprehensive, database-driven sports management system that replaces hardcoded checkboxes with a dynamic, searchable, and scalable solution.

## What Was Implemented

### 1. **Sport Model** (`apps/core/models.py`)
- Centralized database model for all sports
- Fields:
  - `name`: Sport name
  - `slug`: URL-friendly identifier
  - `emoji`: Visual icon
  - `description`: Optional details
  - `category`: Classification (team, individual, racket, water, combat, fitness, outdoor, other)
  - `popularity_score`: For sorting and recommendations
  - `is_active`: Toggle visibility
- 84 sports pre-populated in database

### 2. **UserProfile Integration**
- Added `interested_sports` ManyToMany field
- Maintains backward compatibility with old `sports` TextField
- Users can now have unlimited sports selections
- Easy to query users by sport interests

### 3. **API Endpoints** (`apps/api/views.py`)
- **`/api/sports/search/`**: Search and filter sports
  - Query params: `q` (search), `category`, `limit`, `offset`
  - Returns JSON with sport details
- **`/api/sports/categories/`**: Get all sport categories

### 4. **Enhanced Signup UI** (`templates/users/signup_step2_minimal.html`)

#### Features:
- **Search Bar**: Real-time sport search as you type
- **Category Filters**: Quick filter by sport type (Team, Racket, Fitness, etc.)
- **Dual Display**:
  - **Selected Sports**: Top section showing chosen sports (with × to remove)
  - **Available Sports**: Bottom section showing selectable sports
- **Bumble-Style Capsules**: Beautiful, animated pill-shaped buttons
- **Real-time Validation**: Instant feedback on selection
- **Responsive Design**: Works on all screen sizes

#### User Experience:
1. Type in search bar to find specific sports
2. Click category buttons to filter by type
3. Click any sport capsule to select it
4. Selected sports move to the top with blue gradient
5. Click × on selected sports to deselect
6. Minimum 1 sport required to proceed

### 5. **Management Command**
```bash
python manage.py populate_sports
```
- Populates database with 84 sports
- Updates existing sports if re-run
- Organized by categories with popularity scores

### 6. **Admin Interface**
- Full CRUD operations for sports
- Filter by category and active status
- Search by name and description
- Bulk edit popularity scores and active status

## Database Schema

### Sport Model
```
id              : Integer (PK)
name            : String(100) UNIQUE
slug            : String(100) UNIQUE
emoji           : String(10)
description     : Text
is_active       : Boolean
category        : String(50)
popularity_score: Integer
created_at      : DateTime
updated_at      : DateTime
```

### UserProfile Changes
```
interested_sports : ManyToMany → Sport
sports           : TextField (deprecated, for migration)
```

## Sport Categories

1. **Team Sports** (10): Football, Basketball, Volleyball, Baseball, Rugby, Hockey, etc.
2. **Racket Sports** (7): Tennis, Badminton, Table Tennis, Squash, Padel, etc.
3. **Water Sports** (10): Swimming, Surfing, Kayaking, Rowing, Sailing, etc.
4. **Combat Sports** (10): Boxing, MMA, Karate, Judo, Wrestling, etc.
5. **Individual Sports** (14): Running, Cycling, Golf, Archery, Bowling, etc.
6. **Fitness & Gym** (12): Gym, Yoga, CrossFit, Pilates, HIIT, Zumba, etc.
7. **Outdoor Activities** (12): Hiking, Skiing, Rock Climbing, Skateboarding, etc.
8. **Other** (9): Dance, Gymnastics, Cricket, Horse Riding, etc.

## Future Features to Add

### For Users:
1. **Sport Skill Levels**: Beginner, Intermediate, Advanced per sport
2. **Favorite Sports**: Pin top 3 sports to profile
3. **Sport Recommendations**: AI-based suggestions
4. **Sport Stats**: Track sessions per sport

### For Admin:
1. **Sport Images**: Upload custom images alongside emojis
2. **Sport Aliases**: Alternative names for better search
3. **Seasonal Sports**: Mark sports by season
4. **Equipment List**: Link required equipment to sports

### For Sessions:
1. **Filter by Sport**: Find sessions by sport type
2. **Sport-Specific Fields**: Custom fields per sport (court type, skill level, etc.)
3. **Sport Communities**: Groups dedicated to specific sports

## API Usage Examples

### Search Sports
```javascript
// Search for "foot"
fetch('/api/sports/search/?q=foot')
  .then(res => res.json())
  .then(data => console.log(data.results));

// Filter by category
fetch('/api/sports/search/?category=fitness&limit=50')
  .then(res => res.json())
  .then(data => console.log(data.results));
```

### Get Categories
```javascript
fetch('/api/sports/categories/')
  .then(res => res.json())
  .then(data => console.log(data.categories));
```

## Migration Notes

### Existing Users
- Old `sports` TextField data is preserved
- Need to create a data migration to convert old sports to new ManyToMany
- Can run both systems in parallel during transition

### Recommended Data Migration
```python
# Future: apps/users/migrations/0008_migrate_sports_data.py
def migrate_sports_data(apps, schema_editor):
    UserProfile = apps.get_model('users', 'UserProfile')
    Sport = apps.get_model('core', 'Sport')
    
    for profile in UserProfile.objects.all():
        if profile.sports:
            sport_slugs = json.loads(profile.sports)
            for slug in sport_slugs:
                sport = Sport.objects.filter(slug=slug).first()
                if sport:
                    profile.interested_sports.add(sport)
```

## Benefits of This Approach

1. ✅ **Scalable**: Add unlimited sports without code changes
2. ✅ **Maintainable**: Update sports via admin panel
3. ✅ **Searchable**: Users can quickly find specific sports
4. ✅ **Professional**: Modern, intuitive UI
5. ✅ **Data-Rich**: Analytics on sport popularity
6. ✅ **Flexible**: Easy to add new categories or fields
7. ✅ **API-Ready**: Sports available for mobile apps
8. ✅ **Future-Proof**: Easy to extend functionality

## Files Modified/Created

### Created:
- `apps/core/models.py` - Sport model
- `apps/core/admin.py` - Sport admin
- `apps/core/management/commands/populate_sports.py` - Data seeder
- `apps/api/views.py` - API endpoints
- `SPORTS_IMPLEMENTATION.md` - This documentation

### Modified:
- `apps/users/models.py` - Added interested_sports ManyToMany field
- `apps/api/urls.py` - Added sport API routes
- `templates/users/signup_step2_minimal.html` - Complete UI overhaul

### Migrations:
- `apps/core/migrations/0001_initial.py` - Sport model
- `apps/users/migrations/0007_userprofile_interested_sports_and_more.py` - UserProfile update

## Testing Checklist

- [x] Sports load from database
- [ ] Search functionality works
- [ ] Category filters work
- [ ] Sports can be selected/deselected
- [ ] Form validation works (minimum 1 sport)
- [ ] Selected sports persist on validation errors
- [ ] Sports are saved to user profile
- [ ] Admin interface works
- [ ] API endpoints return correct data
- [ ] Mobile responsive design

## Next Steps

1. Test the signup flow end-to-end
2. Create data migration for existing users
3. Update profile edit page with same UI
4. Add sports filter to session list
5. Implement sport-based matching algorithm
6. Add sport statistics to user dashboard
