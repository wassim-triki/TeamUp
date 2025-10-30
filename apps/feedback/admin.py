from django.contrib import admin
from django.utils.html import format_html
from django.utils.timesince import timesince
from django.contrib.auth.models import User

from .models import (
    Session,
    SessionFeedback,
    ParticipantFeedback,
    Badge,
    UserBadge,
)


# ==========================
# INLINES
# ==========================


class SessionFeedbackInline(admin.TabularInline):
    model = SessionFeedback
    extra = 0
    readonly_fields = ("created_at", "ai_summary")
    fields = (
        "user",
        "user_present",
        "rating",
        "punctual",
        "good_partner",
        "comment",
        "created_at",
    )
    autocomplete_fields = ["user"]


class ParticipantFeedbackInline(admin.TabularInline):
    model = ParticipantFeedback
    extra = 0
    readonly_fields = ("created_at",)
    fields = (
        "author",
        "target",
        "rating",
        "teamwork",
        "punctual",
        "comment",
        "created_at",
    )
    autocomplete_fields = ["author", "target"]


class UserBadgeInline(admin.TabularInline):
    model = UserBadge
    extra = 0
    readonly_fields = ("awarded_at",)
    autocomplete_fields = ["badge"]


# ==========================
# ADMIN MODELS
# ==========================


@admin.register(SessionFeedback)
class SessionFeedbackAdmin(admin.ModelAdmin):
    list_display = (
        "session",
        "user",
        "user_present",
        "rating_display",
        "punctual",
        "good_partner",
        "short_comment",
        "created_at",
    )
    list_filter = (
        "rating",
        "punctual",
        "good_partner",
        "user_present",
        "created_at",
        "session__created_at",
    )
    search_fields = (
        "session__title",
        "user__username",
        "user__email",
        "comment",
    )
    autocomplete_fields = ["session", "user"]
    readonly_fields = ("created_at",)

    def rating_display(self, obj):
        return "👍" if obj.rating == 1 else ("👎" if obj.rating == 0 else "—")

    rating_display.short_description = "Rating"

    def short_comment(self, obj):
        return (obj.comment[:40] + "...") if obj.comment else ""

    short_comment.short_description = "Comment"


@admin.register(ParticipantFeedback)
class ParticipantFeedbackAdmin(admin.ModelAdmin):
    list_display = (
        "session",
        "author",
        "target",
        "rating_display",
        "teamwork",
        "punctual",
        "short_comment",
        "created_at",
    )
    list_filter = (
        "rating",
        "teamwork",
        "punctual",
        "created_at",
        "session__created_at",
    )
    search_fields = (
        "session__title",
        "author__username",
        "target__username",
        "comment",
    )
    autocomplete_fields = ["session", "author", "target"]
    readonly_fields = ("created_at",)
    ordering = ["-created_at"]

    def rating_display(self, obj):
        return "👍" if obj.rating == 1 else ("👎" if obj.rating == 0 else "—")

    rating_display.short_description = "Rating"

    def short_comment(self, obj):
        return (obj.comment[:40] + "...") if obj.comment else ""

    short_comment.short_description = "Comment"


@admin.register(Badge)
class BadgeAdmin(admin.ModelAdmin):
    list_display = ("name", "criteria", "description_short", "icon_preview")
    search_fields = ("name", "criteria", "description")
    list_filter = ("criteria",)
    ordering = ["name"]

    def description_short(self, obj):
        return (
            (obj.description[:60] + "...")
            if len(obj.description) > 60
            else obj.description
        )

    description_short.short_description = "Description"

    def icon_preview(self, obj):
        if obj.icon:
            return format_html(
                '<img src="{}" width="30" height="30" style="border-radius:4px;" />',
                obj.icon.url,
            )
        return "—"

    icon_preview.short_description = "Icon"


@admin.register(UserBadge)
class UserBadgeAdmin(admin.ModelAdmin):
    list_display = ("user", "badge", "criteria", "awarded_at")
    list_filter = ("badge__criteria", "awarded_at")
    search_fields = (
        "user__username",
        "badge__name",
        "badge__criteria",
    )
    autocomplete_fields = ["user", "badge"]
    readonly_fields = ("awarded_at",)

    def criteria(self, obj):
        return obj.badge.criteria

    criteria.short_description = "Criteria"


# Optional: customize User admin to show badges inline
class CustomUserAdmin(admin.ModelAdmin):
    inlines = [UserBadgeInline]
    search_fields = ["username", "email"]
    list_display = ["username", "email", "is_staff", "is_active"]
    list_filter = ["is_staff", "is_active", "date_joined"]


# Uncomment to replace default User admin (optional)
# from django.contrib.auth.admin import UserAdmin as DefaultUserAdmin
# admin.site.unregister(User)
# admin.site.register(User, CustomUserAdmin)
