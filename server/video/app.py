"""App configuration for the video app."""
from django.apps import AppConfig


class VideoConfig(AppConfig):
    """Main configuration for the video app."""
    default_auto_field = "django.db.models.BigAutoField"
    name = "video"
