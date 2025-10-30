# Smart Profile Tagging Feature

## Overview
The Smart Profile Tagging feature uses Google's Gemini AI to automatically generate 2-3 short, descriptive personality tags for user profiles after they complete onboarding.

## What It Does
- **Analyzes** user profile data (sports, availability, location, gender, age)
- **Generates** 2-3 concise personality labels (e.g., "Morning runner · Strength training · Social athlete")
- **Displays** tags on the user's profile page for quick personality insights
- **Lightweight** - runs once during signup, no ongoing AI calls

## Example Outputs
- "Weekend footballer · Weight-loss goal · Beginner level"
- "Morning runner · Team player · Fitness enthusiast"
- "Tennis player · Weekend warrior · Social athlete"

## Implementation Details

### 1. Database Schema
Added `profile_tags` JSONField to `UserProfile` model:
```python
profile_tags = models.JSONField(
    help_text="AI-generated personality tags/labels (2-3 tags)",
    blank=True,
    default=list,
    null=True
)
```

### 2. AI Service Function
Location: `apps/users/utils.py`

**Main Function:** `generate_profile_tags(user_profile)`
- Takes a UserProfile instance
- Builds a prompt from profile data (sports, availability, gender, age, location)
- Calls Gemini API with structured prompt
- Returns list of 2-3 tags
- Falls back to rule-based tags if AI fails

**Fallback Function:** `generate_fallback_tags(user_profile, sports_list)`
- Provides simple tags when AI is unavailable
- Uses sport names and availability patterns
- Ensures users always get some tags

### 3. Integration Point
Location: `apps/users/views.py` - `signup_step4_availability()`

After profile creation:
```python
# Generate AI-powered profile tags
try:
    tags = generate_profile_tags(profile)
    if tags:
        profile.profile_tags = tags
        profile.save(update_fields=['profile_tags'])
except Exception as e:
    # Log error but don't fail signup if tagging fails
    logger.warning(f"Failed to generate profile tags for user {user.id}: {e}")
```

### 4. Display
Location: `templates/users/profile.html`

**Two display locations:**
1. **Under profile name** - Shows as inline text with bullet separators
2. **Basic Information tab** - Shows as colored badges

### 5. Configuration
Uses existing `GEMINI_API_KEY` from settings:
```python
GEMINI_API_KEY = config('GEMINI_API_KEY')
```

Model: Uses `gemini-2.0-flash-exp` (or configured `GEMINI_MODEL` setting)

## Error Handling
- **Non-blocking**: Tag generation errors don't prevent signup
- **Fallback tags**: If AI fails, rule-based tags are generated
- **Logging**: Errors are logged for monitoring
- **Graceful degradation**: Profile works fine without tags

## Testing
To test the feature:

1. **Create a new user** through the signup flow
2. **Complete all steps** (email, password, sports, availability)
3. **Check the profile** - tags should appear under the username
4. **View "Basic Information" tab** - tags shown as badges

## Future Enhancements
Potential improvements:
- Allow users to manually edit/regenerate tags
- Add more profile fields to improve tag quality (fitness goals, experience level)
- Display tags in search results and user cards
- Use tags for better user matching algorithms
- A/B test different prompt strategies for better tags

## API Cost Considerations
- **Frequency**: Once per user at signup
- **Token usage**: ~200 tokens per generation (very low)
- **Cost**: Negligible with Gemini's generous free tier
- **No recurring costs**: Tags are cached, not regenerated

## Privacy
- Tags are generated from existing profile data only
- No external data sources used
- Users can see their own tags on their profile
- Tags are visible to other users (profile is public within the app)
