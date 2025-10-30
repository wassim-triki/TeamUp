from django.db import models
from django.conf import settings

from django.contrib.auth.models import User

from apps.sessions.models import Session


class ParticipantFeedback(models.Model):
    """Feedback a user gives about another participant in the same session."""

    RATING_CHOICES = [
        (1, "👍"),
        (0, "👎"),
    ]

    session = models.ForeignKey(
        Session, on_delete=models.CASCADE, related_name="participant_feedbacks"
    )
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="given_participant_feedbacks",
    )
    target = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="received_participant_feedbacks",
    )

    rating = models.IntegerField(choices=RATING_CHOICES, blank=True, null=True)
    teamwork = models.BooleanField(default=False, help_text="Was a good teammate?")
    punctual = models.BooleanField(default=False, help_text="Was on time?")
    comment = models.TextField(blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("session", "author", "target")

    def __str__(self):
        return f"{self.author} → {self.target} ({self.session.description})"


class SessionFeedback(models.Model):
    """User feedback and attendance confirmation after a session."""

    RATING_CHOICES = [
        (1, "👍"),
        (0, "👎"),
    ]

    session = models.ForeignKey(
        Session, on_delete=models.CASCADE, related_name="feedbacks"
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="session_feedbacks",
    )

    user_present = models.BooleanField(
        default=False, help_text="User confirmed attendance"
    )
    rating = models.IntegerField(choices=RATING_CHOICES, blank=True, null=True)
    punctual = models.BooleanField(default=False)
    good_partner = models.BooleanField(default=False)
    comment = models.TextField(blank=True, null=True)
    ai_summary = models.TextField(
        blank=True, null=True, help_text="AI-generated recap or encouragement"
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Feedback from {self.user} on {self.session.description}"


class Badge(models.Model):
    """Badge definition (e.g., Toujours ponctuel, Première session)."""

    name = models.CharField(max_length=50, unique=True)
    description = models.TextField()
    criteria = models.CharField(
        max_length=100, help_text="e.g., 'punctuality', 'first_session', etc."
    )
    icon = models.ImageField(upload_to="badges/", null=True, blank=True)

    def __str__(self):
        return self.name


class UserBadge(models.Model):
    """Link between users and badges they’ve earned."""

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="badges"
    )
    badge = models.ForeignKey(Badge, on_delete=models.CASCADE)
    awarded_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("user", "badge")

    def __str__(self):
        return f"{self.user} - {self.badge.name}"
