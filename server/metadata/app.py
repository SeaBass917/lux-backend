"""App configuration for the metadata app."""
from django.apps import AppConfig


class MetadataConfig(AppConfig):
    """Main configuration for the metadata app."""
    default_auto_field = "django.db.models.BigAutoField"
    name = "metadata"
