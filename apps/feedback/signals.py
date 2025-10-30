from django.db.models.signals import post_save
from django.dispatch import receiver
from apps.feedback.models import SessionFeedback, ParticipantFeedback
from .services import evaluate_badges


@receiver(post_save, sender=SessionFeedback)
def session_feedback_created(sender, instance, created, **kwargs):
    if created:
        evaluate_badges(instance.user)


@receiver(post_save, sender=ParticipantFeedback)
def participant_feedback_created(sender, instance, created, **kwargs):
    if created:
        evaluate_badges(instance.target)
