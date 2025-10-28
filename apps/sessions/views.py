from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from .models import Session, Invitation, SuggestedSlot
from .forms import SessionForm, InviteForm, ResponseForm

User = get_user_model()

def session_list(request):
    """List all sessions (public for anonymous, personal for logged-in users)."""
    if request.user.is_authenticated:
        queryset = Session.objects.filter(
            Q(creator=request.user) | Q(invitees=request.user)
        ).select_related('creator').prefetch_related('invitation_set__invitee').distinct().order_by('-start_datetime')
    else:
        queryset = Session.objects.filter(status__in=['proposed', 'confirmed']).order_by('-start_datetime')[:10]
    return render(request, 'sessions/list.html', {'object_list': queryset})


def create_session(request):
    """Create a new session. Anonymous users are assigned to the first user."""
    if request.method == 'POST':
        form = SessionForm(request.POST)
        if form.is_valid():
            session = form.save(commit=False)
            if request.user.is_authenticated:
                session.creator = request.user
            else:
                first_user = User.objects.first()
                if first_user:
                    session.creator = first_user
                else:
                    messages.error(request, 'No users in DB. Create one via admin.')
                    return redirect('sessions:list')
            session.save()
            messages.success(request, 'Session created successfully!')
            return redirect('sessions:detail', pk=session.pk)
    else:
        form = SessionForm()
    return render(request, 'sessions/create.html', {'form': form})


def session_detail(request, pk):
    """Show session details if allowed."""
    session = get_object_or_404(Session, pk=pk)
    if not request.user.is_authenticated and session.status not in ['proposed', 'confirmed']:
        messages.warning(request, 'This session is private. Log in to view.')
        return redirect('sessions:list')
    if request.user.is_authenticated:
        if session.creator != request.user and not session.invitation_set.filter(invitee=request.user).exists():
            messages.warning(request, 'Access denied for private session.')
            return redirect('sessions:list')
    return render(request, 'sessions/detail.html', {'session': session})


@login_required
def invite_users(request, pk):
    """Invite users to a session (only by creator)."""
    session = get_object_or_404(Session, pk=pk)
    
    if session.creator != request.user:
        messages.warning(request, 'Only the creator can invite users.')
        return redirect('sessions:detail', pk=pk)

    # Get users who are not already invited and not the creator
    excluded_users = [request.user.id] + list(session.invitation_set.values_list('invitee_id', flat=True))
    available_users = User.objects.exclude(id__in=excluded_users)

    if request.method == 'POST':
        form = InviteForm(request.POST)
        # Set the queryset after form initialization
        form.fields['users'].queryset = available_users
        
        if form.is_valid():
            selected_users = form.cleaned_data['users']
            created_count = 0
            for user in selected_users:
                invitation, created_new = Invitation.objects.get_or_create(
                    session=session,
                    invitee=user,
                    defaults={'status': 'pending'}
                )
                if created_new:
                    created_count += 1
            
            if created_count > 0:
                messages.success(request, f'{created_count} invitation(s) sent!')
            else:
                messages.info(request, 'Selected users were already invited.')
            return redirect('sessions:detail', pk=pk)
    else:
        form = InviteForm()
        # Set the queryset after form initialization
        form.fields['users'].queryset = available_users

    return render(request, 'sessions/invite.html', {'session': session, 'form': form, 'available_users': available_users})


@login_required
def respond_invitation(request, invitation_id):
    """Respond to a session invitation."""
    invitation = get_object_or_404(Invitation, id=invitation_id)
    
    if invitation.invitee != request.user:
        messages.warning(request, 'You can only respond to your own invitations.')
        return redirect('sessions:list')

    if request.method == 'POST':
        form = ResponseForm(request.POST)
        if form.is_valid():
            action = form.cleaned_data['action']
            invitation.status = action
            invitation.response_notes = form.cleaned_data.get('notes', '')
            
            if action == 'reschedule' and form.cleaned_data.get('new_datetime'):
                invitation.rescheduled_datetime = form.cleaned_data['new_datetime']
            
            invitation.save()
            messages.success(request, f'Response submitted for {invitation.session.get_sport_type_display()} session.')
            return redirect('sessions:list')
    else:
        form = ResponseForm(initial={'action': invitation.status})

    return render(request, 'sessions/respond.html', {
        'session': invitation.session,
        'invitation': invitation,
        'form': form
    })


@login_required
def ai_suggest_slots(request, pk):
    """Show AI suggested slots for a session (creator only)."""
    session = get_object_or_404(Session, pk=pk)
    
    if session.creator != request.user:
        messages.warning(request, 'Only the creator can view AI suggestions.')
        return redirect('sessions:detail', pk=pk)

    suggestions = session.suggestions.all()
    return render(request, 'sessions/ai_suggest.html', {
        'session': session,
        'suggestions': suggestions
    })