from django import forms
from .models import SearchFilter

SPORT_CHOICES = [
    ('', 'All Sports'),
    ('football', 'Football'),
    ('basketball', 'Basketball'),
    ('tennis', 'Tennis'),
    ('running', 'Running'),
    ('cycling', 'Cycling'),
    ('swimming', 'Swimming'),
    ('volleyball', 'Volleyball'),
    ('badminton', 'Badminton'),
    ('gym', 'Gym'),
    ('yoga', 'Yoga'),
]

LEVEL_CHOICES = [
    ('', 'All Levels'),
    ('beginner', 'Beginner'),
    ('intermediate', 'Intermediate'),
    ('advanced', 'Advanced'),
    ('expert', 'Expert'),
]

DAYS_CHOICES = [
    ('monday', 'Monday'),
    ('tuesday', 'Tuesday'),
    ('wednesday', 'Wednesday'),
    ('thursday', 'Thursday'),
    ('friday', 'Friday'),
    ('saturday', 'Saturday'),
    ('sunday', 'Sunday'),
]


class SearchFilterForm(forms.ModelForm):
    sport_type = forms.ChoiceField(
        choices=SPORT_CHOICES,
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    
    level = forms.ChoiceField(
        choices=LEVEL_CHOICES,
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    
    availability_days = forms.MultipleChoiceField(
        choices=DAYS_CHOICES,
        required=False,
        widget=forms.CheckboxSelectMultiple()
    )
    
    class Meta:
        model = SearchFilter
        fields = ['name', 'sport_type', 'location', 'max_distance_km', 'level', 
                  'availability_days', 'availability_times', 'is_favorite']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g., My morning soccer partners'
            }),
            'location': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g., Paris, France'
            }),
            'max_distance_km': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': 1,
                'max': 100,
                'value': 10
            }),
            'availability_times': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': '["08:00-10:00", "18:00-20:00"]'
            }),
            'is_favorite': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            })
        }


class AdvancedSearchForm(forms.Form):
    """More detailed search form"""
    sport = forms.ChoiceField(
        choices=SPORT_CHOICES,
        required=False,
        label='Sport',
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    
    location = forms.CharField(
        required=False,
        label='Location',
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'City or address'
        })
    )
    
    max_distance = forms.IntegerField(
        required=False,
        label='Max distance (km)',
        initial=10,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'min': 1,
            'max': 100
        })
    )
    
    level = forms.ChoiceField(
        choices=LEVEL_CHOICES,
        required=False,
        label='Level',
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    
    availability_day = forms.ChoiceField(
        choices=[('', 'All days')] + DAYS_CHOICES,
        required=False,
        label='Availability day',
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    
    availability_time = forms.ChoiceField(
        choices=[
            ('', 'All day'),
            ('morning', 'Morning (6am-12pm)'),
            ('afternoon', 'Afternoon (12pm-6pm)'),
            ('evening', 'Evening (6pm-10pm)'),
        ],
        required=False,
        label='Time slot',
        widget=forms.Select(attrs={'class': 'form-control'})
    )