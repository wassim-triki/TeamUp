from django import template

register = template.Library()


@register.filter(name='user_initials')
def user_initials(user):
    """
    Returns user initials based on first_name/last_name, username, or email.
    Falls back gracefully if user or attributes are missing.
    
    Usage in template: {{ user|user_initials }}
    """
    if not user:
        return "?"
    
    # Try to get first_name and last_name from profile
    if hasattr(user, 'profile'):
        first_name = getattr(user.profile, 'first_name', '').strip()
        last_name = getattr(user.profile, 'last_name', '').strip()
        
        if first_name and last_name:
            return f"{first_name[0]}{last_name[0]}".upper()
        elif first_name:
            return first_name[:2].upper() if len(first_name) >= 2 else first_name[0].upper()
        elif last_name:
            return last_name[:2].upper() if len(last_name) >= 2 else last_name[0].upper()
    
    # Fall back to username
    if hasattr(user, 'username') and user.username:
        username = user.username.strip()
        if len(username) >= 2:
            return username[:2].upper()
        elif len(username) == 1:
            return username[0].upper()
    
    # Fall back to email
    if hasattr(user, 'email') and user.email:
        email = user.email.strip()
        if '@' in email:
            return email[0].upper()
        elif len(email) > 0:
            return email[0].upper()
    
    return "?"


@register.filter(name='user_display_name')
def user_display_name(user):
    """
    Returns the best display name for a user.
    Tries full_name property (first_name + last_name), then username, then email.
    
    Usage in template: {{ user|user_display_name }}
    """
    if not user:
        return "Unknown User"
    
    # Try to get full_name from profile
    if hasattr(user, 'profile') and hasattr(user.profile, 'full_name'):
        full_name = user.profile.full_name
        if full_name and full_name != user.username:  # Don't return username again
            return full_name
    
    # Fall back to username
    if hasattr(user, 'username') and user.username:
        return user.username
    
    # Fall back to email
    if hasattr(user, 'email') and user.email:
        return user.email.split('@')[0]
    
    return "Unknown User"


@register.filter(name='user_avatar_url')
def user_avatar_url(user):
    """
    Returns the URL of the user's avatar if they have one.
    Returns None if no avatar is set.
    
    Usage in template: {{ user|user_avatar_url }}
    """
    if not user:
        return None
    
    if hasattr(user, 'profile') and user.profile.avatar:
        return user.profile.avatar.url
    
    return None
