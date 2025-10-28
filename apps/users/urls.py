from django.urls import path
from . import views

app_name = 'users'

urlpatterns = [
    # Authentication
    path('login/', views.login_view, name='login'),
    
    # Multi-step Signup Wizard
    path('signup/', views.signup_view, name='signup'),  # Redirects to step 1
    path('signup/step1/', views.signup_step1_email, name='signup_step1'),
    path('signup/step2/', views.signup_step2_details, name='signup_step2'),
    path('signup/step3/', views.signup_step3_confirm, name='signup_step3'),
    
    # Email Verification
    path('email-sent/', views.email_sent_view, name='email_sent'),
    path('verify/<str:token>/', views.verify_email, name='verify_email'),
    path('resend-verification/', views.resend_verification, name='resend_verification'),
]
