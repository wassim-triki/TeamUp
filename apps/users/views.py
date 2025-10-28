from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from django.contrib.auth.models import User


def login_view(request):
    """Simple login handler: renders form and authenticates by username/password.
    Note: form currently uses email field; for now we accept email by finding the user
    with that email and authenticating by username.
    """
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        username = None
        if email:
            try:
                user_obj = User.objects.get(email=email)
                username = user_obj.username
            except User.DoesNotExist:
                username = None

        if username:
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect('core:dashboard')

    return render(request, 'users/login.html')


def signup_view(request):
    """Very small signup flow: create a user (username derived from email) and log them in.
    This is intentionally minimal for scaffold purposes — add validation and confirmation later.
    """
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        if email and password:
            username = email.split('@')[0]
            # ensure unique username
            base = username
            counter = 1
            while User.objects.filter(username=username).exists():
                username = f"{base}{counter}"
                counter += 1

            user = User.objects.create_user(username=username, email=email, password=password)
            # authenticate and login
            user = authenticate(request, username=username, password=password)
            if user:
                login(request, user)
                return redirect('core:dashboard')

    return render(request, 'users/signup.html')
