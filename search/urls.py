# search/urls.py
from django.urls import path
from . import views

app_name = 'search'

urlpatterns = [
    # Main search
    path('', views.search_partners, name='search_partners'),
    
    # Recommendations
    path('recommendations/', views.recommendations, name='recommendations'),
    path('recommendations/<int:recommendation_id>/dismiss/', 
         views.dismiss_recommendation, name='dismiss_recommendation'),
    
    # Search filters
    path('filters/save/', views.save_search_filter, name='save_filter'),
    
    # Search history
    path('history/', views.search_history_view, name='search_history'),
    
    # Partner details
    path('partner/<int:user_id>/', views.partner_detail, name='partner_detail'),
]