# Multi-Step Signup Wizard Implementation

## Overview

This implementation provides a complete multi-step signup wizard for the TeamUp application with email verification.

## Features

### 🎯 Multi-Step Signup Flow

1. **Step 1: Email Check** - User enters email, system checks if account exists
2. **Step 2: Account Details** - Password, sports interests, and availability
3. **Step 3: Confirmation** - Review information before account creation

### ✉️ Email Verification

- Verification email sent after signup
- Token-based verification (expires in 24 hours)
- Resend verification email functionality
- Account activation on successful verification

### 🔐 Security Features

- Passwords hashed using Django's authentication system
- Email uniqueness enforced
- Inactive accounts until email verification
- Token expiration for security

## Models

### User (extends AbstractUser)

- `email` - Unique email address (used for login)
- `username` - Auto-generated from email
- `is_active` - Default False until email verified
- `email_verified_at` - Timestamp of verification

### UserProfile (OneToOne → User)

- `display_name` - Optional display name
- `city` - Optional city
- `sports` - JSON array of selected sports
- `availability` - Text description of schedule

### EmailVerificationToken (ForeignKey → User)

- `token` - Unique verification token
- `created_at` - Creation timestamp
- `expires_at` - Expiration timestamp (24 hours)
- `used` - Boolean flag

## URLs

```
/users/signup/           → Redirects to step 1
/users/signup/step1/     → Email entry
/users/signup/step2/     → Account details
/users/signup/step3/     → Confirmation
/users/email-sent/       → Success message
/users/verify/<token>/   → Email verification
/users/resend-verification/ → Resend verification email
/users/login/            → Login page
```

## Setup Instructions

### 1. Install Dependencies

Ensure all requirements are installed:

```bash
pip install -r requirements.txt
```

### 2. Configure Environment Variables

Add to your `.env` file:

```env
# Email Configuration (for production)
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password
DEFAULT_FROM_EMAIL=noreply@teamup.com

# For development (emails print to console)
EMAIL_BACKEND=django.core.mail.backends.console.EmailBackend
```

### 3. Run Migrations

```bash
# If starting fresh, drop and recreate MySQL database first:
# mysql -u root -p
# DROP DATABASE IF EXISTS teamup_db;
# CREATE DATABASE teamup_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
# exit

# Then run migrations
python manage.py makemigrations users
python manage.py migrate
```

### 4. Create Superuser (Optional)

```bash
python manage.py createsuperuser
```

### 5. Run Development Server

```bash
python manage.py runserver
```

## Usage Flow

### New User Signup

1. Visit `/users/signup/` or `/users/signup/step1/`
2. Enter email address
3. If email exists → redirected to login
4. If new → proceed to step 2
5. Enter password, select sports, add availability
6. Review information on step 3
7. Accept terms and create account
8. Account created (inactive)
9. Verification email sent
10. User clicks link in email
11. Account activated
12. User can now log in

### Email Verification

- Check email inbox (and spam folder)
- Click verification link
- Account activated automatically
- Redirect to login page

### Resend Verification

- If email not received
- Go to `/users/resend-verification/`
- Enter email address
- New verification email sent

## Templates

All templates use the existing template-files styling:

- `signup_step1.html` - Email entry form
- `signup_step2.html` - Account details form with sports checkboxes
- `signup_step3.html` - Confirmation page with summary card
- `email_sent.html` - Success page with instructions
- `email_verification.html` - HTML email template
- `verification_failed.html` - Invalid/expired token page
- `resend_verification.html` - Resend verification form

## Session Data

During signup, the following data is stored in session:

- `signup_email`
- `signup_password`
- `signup_sports` (list)
- `signup_availability`
- `signup_display_name` (optional)
- `signup_city` (optional)

Session data is cleared after account creation.

## Admin Interface

Access Django admin at `/admin/` to manage:

- Users (view verification status)
- User Profiles
- Email Verification Tokens

## Testing

### Manual Testing Checklist

- [ ] Step 1: Email entry works
- [ ] Step 1: Existing email redirects to login
- [ ] Step 2: Password validation works
- [ ] Step 2: Sports selection required
- [ ] Step 2: Availability required
- [ ] Step 3: Shows correct summary
- [ ] Account creation successful
- [ ] Verification email sent (check console in dev mode)
- [ ] Verification link activates account
- [ ] Expired token shows error
- [ ] Resend verification works
- [ ] Login only works after verification

### Development Email Testing

In development mode (console backend), verification emails appear in terminal output.

### Production Email Testing

Configure SMTP settings in `.env` for real email delivery.

## Troubleshooting

### Email Not Sending

- Check EMAIL_BACKEND setting
- Verify SMTP credentials in .env
- Check spam folder
- For Gmail: Use app-specific password

### Migration Issues

```bash
python manage.py makemigrations users --empty
# Then manually add migrations
```

### Token Expired

- Users can request new verification email
- Tokens expire after 24 hours
- Old tokens automatically marked as invalid

## Future Enhancements

- [ ] Rate limiting on verification email sending
- [ ] AJAX form validation
- [ ] Social authentication (Google, Facebook)
- [ ] Profile picture upload during signup
- [ ] SMS verification option
- [ ] Remember me checkbox on login
- [ ] Password strength indicator
- [ ] Two-factor authentication

## Related Files

### Models

- `apps/users/models.py`

### Views

- `apps/users/views.py`

### URLs

- `apps/users/urls.py`

### Admin

- `apps/users/admin.py`

### Templates

- `templates/users/*.html`

### Settings

- `config/settings.py` (AUTH*USER_MODEL, EMAIL*\* settings)

## Support

For issues or questions, please refer to:

- Django documentation: https://docs.djangoproject.com/
- Project ARCHITECTURE.md
- Project CONTRIBUTING.md
