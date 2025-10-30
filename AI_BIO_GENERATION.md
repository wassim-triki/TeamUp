# AI Bio Generation Feature

## Overview
Added an AI-powered bio generation button to the profile edit page that creates a personalized bio based on the user's profile information.

## What It Does
- **Analyzes** user profile data (name, sports, availability, location, age, gender, tags)
- **Generates** a friendly, engaging 2-3 sentence bio in first person
- **One-click** generation directly in the edit profile form
- **Smart fallback** - provides simple bio if AI fails

## Location
**Edit Profile Page**: `/users/profile/edit/`
- Button appears next to the "Bio" field label
- Click "Generate with AI" button
- Bio is automatically filled in the textarea

## Example Outputs

**Input Profile:**
```
Name: Sarah Johnson
Sports: Running, Yoga
Availability: Weekend mornings
Age: 28
Location: San Francisco, CA
```

**Generated Bio:**
```
I'm Sarah, passionate about running and yoga. I'm usually free on weekend mornings 
for sports and fitness activities. Looking forward to connecting with fellow athletes 
and exploring new fitness challenges in the San Francisco area!
```

## Implementation Details

### 1. Frontend (profile_edit.html)
- **Button**: Sparkling icon + "Generate with AI" text
- **AJAX call**: Fetches bio from backend endpoint
- **Loading state**: Shows spinner while generating
- **Toast notifications**: Success/error messages

### 2. Backend Function (apps/users/utils.py)
**Main Function:** `generate_user_bio(user_profile)`
- Collects all profile information
- Creates contextual prompt for Gemini
- Returns 2-3 sentence bio in first person
- Falls back to template-based bio if AI fails

**Fallback Function:** `generate_fallback_bio(user_profile, sports_list)`
- Simple template-based bio
- Uses sports and availability
- Always succeeds

### 3. API Endpoint (apps/users/views.py)
**URL:** `/users/profile/generate-bio/`
**Method:** POST
**Auth:** Login required
**Response:**
```json
{
  "success": true,
  "bio": "Generated bio text here..."
}
```

### 4. URL Configuration (apps/users/urls.py)
```python
path('profile/generate-bio/', views.generate_bio, name='generate_bio'),
```

## Design Features
- ✨ Soft primary button style matching UI
- 🎯 Sparkling icon (`ri-sparkling-line`) for AI feature
- ⚡ Instant feedback with loading spinner
- 📱 Responsive button layout
- 🎭 Clean toast notifications

## Prompt Engineering

The AI prompt is designed to:
- Write in **first person** for authenticity
- Be **enthusiastic and approachable**
- Mention **main sports interests and availability**
- Keep it **natural and conversational**
- Limit to **150 words max**
- No hashtags or emojis

## Error Handling
- **Non-blocking**: Errors don't crash the page
- **User feedback**: Clear error messages via toast
- **Fallback bio**: Always provides something usable
- **Logging**: Errors logged for debugging

## Configuration
Uses existing `GEMINI_API_KEY` from settings:
```python
GEMINI_API_KEY = config('GEMINI_API_KEY')
```

Model: `gemini-2.0-flash-exp` (or configured `GEMINI_MODEL`)

## Usage

1. **Go to Edit Profile**: Click "Edit Profile" from your profile
2. **Scroll to Bio section**: Find the bio textarea
3. **Click "Generate with AI"**: Button next to the label
4. **Wait for generation**: 2-3 seconds typically
5. **Review and edit**: Bio appears in textarea
6. **Save changes**: Click "Save Changes" to persist

## API Cost
- **Frequency**: On-demand (user clicks button)
- **Token usage**: ~250 tokens per generation
- **Cost**: Negligible with Gemini's free tier
- **No auto-generation**: Only when user requests

## Benefits

1. **Saves time**: No need to write bio from scratch
2. **Professional**: Well-structured, engaging text
3. **Personalized**: Based on actual profile data
4. **Editable**: User can modify generated text
5. **Optional**: Users can still write their own

## Future Enhancements

- Add "Regenerate" option for multiple variations
- Allow tone selection (professional/casual/funny)
- Add length preferences (short/medium/long)
- Include recent session history in context
- Multi-language support
- Save generated bios as drafts

## Testing

```bash
# Test the generation endpoint
curl -X POST http://localhost:8000/users/profile/generate-bio/ \
  -H "Cookie: sessionid=YOUR_SESSION_ID" \
  -H "X-CSRFToken: YOUR_CSRF_TOKEN"
```

Or simply:
1. Login to your account
2. Go to Edit Profile
3. Click "Generate with AI" button
4. Check if bio appears in textarea

## Privacy & Data Usage
- Only uses profile data already in the database
- No external data sources
- Bio is not automatically saved (user must save)
- User can edit or delete generated bio
- Complies with existing privacy policies
