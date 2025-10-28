from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from django.contrib import messages
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.conf import settings
from django.utils import timezone
from django.urls import reverse
from .models import User, UserProfile, EmailVerificationToken
import json
import uuid


def login_view(request):
    """Simple login handler: renders form and authenticates by email/password."""
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        
        if email and password:
            try:
                user_obj = User.objects.get(email=email)
                user = authenticate(request, username=user_obj.username, password=password)
                if user is not None:
                    if user.is_active:
                        login(request, user)
                        return redirect('core:dashboard')
                    else:
                        messages.error(request, 'Please verify your email before logging in.')
                else:
                    messages.error(request, 'Invalid email or password.')
            except User.DoesNotExist:
                messages.error(request, 'Invalid email or password.')

    return render(request, 'users/login.html')


# ===== Multi-Step Signup Wizard =====

def signup_step1_email(request):
    """
    Step 1: User enters email address.
    Check if email already exists, if not store in session and proceed.
    """
    if request.method == 'POST':
        email = request.POST.get('email', '').strip().lower()
        
        if not email:
            messages.error(request, 'Please enter a valid email address.')
            return render(request, 'users/signup_step1_minimal.html')
        
        # Check if user already exists
        if User.objects.filter(email=email).exists():
            messages.error(request, 'Account already exists with this email. Please log in.')
            return redirect('users:login')
        
        # Store email in session
        request.session['signup_email'] = email
        return redirect('users:signup_step2')
    
    return render(request, 'users/signup_step1_minimal.html')


def signup_step2_details(request):
    """
    Step 2: User enters password, sports, and availability.
    Store all data in session and proceed to confirmation.
    """
    # Check if email exists in session
    if 'signup_email' not in request.session:
        messages.warning(request, 'Please start from the beginning.')
        return redirect('users:signup_step1')
    
    if request.method == 'POST':
        password = request.POST.get('password')
        password_confirm = request.POST.get('password_confirm')
        sports = request.POST.getlist('sports')  # Multiple sports selection
        availability = request.POST.get('availability', '')
        display_name = request.POST.get('display_name', '')
        city = request.POST.get('city', '')
        
        # Validation
        if not password or len(password) < 8:
            messages.error(request, 'Password must be at least 8 characters long.')
            return render(request, 'users/signup_step2_minimal.html', {
                'email': request.session.get('signup_email'),
                'sports': sports,
                'availability': availability,
                'display_name': display_name,
                'city': city,
            })
        
        if password != password_confirm:
            messages.error(request, 'Passwords do not match.')
            return render(request, 'users/signup_step2_minimal.html', {
                'email': request.session.get('signup_email'),
                'sports': sports,
                'availability': availability,
                'display_name': display_name,
                'city': city,
            })
        
        if not sports:
            messages.error(request, 'Please select at least one sport.')
            return render(request, 'users/signup_step2_minimal.html', {
                'email': request.session.get('signup_email'),
                'availability': availability,
                'display_name': display_name,
                'city': city,
            })
        
        if not availability:
            messages.error(request, 'Please provide your availability.')
            return render(request, 'users/signup_step2_minimal.html', {
                'email': request.session.get('signup_email'),
                'sports': sports,
                'display_name': display_name,
                'city': city,
            })
        
        # Store everything in session
        request.session['signup_password'] = password
        request.session['signup_sports'] = sports
        request.session['signup_availability'] = availability
        request.session['signup_display_name'] = display_name
        request.session['signup_city'] = city
        
        return redirect('users:signup_step3')
    
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
        messages.warning(request, 'Please complete all signup steps.')
        return redirect('users:signup_step1')
    
    if request.method == 'POST':
        # Retrieve data from session
        email = request.session['signup_email']
        password = request.session['signup_password']
        sports = request.session['signup_sports']
        availability = request.session['signup_availability']
        display_name = request.session.get('signup_display_name', '')
        city = request.session.get('signup_city', '')
        
        # Create User (inactive until email verification)
        username = email.split('@')[0]
        base_username = username
        counter = 1
        while User.objects.filter(username=username).exists():
            username = f"{base_username}{counter}"
            counter += 1
        
        user = User.objects.create_user(
            username=username,
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
        
        messages.success(request, 'Account created! Please check your email to verify your account.')
        return redirect('users:email_sent')
    
    # Display confirmation page
    context = {
        'email': request.session.get('signup_email'),
        'sports': request.session.get('signup_sports', []),
        'availability': request.session.get('signup_availability'),
        'display_name': request.session.get('signup_display_name', ''),
        'city': request.session.get('signup_city', ''),
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
            
            messages.success(request, 'Email verified successfully! You can now log in.')
            return redirect('users:login')
        else:
            # Token expired or already used
            messages.error(request, 'This verification link is invalid or has expired.')
            return render(request, 'users/verification_failed_minimal.html', {
                'user': verification_token.user
            })
    
    except EmailVerificationToken.DoesNotExist:
        messages.error(request, 'Invalid verification link.')
        return render(request, 'users/verification_failed_minimal.html')


def resend_verification(request):
    """Allow user to resend verification email."""
    if request.method == 'POST':
        email = request.POST.get('email', '').strip().lower()
        
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
            
            messages.success(request, 'Verification email sent! Please check your inbox.')
            return redirect('users:email_sent')
        
        except User.DoesNotExist:
            messages.error(request, 'No inactive account found with this email.')
    
    return render(request, 'users/resend_verification_minimal.html')


# Legacy signup view (keeping for reference, but wizard should be used)
def signup_view(request):
    """Redirect to new multi-step signup wizard."""
    return redirect('users:signup_step1')

