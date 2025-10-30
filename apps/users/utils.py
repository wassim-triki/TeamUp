"""
Utility functions for user-related operations, including availability matching.
"""


def calculate_availability_match(availability1, availability2):
    """
    Calculate match score between two users based on overlapping availability patterns.
    
    Args:
        availability1: List of availability pattern codes (e.g., ['weekday_mornings', 'flexible'])
        availability2: List of availability pattern codes
        
    Returns:
        Integer match score from 0-100, where:
        - 0 = no overlap
        - 100 = complete overlap
        - Higher scores indicate better matches
    """
    if not availability1 or not availability2:
        return 0
    
    # Convert to sets for easy comparison
    set1 = set(availability1)
    set2 = set(availability2)
    
    # If either user has 'flexible', they match with everything
    if 'flexible' in set1 or 'flexible' in set2:
        return 90  # High match but not perfect
    
    # Calculate overlap
    overlap = set1 & set2
    union = set1 | set2
    
    if not union:
        return 0
    
    # Calculate Jaccard similarity (intersection over union)
    match_score = int((len(overlap) / len(union)) * 100)
    
    return match_score


def get_compatible_users(user_profile, min_score=30, limit=10):
    """
    Find users with compatible availability patterns.
    
    Args:
        user_profile: UserProfile instance to find matches for
        min_score: Minimum match score to include (default: 30)
        limit: Maximum number of matches to return (default: 10)
        
    Returns:
        List of tuples: [(user_profile, match_score), ...]
        Sorted by match score (highest first)
    """
    from .models import UserProfile
    
    if not user_profile.availability:
        return []
    
    # Get all other users with availability data
    other_users = UserProfile.objects.exclude(
        user=user_profile.user
    ).filter(
        user__is_active=True
    ).exclude(
        availability__isnull=True
    ).exclude(
        availability=[]
    )
    
    # Calculate match scores
    matches = []
    for other_profile in other_users:
        score = calculate_availability_match(
            user_profile.availability,
            other_profile.availability
        )
        
        if score >= min_score:
            matches.append((other_profile, score))
    
    # Sort by score (highest first) and limit results
    matches.sort(key=lambda x: x[1], reverse=True)
    
    return matches[:limit]


def format_availability_for_display(availability_patterns):
    """
    Convert availability pattern codes to human-readable format.
    
    Args:
        availability_patterns: List of pattern codes
        
    Returns:
        String with formatted availability
    """
    from .models import UserProfile
    
    if not availability_patterns:
        return "Not specified"
    
    pattern_dict = {
        code: name for code, name, _ in UserProfile.AVAILABILITY_PATTERNS
    }
    
    return ", ".join([pattern_dict.get(code, code) for code in availability_patterns])


def generate_profile_tags(user_profile):
    """
    Generate 2-3 AI-powered personality tags for a user profile using Gemini API.
    Tags are short descriptive labels like "Morning runner", "Social athlete", etc.
    
    Args:
        user_profile: UserProfile instance with sports, availability, and other data
        
    Returns:
        List of 2-3 tag strings, or empty list if generation fails
    """
    import logging
    from django.conf import settings
    import google.generativeai as genai
    
    logger = logging.getLogger(__name__)
    
    try:
        # Configure Gemini API
        genai.configure(api_key=settings.GEMINI_API_KEY)
        
        # Gather profile information
        sports_list = []
        if user_profile.interested_sports.exists():
            sports_list = [sport.name for sport in user_profile.interested_sports.all()]
        elif user_profile.sports:
            # Fallback to old sports field if using deprecated format
            import json
            try:
                sports_list = json.loads(user_profile.sports)
            except:
                pass
        
        # Format availability patterns
        availability_display = format_availability_for_display(user_profile.availability)
        
        # Build profile summary
        profile_info = []
        if sports_list:
            profile_info.append(f"Sports: {', '.join(sports_list)}")
        if user_profile.availability:
            profile_info.append(f"Availability: {availability_display}")
        if user_profile.gender:
            profile_info.append(f"Gender: {user_profile.gender}")
        if user_profile.age:
            profile_info.append(f"Age: {user_profile.age}")
        if user_profile.city:
            profile_info.append(f"Location: {user_profile.city}")
        
        profile_text = "\n".join(profile_info) if profile_info else "Basic profile"
        
        # Create prompt for Gemini
        prompt = f"""Based on this user's profile, generate exactly 3 short personality tags or labels (2-4 words each).
These tags should capture their athletic personality, activity preferences, and lifestyle.

Profile:
{profile_text}

Requirements:
- Output ONLY 3 tags, one per line
- Each tag should be 2-4 words maximum
- Use descriptive, positive language
- Format examples: "Morning runner", "Team player", "Fitness enthusiast", "Weekend warrior", "Beginner athlete"
- No bullets, numbers, or extra formatting
- Just the tags, nothing else

Tags:"""

        # Generate tags using Gemini
        model_name = getattr(settings, 'GEMINI_MODEL', 'gemini-2.0-flash-exp')
        model = genai.GenerativeModel(model_name)
        response = model.generate_content(prompt)
        
        if response.text:
            # Parse response - split by newlines and clean up
            lines = response.text.strip().split('\n')
            tags = []
            
            for line in lines:
                # Clean up the line (remove bullets, numbers, extra spaces)
                tag = line.strip()
                tag = tag.lstrip('•-*123456789.)').strip()
                
                # Only include non-empty tags
                if tag and len(tag.split()) <= 5:  # Max 5 words per tag
                    tags.append(tag)
            
            # Return exactly 2-3 tags
            if len(tags) >= 2:
                return tags[:3]
            elif len(tags) == 1:
                # If only got 1 tag, add a generic one based on sports
                if sports_list:
                    tags.append(f"{sports_list[0]} enthusiast")
                return tags[:2]
        
        # Fallback tags if AI fails
        logger.warning(f"AI tag generation returned insufficient tags for user {user_profile.user.id}")
        return generate_fallback_tags(user_profile, sports_list)
        
    except Exception as e:
        logger.error(f"Error generating profile tags for user {user_profile.user.id}: {e}")
        return generate_fallback_tags(user_profile, sports_list if 'sports_list' in locals() else [])


def generate_fallback_tags(user_profile, sports_list=None):
    """
    Generate simple fallback tags when AI generation fails.
    
    Args:
        user_profile: UserProfile instance
        sports_list: List of sport names (optional)
        
    Returns:
        List of 2-3 simple tags
    """
    tags = []
    
    # Sport-based tag
    if sports_list and len(sports_list) > 0:
        tags.append(f"{sports_list[0]} enthusiast")
    
    # Availability-based tag
    if user_profile.availability:
        if 'morning' in str(user_profile.availability).lower():
            tags.append("Morning athlete")
        elif 'weekend' in str(user_profile.availability).lower():
            tags.append("Weekend warrior")
        elif 'flexible' in user_profile.availability:
            tags.append("Flexible schedule")
        else:
            tags.append("Active member")
    
    # Generic tag if we don't have enough
    if len(tags) < 2:
        tags.append("Team player")
    
    return tags[:3]
