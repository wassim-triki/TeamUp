from django.contrib import admin
from .models import Session, Invitation, SuggestedSlot


# Inline pour gérer les invitations directement depuis Session
class InvitationInline(admin.TabularInline):
    model = Invitation
    extra = 1  # ajoute un formulaire vide par défaut


# Admin pour Session
class SessionAdmin(admin.ModelAdmin):
    list_display = ['sport_type', 'start_datetime', 'location', 'status', 'creator']
    list_filter = ['status', 'sport_type', 'creator', 'start_datetime']
    search_fields = ['location', 'description', 'creator__email']
    ordering = ['-start_datetime']
    inlines = [InvitationInline]
    readonly_fields = ['created_at', 'updated_at']


admin.site.register(Session, SessionAdmin)


# Admin simple pour Invitation
class InvitationAdmin(admin.ModelAdmin):
    list_display = ['session', 'invitee', 'status', 'rescheduled_datetime']
    list_filter = ['status']


admin.site.register(Invitation, InvitationAdmin)


# Admin simple pour SuggestedSlot
@admin.register(SuggestedSlot)
class SuggestedSlotAdmin(admin.ModelAdmin):
    list_display = ['session', 'proposed_datetime']
