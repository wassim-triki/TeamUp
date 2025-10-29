from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.urls import reverse_lazy
from django.views.generic.edit import UpdateView, DeleteView
from django.db.models import Q
from django.core.mail import send_mail  # For optional email notification
from .models import Session, Invitation, SuggestedSlot
from .forms import SessionForm, InviteForm, ResponseForm

User = get_user_model()

def session_list(request):
    """List all sessions for authenticated users (discovery mode); limited public for anonymous."""
    if request.user.is_authenticated:
        # Show ALL sessions for discovery
        queryset = Session.objects.all().select_related('creator').prefetch_related('invitation_set__invitee').order_by('-start_datetime')
        
        # Optional: Filter to personal if ?view=my
        if request.GET.get('view') == 'my':
            queryset = Session.objects.filter(
                Q(creator=request.user) | 
                Q(invitees=request.user)
            ).select_related('creator').prefetch_related('invitation_set__invitee').distinct().order_by('-start_datetime')
    else:
        # Limited public for anonymous
        queryset = Session.objects.filter(status__in=['proposed', 'confirmed']).order_by('-start_datetime')[:10]
    return render(request, 'sessions/list.html', {'object_list': queryset})


def session_detail(request, pk):
    """Show session details: accessible to all authenticated users."""
    session = get_object_or_404(Session, pk=pk)
    
    # Anonymous: only public sessions
    if not request.user.is_authenticated and session.status not in ['proposed', 'confirmed']:
        messages.warning(request, 'This session is private. Log in to view.')
        return redirect('sessions:list')
    
    # Pre-compute for template
    invitations = session.invitation_set.select_related('invitee').all()
    responses_count = session.invitation_set.filter(status__in=['accepted', 'refused', 'rescheduled']).count()
    responses_with_notes = session.invitation_set.filter(response_notes__isnull=False).select_related('invitee').all()
    user_invitation = None
    if request.user.is_authenticated:
        user_invitation = session.invitation_set.filter(invitee=request.user).first()

    context = {
        'session': session,
        'invitations': invitations,
        'responses_count': responses_count,
        'responses_with_notes': responses_with_notes,
        'user_invitation': user_invitation,
    }

    # Handle join request (POST)
    if request.method == 'POST' and request.user.is_authenticated:
        if session.creator == request.user:
            messages.info(request, 'You are the creator of this session.')
        elif user_invitation:
            messages.info(request, 'You are already invited.')
        else:
            # Create pending invitation as join request
            Invitation.objects.get_or_create(
                session=session,
                invitee=request.user,
                defaults={'status': 'pending'}
            )
            messages.success(request, 'Join request sent! The creator will be notified.')
            
            # Optional: Email creator (configure SMTP in settings.py)
            try:
                send_mail(
                    'Join Request for Your Session',
                    f'{request.user.username} wants to join your {session.get_sport_type_display()} session.',
                    'noreply@teamup.com',  # Update with your email
                    [session.creator.email],
                    fail_silently=True,
                )
            except:
                pass  # Fail silently if email not configured
        return redirect('sessions:detail', pk=pk)

    return render(request, 'sessions/detail.html', context)


@login_required
def request_join(request, pk):
    """Alternative endpoint for join request (if using separate URL)."""
    session = get_object_or_404(Session, pk=pk)
    if session.creator == request.user or session.invitation_set.filter(invitee=request.user).exists():
        messages.info(request, 'You are already involved in this session.')
        return redirect('sessions:detail', pk=pk)
    
    Invitation.objects.get_or_create(
        session=session,
        invitee=request.user,
        defaults={'status': 'pending'}
    )
    messages.success(request, 'Join request sent to the creator!')
    return redirect('sessions:detail', pk=pk)


# ... (rest of your views remain the same: create_session, invite_users, respond_invitation, ai_suggest_slots, SessionUpdateView, SessionDeleteView)
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
            session.status = 'proposed'  # Set initial status if model has it
            session.save()
            messages.success(request, 'Session created successfully!')
            return redirect('sessions:detail', pk=session.pk)
    else:
        form = SessionForm()
    return render(request, 'sessions/session_form.html', {
        'form': form,
        'title': 'Create Session',
        'submit_text': 'Create Session'
    })


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


# New views for edit and delete
class SessionUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Session
    form_class = SessionForm
    template_name = 'sessions/session_form.html'
    success_url = reverse_lazy('sessions:list')

    def form_valid(self, form):
        messages.success(self.request, 'Session updated successfully!')
        return super().form_valid(form)

    def test_func(self):
        session = self.get_object()
        return self.request.user == session.creator

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Edit Session'
        context['submit_text'] = 'Update Session'
        return context


class SessionDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Session
    template_name = 'sessions/session_confirm_delete.html'
    success_url = reverse_lazy('sessions:list')

    def delete(self, request, *args, **kwargs):
        session = self.get_object()
        # Cancel all invitations (assuming Invitation has status field)
        Invitation.objects.filter(session=session).update(status='cancelled')
        messages.success(self.request, f'Session "{session.get_sport_type_display()}" deleted. All invites have been cancelled.')
        return super().delete(request, *args, **kwargs)

    def test_func(self):
        session = self.get_object()
        return self.request.user == session.creator

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Delete Session'
        context['session'] = self.get_object()  # For display in template
        return context