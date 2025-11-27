"""App configuration for the auth app."""
from django.apps import AppConfig


class AuthConfig(AppConfig):
    """Main configuration for the auth app."""
    default_auto_field = "django.db.models.BigAutoField"
    name = "auth"
