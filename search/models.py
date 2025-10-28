# search/models.py
from django.db import models
from django.contrib.auth.models import User

# Temporary stub models - to be replaced by team members' implementations
class UserProfile(models.Model):
    """Temporary model - will be replaced by team member's implementation"""
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    sports = models.JSONField(default=list)  # e.g., ["Football", "Basketball"]
    level = models.CharField(max_length=50, choices=[
        ('beginner', 'Beginner'),
        ('intermediate', 'Intermediate'),
        ('advanced', 'Advanced'),
        ('expert', 'Expert')
    ])
    location = models.CharField(max_length=255, blank=True)
    latitude = models.FloatField(null=True, blank=True)
    longitude = models.FloatField(null=True, blank=True)
    availability = models.JSONField(default=dict)  # e.g., {"monday": ["08:00-10:00", "18:00-20:00"]}
    goals = models.JSONField(default=list)  # e.g., ["weight loss", "competition"]
    bio = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username}'s profile"


# Your actual search-related models
class SearchFilter(models.Model):
    """Stores user's search filters for quick access"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='search_filters')
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
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='recommendations')
    recommended_user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='recommended_to')
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
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='search_history')
    search_query = models.CharField(max_length=255)
    filters_used = models.JSONField(default=dict)
    results_count = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name_plural = 'Search histories'

    def __str__(self):
        return f"{self.user.username} - {self.search_query} ({self.created_at})"