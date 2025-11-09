"""User app configuration."""
from django.apps import AppConfig


class UserConfig(AppConfig):
    """Main configuration for the user app."""
    default_auto_field = "django.db.models.BigAutoField"
    name = "users"
