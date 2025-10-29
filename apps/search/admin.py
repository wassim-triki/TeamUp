from django.contrib import admin
from .models import SearchFilter, PartnerRecommendation, SearchHistory

# DON'T import or register UserProfile - it's managed by apps.users


@admin.register(SearchFilter)
class SearchFilterAdmin(admin.ModelAdmin):
    list_display = ['name', 'user', 'sport_type', 'level', 'is_favorite', 'created_at']
    list_filter = ['is_favorite', 'sport_type', 'level', 'created_at']
    search_fields = ['name', 'user__username', 'user__email', 'location']
    readonly_fields = ['created_at']
    
    fieldsets = (
        ('Filter Info', {
            'fields': ('user', 'name', 'is_favorite')
        }),
        ('Search Criteria', {
            'fields': ('sport_type', 'location', 'max_distance_km', 'level')
        }),
        ('Availability', {
            'fields': ('availability_days', 'availability_times')
        }),
        ('Metadata', {
            'fields': ('created_at',)
        }),
    )


@admin.register(PartnerRecommendation)
class PartnerRecommendationAdmin(admin.ModelAdmin):
    list_display = ['user', 'recommended_user', 'match_score', 'is_viewed', 'is_dismissed', 'created_at']
    list_filter = ['is_viewed', 'is_dismissed', 'created_at']
    search_fields = ['user__username', 'user__email', 'recommended_user__username', 'recommended_user__email']
    readonly_fields = ['created_at']
    
    fieldsets = (
        ('Recommendation', {
            'fields': ('user', 'recommended_user', 'match_score')
        }),
        ('Explanation', {
            'fields': ('explanation', 'reasons')
        }),
        ('Status', {
            'fields': ('is_viewed', 'is_dismissed', 'created_at')
        }),
    )
    
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.select_related('user', 'recommended_user')


@admin.register(SearchHistory)
class SearchHistoryAdmin(admin.ModelAdmin):
    list_display = ['user', 'search_query', 'results_count', 'created_at']
    list_filter = ['created_at']
    search_fields = ['user__username', 'user__email', 'search_query']
    readonly_fields = ['created_at']
    
    fieldsets = (
        ('Search Info', {
            'fields': ('user', 'search_query', 'results_count')
        }),
        ('Filters Used', {
            'fields': ('filters_used',)
        }),
        ('Metadata', {
            'fields': ('created_at',)
        }),
    )