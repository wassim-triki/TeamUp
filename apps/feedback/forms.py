from django import forms
from .models import ParticipantFeedback, SessionFeedback


class SessionFeedbackForm(forms.ModelForm):
    class Meta:
        model = SessionFeedback
        fields = ["user_present", "rating", "punctual", "good_partner", "comment"]
        widgets = {
            "user_present": forms.CheckboxInput(attrs={"class": "form-check-input"}),
            "punctual": forms.CheckboxInput(attrs={"class": "form-check-input"}),
            "good_partner": forms.CheckboxInput(attrs={"class": "form-check-input"}),
            "rating": forms.Select(attrs={"class": "form-select"}),
            "comment": forms.Textarea(attrs={"class": "form-control", "rows": 3}),
        }


class ParticipantFeedbackForm(forms.ModelForm):
    class Meta:
        model = ParticipantFeedback
        exclude = ["session", "author", "target", "created_at"]
        widgets = {
            "rating": forms.RadioSelect(attrs={"class": "form-check-input"}),
            "teamwork": forms.CheckboxInput(attrs={"class": "form-check-input"}),
            "punctual": forms.CheckboxInput(attrs={"class": "form-check-input"}),
            "comment": forms.Textarea(attrs={"class": "form-control", "rows": 3}),
        }
        labels = {
            "rating": "Évaluation générale",
            "teamwork": "Bon coéquipier",
            "punctual": "Ponctuel",
            "comment": "Commentaire",
        }
