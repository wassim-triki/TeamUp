from django.contrib import admin
from .models import Example, Sport


@admin.register(Sport)
class SportAdmin(admin.ModelAdmin):
    list_display = ('emoji', 'name', 'category', 'popularity_score', 'is_active', 'created_at')
    list_filter = ('category', 'is_active')
    search_fields = ('name', 'description')
    prepopulated_fields = {'slug': ('name',)}
    list_editable = ('is_active', 'popularity_score')
    ordering = ['-popularity_score', 'name']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'slug', 'emoji', 'description')
        }),
        ('Classification', {
            'fields': ('category', 'popularity_score', 'is_active')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    readonly_fields = ('created_at', 'updated_at')


@admin.register(Example)
class ExampleAdmin(admin.ModelAdmin):
    list_display = ('id', 'name')
