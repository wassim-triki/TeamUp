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
from django.contrib.auth.decorators import login_required
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
                        return redirect('/')
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
    Step 2: User enters password and basic personal information.
    No sports or availability - just core account details.
    """
    # Check if email exists in session
    if 'signup_email' not in request.session:
        return redirect('users:signup_step1')
    
    error_messages = []
    warning_message = None
    
    if request.method == 'POST':
        password = request.POST.get('password', '')
        password_confirm = request.POST.get('password_confirm', '')
        first_name = request.POST.get('first_name', '').strip()
        last_name = request.POST.get('last_name', '').strip()
        gender = request.POST.get('gender', '').strip()
        country = request.POST.get('country', '').strip()
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
        
        # Required field validation
        if not first_name:
            error_messages.append('First name is required.')
        
        if not last_name:
            error_messages.append('Last name is required.')
        
        if not gender:
            error_messages.append('Gender is required.')
        
        if not country:
            error_messages.append('Country is required.')
        
        # If no errors, store and proceed to sports selection
        if not error_messages:
            # Store everything in session
            request.session['signup_password'] = password
            request.session['signup_first_name'] = first_name
            request.session['signup_last_name'] = last_name
            request.session['signup_gender'] = gender
            request.session['signup_country'] = country
            request.session['signup_city'] = city
            
            return redirect('users:signup_step3')
        else:
            # Return to form with context
            context = {
                'email': request.session.get('signup_email'),
                'first_name': first_name,
                'last_name': last_name,
                'gender': gender,
                'country': country,
                'city': city,
                'error_messages': error_messages,
                'warning_message': warning_message,
            }
            return render(request, 'users/signup_step2_minimal.html', context)
    
    # Clear any stale messages from other pages
    storage = messages.get_messages(request)
    storage.used = True
    
    return render(request, 'users/signup_step2_minimal.html', {
        'email': request.session.get('signup_email'),
        'first_name': request.session.get('signup_first_name', ''),
        'last_name': request.session.get('signup_last_name', ''),
        'gender': request.session.get('signup_gender', ''),
        'country': request.session.get('signup_country', ''),
        'city': request.session.get('signup_city', ''),
    })


def signup_step3_sports(request):
    """
    Step 3: User selects sports interests.
    """
    # Check if previous steps are completed
    if 'signup_email' not in request.session or 'signup_password' not in request.session:
        return redirect('users:signup_step1')
    
    error_messages = []
    
    if request.method == 'POST':
        sports = request.POST.getlist('sports')  # Multiple sports selection
        
        # Sports validation
        if not sports:
            error_messages.append('Please select at least one sport.')
        
        # If no errors, store and proceed to availability
        if not error_messages:
            request.session['signup_sports'] = sports
            return redirect('users:signup_step4')
        else:
            context = {
                'email': request.session.get('signup_email'),
                'sports': sports,
                'error_messages': error_messages,
            }
            return render(request, 'users/signup_step3_minimal.html', context)
    
    # Clear any stale messages
    storage = messages.get_messages(request)
    storage.used = True
    
    return render(request, 'users/signup_step3_minimal.html', {
        'email': request.session.get('signup_email'),
        'sports': request.session.get('signup_sports', []),
    })


def signup_step4_availability(request):
    """
    Step 4: User selects availability patterns and confirms.
    Create user, profile, and send verification email.
    """
    # Check if all previous steps are completed
    required_keys = ['signup_email', 'signup_password', 'signup_sports']
    if not all(key in request.session for key in required_keys):
        return redirect('users:signup_step1')
    
    error_message = None
    
    if request.method == 'POST':
        # Get selected availability patterns from checkboxes
        availability_patterns = request.POST.getlist('availability')
        
        # Availability validation
        if not availability_patterns:
            error_message = 'Please select at least one availability pattern.'
            context = {
                'email': request.session.get('signup_email'),
                'availability_patterns': UserProfile.get_availability_choices(),
                'selected_availability': [],
                'error_message': error_message,
            }
            return render(request, 'users/signup_step4_minimal.html', context)
        
        # Store availability
        request.session['signup_availability'] = availability_patterns
        
        # Now create the user account
        try:
            # Retrieve data from session
            email = request.session['signup_email']
            password = request.session['signup_password']
            sports = request.session['signup_sports']
            first_name = request.session.get('signup_first_name', '')
            last_name = request.session.get('signup_last_name', '')
            gender = request.session.get('signup_gender', '')
            country = request.session.get('signup_country', '')
            city = request.session.get('signup_city', '')
            
            # Double-check email doesn't exist (in case user opened multiple tabs)
            if User.objects.filter(email=email).exists():
                error_message = 'An account with this email already exists.'
                # Clear session
                for key in ['signup_email', 'signup_password', 'signup_sports', 'signup_availability', 
                           'signup_first_name', 'signup_last_name', 'signup_gender', 'signup_country', 'signup_city']:
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
                availability=availability_patterns,  # Store as list
                first_name=first_name,
                last_name=last_name,
                gender=gender,
                country=country,
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
            for key in ['signup_email', 'signup_password', 'signup_sports', 'signup_availability',
                       'signup_first_name', 'signup_last_name', 'signup_gender', 'signup_country', 'signup_city']:
                request.session.pop(key, None)
            
            # Clear any stale messages before redirect
            storage = messages.get_messages(request)
            storage.used = True
            
            # Redirect to success page (no message needed, page has its own success display)
            return redirect('users:email_sent')
            
        except Exception as e:
            error_message = 'An error occurred while creating your account. Please try again.'
            context = {
                'email': request.session.get('signup_email'),
                'availability_patterns': UserProfile.get_availability_choices(),
                'selected_availability': availability_patterns,
                'error_message': error_message,
            }
            return render(request, 'users/signup_step4_minimal.html', context)
    
    # Clear any stale messages from other pages
    storage = messages.get_messages(request)
    storage.used = True
    
    # Display availability form
    context = {
        'email': request.session.get('signup_email'),
        'availability_patterns': UserProfile.get_availability_choices(),
        'selected_availability': request.session.get('signup_availability', []),
    }
    return render(request, 'users/signup_step4_minimal.html', context)


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


# ===== Profile Management =====

from .forms import ProfileEditForm


@login_required
def edit_profile(request):
    """
    Edit user profile - Personal Information only
    """
    # Get or create profile for the user
    profile, created = UserProfile.objects.get_or_create(user=request.user)
    
    if request.method == 'POST':
        form = ProfileEditForm(request.POST, request.FILES, instance=profile)
        
        if form.is_valid():
            # Save profile
            form.save()
            
            messages.success(request, 'Profile updated successfully!')
            return redirect('users:edit_profile')
    else:
        form = ProfileEditForm(instance=profile)
    
    context = {
        'form': form,
        'profile': profile,
        'user': request.user,
        'active_tab': 'personal-information'
    }
    
    return render(request, 'users/profile_edit.html', context)


@login_required
def change_password(request):
    """
    Change user password
    """
    from .forms import CustomPasswordChangeForm
    from django.contrib.auth import update_session_auth_hash
    
    if request.method == 'POST':
        form = CustomPasswordChangeForm(user=request.user, data=request.POST)
        
        if form.is_valid():
            # Save the new password
            user = form.save()
            # Update session to prevent logout
            update_session_auth_hash(request, user)
            
            messages.success(request, 'Your password has been changed successfully!')
            return redirect('users:change_password')
        else:
            # Add form errors to messages for better visibility
            for field, errors in form.errors.items():
                for error in errors:
                    if field == '__all__':
                        messages.error(request, error)
    else:
        form = CustomPasswordChangeForm(user=request.user)
    
    context = {
        'form': form,
        'user': request.user,
        'active_tab': 'change-pwd'
    }
    
    return render(request, 'users/change_password.html', context)


@login_required
def manage_contact(request):
    """
    Manage email address
    Email changes require password confirmation
    """
    from .forms import ContactEditForm
    
    if request.method == 'POST':
        form = ContactEditForm(request.POST, user=request.user)
        
        if form.is_valid():
            # Check if email has changed
            new_email = form.cleaned_data.get('email', '').strip().lower()
            if new_email != request.user.email.lower():
                # Update email
                request.user.email = new_email
                request.user.save()
                messages.success(request, 'Your email address has been changed successfully!')
            else:
                messages.info(request, 'No changes were made to your email address.')
            
            return redirect('users:manage_contact')
        else:
            # Add form errors to messages for better visibility
            for field, errors in form.errors.items():
                for error in errors:
                    if field == '__all__':
                        messages.error(request, error)
    else:
        form = ContactEditForm(user=request.user)
    
    context = {
        'form': form,
        'user': request.user,
        'active_tab': 'manage-contact'
    }
    
    return render(request, 'users/manage_contact.html', context)


def profile_view(request, username):
    """
    Display user profile page with About tab showing user information.
    """
    from django.shortcuts import get_object_or_404
    from apps.sessions.models import Session
    
    # Get the user whose profile we're viewing
    profile_user = get_object_or_404(User, username=username)
    
    # Check if this is the authenticated user's own profile
    is_own_profile = request.user.is_authenticated and request.user.username == username
    
    # Get the user's profile (one-to-one relationship)
    try:
        user_profile = profile_user.profile
    except UserProfile.DoesNotExist:
        user_profile = None
    
    # Parse sports if available
    sports_list = []
    if user_profile and user_profile.sports:
        try:
            import json
            sports_list = json.loads(user_profile.sports)
        except:
            sports_list = []
    
    # Get session statistics
    sessions_created = Session.objects.filter(creator=profile_user).count()
    sessions_joined = Session.objects.filter(invitees=profile_user).count()
    
    context = {
        'profile_user': profile_user,
        'user_profile': user_profile,
        'is_own_profile': is_own_profile,
        'sports_list': sports_list,
        'sessions_created': sessions_created,
        'sessions_joined': sessions_joined,
    }
    
    return render(request, 'users/profile.html', context)
