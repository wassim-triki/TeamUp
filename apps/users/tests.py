"""
Test script for the Multi-Step Signup Wizard
Run this after setting up the database to verify functionality
"""

from django.test import TestCase, Client
from django.urls import reverse
from django.utils import timezone
from apps.users.models import User, UserProfile, EmailVerificationToken
import json


class SignupWizardTestCase(TestCase):
    """Test cases for the signup wizard flow."""
    
    def setUp(self):
        """Set up test client."""
        self.client = Client()
    
    def test_step1_email_entry(self):
        """Test Step 1: Email entry."""
        # GET request should render form
        response = self.client.get(reverse('users:signup_step1'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Enter your email')
        
        # POST with valid email should proceed to step 2
        response = self.client.post(reverse('users:signup_step1'), {
            'email': 'test@example.com'
        })
        self.assertEqual(response.status_code, 302)  # Redirect
        self.assertIn('signup_email', self.client.session)
    
    def test_step1_existing_email(self):
        """Test Step 1 with existing email redirects to login."""
        # Create existing user
        User.objects.create_user(
            username='existing',
            email='existing@example.com',
            password='testpass123'
        )
        
        # Try to signup with same email
        response = self.client.post(reverse('users:signup_step1'), {
            'email': 'existing@example.com'
        })
        self.assertEqual(response.status_code, 302)
        # Should redirect to login
    
    def test_step2_requires_session(self):
        """Test Step 2 requires email in session."""
        # Without session, should redirect to step 1
        response = self.client.get(reverse('users:signup_step2'))
        self.assertEqual(response.status_code, 302)
    
    def test_step2_account_details(self):
        """Test Step 2: Account details submission."""
        # Set up session
        session = self.client.session
        session['signup_email'] = 'test@example.com'
        session.save()
        
        # POST valid data
        response = self.client.post(reverse('users:signup_step2'), {
            'password': 'SecurePass123!',
            'password_confirm': 'SecurePass123!',
            'sports': ['football', 'basketball'],
            'availability': 'Weekends mornings',
            'display_name': 'Test User',
            'city': 'Test City'
        })
        self.assertEqual(response.status_code, 302)  # Redirect to step 3
        self.assertIn('signup_password', self.client.session)
        self.assertIn('signup_sports', self.client.session)
    
    def test_step2_password_validation(self):
        """Test password validation in Step 2."""
        session = self.client.session
        session['signup_email'] = 'test@example.com'
        session.save()
        
        # Test passwords don't match
        response = self.client.post(reverse('users:signup_step2'), {
            'password': 'Password123!',
            'password_confirm': 'DifferentPass123!',
            'sports': ['football'],
            'availability': 'Weekends'
        })
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'do not match')
    
    def test_step3_confirmation(self):
        """Test Step 3: Confirmation and account creation."""
        # Set up full session
        session = self.client.session
        session['signup_email'] = 'newuser@example.com'
        session['signup_password'] = 'SecurePass123!'
        session['signup_sports'] = ['football', 'tennis']
        session['signup_availability'] = 'Weekday evenings'
        session['signup_display_name'] = 'New User'
        session['signup_city'] = 'New City'
        session.save()
        
        # GET should show summary
        response = self.client.get(reverse('users:signup_step3'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'newuser@example.com')
        self.assertContains(response, 'football')
        
        # POST should create user
        response = self.client.post(reverse('users:signup_step3'))
        self.assertEqual(response.status_code, 302)  # Redirect to email_sent
        
        # Verify user created
        user = User.objects.get(email='newuser@example.com')
        self.assertFalse(user.is_active)  # Should be inactive
        self.assertIsNone(user.email_verified_at)
        
        # Verify profile created
        profile = UserProfile.objects.get(user=user)
        self.assertEqual(profile.display_name, 'New User')
        self.assertEqual(profile.city, 'New City')
        self.assertIn('football', profile.sports)
        
        # Verify token created
        token = EmailVerificationToken.objects.filter(user=user).first()
        self.assertIsNotNone(token)
        self.assertTrue(token.is_valid())
    
    def test_email_verification(self):
        """Test email verification process."""
        # Create inactive user
        user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123',
            is_active=False
        )
        
        # Create verification token
        token = EmailVerificationToken.objects.create(user=user)
        
        # Visit verification URL
        response = self.client.get(reverse('users:verify_email', kwargs={'token': token.token}))
        self.assertEqual(response.status_code, 302)  # Redirect to login
        
        # Verify user is now active
        user.refresh_from_db()
        self.assertTrue(user.is_active)
        self.assertIsNotNone(user.email_verified_at)
        
        # Verify token marked as used
        token.refresh_from_db()
        self.assertTrue(token.used)
    
    def test_invalid_verification_token(self):
        """Test verification with invalid token."""
        response = self.client.get(reverse('users:verify_email', kwargs={'token': 'invalid-token'}))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'invalid')
    
    def test_expired_verification_token(self):
        """Test verification with expired token."""
        user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123',
            is_active=False
        )
        
        # Create expired token
        token = EmailVerificationToken.objects.create(user=user)
        token.expires_at = timezone.now() - timezone.timedelta(hours=1)
        token.save()
        
        # Try to verify
        response = self.client.get(reverse('users:verify_email', kwargs={'token': token.token}))
        self.assertContains(response, 'expired')
        
        # User should still be inactive
        user.refresh_from_db()
        self.assertFalse(user.is_active)
    
    def test_resend_verification(self):
        """Test resend verification email."""
        # Create inactive user
        user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123',
            is_active=False
        )
        
        # Request resend
        response = self.client.post(reverse('users:resend_verification'), {
            'email': 'test@example.com'
        })
        self.assertEqual(response.status_code, 302)
        
        # Verify new token created
        tokens = EmailVerificationToken.objects.filter(user=user)
        self.assertGreater(tokens.count(), 0)
    
    def test_login_requires_verification(self):
        """Test that login fails for unverified users."""
        # Create inactive user
        user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123',
            is_active=False
        )
        
        # Try to login
        response = self.client.post(reverse('users:login'), {
            'email': 'test@example.com',
            'password': 'testpass123'
        })
        
        # Should not be logged in
        self.assertNotIn('_auth_user_id', self.client.session)


# Instructions for running tests:
print("""
To run these tests:

1. Make sure migrations are applied:
   python manage.py migrate

2. Run the tests:
   python manage.py test apps.users

3. Run specific test:
   python manage.py test apps.users.tests.SignupWizardTestCase.test_step1_email_entry

4. Run with verbose output:
   python manage.py test apps.users --verbosity=2

5. Keep the test database:
   python manage.py test apps.users --keepdb
""")
