from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.urls import reverse_lazy
from django.views.generic.edit import UpdateView, DeleteView
from django.db.models import Q
from django.core.mail import send_mail  # For optional email notification
from django.conf import settings  # For email config
from django.core.paginator import Paginator  # For pagination
from django.views.decorators.cache import cache_page  # Optional caching for AI
from .models import Session, Invitation, SuggestedSlot
from .forms import SessionForm, InviteForm, ResponseForm
from .services import generate_ai_insight  # Import the service for AI insights
from markdown import markdown  # For AI Markdown rendering (pip install markdown)

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

        # Pre-compute flags for template (avoid list conversion for performance)
        invited_session_ids = set(Invitation.objects.filter(invitee=request.user).values_list('session_id', flat=True))
        is_creator_ids = set(Session.objects.filter(creator=request.user).values_list('id', flat=True))

        # Pagination
        paginator = Paginator(queryset, 20)  # 20 per page
        page_number = request.GET.get('page')
        sessions = paginator.get_page(page_number)

        context = {
            'object_list': sessions,
            'invited_session_ids': invited_session_ids,
            'is_creator_ids': is_creator_ids,
        }
    else:
        # Limited public for anonymous
        queryset = Session.objects.filter(status__in=['proposed', 'confirmed']).order_by('-start_datetime')[:10]
        context = {'object_list': queryset}
    return render(request, 'sessions/list.html', context)


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
            
            # Optional: Email creator (use settings)
            try:
                send_mail(
                    subject='Join Request for Your Session',
                    message=f'{request.user.username} wants to join your {session.get_sport_type_display()} session on {session.start_datetime.date()}.',
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=[session.creator.email],
                    fail_silently=True,
                )
            except Exception:
                # Log if needed, but fail silently
                pass
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


@login_required  # Block anonymous creates
def create_session(request):
    """Create a new session (authenticated only)."""
    if request.method == 'POST':
        form = SessionForm(request.POST)
        if form.is_valid():
            session = form.save(commit=False)
            session.creator = request.user
            session.status = 'draft'  # Use model default
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
        form.fields['users'].queryset = available_users  # Set queryset post-init
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
        form.fields['users'].queryset = available_users  # Set for GET

    return render(request, 'sessions/invite.html', {'session': session, 'form': form, 'available_users': available_users})


@login_required
def respond_invitation(request, invitation_id):
    """Respond to a session invitation (supports HTMX + form)."""
    invitation = get_object_or_404(Invitation, id=invitation_id, invitee=request.user)

    # Prevent responding twice
    if invitation.status != 'pending':
        messages.info(request, 'This invitation has already been responded to.')
        return redirect('sessions:list')

    if request.method == 'POST':
        form = ResponseForm(request.POST)
        if form.is_valid():
            action = form.cleaned_data['action']
            invitation.status = action
            invitation.response_notes = form.cleaned_data.get('notes', '')

            # Optional: reschedule support
            if action == 'rescheduled' and form.cleaned_data.get('new_datetime'):
                invitation.rescheduled_datetime = form.cleaned_data['new_datetime']

            invitation.save()
            messages.success(
                request,
                f'Response submitted for {invitation.session.get_sport_type_display()} session.'
            )

            # If HTMX request, send empty response to remove the row
            if getattr(request, "htmx", False):
                return HttpResponse("")

            return redirect('sessions:list')
    else:
        form = ResponseForm()

    return render(request, 'sessions/respond.html', {
        'session': invitation.session,
        'invitation': invitation,
        'form': form
    })


@login_required
@cache_page(60 * 5)  # Cache for 5 minutes (optional, for API savings)
def ai_insight(request, pk):
    """Generate and display AI insights for a session."""
    session = get_object_or_404(Session, pk=pk)
    
    # Generate fresh insights (no model persistence; use cache decorator for reuse)
    raw_insights = generate_ai_insight(session)
    
    # Convert to HTML if valid
    if raw_insights and not raw_insights.startswith(('No insights', 'Failed', 'Gemini returned')):
        insights_html = markdown(raw_insights, extensions=['extra', 'fenced_code'])
    else:
        insights_html = None
        messages.warning(request, raw_insights or 'AI generation failed—try richer session details.')
    
    context = {
        'session': session,
        'insights_html': insights_html,
    }
    return render(request, 'sessions/ai_insight.html', context)


# Creator management for invitations (accept/refuse)
@login_required
def manage_invitation(request, invitation_id):
    """Allow the session creator to accept or refuse a pending invitation (join request)."""
    invitation = get_object_or_404(Invitation, id=invitation_id)
    session = invitation.session

    # Only the session creator can manage invitations
    if request.user != session.creator:
        messages.warning(request, 'Only the session creator can manage invitations.')
        return redirect('sessions:detail', pk=session.pk)

    if request.method == 'POST':
        action = request.POST.get('action')
        if action == 'accept':
            invitation.status = 'accepted'
            invitation.response_notes = request.POST.get('notes', '')
            invitation.save()
            messages.success(request, f"{invitation.invitee.username} has been accepted to the session.")
        elif action in ['refuse', 'decline']:
            invitation.status = 'refused'
            invitation.response_notes = request.POST.get('notes', '')
            invitation.save()
            messages.success(request, f"{invitation.invitee.username} has been declined.")
        else:
            messages.info(request, 'No action taken.')

    return redirect('sessions:detail', pk=session.pk)


@login_required
def manage_requests(request, pk):
    """Page for the session creator to view and manage pending join requests."""
    session = get_object_or_404(Session, pk=pk)
    if request.user != session.creator:
        messages.warning(request, 'Only the session creator can manage requests.')
        return redirect('sessions:detail', pk=pk)

    pending = session.invitation_set.filter(status='pending').select_related('invitee')

    if request.method == 'POST':
        # Bulk actions: accept_all / decline_all (add notes if needed via form)
        action = request.POST.get('action')
        if action == 'accept_all':
            updated = pending.update(status='accepted')
            messages.success(request, f'Accepted {updated} request(s).')
        elif action == 'decline_all':
            updated = pending.update(status='refused')
            messages.success(request, f'Declined {updated} request(s).')
        return redirect('sessions:manage_requests', pk=pk)

    return render(request, 'sessions/manage_requests.html', {
        'session': session,
        'pending': pending,
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
        # Decline all invitations ('refused' as 'cancelled' not in choices)
        Invitation.objects.filter(session=session).update(status='refused')
        messages.success(self.request, f'Session "{session.get_sport_type_display()}" deleted. All invites have been declined.')
        return super().delete(request, *args, **kwargs)

    def test_func(self):
        session = self.get_object()
        return self.request.user == session.creator

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Delete Session'
        context['session'] = self.get_object()  # For display in template
        return context