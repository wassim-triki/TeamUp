from django.urls import path
from . import views

urlpatterns = [
    path(
        "session/<int:session_id>/confirm/",
        views.confirm_presence,
        name="confirm_presence",
    ),
    path(
        "session/<int:session_id>/feedback/",
        views.submit_feedback,
        name="submit_feedback",
    ),
    path("session/<int:session_id>/", views.session_feedback, name="session_feedback"),
    path(
        "session/<int:session_id>/summary/",
        views.generate_session_summary,
        name="generate_session_summary",
    ),
    path("feedback/<int:pk>/edit/", views.edit_feedback, name="edit_feedback"),
    path("feedback/<int:pk>/delete/", views.delete_feedback, name="delete_feedback"),
    path("user/summary/", views.user_feedback_summary, name="user_feedback_summary"),
    path(
        "ai-summary/", views.generate_user_summary_api, name="generate_user_summary_api"
    ),
    path(
        "session/<int:session_id>/participant-feedback/",
        views.give_participant_feedback,
        name="give_participant_feedback",
        ),
]
