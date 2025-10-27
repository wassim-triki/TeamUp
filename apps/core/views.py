from django.shortcuts import render


def index(request):
    """Simple landing view to verify templates are wired."""
    return render(request, 'core/index.html')


def dashboard_index(request):
    """Dashboard view moved into core (Medium layout): simple placeholder."""
    return render(request, 'core/dashboard.html')
