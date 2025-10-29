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
    Returns a string with formatted insights or an error message if generation fails.
    
    Args:
        session: A Session model instance.
    
    Returns:
        str: Generated insights or fallback message.
    """
    try:
        # Configure the API with the Gemini key directly
        genai.configure(api_key=settings.GEMINI_API_KEY)
        
        # Extract session details safely
        session_title = getattr(session, 'title', getattr(session, 'name', 'Untitled Session'))
        session_description = getattr(session, 'description', 'No description provided')
        session_notes = getattr(session, 'notes', 'No notes provided')

        # Participants
        accepted_invitations = session.invitation_set.filter(status='accepted').select_related('invitee')
        accepted_participants = [inv.invitee for inv in accepted_invitations]
        all_participants = [session.creator] + accepted_participants
        participants_str = ", ".join([p.get_full_name() or p.email for p in all_participants]) or "No participants"
        member_count = len(all_participants)

        # Date/time
        session_date = getattr(session, 'start_datetime', getattr(session, 'created_at', None))
        date_str = session_date.strftime('%Y-%m-%d %H:%M') if session_date else 'Unknown date'

        # Build prompt
        prompt = f"""
        You are an expert sports coach AI. Based on the session details below, 
        generate a short and practical program for the group, including:
        - Key takeaways from notes/discussion
        - Action items with owners (assign to participants if possible)
        - Potential follow-ups
        - Overall sentiment (positive/neutral/negative)
        - Warm-up ideas, team drills, and recovery tips based on sport type

        Session details:
        - Title/Name: {session_title}
        - Sport Type: {getattr(session, 'sport_type', 'General')}
        - Description: {session_description}
        - Notes/Transcript: {session_notes}
        - Participants ({member_count}): {participants_str}
        - Date/Time: {date_str}
        - Duration: {getattr(session, 'duration_minutes', 60)} minutes
        - Location: {getattr(session, 'location', 'Not specified')}

        Keep the response under 500 words, structured with bullet points for readability.
        """

        # Generate insights using the native Gemini model
        model = genai.GenerativeModel('gemini-2.5-flash')
        response = model.generate_content(prompt)

        # Extract content
        if response.text:
            return response.text.strip()
        else:
            return "No insights generated—check your API key or session data."

    except Exception as e:
        logger.error(f"Error generating AI insight: {e}")
        return f"Failed to generate insights: {str(e)}. Ensure GEMINI_API_KEY is valid and SDK is up-to-date."