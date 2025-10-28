from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from django.contrib import messages
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.conf import settings
from django.utils import timezone
from django.urls import reverse
from django.core.validators import validate_email
from django.core.exceptions import ValidationError
from .models import User, UserProfile, EmailVerificationToken
import json
import uuid
import re


def login_view(request):
    """Simple login handler: renders form and authenticates by email/password."""
    error_message = None
    warning_message = None
    
    if request.method == 'POST':
        email = request.POST.get('email', '').strip().lower()
        password = request.POST.get('password', '')
        
        # Validation
        if not email:
            error_message = 'Please enter your email address.'
        elif not password:
            error_message = 'Please enter your password.'
        else:
            # Validate email format
            try:
                validate_email(email)
            except ValidationError:
                error_message = 'Please enter a valid email address.'
            
            if not error_message:
                # Authenticate using email directly (our custom backend handles this)
                user = authenticate(request, username=email, password=password)
                
                if user is not None:
                    if user.is_active:
                        login(request, user)
                        messages.success(request, f'Welcome back, {user.username}!')
                        return redirect('core:dashboard')
                    else:
                        warning_message = 'Please verify your email before logging in. Check your inbox for the verification link.'
                else:
                    error_message = 'Invalid email or password'
    
    # Get success messages from session (if any) and clear all messages
    storage = messages.get_messages(request)
    # Convert to list to preserve messages before marking as used
    all_messages = list(storage)
    success_messages = [str(msg) for msg in all_messages if msg.level_tag == 'success']
    storage.used = True  # Mark all messages as used to prevent carryover
    
    return render(request, 'users/login.html', {
        'error_message': error_message,
        'warning_message': warning_message,
        'success_messages': success_messages
    })


# ===== Multi-Step Signup Wizard =====

def signup_step1_email(request):
    """
    Step 1: User enters email address.
    Check if email already exists, if not store in session and proceed.
    """
    error_message = None
    
    if request.method == 'POST':
        email = request.POST.get('email', '').strip().lower()
        
        # Validation
        if not email:
            error_message = 'Please enter an email address.'
        else:
            # Validate email format
            try:
                validate_email(email)
            except ValidationError:
                error_message = 'Please enter a valid email address (e.g., user@example.com).'
            
            if not error_message:
                # Check if user already exists
                if User.objects.filter(email=email).exists():
                    error_message = 'An account already exists with this email address.'
                else:
                    # Store email in session and redirect (no message, step 2 will show form)
                    request.session['signup_email'] = email
                    return redirect('users:signup_step2')
    
    # Clear any stale messages from other pages
    storage = messages.get_messages(request)
    storage.used = True
    
    return render(request, 'users/signup_step1_minimal.html', {
        'error_message': error_message
    })


def signup_step2_details(request):
    """
    Step 2: User enters password, sports, and availability.
    Store all data in session and proceed to confirmation.
    """
    # Check if email exists in session
    if 'signup_email' not in request.session:
        return redirect('users:signup_step1')
    
    error_messages = []
    warning_message = None
    
    if request.method == 'POST':
        password = request.POST.get('password', '')
        password_confirm = request.POST.get('password_confirm', '')
        sports = request.POST.getlist('sports')  # Multiple sports selection
        availability = request.POST.get('availability', '')
        display_name = request.POST.get('display_name', '').strip()
        city = request.POST.get('city', '').strip()
        
        # Validation with detailed messages
        
        # Password validation
        if not password:
            error_messages.append('Password is required.')
        elif len(password) < 8:
            error_messages.append('Password must be at least 8 characters long.')
        elif password != password_confirm:
            error_messages.append('Passwords do not match.')
        else:
            # Check password strength
            if not re.search(r'[A-Za-z]', password) or not re.search(r'\d', password):
                warning_message = 'For better security, consider using a password with both letters and numbers.'
        
        # Sports validation
        if not sports:
            error_messages.append('Please select at least one sport.')
        
        # Availability validation
        if not availability:
            error_messages.append('Please select your availability.')
        
        # If no errors, store and proceed
        if not error_messages:
            # Store everything in session
            request.session['signup_password'] = password
            request.session['signup_sports'] = sports
            request.session['signup_availability'] = availability
            request.session['signup_display_name'] = display_name
            request.session['signup_city'] = city
            
            return redirect('users:signup_step3')
        else:
            # Return to form with context
            context = {
                'email': request.session.get('signup_email'),
                'sports': sports,
                'availability': availability,
                'display_name': display_name,
                'city': city,
                'error_messages': error_messages,
                'warning_message': warning_message,
            }
            return render(request, 'users/signup_step2_minimal.html', context)
    
    # Clear any stale messages from other pages
    storage = messages.get_messages(request)
    storage.used = True
    
    return render(request, 'users/signup_step2_minimal.html', {
        'email': request.session.get('signup_email')
    })


