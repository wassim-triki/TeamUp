# Signup Wizard Flow - Testing Guide

## Overview

The multi-step signup wizard is now fully implemented with all minimal templates in place.

## Complete Flow

### Step 1: Email Entry

**URL:** http://localhost:8000/accounts/signup/step1/

- Enter email address
- System checks if email already exists
- Stores email in session
- Redirects to Step 2

### Step 2: Account Details

**URL:** http://localhost:8000/accounts/signup/step2/

- Enter password (min 8 characters) and confirm password
- Enter display name
- Enter city
- Select sports (checkboxes):
  - Football
  - Basketball
  - Tennis
  - Volleyball
  - Swimming
  - Running
  - Cycling
  - Yoga
  - Gym
  - Other
- Enter availability (textarea)
- Stores all data in session
- Redirects to Step 3

### Step 3: Confirmation

**URL:** http://localhost:8000/accounts/signup/step3/

- Review all entered information
- Accept terms and conditions (required checkbox)
- Click "Create Account"
- System creates:
  1. User account (is_active=False)
  2. UserProfile with sports/availability
  3. EmailVerificationToken (UUID, expires in 24 hours)
- Sends verification email
- Redirects to Email Sent page

### Step 4: Email Sent

**URL:** http://localhost:8000/accounts/email-sent/

- Shows success message
- Lists verification instructions
- Provides link to resend verification
- Link back to login

### Step 5: Email Verification

**URL:** http://localhost:8000/accounts/verify/<token>/

- User clicks link in email
- System validates token:
  - If valid: Activates user, sets email_verified_at, redirects to login
  - If invalid/expired: Shows verification failed page

### Additional Pages

#### Verification Failed

**URL:** http://localhost:8000/accounts/verify/<invalid-token>/

- Shows error message
- Provides link to resend verification
- Link back to login

#### Resend Verification

**URL:** http://localhost:8000/accounts/resend-verification/

- Form to enter email
- Generates new token
- Sends new verification email
- Redirects to Email Sent page

## Templates Created (Minimal Versions)

All templates use the SocialV theme from template-files:

1. ✅ `signup_step1_minimal.html` - Email entry form
2. ✅ `signup_step2_minimal.html` - Account details form
3. ✅ `signup_step3_minimal.html` - Confirmation page
4. ✅ `email_sent_minimal.html` - Post-signup success page
5. ✅ `verification_failed_minimal.html` - Failed verification page
6. ✅ `resend_verification_minimal.html` - Resend verification form

## Email Template

The email verification template exists at:

- `templates/users/email_verification.html`

This is sent via Gmail SMTP (wsmtriki@gmail.com).

## Testing Checklist

### Basic Flow Test

- [ ] Visit http://localhost:8000/accounts/signup/step1/
- [ ] Verify form displays correctly (email input, logo, design)
- [ ] Enter valid email and click Continue
- [ ] Verify Step 2 displays (password, sports, availability fields)
- [ ] Fill all required fields and click Continue
- [ ] Verify Step 3 shows summary of entered data
- [ ] Check "Accept Terms" and click "Create Account"
- [ ] Verify Email Sent page displays

### Email Verification Test

- [ ] Check terminal/console for email output (console backend)
- [ ] Copy verification link from email
- [ ] Click verification link
- [ ] Verify redirect to login page with success message
- [ ] Try logging in with verified account

### Error Handling Tests

- [ ] Try using same email twice (should show error in Step 1)
- [ ] Try mismatched passwords (should show error in Step 2)
- [ ] Try skipping to Step 2 directly (should redirect to Step 1)
- [ ] Try expired/invalid token (should show verification failed page)
- [ ] Test resend verification with valid unverified email
- [ ] Test resend verification with invalid email

## Database Records

After successful signup, check:

```bash
# User record (inactive)
python manage.py shell
>>> from apps.users.models import User
>>> User.objects.filter(is_active=False)

# UserProfile
>>> from apps.users.models import UserProfile
>>> UserProfile.objects.all()

# Verification tokens
>>> from apps.users.models import EmailVerificationToken
>>> EmailVerificationToken.objects.all()
```

## Notes

1. **Email Backend**: Currently using console backend (check terminal for emails)

   - To use real SMTP, ensure .env has EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend

2. **Token Expiration**: Tokens expire after 24 hours (set in EmailVerificationToken.expires_at)

3. **Session Data**: Wizard uses sessions to store data between steps

   - Email, password, sports, availability, display_name, city

4. **URL Namespace**: All URLs use 'users' namespace

   - Example: {% url 'users:signup_step1' %}

5. **Static Files**: All templates reference static/core/ directory
   - CSS: libs.min.css, socialv.css
   - JS: libs.min.js, slider.js, app.js, lottie.js
   - Images: logo-full.png

## Common Issues

### Only Logo Displays

- Fixed by using minimal templates
- Original templates had formatting issues

### Session Data Lost

- Make sure SESSION_ENGINE is properly configured
- Check that cookies are enabled

### Email Not Sending

- Check EMAIL_BACKEND in .env
- For console backend, check terminal output
- For SMTP, verify credentials

### Static Files Not Loading

- Run `python manage.py collectstatic`
- Check STATIC_URL and STATICFILES_DIRS in settings.py

## Next Steps

1. Test the complete flow end-to-end
2. Verify email sending works
3. Test with real Gmail SMTP if needed
4. Add additional validation as needed
5. Customize email template styling
6. Add password strength indicator
7. Add CAPTCHA for security
8. Add rate limiting for signup attempts
