"""App configuration for the manga app."""
from django.apps import AppConfig


class MangaConfig(AppConfig):
    """Main configuration for the manga app."""
    default_auto_field = "django.db.models.BigAutoField"
    name = "manga"
