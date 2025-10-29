# apps/sessions/models.py
from django.db import models
from django.conf import settings
from django.utils import timezone

# Exemple de choix de sports
SPORT_CHOICES = [
    ('football', 'Football'),
    ('basketball', 'Basketball'),
    ('tennis', 'Tennis'),
    ('volleyball', 'Volleyball'),
    ('swimming', 'Swimming'),
    ('running', 'Running'),
    ('cycling', 'Cycling'),
    ('gym', 'Gym / Fitness'),
    ('yoga', 'Yoga'),
    ('badminton', 'Badminton'),
    ('table_tennis', 'Table Tennis'),
    ('cricket', 'Cricket'),
    ('baseball', 'Baseball'),
    ('golf', 'Golf'),
    ('hiking', 'Hiking'),
    ('skateboarding', 'Skateboarding'),
    ('dance', 'Dance'),
    ('martial_arts', 'Martial Arts'),
    ('other', 'Other'),
]

# Icon map: value → Remixicon class
SPORT_ICONS = {
    'football': 'ri-football-fill',
    'basketball': 'ri-basketball-fill',
    'tennis': 'ri-ping-pong-fill',
    'volleyball': 'ri-volleyball-fill',
    'swimming': 'ri-water-flash-fill',
    'running': 'ri-run-fill',
    'cycling': 'ri-bike-fill',
    'gym': 'ri-barbell-fill',
    'yoga': 'ri-medal-fill',
    'badminton': 'ri-shield-cross-fill',
    'table_tennis': 'ri-ping-pong-fill',
    'cricket': 'ri-trophy-fill',
    'baseball': 'ri-baseball-fill',
    'golf': 'ri-flag-fill',
    'hiking': 'ri-map-pin-4-fill',
    'skateboarding': 'ri-skateboard-fill',
    'dance': 'ri-dance-fill',
    'martial_arts': 'ri-boxing-fill',
    'other': 'ri-trophy-fill',
}

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
