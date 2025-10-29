# 4-Step Signup Flow Restructuring - Complete

## Overview
Successfully restructured the signup process from 3 steps to 4 steps, separating sports selection and availability into distinct steps for a cleaner, more focused user experience.

## New Signup Flow Structure

### Step 1: Email Verification
- **Route**: `/signup/`
- **Template**: `signup_step1.html`
- **Purpose**: Email entry and validation
- **Progress**: 25%
- **Session Data**: `signup_email`

### Step 2: Basic Information
- **Route**: `/signup/step2/`
- **Template**: `signup_step2_minimal.html`
- **View Function**: `signup_step2_details()`
- **Purpose**: Password and personal details
- **Progress**: 50%
- **Fields**:
  - Password (min 8 characters)
  - Password Confirmation
  - First Name (required)
  - Last Name (required)
  - Gender (required - Male/Female)
  - Country (required - dropdown with 23 countries)
  - City (optional)
- **Session Data**: 
  - `signup_password`
  - `signup_first_name`
  - `signup_last_name`
  - `signup_gender`
  - `signup_country`
  - `signup_city`

### Step 3: Sports Interests
- **Route**: `/signup/step3/`
- **Template**: `signup_step3_minimal.html`
- **View Function**: `signup_step3_sports()`
- **Purpose**: Sports selection with advanced UI
- **Progress**: 75%
- **Features**:
  - Real-time search (150ms debounce)
  - Category filters (All, Team, Racket, Fitness, Water, Combat)
  - Pagination (15 initial, load 10 more)
  - Bumble-style capsule buttons with emojis
  - Selected sports display with remove option
  - 84 sports available in database
  - Validates at least 1 sport selected
- **Session Data**: `signup_sports` (array of sport slugs)
- **API Endpoint**: `/api/sports/search/`

### Step 4: Availability & Account Creation
- **Route**: `/signup/step4/`
- **Template**: `signup_step4_minimal.html`
- **View Function**: `signup_step4_availability()`
- **Purpose**: Availability input and final account creation
- **Progress**: 100%
- **Fields**:
  - Availability (textarea, required)
- **Actions**:
  - Creates UserProfile with all collected data
  - Links selected sports via ManyToMany relationship
  - Sends verification email
  - Clears all signup session data
  - Redirects to verification pending page
- **Session Data**: `signup_availability`

## Technical Implementation

### Backend Changes

#### File: `apps/users/views.py`

**Modified Functions:**
1. `signup_step2_details()` - Now handles only password and basic info (no sports/availability)
2. `signup_step3_sports()` - NEW - Handles sports selection only
3. `signup_step4_availability()` - NEW - Handles availability + creates user account

**Key Logic:**
- Session-based data persistence across all 4 steps
- Validation at each step before allowing progression
- User creation moved to step 4 (final step)
- Email verification sent after step 4 completion
- All session data cleared after successful registration

#### File: `apps/users/urls.py`

**URL Patterns:**
```python
path('signup/', views.signup_step1, name='signup_step1'),
path('signup/step2/', views.signup_step2_details, name='signup_step2'),
path('signup/step3/', views.signup_step3_sports, name='signup_step3'),
path('signup/step4/', views.signup_step4_availability, name='signup_step4'),
```

### Frontend Changes

#### Template Files Modified/Created:

1. **signup_step2_minimal.html** (Modified)
   - Removed sports section (moved to step 3)
   - Removed availability section (moved to step 4)
   - Updated progress bar to 50%
   - Updated step description and imagery
   - Simplified JavaScript validation (password, name, gender, country only)
   - Continue button redirects to step 3

