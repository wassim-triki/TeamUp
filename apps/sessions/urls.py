from django.urls import path
from . import views

app_name = 'sessions'

urlpatterns = [
    path('', views.session_list, name='list'),
    path('create/', views.create_session, name='create'),
    path('detail/<int:pk>/', views.session_detail, name='detail'),
    path('invite/<int:pk>/', views.invite_users, name='invite'),
    path('respond/<int:invitation_id>/', views.respond_invitation, name='respond'),
    path('ai-suggest/<int:pk>/', views.ai_suggest_slots, name='ai_suggest'),
]
