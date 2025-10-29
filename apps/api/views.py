from django.http import JsonResponse
from django.db.models import Q
from apps.core.models import Sport


def api_index(request):
    return JsonResponse({'status': 'ok', 'service': 'TeamUp API placeholder'})


def search_sports(request):
    """
    API endpoint to search sports by name or category.
    Supports pagination and filtering.
    
    Query parameters:
    - q: search query (searches in name)
    - category: filter by category
    - limit: number of results (default: 20, max: 100)
    - offset: pagination offset (default: 0)
    """
    query = request.GET.get('q', '').strip()
    category = request.GET.get('category', '').strip()
    limit = min(int(request.GET.get('limit', 20)), 100)
    offset = int(request.GET.get('offset', 0))
    
    # Start with active sports
    sports = Sport.objects.filter(is_active=True)
    
    # Apply search filter
    if query:
        sports = sports.filter(
            Q(name__icontains=query) | 
            Q(description__icontains=query)
        )
    
    # Apply category filter
    if category:
        sports = sports.filter(category=category)
    
    # Get total count before pagination
    total_count = sports.count()
    
    # Apply pagination
    sports = sports[offset:offset + limit]
    
    # Serialize the results
    results = [
        {
            'id': sport.id,
            'name': sport.name,
            'slug': sport.slug,
            'emoji': sport.emoji,
            'category': sport.category,
            'popularity_score': sport.popularity_score,
        }
        for sport in sports
    ]
    
    return JsonResponse({
        'status': 'success',
        'results': results,
        'count': len(results),
        'total': total_count,
        'limit': limit,
        'offset': offset,
    })


def get_sport_categories(request):
    """
    API endpoint to get all available sport categories.
    """
    from apps.core.models import Sport
    
    categories = Sport._meta.get_field('category').choices
    
    return JsonResponse({
        'status': 'success',
        'categories': [
            {
                'value': value,
                'label': label
            }
            for value, label in categories
        ]
    })

