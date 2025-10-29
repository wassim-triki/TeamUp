from django.urls import path
from . import views

app_name = 'api'

urlpatterns = [
    path('', views.api_index, name='index'),
    path('sports/search/', views.search_sports, name='search_sports'),
    path('sports/categories/', views.get_sport_categories, name='sport_categories'),
]
