from apps.feedback.models import Badge, UserBadge, SessionFeedback, ParticipantFeedback
import openai
from apps.feedback.models import Session
from decouple import config


def generate_ai_summary(session: Session) -> str:
    """Generate a motivating French summary for a session using the OpenAI API."""
    api_key = config("MYOPENAI_API_KEY", default="nothing")
    if not api_key:
        raise RuntimeError("MYOPENAI_API_KEY not found in environment variables")

    client = openai.OpenAI(api_key=api_key)  # type: ignore

    prompt = f"""
    Résume cette session sportive :
    - Durée : {session.duration_minutes or "inconnue"}
    - Donne un ton positif, motivant et personnalisé en français.
    """

    response = client.chat.completions.create(
        model="gpt-5-nano",
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
    return prompt


def generate_ai_summary_from_feedbacks(session, feedback_text):
    """Generate a global summary of all user feedbacks for a session."""
    api_key = config("MYOPENAI_API_KEY", default="nothing")
    if not api_key:
        raise RuntimeError("MYOPENAI_API_KEY not found in environment variables")

    client = openai.OpenAI(api_key=api_key)  # type: ignore

    prompt = f"""
                Résume les points clés de ces feedbacks pour la session '{session.description}' :
            {feedback_text}
            Présente-les sous forme de points concis, en français, ton positif et constructif."""

    response = client.chat.completions.create(
        model="gpt-5-nano",
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
    return prompt


def award(user, criteria):
    badge = Badge.objects.filter(criteria=criteria).first()
    if badge:
        UserBadge.objects.get_or_create(user=user, badge=badge)


def evaluate_badges(user):
    # 1) Première session
    if SessionFeedback.objects.filter(user=user, user_present=True).count() >= 1:
        award(user, "first_session")

    # 2) Toujours ponctuel
    if SessionFeedback.objects.filter(user=user, punctual=True).count() >= 5:
        award(user, "punctuality_streak")

    # 3) Bon partenaire
    if SessionFeedback.objects.filter(user=user, good_partner=True).count() >= 5:
        award(user, "good_partner_streak")

    # 4) Apprécié par les autres
    if ParticipantFeedback.objects.filter(target=user, rating=1).count() >= 5:
        award(user, "well_rated")


def generate_user_feedback_summary(user) -> str:
    """
    Generate an AI-powered personalized summary for a user,
    structured professionally with sections and bullets.
    """
    api_key = config("MYOPENAI_API_KEY", default="nothing")
    if not api_key:
        raise RuntimeError("MYOPENAI_API_KEY not found in environment variables")

    client = openai.OpenAI(api_key=api_key)  # type: ignore

    # Gather data
    participant_feedbacks = ParticipantFeedback.objects.filter(
        target=user
    ).select_related("author", "session")
    session_feedbacks = SessionFeedback.objects.filter(user=user).select_related(
        "session"
    )
    badges = user.badges.select_related("badge")

    # Build concise prompt
    prompt_lines = [
        f"L'utilisateur {user.get_full_name() or user.username} a reçu les feedbacks suivants :",
        "\n-- Feedback des participants --",
    ]

    for f in participant_feedbacks:
        line = f"- {f.author.username} sur '{f.session.description}': "
        line += f"{'👍' if f.rating else '👎'} "
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
            line += f"Note : {'👍' if f.rating else '👎'} "
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
        "en utilisant une structure claire avec les sections suivantes :\n"
        "🎉 Félicitations & Badge\n"
        "💪 Points forts\n"
        "🗣️ Retours des participants\n"
        "📈 Axes d’amélioration\n"
        "🎯 Objectifs pour la prochaine session\n"
        "💡 Bonus / Plan d’action (optionnel)\n"
        "Utilise des bullet points, garde un ton motivant et bienveillant."
    )

    prompt = "\n".join(prompt_lines)

    # Call OpenAI
    response = client.chat.completions.create(
        model="gpt-5-nano",
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
