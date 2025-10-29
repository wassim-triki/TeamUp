from django import template

register = template.Library()


@register.filter(name='user_initials')
def user_initials(user):
    """
    Returns user initials based on display_name, username, or email.
    Falls back gracefully if user or attributes are missing.
    
    Usage in template: {{ user|user_initials }}
    """
    if not user:
        return "?"
    
    # Try to get display_name from profile
    if hasattr(user, 'profile') and user.profile.display_name:
        name = user.profile.display_name.strip()
        parts = name.split()
        if len(parts) >= 2:
            return f"{parts[0][0]}{parts[1][0]}".upper()
        elif len(parts) == 1 and len(parts[0]) > 0:
            return parts[0][0].upper()
    
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
    Tries display_name, then username, then email.
    
    Usage in template: {{ user|user_display_name }}
    """
    if not user:
        return "Unknown User"
    
    # Try to get display_name from profile
    if hasattr(user, 'profile') and user.profile.display_name:
        return user.profile.display_name
    
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
