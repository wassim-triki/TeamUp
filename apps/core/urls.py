from django.urls import path
from . import views

app_name = 'core'

urlpatterns = [
    path('', views.index, name='index'),
    # Dashboard moved into core (Medium layout)
    path('dashboard/', views.dashboard_index, name='dashboard'),
]
