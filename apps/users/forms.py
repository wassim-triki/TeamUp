from django import forms
from django.contrib.auth.forms import PasswordChangeForm
from .models import UserProfile, User
from datetime import date


class ProfileEditForm(forms.ModelForm):
    """
    Form for editing user profile information
    """
    # Add username field from User model
    username = forms.CharField(
        max_length=150,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Username'
        })
    )
    
    class Meta:
        model = UserProfile
        fields = [
            'first_name', 'last_name', 'avatar', 'date_of_birth', 
            'age', 'gender', 'city', 'state', 
            'address', 'phone', 'bio'
        ]
        widgets = {
            'first_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'First Name'
            }),
            'last_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Last Name'
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
            'age': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Age',
                'min': 1,
                'max': 150
            }),
            'gender': forms.Select(attrs={
                'class': 'form-select'
            }),
            'city': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'City'
            }),
            'state': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'State'
            }),
            'address': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 5,
                'placeholder': 'Full Address'
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
    
    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        
        # Populate username field if user is provided
        if user:
            self.fields['username'].initial = user.username
    
    def clean_age(self):
        """Validate age is reasonable"""
        age = self.cleaned_data.get('age')
        if age is not None:
            if age < 1 or age > 150:
                raise forms.ValidationError('Please enter a valid age between 1 and 150.')
        return age
    
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
    Form for editing contact information
    """
    phone = forms.CharField(
        max_length=20,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Contact Number'
        })
    )
    
    email = forms.EmailField(
        required=False,
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'Email Address',
            'readonly': 'readonly'
        })
    )
    
    url = forms.URLField(
        required=False,
        widget=forms.URLInput(attrs={
            'class': 'form-control',
            'placeholder': 'Website URL'
        })
    )


class CustomPasswordChangeForm(PasswordChangeForm):
    """
    Custom password change form with Bootstrap styling
    """
    old_password = forms.CharField(
        label='Current Password',
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Current Password'
        })
    )
    new_password1 = forms.CharField(
        label='New Password',
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'New Password'
        })
    )
    new_password2 = forms.CharField(
        label='Verify Password',
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Verify Password'
        })
    )
