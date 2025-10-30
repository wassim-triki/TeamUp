from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth.models import User
from apps.feedback.forms import ParticipantFeedbackForm, SessionFeedbackForm
from .models import ParticipantFeedback, Session, SessionFeedback
from .services import (
    generate_ai_summary,
    generate_ai_summary_from_feedbacks,
    generate_user_feedback_summary,
)
from django.http import JsonResponse
import logging

logger = logging.getLogger(__name__)


@login_required
def confirm_presence(request, session_id):
    """Step 1: Confirm presence — then redirect to feedback form."""
    session = get_object_or_404(Session, id=session_id)

    # Check if feedback already exists
    feedback, created = SessionFeedback.objects.get_or_create(
        user=request.user, session=session
    )

    if request.method == "POST":
        feedback.user_present = True
        # Generate AI summary immediately
        summary_text = generate_ai_summary(session)
        feedback.ai_summary = summary_text
        feedback.save(update_fields=["user_present", "ai_summary"])
        return redirect("submit_feedback", session_id=session.id)

    return render(request, "feedback/confirm_presence.html", {"session": session})


@login_required
def submit_feedback(request, session_id):
    """Step 2: User writes feedback, sees AI summary."""
    session = get_object_or_404(Session, id=session_id)
    feedback = get_object_or_404(SessionFeedback, session=session, user=request.user)

    if request.method == "POST":
        feedback.rating = request.POST.get("rating")
        feedback.punctual = bool(request.POST.get("punctual"))
        feedback.good_partner = bool(request.POST.get("good_partner"))
        feedback.comment = request.POST.get("comment")
        feedback.save()
        return redirect("sessions:detail", pk=session.pk)

    context = {
        "session": session,
        "feedback": feedback,
        "ai_summary": feedback.ai_summary,
    }
    return render(request, "feedback/submit_feedback.html", context)


@login_required
def session_feedback(request, session_id):
    """Display all feedbacks for a specific session."""
    session = get_object_or_404(Session, id=session_id)
    feedbacks = (
        SessionFeedback.objects.filter(session=session)
        .select_related("user")
        .order_by("-created_at")
    )

    participants = session.invitees.all()

    return render(
        request,
        "feedback/session_feedback.html",
        {
            "session": session,
            "feedbacks": feedbacks,
            "participants": participants,
        },
    )


@login_required
def generate_session_summary(request, session_id):
    """Generate a global AI summary of all feedback for a session."""
    session = get_object_or_404(Session, id=session_id)
    feedbacks = SessionFeedback.objects.filter(session=session)

    if not feedbacks.exists():
        return JsonResponse(
            {"summary": "Aucun feedback disponible pour cette session."}
        )

    # Combine all feedbacks into one text prompt
    combined_feedback = "\n".join(
        f"- {fb.user}: {fb.comment or 'Pas de commentaire.'}" for fb in feedbacks
    )

    # Call your AI summary function
    try:
        ai_summary = generate_ai_summary_from_feedbacks(session, combined_feedback)
    except Exception as e:
        return JsonResponse({"summary": f"Erreur lors de la génération : {str(e)}"})

    return JsonResponse({"summary": ai_summary})


@login_required
def edit_feedback(request, pk):
    """Allow user to edit their own feedback."""
    feedback = get_object_or_404(SessionFeedback, pk=pk, user=request.user)

    if request.method == "POST":
        form = SessionFeedbackForm(request.POST, instance=feedback)
        if form.is_valid():
            form.save()
            messages.success(request, "Votre feedback a été mis à jour ✅")
            return redirect("session_feedback", session_id=feedback.session.id)
    else:
        form = SessionFeedbackForm(instance=feedback)

    return render(
        request, "feedback/edit_feedback.html", {"form": form, "feedback": feedback}
    )


@login_required
def delete_feedback(request, pk):
    """Allow user to delete their own feedback, with confirmation."""
    feedback = get_object_or_404(SessionFeedback, pk=pk, user=request.user)

    if request.method == "POST":
        session_id = feedback.session.id
        feedback.delete()
        messages.success(request, "Votre feedback a été supprimé 🗑️")
        return redirect("session_feedback", session_id=session_id)

    return render(request, "feedback/delete_feedback.html", {"feedback": feedback})


@login_required
def give_participant_feedback(request, session_id):
    session = get_object_or_404(Session, id=session_id)
    user = request.user
    target_id = request.GET.get("target")

    if not target_id:
        messages.error(request, "Aucun participant spécifié.")
        return redirect("session_feedback", session_id=session.id)

    target_user = session.invitees.filter(id=target_id).first()
    if not target_user:
        messages.error(request, "Participant introuvable pour cette session.")
        return redirect("session_feedback", session_id=session.id)

    feedback, _ = ParticipantFeedback.objects.get_or_create(
        session=session,
        author=user,
        target=target_user,
    )

    if request.method == "POST":
        form = ParticipantFeedbackForm(request.POST, instance=feedback)
        if form.is_valid():
            form.instance.session = session
            form.instance.author = user
            form.instance.target = target_user
            form.save()
            messages.success(request, f"Feedback envoyé pour {target_user.username} ✅")
            return redirect("session_feedback", session_id=session.id)
    else:
        form = ParticipantFeedbackForm(instance=feedback)

    return render(
        request,
        "feedback/give_participant_feedback.html",
        {"form": form, "session": session, "target_user": target_user},
    )


@login_required
def user_feedback_summary(request):
    user = request.user

    participant_feedbacks = ParticipantFeedback.objects.filter(
        target=user
    ).select_related("author", "session")
    session_feedbacks = SessionFeedback.objects.filter(user=user).select_related(
        "session"
    )
    user_badges = user.badges.select_related("badge")  # ⭐ Add this

    return render(
        request,
        "feedback/user_summary.html",
        {
            "participant_feedbacks": participant_feedbacks,
            "session_feedbacks": session_feedbacks,
            "user_badges": user_badges,  # ⭐ Pass to template
        },
    )


@login_required
def generate_user_summary_api(request):
    user = request.user
    try:
        summary = generate_user_feedback_summary(user)
        return JsonResponse({"summary": summary})
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)
