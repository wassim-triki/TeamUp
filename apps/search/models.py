from django.db import models
from django.conf import settings


class SearchFilter(models.Model):
    """Stores user's search filters for quick access"""
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='search_filters')
    name = models.CharField(max_length=100)  # e.g., "My morning soccer search"
    sport_type = models.CharField(max_length=100, blank=True)
    location = models.CharField(max_length=255, blank=True)
    max_distance_km = models.IntegerField(default=10)
    level = models.CharField(max_length=50, blank=True)
    availability_days = models.JSONField(default=list)  # e.g., ["monday", "wednesday"]
    availability_times = models.JSONField(default=list)  # e.g., ["08:00-10:00"]
    is_favorite = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.name} - {self.user.username}"


class PartnerRecommendation(models.Model):
    """Stores AI recommendations for transparency and caching"""
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='recommendations')
    recommended_user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='recommended_to')
    match_score = models.FloatField()  # 0-100
    explanation = models.JSONField(default=dict)  # e.g., {"sport_match": true, "level_compatible": true, "distance_km": 2.5}
    reasons = models.JSONField(default=list)  # e.g., ["Same sport", "Similar level", "2.5km away"]
    created_at = models.DateTimeField(auto_now_add=True)
    is_viewed = models.BooleanField(default=False)
    is_dismissed = models.BooleanField(default=False)

    class Meta:
        ordering = ['-match_score', '-created_at']
        unique_together = ['user', 'recommended_user', 'created_at']

    def __str__(self):
        return f"Recommendation: {self.recommended_user.username} for {self.user.username} ({self.match_score}%)"


class SearchHistory(models.Model):
    """Track user searches for analytics and improvements"""
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='search_history')
    search_query = models.CharField(max_length=255)
    filters_used = models.JSONField(default=dict)
    results_count = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name_plural = 'Search histories'

    def __str__(self):
        return f"{self.user.username} - {self.search_query} ({self.created_at})"