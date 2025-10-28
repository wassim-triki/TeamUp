# apps/sessions/models.py
from django.db import models
from django.conf import settings
from django.utils import timezone

# Exemple de choix de sports
SPORT_CHOICES = [
    ('soccer', 'Soccer'),
    ('basketball', 'Basketball'),
    ('tennis', 'Tennis'),
    ('running', 'Running'),
    # ajouter d'autres si nécessaire
]

STATUS_CHOICES = [
    ('draft', 'Draft'),
    ('proposed', 'Proposed'),
    ('confirmed', 'Confirmed'),
    ('cancelled', 'Cancelled'),
    ('completed', 'Completed'),
]

INVITATION_STATUS_CHOICES = [
    ('pending', 'Pending'),
    ('accepted', 'Accepted'),
    ('refused', 'Refused'),
    ('rescheduled', 'Rescheduled'),
]


class Session(models.Model):
    sport_type = models.CharField(max_length=20, choices=SPORT_CHOICES)
    start_datetime = models.DateTimeField()
    duration_minutes = models.PositiveIntegerField(default=60)
    location = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')

    creator = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='created_sessions'
    )
    invitees = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        through='Invitation',
        related_name='invited_sessions'
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.sport_type} session on {self.start_datetime.date()}"

    def is_upcoming(self):
        return self.start_datetime > timezone.now()


class Invitation(models.Model):
    session = models.ForeignKey(Session, on_delete=models.CASCADE)
    invitee = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    status = models.CharField(max_length=20, choices=INVITATION_STATUS_CHOICES, default='pending')
    response_notes = models.TextField(blank=True)
    rescheduled_datetime = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"Invite to {self.session} for {self.invitee.email}"


# Optionnel, stub pour IA / suggestions
class SuggestedSlot(models.Model):
    session = models.ForeignKey(Session, on_delete=models.CASCADE, related_name='suggestions')
    proposed_datetime = models.DateTimeField()
    rationale = models.TextField()

    def __str__(self):
        return f"Suggested slot for {self.session} at {self.proposed_datetime}"
