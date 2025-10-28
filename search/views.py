# search/views.py
from django.shortcuts import get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from .models import SearchFilter, PartnerRecommendation, SearchHistory, UserProfile
from django.contrib.auth.models import User
from django.utils import timezone
import json

# -------------------------------
# /search/  → Main search page
# -------------------------------
@login_required
def main_search_page(request):
    """Display the main search page or perform a search."""
    if request.method == "GET":
        return JsonResponse({"message": "Welcome to the Main Search Page"})

    elif request.method == "POST":
        data = json.loads(request.body)
        query = data.get("query", "")
        filters = data.get("filters", {})
        results = list(UserProfile.objects.filter(sports__icontains=query).values())

        # Save search to history
        SearchHistory.objects.create(
            user=request.user,
            search_query=query,
            filters_used=filters,
            results_count=len(results)
        )
        return JsonResponse({
            "query": query,
            "filters": filters,
            "results_count": len(results),
            "results": results
        })


# -----------------------------------------
# /search/recommendations/ → AI Recommendations
# -----------------------------------------
@login_required
def ai_recommendations(request):
    """Fetch AI-based partner recommendations."""
    recs = PartnerRecommendation.objects.filter(user=request.user, is_dismissed=False)
    data = [{
        "recommended_user": r.recommended_user.username,
        "match_score": r.match_score,
        "reasons": r.reasons,
        "created_at": r.created_at
    } for r in recs]

    return JsonResponse({"recommendations": data})


# --------------------------------------------------
# /search/partner/<id>/ → Partner details
# --------------------------------------------------
@login_required
def partner_details(request, id):
    """View specific partner profile details."""
    partner = get_object_or_404(UserProfile, user__id=id)
    data = {
        "username": partner.user.username,
        "sports": partner.sports,
        "level": partner.level,
        "location": partner.location,
        "goals": partner.goals,
        "bio": partner.bio
    }
    return JsonResponse(data)


# --------------------------------------------------
# /search/history/ → Search history
# --------------------------------------------------
@login_required
def search_history(request):
    """List user's previous searches."""
    history = SearchHistory.objects.filter(user=request.user)
    data = [{
        "query": h.search_query,
        "filters": h.filters_used,
        "results_count": h.results_count,
        "created_at": h.created_at
    } for h in history]
    return JsonResponse({"history": data})


# --------------------------------------------------
# /search/filters/save/ → Save a filter
# --------------------------------------------------
@require_http_methods(["POST"])
@login_required
def save_filter(request):
    """Save a custom search filter."""
    data = json.loads(request.body)
    name = data.get("name")
    sport_type = data.get("sport_type", "")
    location = data.get("location", "")
    max_distance_km = data.get("max_distance_km", 10)
    level = data.get("level", "")
    availability_days = data.get("availability_days", [])
    availability_times = data.get("availability_times", [])
    is_favorite = data.get("is_favorite", False)

    filt = SearchFilter.objects.create(
        user=request.user,
        name=name,
        sport_type=sport_type,
        location=location,
        max_distance_km=max_distance_km,
        level=level,
        availability_days=availability_days,
        availability_times=availability_times,
        is_favorite=is_favorite
    )
    return JsonResponse({
        "message": "Filter saved successfully",
        "filter_id": filt.id
    })
