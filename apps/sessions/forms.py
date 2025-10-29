from django import forms
from django.utils import timezone
from django.contrib.auth import get_user_model
from .models import Session

User = get_user_model()

class SessionForm(forms.ModelForm):
    class Meta:
        model = Session
        fields = ['sport_type', 'start_datetime', 'duration_minutes', 'location', 'description']

    def clean_start_datetime(self):
        dt = self.cleaned_data['start_datetime']
        if dt <= timezone.now():
            raise forms.ValidationError("Date must be in the future.")
        return dt

class InviteForm(forms.Form):
    users = forms.ModelMultipleChoiceField(queryset=User.objects.all(), required=False)

class ResponseForm(forms.Form):
    action = forms.ChoiceField(choices=[('accept','Accept'), ('refuse','Refuse'), ('reschedule','Reschedule')])
    notes = forms.CharField(widget=forms.Textarea, required=False)
    new_datetime = forms.DateTimeField(required=False)
