from apps.feedback.models import Badge, UserBadge, SessionFeedback, ParticipantFeedback
import openai
from apps.feedback.models import Session
from decouple import config


def generate_ai_summary(session: Session) -> str:
    """Generate a motivating French summary for a session using the OpenAI API."""
    api_key = config("MYOPENAI_API_KEY", default="")
    if not api_key or api_key == "nothing":
        return "Résumé IA non disponible - Clé API non configurée."

    try:
        client = openai.OpenAI(api_key=api_key)

        prompt = f"""
        Résume cette session sportive :
        - Durée : {session.duration_minutes or "inconnue"}
        - Donne un ton positif, motivant et personnalisé en français.
        """

        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {
                    "role": "system",
                    "content": "Tu es un coach sportif motivant et bienveillant.",
                },
                {"role": "user", "content": prompt},
            ],
        )

        text = response.choices[0].message.content
        if text:
            return text.strip()
        return "Session complétée avec succès"
    except Exception as e:
        return f"Résumé IA temporairement indisponible. Erreur: {str(e)[:100]}"


def generate_ai_summary_from_feedbacks(session, feedback_text):
    """Generate a global summary of all user feedbacks for a session."""
    api_key = config("MYOPENAI_API_KEY", default="")
    if not api_key or api_key == "nothing":
        return "Résumé IA non disponible - Clé API non configurée."

    try:
        client = openai.OpenAI(api_key=api_key)

        prompt = f"""
                    Résume les points clés de ces feedbacks pour la session '{session.description}' :
                {feedback_text}
                Présente-les sous forme de points concis, en français, ton positif et constructif."""

        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {
                    "role": "system",
                    "content": "Tu es un assistant sportif et bienveillant.",
                },
                {"role": "user", "content": prompt},
            ],
        )
        text = response.choices[0].message.content
        if text:
            return text.strip()
        return "Résumé des feedbacks disponible."
    except Exception as e:
        return f"Résumé IA temporairement indisponible. Erreur: {str(e)[:100]}"


def award(user, criteria):
    badge = Badge.objects.filter(criteria=criteria).first()
    if badge:
        UserBadge.objects.get_or_create(user=user, badge=badge)


def evaluate_badges(user):
    if SessionFeedback.objects.filter(user=user, user_present=True).count() >= 1:
        award(user, "first_session")

    if SessionFeedback.objects.filter(user=user, punctual=True).count() >= 5:
        award(user, "punctuality_streak")

    if SessionFeedback.objects.filter(user=user, good_partner=True).count() >= 5:
        award(user, "good_partner_streak")

    if ParticipantFeedback.objects.filter(target=user, rating=1).count() >= 5:
        award(user, "well_rated")


def generate_user_feedback_summary(user) -> str:
    """Generate an AI-powered personalized summary for a user."""
    api_key = config("MYOPENAI_API_KEY", default="")
    if not api_key or api_key == "nothing":
        return "Résumé IA non disponible - Clé API non configurée."

    try:
        client = openai.OpenAI(api_key=api_key)

        participant_feedbacks = ParticipantFeedback.objects.filter(
            target=user
        ).select_related("author", "session")
        session_feedbacks = SessionFeedback.objects.filter(user=user).select_related(
            "session"
        )
        badges = user.badges.select_related("badge")

        prompt_lines = [
            f"L'utilisateur {user.get_full_name() or user.username} a reçu les feedbacks suivants :",
            "\n-- Feedback des participants --",
        ]

        for f in participant_feedbacks:
            line = f"- {f.author.username} sur '{f.session.description}': "
            line += f"{'���' if f.rating else '���'} "
            if f.teamwork:
                line += "(bon coéquipier) "
            if f.punctual:
                line += "(ponctuel) "
            if f.comment:
                line += f"- Commentaire : {f.comment}"
            prompt_lines.append(line)

        prompt_lines.append("\n-- Feedback des sessions --")
        for f in session_feedbacks:
            line = f"- Session '{f.session.description}': "
            line += f"{'Présent' if f.user_present else 'Absent'}, "
            if f.rating is not None:
                line += f"Note : {'���' if f.rating else '���'} "
            if f.punctual:
                line += "(ponctuel) "
            if f.good_partner:
                line += "(bon partenaire) "
            if f.comment:
                line += f"- Commentaire : {f.comment}"
            prompt_lines.append(line)

        if badges.exists():
            badge_list = ", ".join([ub.badge.name for ub in badges])
            prompt_lines.append(
                f"\nL'utilisateur a gagné les badges suivants : {badge_list}"
            )

        prompt_lines.append(
            "\nFais un résumé motivant, positif et constructif pour cet utilisateur en français, "
            "avec points forts, retours et axes d'amélioration."
        )

        prompt = "\n".join(prompt_lines)

        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {
                    "role": "system",
                    "content": "Tu es un coach sportif motivant et bienveillant.",
                },
                {"role": "user", "content": prompt},
            ],
        )

        text = response.choices[0].message.content
        return text.strip() if text else "Résumé indisponible pour le moment."
    except Exception as e:
        return f"Résumé IA temporairement indisponible. Erreur: {str(e)[:100]}"
