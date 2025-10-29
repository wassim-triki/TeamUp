from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

app_name = 'users'

urlpatterns = [
    # Authentication
    path('login/', views.login_view, name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    
    # Multi-step Signup Wizard
    path('signup/', views.signup_view, name='signup'),  # Redirects to step 1
    path('signup/step1/', views.signup_step1_email, name='signup_step1'),
    path('signup/step2/', views.signup_step2_details, name='signup_step2'),
    path('signup/step3/', views.signup_step3_sports, name='signup_step3'),
    path('signup/step4/', views.signup_step4_availability, name='signup_step4'),
    
    # Email Verification
    path('email-sent/', views.email_sent_view, name='email_sent'),
    path('verify/<str:token>/', views.verify_email, name='verify_email'),
    path('resend-verification/', views.resend_verification, name='resend_verification'),
    
    # Profile Management
    path('profile/edit/', views.edit_profile, name='edit_profile'),
    path('profile/edit/sports/', views.edit_sports, name='edit_sports'),
    path('profile/change-password/', views.change_password, name='change_password'),
    path('profile/manage-contact/', views.manage_contact, name='manage_contact'),
    path('profile/<str:username>/', views.profile_view, name='profile'),
]