2. **signup_step3_minimal.html** (Recreated)
   - Full sports selection UI with Bumble-style capsules
   - Search bar with real-time filtering
   - Category filter buttons
   - Selected sports display with remove functionality
   - Available sports with pagination (15 initial, 10 per load more)
   - Progress bar at 75%
   - Back button to step 2, Continue button to step 4
   - JavaScript sports management system:
     - `loadSports()` - Fetches 84 sports from API
     - `selectSport()` / `deselectSport()` - Sports selection logic
     - `renderAvailableSports()` - Pagination rendering
     - `updateHiddenInputs()` - Form submission preparation

3. **signup_step4_minimal.html** (Created)
   - Simple availability textarea
   - Progress bar at 100%
   - Final submission with "Create Account" button
   - Informational alert about verification email
   - Minimal validation (availability required)
   - Back button to step 3

## Database Schema

### Related Models:

**Sport Model** (`apps/core/models.py`):
- 84 sports with emojis and categories
- Fields: name, slug, emoji, description, category, popularity_score, is_active

**UserProfile Model** (`apps/users/models.py`):
- `interested_sports` - ManyToManyField to Sport model
- Maintains backward compatibility with old sports TextField

## API Endpoints

### Sports Search API
- **URL**: `/api/sports/search/`
- **Method**: GET
- **Parameters**: 
  - `limit` (optional, default 20)
  - `offset` (optional, default 0)
- **Response**: JSON with sports list
- **Used in**: Step 3 sports selection

## Session Flow

```
User visits step 1
  ↓
Enters email → stores in session['signup_email']
  ↓
Step 2: Password & basic info → stores in session
  ↓
Step 3: Sports selection → stores in session['signup_sports']
  ↓
Step 4: Availability → stores in session['signup_availability']
  ↓
Creates UserProfile with all data → clears session
  ↓
Sends verification email → redirects to pending page
```

## Validation

### Step 2 Validation:
- Password: min 8 characters
- Password confirmation: must match
- First name: required
- Last name: required
- Gender: required (radio buttons)
- Country: required (dropdown)

### Step 3 Validation:
- Sports: minimum 1 sport required
- Client-side check: `selectedSports.size === 0`
- Server-side check: `len(request.POST.getlist('sports')) == 0`

### Step 4 Validation:
- Availability: required (textarea with min length check)

## Benefits of 4-Step Flow

1. **Cleaner UX**: Each step has a single focused purpose
2. **Better Progress Tracking**: Clear 25% increments (25%, 50%, 75%, 100%)
3. **Reduced Cognitive Load**: Users aren't overwhelmed with multiple sections
4. **Improved Completion Rates**: Shorter, focused steps increase completion
5. **Easier Maintenance**: Separated concerns make debugging simpler
6. **Mobile-Friendly**: Less scrolling per page
7. **Professional Polish**: Matches modern onboarding flows (like Bumble, LinkedIn)

## Migration Notes

- No database migrations required (schema unchanged)
- Existing users unaffected
- Session keys remain compatible
- API endpoints unchanged
- No breaking changes to Sport model or UserProfile model

## Testing Checklist

- [ ] Test complete flow from step 1 to step 4
- [ ] Verify session data persists across steps
- [ ] Test back button navigation (maintains previously entered data)
- [ ] Test validation at each step
- [ ] Test sports search and filtering
- [ ] Test pagination (load more button)
- [ ] Verify user creation in step 4
- [ ] Confirm verification email sent
- [ ] Test error handling at each step
- [ ] Verify session cleanup after completion

## Files Changed Summary

**Backend:**
- `apps/users/views.py` - Split signup_step2 into 3 functions (step2, step3, step4)
- `apps/users/urls.py` - Added signup_step3 and signup_step4 routes

**Frontend:**
- `templates/users/signup_step2_minimal.html` - Removed sports/availability sections
- `templates/users/signup_step3_minimal.html` - Recreated with sports UI
- `templates/users/signup_step4_minimal.html` - Created new availability page

**Database/API:**
- No changes (existing Sport model and API endpoints used as-is)

## Status: ✅ COMPLETE

All template files created, backend restructured, and ready for testing.