def signup_step3_confirm(request):
    """
    Step 3: Review and confirm signup data.
    Create user, profile, and send verification email.
    """
    # Check if all session data exists
    required_keys = ['signup_email', 'signup_password', 'signup_sports', 'signup_availability']
    if not all(key in request.session for key in required_keys):
        return redirect('users:signup_step1')
    
    error_message = None
    
    if request.method == 'POST':
        try:
            # Retrieve data from session
            email = request.session['signup_email']
            password = request.session['signup_password']
            sports = request.session['signup_sports']
            availability = request.session['signup_availability']
            display_name = request.session.get('signup_display_name', '')
            city = request.session.get('signup_city', '')
            
            # Double-check email doesn't exist (in case user opened multiple tabs)
            if User.objects.filter(email=email).exists():
                error_message = 'An account with this email already exists.'
                # Clear session
                for key in required_keys + ['signup_display_name', 'signup_city']:
                    request.session.pop(key, None)
                
                # Clear messages and store success message for login page
                storage = messages.get_messages(request)
                storage.used = True
                messages.success(request, 'Please sign in with your existing account.')
                return redirect('users:login')
            
            # Create User (inactive until email verification)
            # The username generation is now handled by CustomUserManager
            user = User.objects.create_user(
                email=email,
                password=password,
                is_active=False
            )
            
            # Create UserProfile
            profile = UserProfile.objects.create(
                user=user,
                sports=json.dumps(sports),
                availability=availability,
                display_name=display_name,
                city=city
            )
            
            # Generate Email Verification Token
            token = EmailVerificationToken.objects.create(user=user)
            
            # Send verification email
            verification_link = request.build_absolute_uri(
                reverse('users:verify_email', kwargs={'token': token.token})
            )
            
            html_message = render_to_string('users/email_verification.html', {
                'user': user,
                'verification_link': verification_link,
            })
            plain_message = strip_tags(html_message)
            
            send_mail(
                subject='Verify your TeamUp account',
                message=plain_message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[user.email],
                html_message=html_message,
                fail_silently=False,
            )
            
            # Clear session data
            for key in required_keys + ['signup_display_name', 'signup_city']:
                request.session.pop(key, None)
            
            # Clear any stale messages before redirect
            storage = messages.get_messages(request)
            storage.used = True
            
            # Redirect to success page (no message needed, page has its own success display)
            return redirect('users:email_sent')
            
        except Exception as e:
            error_message = 'An error occurred while creating your account. Please try again.'
    
    # Clear any stale messages from other pages
    storage = messages.get_messages(request)
    storage.used = True
    
    # Display confirmation page
    context = {
        'email': request.session.get('signup_email'),
        'sports': request.session.get('signup_sports', []),
        'availability': request.session.get('signup_availability'),
        'display_name': request.session.get('signup_display_name', ''),
        'city': request.session.get('signup_city', ''),
        'error_message': error_message,
    }
    return render(request, 'users/signup_step3_minimal.html', context)


def email_sent_view(request):
    """Page shown after successful signup, telling user to check email."""
    return render(request, 'users/email_sent_minimal.html')


def verify_email(request, token):
    """
    Email verification handler.
    Validates token, activates user, and redirects to login.
    """
    try:
        verification_token = EmailVerificationToken.objects.get(token=token)
        
        if verification_token.is_valid():
            # Activate user
            user = verification_token.user
            user.is_active = True
            user.email_verified_at = timezone.now()
            user.save()
            
            # Mark token as used
            verification_token.used = True
            verification_token.save()
            
            messages.success(request, 'Email verified successfully! You can now sign in to your account.')
            return redirect('users:login')
        else:
            # Token expired or already used
            messages.error(request, 'This verification link has expired or has already been used. Please request a new verification email.')
            return render(request, 'users/verification_failed_minimal.html', {
                'user': verification_token.user
            })
    
    except EmailVerificationToken.DoesNotExist:
        messages.error(request, 'Invalid verification link. Please check the link or request a new verification email.')
        return render(request, 'users/verification_failed_minimal.html')


def resend_verification(request):
    """Allow user to resend verification email."""
    error_message = None
    
    if request.method == 'POST':
        email = request.POST.get('email', '').strip().lower()
        
        # Validate email format
        if not email:
            error_message = 'Please enter your email address.'
        else:
            try:
                validate_email(email)
            except ValidationError:
                error_message = 'Please enter a valid email address.'
        
        if not error_message:
            try:
                user = User.objects.get(email=email, is_active=False)
                
                # Generate new token
                token = EmailVerificationToken.objects.create(user=user)
                
                # Send verification email
                verification_link = request.build_absolute_uri(
                    reverse('users:verify_email', kwargs={'token': token.token})
                )
                
                html_message = render_to_string('users/email_verification.html', {
                    'user': user,
                    'verification_link': verification_link,
                })
                plain_message = strip_tags(html_message)
                
                send_mail(
                    subject='Verify your TeamUp account',
                    message=plain_message,
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=[user.email],
                    html_message=html_message,
                    fail_silently=False,
                )
                
                # Clear any stale messages before redirect
                storage = messages.get_messages(request)
                storage.used = True
                
                # Success - redirect to email_sent page (has its own success display)
                return redirect('users:email_sent')
            
            except User.DoesNotExist:
                error_message = 'No inactive account found with this email address. The account may already be verified or does not exist.'
    
    # Clear any stale messages from other pages
    storage = messages.get_messages(request)
    storage.used = True
    
    return render(request, 'users/resend_verification_minimal.html', {'error_message': error_message})


# Legacy signup view (keeping for reference, but wizard should be used)
def signup_view(request):
    """Redirect to new multi-step signup wizard."""
    return redirect('users:signup_step1')