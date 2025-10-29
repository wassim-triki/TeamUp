from django.urls import path
from . import views

app_name = 'sessions'

urlpatterns = [
    path('', views.session_list, name='list'),
    path('create/', views.create_session, name='create'),
    path('detail/<int:pk>/', views.session_detail, name='detail'),
    path('invite/<int:pk>/', views.invite_users, name='invite'),
    path('respond/<int:invitation_id>/', views.respond_invitation, name='respond'),

    # ✅ Renamed AI insight route
    path('ai-insight/<int:pk>/', views.ai_insight, name='ai_insight'),

    # Edit/Delete
    path('<int:pk>/edit/', views.SessionUpdateView.as_view(), name='update'),
    path('<int:pk>/delete/', views.SessionDeleteView.as_view(), name='delete'),

    # Optional separate join path
    path('<int:pk>/request-join/', views.request_join, name='request_join'),

    # Creator manages pending invitations (accept/refuse)
    path('invitation/<int:invitation_id>/manage/', views.manage_invitation, name='manage_invitation'),

    # Page for session creators to manage join requests for a given session
    path('<int:pk>/manage-requests/', views.manage_requests, name='manage_requests'),
]
