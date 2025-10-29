"""
Services module for the sessions app.
Contains business logic for AI-powered insights generation using Google Gemini API.
Keeps views.py clean and reusable.
"""

import logging
from django.conf import settings
import google.generativeai as genai

logger = logging.getLogger(__name__)

def generate_ai_insight(session):
    """
    Generate AI-powered insights for a given session using Google Gemini API.
    Returns a string with formatted Markdown insights or an error message if generation fails.
    
    Args:
        session: A Session model instance.
    
    Returns:
        str: Generated Markdown insights or fallback message.
    """
    try:
        # Configure the API with the Gemini key directly
        genai.configure(api_key=settings.GEMINI_API_KEY)
        
        # Extract session details safely (tailored to Session model)
        session_title = f"{session.sport_type} Session"  # Derive from sport_type
        session_description = session.description or 'No description provided'
        session_notes = session.description  # Reuse description as notes for now; add dedicated field later

        # Participants (use related_name if added; fallback to default)
        try:
            accepted_invitations = session.invitations.filter(status='accepted').select_related('invitee')  # Assumes related_name='invitations'
        except AttributeError:
            accepted_invitations = session.invitation_set.filter(status='accepted').select_related('invitee')
        accepted_participants = [inv.invitee for inv in accepted_invitations]
        all_participants = [session.creator] + accepted_participants
        # Anonymize for prompt privacy (use initials or usernames)
        participants_str = ", ".join([p.get_full_name() or p.username or f"User{p.id}" for p in all_participants]) or "No participants"
        member_count = len(all_participants)

        # Date/time with null safety
        session_date = session.start_datetime or session.created_at or None
        date_str = session_date.strftime('%Y-%m-%d %H:%M') if session_date else 'Date TBD'

        # Conditional prompt based on session status
        base_prompt = f"""
        You are an expert sports coach AI. Based on the session details below, 
        generate a short and practical program for the group, including:
        - Key takeaways from notes/discussion
        - Action items with owners (assign to participants if possible, e.g., {participants_str})
        - Potential follow-ups
        - Overall sentiment (positive/neutral/negative)
        - Warm-up ideas, team drills, and recovery tips based on sport type ({session.sport_type})

        Session details:
        - Title: {session_title}
        - Description: {session_description}
        - Notes: {session_notes}
        - Participants ({member_count}): {participants_str}
        - Date/Time: {date_str}
        - Duration: {session.duration_minutes or 60} minutes
        - Location: {session.location or 'Not specified'}
        """

        if session.status == 'completed':
            prompt = base_prompt + "\nFocus on recap: Analyze what went well and improvements."
        else:
            prompt = base_prompt + "\nFocus on planning: Suggest prep for upcoming session."

        # Enforce Markdown for structured output
        prompt += f"""
        Keep under 500 words.

        **Output Format (Strict Markdown):**
        - Start directly with # Main Sections (e.g., # Key Takeaways from Session Details)
        - Use ## for subsections (e.g., ## 1. Warm-up (10-15 minutes))
        - Use ### for subdrills (e.g., ### Light Jogging & Dynamic Stretches)
        - Use - for bullets (indented for subs:   - Indent with spaces)
        - Use **bold** for emphasis (e.g., **Objective:**)
        - Use --- for dividers between major parts
        - No intro/outro text; headings only.
        """

        # Generate insights using configurable model (default to 2.5 Flash as requested)
        model_name = getattr(settings, 'GEMINI_MODEL', 'gemini-2.5-flash')  # Uses 2.5 Flash; stable as of Oct 2025
        model = genai.GenerativeModel(model_name)
        response = model.generate_content(prompt)

        # Extract and validate content
        if response.text and len(response.text.strip()) > 50:  # Basic quality check
            return response.text.strip()
        else:
            return "Gemini returned empty response—ensure session has rich details (e.g., description)."

    except Exception as e:
        logger.error(f"Error generating AI insight for session {getattr(session, 'id', 'unknown')}: {e}")
        return f"Failed to generate: {str(e)[:100]}. Check GEMINI_API_KEY or try regenerating."