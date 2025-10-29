from django import forms
from django.contrib.auth.forms import PasswordChangeForm
from .models import UserProfile, User
from datetime import date
import re


class ProfileEditForm(forms.ModelForm):
    """
    Form for editing user profile information
    """
    
    class Meta:
        model = UserProfile
        fields = [
            'first_name', 'last_name', 'gender', 'country', 'avatar',
            'date_of_birth', 'city', 'phone', 'bio'
        ]
        widgets = {
            'first_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'First Name',
                'required': True
            }),
            'last_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Last Name',
                'required': True
            }),
            'gender': forms.RadioSelect(attrs={
                'required': True
            }),
            'country': forms.Select(attrs={
                'class': 'form-select',
                'required': True
            }),
            'avatar': forms.FileInput(attrs={
                'class': 'file-upload',
                'accept': 'image/*'
            }),
            'date_of_birth': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date',
                'placeholder': 'YYYY-MM-DD'
            }),
            'city': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'City'
            }),
            'phone': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Phone Number'
            }),
            'bio': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Tell us about yourself...'
            }),
        }
    
    def clean_first_name(self):
        """Validate first name is provided"""
        first_name = self.cleaned_data.get('first_name', '').strip()
        if not first_name:
            raise forms.ValidationError('First name is required.')
        return first_name
    
    def clean_last_name(self):
        """Validate last name is provided"""
        last_name = self.cleaned_data.get('last_name', '').strip()
        if not last_name:
            raise forms.ValidationError('Last name is required.')
        return last_name
    
    def clean_gender(self):
        """Validate gender is provided"""
        gender = self.cleaned_data.get('gender')
        if not gender:
            raise forms.ValidationError('Gender is required.')
        return gender
    
    def clean_country(self):
        """Validate country is provided"""
        country = self.cleaned_data.get('country')
        if not country or country == '':
            raise forms.ValidationError('Country is required.')
        return country
    
    def clean_phone(self):
        """Validate phone number format"""
        phone = self.cleaned_data.get('phone', '').strip()
        
        if phone:
            # Remove common separators for validation
            phone_digits = re.sub(r'[\s\-\(\)\+]', '', phone)
            
            # Check if it contains only digits and common phone symbols
            if not re.match(r'^[\d\s\-\(\)\+]+$', phone):
                raise forms.ValidationError('Please enter a valid phone number.')
            
            # Check reasonable length
            if len(phone_digits) < 7 or len(phone_digits) > 15:
                raise forms.ValidationError('Phone number must be between 7 and 15 digits.')
        
        return phone
    
    def clean_date_of_birth(self):
        """Validate date of birth is not in the future"""
        dob = self.cleaned_data.get('date_of_birth')
        if dob:
            if dob > date.today():
                raise forms.ValidationError('Date of birth cannot be in the future.')
            # Calculate age if date of birth is provided
            today = date.today()
            age = today.year - dob.year - ((today.month, today.day) < (dob.month, dob.day))
            if age < 1:
                raise forms.ValidationError('You must be at least 1 year old.')
        return dob
    
    def clean_avatar(self):
        """Validate avatar file size and type"""
        avatar = self.cleaned_data.get('avatar')
        if avatar:
            # Check file size (max 5MB)
            if avatar.size > 5 * 1024 * 1024:
                raise forms.ValidationError('Avatar file size cannot exceed 5MB.')
            
            # Check file type
            valid_extensions = ['jpg', 'jpeg', 'png', 'gif', 'webp']
            ext = avatar.name.split('.')[-1].lower()
            if ext not in valid_extensions:
                raise forms.ValidationError(f'Only image files are allowed ({", ".join(valid_extensions)}).')
        
        return avatar


class ContactEditForm(forms.Form):
    """
    Form for changing email address
    Email changes require password confirmation for security
    """
    email = forms.EmailField(
        required=True,
        label='Email Address',
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'Email Address'
        }),
        error_messages={
            'required': 'Email address is required.',
            'invalid': 'Please enter a valid email address.'
        }
    )
    
    password = forms.CharField(
        required=False,
        label='Current Password (required to change email)',
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter password to confirm email change'
        }),
        help_text='Only required if you change your email address'
    )
    
    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        
        # Pre-populate email with current value
        if self.user and not self.is_bound:
            self.fields['email'].initial = self.user.email
    
    def clean_email(self):
        """Validate email is unique and properly formatted"""
        email = self.cleaned_data.get('email', '').strip().lower()
        
        if not email:
            raise forms.ValidationError('Email address is required.')
        
        # Check if email has changed
        if self.user and email != self.user.email.lower():
            # Check if email is already taken by another user
            if User.objects.filter(email=email).exclude(pk=self.user.pk).exists():
                raise forms.ValidationError('This email address is already in use by another account.')
        
        return email
    
    def clean(self):
        """Validate that password is provided if email is changed"""
        cleaned_data = super().clean()
        email = cleaned_data.get('email', '').strip().lower()
        password = cleaned_data.get('password')
        
        # Check if email has changed
        if self.user and email != self.user.email.lower():
            # Password is required when changing email
            if not password:
                raise forms.ValidationError('Please enter your current password to change your email address.')
            
            # Verify the password is correct
            if not self.user.check_password(password):
                raise forms.ValidationError('The password you entered is incorrect.')
        
        return cleaned_data


class CustomPasswordChangeForm(PasswordChangeForm):
    """
    Custom password change form with Bootstrap styling and enhanced validation
    """
    old_password = forms.CharField(
        label='Current Password',
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter your current password',
            'required': True
        }),
        error_messages={
            'required': 'Current password is required.',
        }
    )
    new_password1 = forms.CharField(
        label='New Password',
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter new password (min 8 characters)',
            'required': True
        }),
        error_messages={
            'required': 'New password is required.',
        }
    )
    new_password2 = forms.CharField(
        label='Verify Password',
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Re-enter new password',
            'required': True
        }),
        error_messages={
            'required': 'Please verify your new password.',
        }
    )
    
    def clean_old_password(self):
        """Validate the old password"""
        old_password = self.cleaned_data.get('old_password')
        if not old_password:
            raise forms.ValidationError('Current password is required.')
        
        # Django's PasswordChangeForm will automatically check if old password is correct
        # We just need to call the parent method
        return super().clean_old_password()
    
    def clean_new_password1(self):
        """Validate new password strength"""
        password = self.cleaned_data.get('new_password1')
        old_password = self.cleaned_data.get('old_password')
        
        if not password:
            raise forms.ValidationError('New password is required.')
        
        if len(password) < 8:
            raise forms.ValidationError('Password must be at least 8 characters long.')
        
        # Check if password contains both letters and numbers
        if not re.search(r'[A-Za-z]', password):
            raise forms.ValidationError('Password must contain at least one letter.')
        
        if not re.search(r'\d', password):
            raise forms.ValidationError('Password must contain at least one number.')
        
        # Check if new password is different from old password
        if old_password and password == old_password:
            raise forms.ValidationError('New password must be different from your current password.')
        
        return password
    
    def clean_new_password2(self):
        """Validate that the two password fields match"""
        password1 = self.cleaned_data.get('new_password1')
        password2 = self.cleaned_data.get('new_password2')
        
        if password1 and password2:
            if password1 != password2:
                raise forms.ValidationError('The two password fields must match.')
        
        return password2
