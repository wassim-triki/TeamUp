# search/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('', views.main_search_page, name='main_search_page'),
    path('recommendations/', views.ai_recommendations, name='ai_recommendations'),
    path('partner/<int:id>/', views.partner_details, name='partner_details'),
    path('history/', views.search_history, name='search_history'),
    path('filters/save/', views.save_filter, name='save_filter'),
]
