# Google Email Deployment Guide

## Overview
This guide explains how to configure Google Gmail SMTP for your TeamUp Django application in production.

## Prerequisites
- Gmail account
- Django project with email functionality
- Access to your deployment environment variables

## Step 1: Set Up Gmail App Password

### Why App Passwords?
Google no longer allows "less secure app access". You must use App Passwords for third-party applications.

### Create an App Password:

1. **Enable 2-Factor Authentication** (required for App Passwords)
   - Go to https://myaccount.google.com/security
   - Click "2-Step Verification"
   - Follow the setup process

2. **Generate App Password**
   - Go to https://myaccount.google.com/apppasswords
   - Select "Mail" as the app
   - Select "Other (Custom name)" as the device
   - Name it "TeamUp Django App" or similar
   - Click "Generate"
   - **Copy the 16-character password** (spaces are optional)
   - Store it securely - you won't see it again!

## Step 2: Configure Environment Variables

### For Local Development (.env file):
```properties
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-16-char-app-password
DEFAULT_FROM_EMAIL=TeamUp <noreply@teamup.com>
```

### For Production (Render, Heroku, etc.):

#### Render.com:
1. Go to your service dashboard
2. Navigate to "Environment" tab
3. Add these environment variables:
   ```
   EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
   EMAIL_HOST=smtp.gmail.com
   EMAIL_PORT=587
   EMAIL_USE_TLS=True
   EMAIL_HOST_USER=your-email@gmail.com
   EMAIL_HOST_PASSWORD=your-16-char-app-password
   DEFAULT_FROM_EMAIL=TeamUp <noreply@teamup.com>
   ```

#### Heroku:
```bash
heroku config:set EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
heroku config:set EMAIL_HOST=smtp.gmail.com
heroku config:set EMAIL_PORT=587
heroku config:set EMAIL_USE_TLS=True
heroku config:set EMAIL_HOST_USER=your-email@gmail.com
heroku config:set EMAIL_HOST_PASSWORD=your-16-char-app-password
heroku config:set DEFAULT_FROM_EMAIL="TeamUp <noreply@teamup.com>"
```

#### Railway:
1. Go to your project settings
2. Click "Variables" tab
3. Add each variable individually

#### DigitalOcean App Platform:
1. Go to your app settings
2. Navigate to "Environment Variables"
3. Add each variable

## Step 3: Update Django Settings

Ensure your `settings.py` reads from environment variables:

```python
import os
from decouple import config  # or use os.environ.get()

# Email Configuration
EMAIL_BACKEND = config('EMAIL_BACKEND', default='django.core.mail.backends.console.EmailBackend')
EMAIL_HOST = config('EMAIL_HOST', default='smtp.gmail.com')
EMAIL_PORT = config('EMAIL_PORT', default=587, cast=int)
EMAIL_USE_TLS = config('EMAIL_USE_TLS', default=True, cast=bool)
EMAIL_HOST_USER = config('EMAIL_HOST_USER', default='')
EMAIL_HOST_PASSWORD = config('EMAIL_HOST_PASSWORD', default='')
DEFAULT_FROM_EMAIL = config('DEFAULT_FROM_EMAIL', default='noreply@example.com')

# Optional: For SSL (port 465)
# EMAIL_USE_SSL = config('EMAIL_USE_SSL', default=False, cast=bool)
```

## Step 4: Test Email Configuration

### Create a management command to test emails:

Create `apps/core/management/commands/test_email.py`:

```python
from django.core.management.base import BaseCommand
from django.core.mail import send_mail
from django.conf import settings

class Command(BaseCommand):
    help = 'Test email configuration'

    def add_arguments(self, parser):
        parser.add_argument('recipient', type=str, help='Email address to send test email to')

    def handle(self, *args, **options):
        recipient = options['recipient']
        
        try:
            send_mail(
                subject='TeamUp - Test Email',
                message='This is a test email from TeamUp Django application.',
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[recipient],
                fail_silently=False,
            )
            self.stdout.write(self.style.SUCCESS(f'✓ Email sent successfully to {recipient}'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'✗ Failed to send email: {str(e)}'))
```

### Run the test:
```bash
python manage.py test_email your-email@example.com
```

## Step 5: Security Best Practices

### ⚠️ IMPORTANT SECURITY NOTES:

1. **Never commit credentials to Git**
   - Add `.env` to `.gitignore`
   - Use environment variables in production
   - Rotate passwords if exposed

2. **Use App Passwords, not regular passwords**
   - More secure
   - Can be revoked individually
   - Doesn't expose main account password

3. **Limit sender permissions**
   - Consider using a dedicated email account for the app
   - Monitor usage through Google account activity

4. **Handle errors gracefully**
   ```python
   # In production, log errors but don't expose them to users
   try:
       send_mail(...)
   except Exception as e:
       logger.error(f"Email send failed: {str(e)}")
       # Show user-friendly message
   ```

## Step 6: Gmail Sending Limits

Be aware of Gmail's sending limits:
- **Free Gmail accounts**: ~500 emails/day
- **Google Workspace**: ~2,000 emails/day

For higher volume, consider:
- **SendGrid** (12,000 free emails/month)
- **Mailgun** (5,000 free emails/month)
- **Amazon SES** (62,000 free emails/month with AWS)

## Troubleshooting

### Issue: "SMTPAuthenticationError"
**Solution**: 
- Verify App Password is correct (no spaces)
- Ensure 2FA is enabled on Gmail
- Check if the Gmail account is locked

### Issue: "SMTPServerDisconnected"
**Solution**:
- Check firewall/network settings
- Verify EMAIL_PORT is correct (587 for TLS)
- Try EMAIL_USE_SSL=True with port 465

### Issue: Emails going to spam
**Solution**:
- Set up SPF, DKIM, DMARC records (if using custom domain)
- Use a verified sender address
- Avoid spam trigger words in subject/body

### Issue: "Application-specific password required"
**Solution**: You're using your regular Gmail password instead of an App Password

## Testing Checklist

Before deployment:
- [ ] App Password created and saved securely
- [ ] Environment variables set in deployment platform
- [ ] Test email sent successfully from production
- [ ] Email appears in inbox (not spam)
- [ ] Error handling implemented
- [ ] Logging configured for email failures

## Alternative: Using SendGrid (Recommended for Production)

For more reliable production email:

```bash
pip install sendgrid
```

Environment variables:
```properties
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.sendgrid.net
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=apikey
EMAIL_HOST_PASSWORD=your-sendgrid-api-key
```

## Resources

- [Django Email Documentation](https://docs.djangoproject.com/en/stable/topics/email/)
- [Google App Passwords](https://support.google.com/accounts/answer/185833)
- [Gmail SMTP Settings](https://support.google.com/mail/answer/7126229)

## Current Configuration Status

Your current `.env` has:
- ✓ Email backend configured
- ✓ Gmail SMTP host
- ✓ TLS enabled
- ✓ Host user set
- ⚠️ App password format (verify it's an App Password, not regular password)

**Next Steps:**
1. Verify the EMAIL_HOST_PASSWORD is an App Password (16 chars)
2. Set these same variables in your deployment environment
3. Test email functionality after deployment
4. Monitor email delivery in production

---

**Last Updated**: October 30, 2025
**Tested With**: Django 4.x/5.x, Gmail SMTP
