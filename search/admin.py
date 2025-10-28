from django.contrib import admin
from .models import UserProfile, SearchFilter, PartnerRecommendation, SearchHistory


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'level', 'location', 'created_at']
    list_filter = ['level', 'created_at']
    search_fields = ['user__username', 'location', 'bio']
    readonly_fields = ['created_at']
    
    fieldsets = (
        ('User Info', {
            'fields': ('user', 'bio')
        }),
        ('Sports & Level', {
            'fields': ('sports', 'level', 'goals')
        }),
        ('Location', {
            'fields': ('location', 'latitude', 'longitude')
        }),
        ('Availability', {
            'fields': ('availability',)
        }),
        ('Metadata', {
            'fields': ('created_at',)
        }),
    )


@admin.register(SearchFilter)
class SearchFilterAdmin(admin.ModelAdmin):
    list_display = ['name', 'user', 'sport_type', 'level', 'is_favorite', 'created_at']
    list_filter = ['is_favorite', 'sport_type', 'level', 'created_at']
    search_fields = ['name', 'user__username', 'location']
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
    search_fields = ['user__username', 'recommended_user__username']
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
    search_fields = ['user__username', 'search_query']
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