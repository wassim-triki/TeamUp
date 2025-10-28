# search/views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.contrib.auth.models import User
from django.http import JsonResponse
from .models import UserProfile, SearchFilter, PartnerRecommendation, SearchHistory
from .forms import SearchFilterForm
import json
from math import radians, sin, cos, sqrt, atan2


def calculate_distance(lat1, lon1, lat2, lon2):
    """Calculate distance between two coordinates in km using Haversine formula"""
    R = 6371  # Earth's radius in km
    
    lat1, lon1, lat2, lon2 = map(radians, [lat1, lon1, lat2, lon2])
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    
    a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
    c = 2 * atan2(sqrt(a), sqrt(1-a))
    return R * c


# @login_required  # Comment this out for now
def search_partners(request):
    """Main search view with filters"""
    
    # Get search parameters
    sport = request.GET.get('sport', '')
    location = request.GET.get('location', '')
    max_distance = request.GET.get('max_distance', 10)
    level = request.GET.get('level', '')
    availability = request.GET.get('availability', '')
    
    # Start with all profiles
    results = UserProfile.objects.all()
    
    # Exclude current user if authenticated
    if request.user.is_authenticated:
        results = results.exclude(user=request.user)
    
    # Apply filters
    if sport:
        results = results.filter(sports__contains=sport)
    
    if level:
        results = results.filter(level=level)
    
    # Location-based filtering - only if user is authenticated and has a profile
    if request.user.is_authenticated:
        try:
            user_profile = UserProfile.objects.get(user=request.user)
            if user_profile.latitude and user_profile.longitude and max_distance:
                try:
                    max_dist = float(max_distance)
                    nearby_profiles = []
                    
                    for profile in results:
                        if profile.latitude and profile.longitude:
                            distance = calculate_distance(
                                user_profile.latitude, 
                                user_profile.longitude,
                                profile.latitude,
                                profile.longitude
                            )
                            if distance <= max_dist:
                                profile.distance = round(distance, 1)
                                nearby_profiles.append(profile)
                    
                    results = sorted(nearby_profiles, key=lambda x: x.distance)
                except ValueError:
                    results = list(results)
            else:
                results = list(results)
        except UserProfile.DoesNotExist:
            results = list(results)
    else:
        results = list(results)
    
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
            results_count=len(results)
        )
    
    # Get saved filters only if authenticated
    saved_filters = []
    if request.user.is_authenticated:
        saved_filters = SearchFilter.objects.filter(user=request.user)
    
    context = {
        'results': results[:20],  # Limit to 20 results
        'sport': sport,
        'location': location,
        'max_distance': max_distance,
        'level': level,
        'total_results': len(results),
        'saved_filters': saved_filters
    }
    
    return render(request, 'search/search_partners.html', context)


# @login_required  # Comment this out for now
def recommendations(request):
    """View showing AI-based partner recommendations"""
    
    # Get recommendations only if authenticated
    recommendations_list = []
    if request.user.is_authenticated:
        recommendations_list = PartnerRecommendation.objects.filter(
            user=request.user,
            is_dismissed=False
        )[:10]
        
        # Mark as viewed
        recommendations_list.update(is_viewed=True)
    
    context = {
        'recommendations': recommendations_list,
    }
    
    return render(request, 'search/recommendations.html', context)


# @login_required  # Comment this out for now
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
    partner_profile = get_object_or_404(UserProfile, user_id=user_id)
    
    # Calculate distance only if user is authenticated and has a profile
    distance = None
    common_sports = []
    
    if request.user.is_authenticated:
        try:
            user_profile = UserProfile.objects.get(user=request.user)
            
            # Calculate distance if coordinates available
            if (user_profile.latitude and user_profile.longitude and 
                partner_profile.latitude and partner_profile.longitude):
                distance = round(calculate_distance(
                    user_profile.latitude,
                    user_profile.longitude,
                    partner_profile.latitude,
                    partner_profile.longitude
                ), 1)
            
            # Find common sports
            common_sports = list(set(user_profile.sports) & set(partner_profile.sports))
        except UserProfile.DoesNotExist:
            pass
    
    context = {
        'partner': partner_profile,
        'distance': distance,
        'common_sports': common_sports,
    }
    
    return render(request, 'search/partner_detail.html', context)