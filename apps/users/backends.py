from django.contrib.auth.backends import ModelBackend
from django.contrib.auth import get_user_model

User = get_user_model()


class EmailAuthBackend(ModelBackend):
    """
    Custom authentication backend that allows users to log in using their email address.
    """
    def authenticate(self, request, username=None, password=None, **kwargs):
        """
        Authenticate using email instead of username.
        The 'username' parameter is actually the email in this context.
        """
        # Support both 'username' and 'email' parameters
        email = kwargs.get('email', username)
        
        if email is None or password is None:
            return None
        
        try:
            # Normalize email to lowercase
            email = email.lower().strip()
            user = User.objects.get(email=email)
            
            # Check if the password is correct
            if user.check_password(password):
                return user
        except User.DoesNotExist:
            # Run the default password hasher once to reduce the timing
            # difference between an existing and a nonexistent user (#20760).
            User().set_password(password)
            return None
        
        return None
    
    def get_user(self, user_id):
        """
        Get a user by their primary key.
        """
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None
