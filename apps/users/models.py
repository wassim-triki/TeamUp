from django.contrib.auth.models import AbstractUser, UserManager
from django.db import models
from django.utils import timezone
import uuid
from datetime import timedelta


class CustomUserManager(UserManager):
    """
    Custom user manager to handle user creation with email-based authentication
    """
    def create_user(self, email=None, password=None, **extra_fields):
        """
        Create and save a regular user with the given email and password.
        """
        if not email:
            raise ValueError('Email is required')
        
        email = self.normalize_email(email)
        
        # Generate username from email if not provided
        if 'username' not in extra_fields:
            username = email.split('@')[0]
            base_username = username
            counter = 1
            # Ensure username is unique
            while self.model.objects.filter(username=username).exists():
                username = f"{base_username}{counter}"
                counter += 1
            extra_fields['username'] = username
        
        extra_fields.setdefault('is_staff', False)
        extra_fields.setdefault('is_superuser', False)
        extra_fields.setdefault('is_active', False)  # Regular users need email verification
        
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user
    
    def create_superuser(self, email, password=None, **extra_fields):
        """
        Create and save a superuser with is_active=True
        """
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)  # Superusers are active by default
        
        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')
        
        return self.create_user(email, password, **extra_fields)


class User(AbstractUser):
    """
    Custom User model extending AbstractUser.
    Uses email as the primary identifier for authentication.
    """
    email = models.EmailField(unique=True, verbose_name="Email Address")
    is_active = models.BooleanField(default=False, help_text="Designates whether this user should be treated as active. Set to False until email is verified.")
    email_verified_at = models.DateTimeField(null=True, blank=True, verbose_name="Email Verified At")
    
    # Override username to make it auto-generated
    username = models.CharField(max_length=150, unique=True)
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']
    
    objects = CustomUserManager()  # Use custom manager
    
    class Meta:
        verbose_name = 'User'
        verbose_name_plural = 'Users'
    
    def __str__(self):
        return self.email


class UserProfile(models.Model):
    """
    User profile with additional information like sports and availability.
    OneToOne relationship with User model.
    """
    # Keep old choices for backwards compatibility during migration
    SPORT_CHOICES = [
        ('football', 'Football'),
        ('basketball', 'Basketball'),
        ('tennis', 'Tennis'),
        ('volleyball', 'Volleyball'),
        ('swimming', 'Swimming'),
        ('running', 'Running'),
        ('cycling', 'Cycling'),
        ('gym', 'Gym/Fitness'),
        ('yoga', 'Yoga'),
        ('other', 'Other'),
    ]
    
    GENDER_CHOICES = [
        ('male', 'Male'),
        ('female', 'Female'),
    ]
    
    # ISO 3166-1 alpha-2 country codes - commonly used countries
    COUNTRY_CHOICES = [
        ('', 'Select Country'),
        ('TN', 'Tunisia'),
        ('DZ', 'Algeria'),
        ('MA', 'Morocco'),
        ('EG', 'Egypt'),
        ('LY', 'Libya'),
        ('FR', 'France'),
        ('DE', 'Germany'),
        ('GB', 'United Kingdom'),
        ('US', 'United States'),
        ('CA', 'Canada'),
        ('IT', 'Italy'),
        ('ES', 'Spain'),
        ('PT', 'Portugal'),
        ('BE', 'Belgium'),
        ('NL', 'Netherlands'),
        ('SA', 'Saudi Arabia'),
        ('AE', 'United Arab Emirates'),
        ('QA', 'Qatar'),
        ('KW', 'Kuwait'),
        ('TR', 'Turkey'),
        ('XX', 'Other'),
    ]
    
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    
    # Personal Information (Required fields)
    first_name = models.CharField(max_length=50, help_text="Required", default='')
    last_name = models.CharField(max_length=50, help_text="Required", default='')
    gender = models.CharField(max_length=10, choices=GENDER_CHOICES, help_text="Required", default='male')
    country = models.CharField(max_length=10, choices=COUNTRY_CHOICES, help_text="Required", default='TN')
    
    # Personal Information (Optional fields)
    avatar = models.ImageField(upload_to='avatars/', blank=True, null=True, help_text="User profile picture")
    date_of_birth = models.DateField(blank=True, null=True, help_text="Date of birth")
    age = models.PositiveIntegerField(blank=True, null=True, help_text="Age in years")
    city = models.CharField(max_length=100, blank=True, default='', help_text="City name")
    phone = models.CharField(max_length=20, blank=True, default='', help_text="Contact phone number")
    bio = models.TextField(blank=True, default='', help_text="Short bio or description")
    
    # Sports - ManyToMany relationship with Sport model
    interested_sports = models.ManyToManyField(
        'core.Sport',
        blank=True,
        related_name='interested_users',
        help_text="Sports the user is interested in"
    )
    
    # Keep old sports field for backwards compatibility during migration
    sports = models.TextField(help_text="JSON array of selected sports (deprecated - use interested_sports)", blank=True, default='[]')
    
    # Availability stored as text summary or JSON
    availability = models.TextField(help_text="User's availability schedule", blank=True, default='')
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'User Profile'
        verbose_name_plural = 'User Profiles'
    
    def __str__(self):
        return f"Profile of {self.user.email}"
    
    @property
    def full_name(self):
        """Return the full name of the user"""
        if self.first_name and self.last_name:
            return f"{self.first_name} {self.last_name}"
        elif self.first_name:
            return self.first_name
        return self.user.username


class EmailVerificationToken(models.Model):
    """
    Token for email verification during signup.
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='verification_tokens')
    token = models.CharField(max_length=100, unique=True, default=uuid.uuid4)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()
    used = models.BooleanField(default=False)
    
    class Meta:
        verbose_name = 'Email Verification Token'
        verbose_name_plural = 'Email Verification Tokens'
        ordering = ['-created_at']
    
    def save(self, *args, **kwargs):
        # Set expiration to 24 hours from creation if not set
        if not self.expires_at:
            self.expires_at = timezone.now() + timedelta(hours=24)
        super().save(*args, **kwargs)
    
    def is_valid(self):
        """Check if token is valid (not used and not expired)"""
        return not self.used and timezone.now() < self.expires_at
    
    def __str__(self):
        return f"Token for {self.user.email} - {'Used' if self.used else 'Active'}"
