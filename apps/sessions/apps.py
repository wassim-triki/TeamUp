from django.apps import AppConfig

class SessionsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.sessions'
    label = 'user_sessions'  # <-- rend le label unique
    verbose_name = 'Sessions et Planification'
