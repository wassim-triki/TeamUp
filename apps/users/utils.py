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
