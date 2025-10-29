from django.db import models
from django.utils.text import slugify


class Sport(models.Model):
    """
    Sport model to store all available sports with their icons and metadata.
    This allows for easy management and scalability of sports offerings.
    """
    name = models.CharField(max_length=100, unique=True, help_text="Name of the sport")
    slug = models.SlugField(max_length=100, unique=True, blank=True, help_text="URL-friendly version of the name")
    emoji = models.CharField(max_length=10, default='🏃', help_text="Emoji icon representing the sport")
    description = models.TextField(blank=True, help_text="Brief description of the sport")
    is_active = models.BooleanField(default=True, help_text="Whether this sport is available for selection")
    category = models.CharField(
        max_length=50, 
        choices=[
            ('team', 'Team Sport'),
            ('individual', 'Individual Sport'),
            ('racket', 'Racket Sport'),
            ('water', 'Water Sport'),
            ('combat', 'Combat Sport'),
            ('fitness', 'Fitness & Gym'),
            ('outdoor', 'Outdoor Activity'),
            ('other', 'Other'),
        ],
        default='other',
        help_text="Category of the sport"
    )
    popularity_score = models.IntegerField(default=0, help_text="Score used for sorting popular sports")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-popularity_score', 'name']
        verbose_name = 'Sport'
        verbose_name_plural = 'Sports'
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"{self.emoji} {self.name}"
    
    def increment_popularity(self):
        """Increment popularity score when a user selects this sport"""
        self.popularity_score += 1
        self.save(update_fields=['popularity_score'])


# Add shared models for the public site here.
class Example(models.Model):
    name = models.CharField(max_length=200)

    def __str__(self):
        return self.name
