# yourapp/context_processors.py
from .models import Invitation

def session_invitations(request):
    if request.user.is_authenticated:
        pending = Invitation.objects.filter(
            invitee=request.user,
            status='pending'
        ).select_related('session')[:5]
        return {
            'pending_invitations': pending,
            'pending_invitations_count': pending.count(),
        }
    return {}