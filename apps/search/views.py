from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.http import JsonResponse
from django.conf import settings
import json
from math import radians, sin, cos, sqrt, atan2

# Import User and UserProfile from apps.users
from apps.users.models import User, UserProfile

# Import local models
from .models import SearchFilter, PartnerRecommendation, SearchHistory
from .forms import SearchFilterForm


def calculate_distance(lat1, lon1, lat2, lon2):
    """Calculate distance between two coordinates in km using Haversine formula"""
    R = 6371  # Earth's radius in km
    
    lat1, lon1, lat2, lon2 = map(radians, [lat1, lon1, lat2, lon2])
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    
    a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
    c = 2 * atan2(sqrt(a), sqrt(1-a))
    return R * c


def parse_sports(sports_field):
    """Helper function to parse sports JSON field"""
    try:
        if isinstance(sports_field, str):
            sports = json.loads(sports_field or '[]')
            return sports if isinstance(sports, list) else []
        elif isinstance(sports_field, list):
            return sports_field
        return []
    except (json.JSONDecodeError, TypeError):
        return []


@login_required
def search_partners(request):
    """Main search view with filters"""
    
    # Get search parameters
    sport = request.GET.get('sport', '')
    location = request.GET.get('location', '')
    max_distance = request.GET.get('max_distance', 10)
    level = request.GET.get('level', '')
    availability = request.GET.get('availability', '')
    
    # Start with all profiles
    profiles = UserProfile.objects.select_related('user').all()
    
    # Exclude current user if authenticated
    if request.user.is_authenticated:
        profiles = profiles.exclude(user=request.user)
    
    # Apply sport filter
    if sport:
        filtered_profiles = []
        for profile in profiles:
            profile_sports = parse_sports(profile.sports)
            if sport in profile_sports:
                filtered_profiles.append(profile)
        profiles = filtered_profiles
    else:
        profiles = list(profiles)
    
    # Add parsed sports to each profile for template
    for profile in profiles:
        profile.sports_list = parse_sports(profile.sports)
    
    # Save search history only if authenticated
    if request.user.is_authenticated:
        SearchHistory.objects.create(
            user=request.user,
            search_query=f"{sport} {location}".strip(),
            filters_used={
                'sport': sport,
                'location': location,
                'max_distance': max_distance,
                'level': level,
                'availability': availability
            },
            results_count=len(profiles)
        )
    
    # Get saved filters only if authenticated
    saved_filters = []
    if request.user.is_authenticated:
        saved_filters = SearchFilter.objects.filter(user=request.user)
    
    context = {
        'results': profiles[:20],  # Limit to 20 results
        'sport': sport,
        'location': location,
        'max_distance': max_distance,
        'level': level,
        'total_results': len(profiles),
        'saved_filters': saved_filters
    }
    
    return render(request, 'search/search_partners.html', context)


@login_required
def recommendations(request):
    """View showing AI-based partner recommendations"""
    
    # Get recommendations only if authenticated
    recommendations_list = []
    if request.user.is_authenticated:
        recommendations_list = PartnerRecommendation.objects.select_related(
            'recommended_user', 
            'recommended_user__profile'
        ).filter(
            user=request.user,
            is_dismissed=False
        )[:10]
        
        # Mark as viewed
        recommendations_list.update(is_viewed=True)
        
        # Add parsed sports to each recommendation
        for rec in recommendations_list:
            rec.recommended_user.profile.sports_list = parse_sports(
                rec.recommended_user.profile.sports
            )
    
    context = {
        'recommendations': recommendations_list,
    }
    
    return render(request, 'search/recommendations.html', context)

@login_required
def save_search_filter(request):
    """Save a search filter for quick access"""
    
    # Require authentication for this feature
    if not request.user.is_authenticated:
        return redirect('search:search_partners')
    
    if request.method == 'POST':
        form = SearchFilterForm(request.POST)
        if form.is_valid():
            search_filter = form.save(commit=False)
            search_filter.user = request.user
            search_filter.save()
            return redirect('search:search_partners')
    else:
        form = SearchFilterForm()
    
    return render(request, 'search/save_filter.html', {'form': form})


# @login_required  # Comment this out for now
def dismiss_recommendation(request, recommendation_id):
    """Dismiss a recommendation"""
    
    # Require authentication for this feature
    if not request.user.is_authenticated:
        return JsonResponse({'status': 'error', 'message': 'Authentication required'})
    
    recommendation = get_object_or_404(
        PartnerRecommendation, 
        id=recommendation_id, 
        user=request.user
    )
    recommendation.is_dismissed = True
    recommendation.save()
    
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({'status': 'success'})
    
    return redirect('search:recommendations')


# @login_required  # Comment this out for now
def search_history_view(request):
    """View user's search history"""
    
    # Get history only if authenticated
    history = []
    if request.user.is_authenticated:
        history = SearchHistory.objects.filter(user=request.user)[:20]
    
    context = {
        'history': history
    }
    
    return render(request, 'search/search_history.html', context)


# @login_required  # Comment this out for now
def partner_detail(request, user_id):
    """View detailed profile of a potential partner"""
    partner_user = get_object_or_404(User, id=user_id)
    partner_profile = get_object_or_404(UserProfile, user=partner_user)
    
    # Calculate distance only if user is authenticated and has a profile
    distance = None
    common_sports = []
    
    if request.user.is_authenticated:
        try:
            user_profile = UserProfile.objects.get(user=request.user)
            
            # Parse sports from JSON
            user_sports = parse_sports(user_profile.sports)
            partner_sports = parse_sports(partner_profile.sports)
            
            # Find common sports
            common_sports = list(set(user_sports) & set(partner_sports))
        except UserProfile.DoesNotExist:
            pass
    
    # Parse partner sports for display
    partner_sports_list = parse_sports(partner_profile.sports)
    
    context = {
        'partner': partner_profile,
        'partner_sports': partner_sports_list,
        'distance': distance,
        'common_sports': common_sports,
    }
    
    return render(request, 'search/partner_detail.html', context)