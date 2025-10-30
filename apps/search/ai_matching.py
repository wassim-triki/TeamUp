"""
Simple AI-based partner matching algorithm
Calculates compatibility scores based on multiple factors
"""
import json
from apps.users.models import UserProfile
from .models import PartnerRecommendation


def parse_sports(sports_field):
    """Helper to parse sports JSON"""
    try:
        if isinstance(sports_field, str):
            return json.loads(sports_field or '[]')
        elif isinstance(sports_field, list):
            return sports_field
        return []
    except (json.JSONDecodeError, TypeError):
        return []


def calculate_match_score(user_profile, partner_profile):
    """
    Calculate match score between two users (0-100)
    Based on: sports, location, age, availability
    """
    score = 0
    reasons = []
    explanation = {}
    
    # Get sports lists
    user_sports = set(parse_sports(user_profile.sports))
    partner_sports = set(parse_sports(partner_profile.sports))
    
    # 1. SPORTS COMPATIBILITY (40 points max)
    common_sports = user_sports & partner_sports
    if common_sports:
        sports_score = min(len(common_sports) * 15, 40)  # 15 points per common sport, max 40
        score += sports_score
        explanation['sport_match'] = True
        explanation['common_sports_count'] = len(common_sports)
        if len(common_sports) == 1:
            reasons.append(f'Both practice {list(common_sports)[0]}')
        else:
            reasons.append(f'{len(common_sports)} sports in common')
    else:
        explanation['sport_match'] = False
    
    # 2. LOCATION COMPATIBILITY (25 points max)
    if user_profile.country == partner_profile.country:
        score += 15
        explanation['same_country'] = True
        
        if user_profile.city and partner_profile.city:
            if user_profile.city.lower() == partner_profile.city.lower():
                score += 10
                explanation['same_city'] = True
                reasons.append(f'Both in {user_profile.city}')
            else:
                explanation['same_city'] = False
                reasons.append(f'Same country ({user_profile.get_country_display()})')
        else:
            reasons.append(f'Same country ({user_profile.get_country_display()})')
    else:
        explanation['same_country'] = False
    
    # 3. AGE COMPATIBILITY (20 points max)
    if user_profile.age and partner_profile.age:
        age_diff = abs(user_profile.age - partner_profile.age)
        explanation['age_difference'] = age_diff
        
        if age_diff <= 5:
            score += 20
            reasons.append('Similar age group')
        elif age_diff <= 10:
            score += 15
            reasons.append('Compatible age range')
        elif age_diff <= 15:
            score += 10
    
    # 4. AVAILABILITY COMPATIBILITY (15 points max)
    if user_profile.availability and partner_profile.availability:
        # Simple text matching for availability
        user_avail = user_profile.availability.lower()
        partner_avail = partner_profile.availability.lower()
        
        # Check for common time slots
        common_times = []
        for time_keyword in ['morning', 'afternoon', 'evening', 'weekend', 'flexible']:
            if time_keyword in user_avail and time_keyword in partner_avail:
                common_times.append(time_keyword)
        
        if common_times:
            score += min(len(common_times) * 7, 15)
            explanation['availability_match'] = True
            reasons.append('Similar availability')
        else:
            explanation['availability_match'] = False
    
    # 5. BONUS: Same gender preference for some sports (bonus 5 points)
    if user_profile.gender == partner_profile.gender:
        score += 5
        explanation['same_gender'] = True
    
    # Ensure score is between 0-100
    final_score = min(max(score, 0), 100)
    
    return final_score, reasons, explanation


def generate_recommendations_for_user(user, limit=10):
    """
    Generate AI recommendations for a user
    Returns: Number of recommendations created
    """
    try:
        user_profile = UserProfile.objects.get(user=user)
    except UserProfile.DoesNotExist:
        return 0
    
    # Get all other users with profiles
    other_profiles = UserProfile.objects.select_related('user').exclude(
        user=user
    ).filter(
        user__is_active=True
    )
    
    # Calculate scores for all potential partners
    potential_matches = []
    
    for partner_profile in other_profiles:
        # Skip if recommendation already exists
        if PartnerRecommendation.objects.filter(
            user=user,
            recommended_user=partner_profile.user
        ).exists():
            continue
        
        # Calculate match score
        score, reasons, explanation = calculate_match_score(user_profile, partner_profile)
        
        # Only recommend if score is above threshold (60%)
        if score >= 60:
            potential_matches.append({
                'partner': partner_profile.user,
                'score': score,
                'reasons': reasons,
                'explanation': explanation
            })
    
    # Sort by score (highest first)
    potential_matches.sort(key=lambda x: x['score'], reverse=True)
    
    # Create recommendations for top matches
    created_count = 0
    for match in potential_matches[:limit]:
        PartnerRecommendation.objects.create(
            user=user,
            recommended_user=match['partner'],
            match_score=match['score'],
            explanation=match['explanation'],
            reasons=match['reasons']
        )
        created_count += 1
    
    return created_count


def refresh_recommendations_for_user(user):
    """
    Delete old recommendations and generate new ones
    """
    # Delete old recommendations
    PartnerRecommendation.objects.filter(user=user).delete()
    
    # Generate new ones
    return generate_recommendations_for_user(user)